from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.utils import timezone
from django.db.models import Q, Count
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Club, Player, Fixture, MatchResult, Booking, Goal
from .forms import (
    FixtureForm, MatchResultForm, DynamicMatchResultForm, GoalFormSet, BookingFormSet, 
    ClubForm, PlayerForm, UserRegistrationForm
)
from .utils import calculate_table, get_recent_form, get_club_statistics


class HomeView(TemplateView):
    """Home page with links to main sections"""
    template_name = 'matches/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest fixtures (only those without results)
        upcoming_fixtures = Fixture.objects.filter(
            date__gte=timezone.now()
        ).exclude(
            result__isnull=False
        ).select_related('team1', 'team2').order_by('date')[:5]
        
        # Get latest results
        recent_results = MatchResult.objects.filter(
        ).select_related(
            'fixture__team1', 'fixture__team2'
        ).order_by('-fixture__date')[:5]
        
        # Calculate real statistics
        from .models import Club, Goal, Booking
        from django.db.models import Count, Sum
        
        total_clubs = Club.objects.count()
        total_matches_played = MatchResult.objects.count()
        total_goals_scored = Goal.objects.count()
        total_fixtures = Fixture.objects.count()
        
        # Calculate season progress (matches played vs total fixtures)
        season_progress = 0
        if total_fixtures > 0:
            season_progress = round((total_matches_played / total_fixtures) * 100, 1)
        
        context.update({
            'upcoming_fixtures': upcoming_fixtures,
            'recent_results': recent_results,
            'total_clubs': total_clubs,
            'total_matches_played': total_matches_played,
            'total_goals_scored': total_goals_scored,
            'season_progress': season_progress,
        })
        return context


class TableView(TemplateView):
    """Display league table with standings"""
    template_name = 'matches/league_table.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table_data = calculate_table()
        
        # Add form data for each club
        for club_data in table_data:
            club = club_data['club']
            club_data['form'] = get_recent_form(club)
            club_data.update(get_club_statistics(club_data))
        
        context.update({
            'table_data': table_data,
            'season_title': 'Wasl Village Premier League Season 3 - 2025',
        })
        return context


class FixtureListView(ListView):
    """List all fixtures, both upcoming and past"""
    model = Fixture
    template_name = 'matches/fixtures.html'
    context_object_name = 'fixtures'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Fixture.objects.select_related(
            'team1', 'team2', 'result'
        ).order_by('-date')
        
        # Filter by if it's upcoming or past
        date_filter = self.request.GET.get('filter')
        if date_filter == 'upcoming':
            queryset = queryset.filter(date__gte=timezone.now()).exclude(result__isnull=False)
        elif date_filter == 'past':
            queryset = queryset.filter(date__lt=timezone.now())
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'filter': self.request.GET.get('filter', 'all'),
        })
        return context


class MatchDetailView(DetailView):
    """Display detailed match information including result, goals, and bookings"""
    model = MatchResult
    template_name = 'matches/match_detail.html'
    context_object_name = 'match'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object
        
        # Get goals ordered by minute
        goals = match.goals.select_related('scorer__club').order_by('minute')
        
        # Get bookings ordered by minute
        bookings = match.bookings.select_related('player__club').order_by('minute')
        
        # Separate team1 and team2 stats
        team1_stats = self._get_team_match_stats(match.fixture.team1, match)
        team2_stats = self._get_team_match_stats(match.fixture.team2, match)
        
        context.update({
            'goals': goals,
            'bookings': bookings,
            'team1_stats': team1_stats,
            'team2_stats': team2_stats,
        })
        return context
    
    def _get_team_match_stats(self, team, match_result):
        """Get team-specific stats for a match"""
        goals_for = 0
        goals_against = 0
        player_stats = {}
        
        if team == match_result.fixture.home_team:
            goals_for = match_result.home_goals
            goals_against = match_result.away_goals
        else:
            goals_for = match_result.away_goals
            goals_against = match_result.home_goals
        
        # Get player stats (goals, cards)
        team_players = Player.objects.filter(club=team)
        for player in team_players:
            goals = Goal.objects.filter(scorer=player, match=match_result)
            bookings = Booking.objects.filter(player=player, match=match_result)
            
            player_stats[player] = {
                'goals': goals,
                'bookings': bookings,
                'goals_count': goals.count(),
                'bookings_count': bookings.count(),
            }
        
        return {
            'team': team,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against,
            'player_stats': player_stats,
        }


class LoginPageView(LoginView):
    """Custom login view"""
    template_name = 'matches/login.html'
    
    def get_success_url(self):
        return '/'


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'matches/register.html'
    success_url = '/login/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully! Please log in.')
        return super().form_valid(form)


class ResultEntryView(LoginRequiredMixin, CreateView):
    """Enhanced dynamic form for entering match results, goals, and bookings"""
    model = MatchResult
    form_class = DynamicMatchResultForm
    template_name = 'matches/dynamic_result_entry.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        fixture_id = self.kwargs.get('fixture_id')
        try:
            fixture = Fixture.objects.get(id=fixture_id)
            kwargs['fixture'] = fixture
        except Fixture.DoesNotExist:
            pass
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixture_id = self.kwargs.get('fixture_id')
        
        try:
            fixture = get_object_or_404(Fixture, id=fixture_id)
        except Fixture.DoesNotExist:
            messages.error(self.request, "Fixture not found.")
            return redirect('matches:fixtures')
        
        # Check if result already exists
        if hasattr(fixture, 'result'):
            messages.warning(self.request, "This fixture already has a result.")
            return redirect('matches:match_detail', pk=fixture.result.id)
        
        # Get players for both teams to filter formsets
        from django.db.models import Q
        all_fixture_players = Player.objects.filter(
            Q(club=fixture.team1) | Q(club=fixture.team2)
        ).order_by('first_name', 'last_name')
        
        # Initialize formsets
        if self.request.method == 'POST':
            goal_formset = GoalFormSet(
                self.request.POST,
                prefix='goals'
            )
            booking_formset = BookingFormSet(
                self.request.POST,
                prefix='bookings'
            )
        else:
            goal_formset = GoalFormSet(prefix='goals')
            booking_formset = BookingFormSet(prefix='bookings')
        
        # Update player choices for all forms in the formsets
        for form in goal_formset:
            if hasattr(form, 'fields') and 'scorer' in form.fields:
                form.fields['scorer'].queryset = all_fixture_players
        
        for form in booking_formset:
            if hasattr(form, 'fields') and 'player' in form.fields:
                form.fields['player'].queryset = all_fixture_players
        
        context['goal_formset'] = goal_formset
        context['booking_formset'] = booking_formset
        
        context.update({
            'fixture': fixture,
            'team1': fixture.team1,
            'team2': fixture.team2,
        })
        return context
    
    def form_valid(self, form):
        fixture_id = self.kwargs.get('fixture_id')
        fixture = get_object_or_404(Fixture, id=fixture_id)
        
        # Assign fixture to the form
        form.instance.fixture = fixture
        
        # Validate formsets
        goal_formset = GoalFormSet(self.request.POST, prefix='goals')
        booking_formset = BookingFormSet(self.request.POST, prefix='bookings')
        
        if goal_formset.is_valid() and booking_formset.is_valid():
            # Save match result
            match_result = form.save()
            
            # Save goals and bookings
            goal_formset.instance = match_result
            booking_formset.instance = match_result
            
            for goal_form in goal_formset.save(commit=False):
                if goal_form.scorer:  # Only save if scorer is selected
                    goal_form.match = match_result
                    goal_form.save()
            
            for booking_form in booking_formset.save(commit=False):
                if booking_form.player:  # Only save if player is selected
                    booking_form.match = match_result
                    booking_form.save()
            
            messages.success(self.request, f'Match result saved successfully!')
            return redirect('matches:match_detail', pk=match_result.id)
        else:
            messages.error(self.request, "Please correct the errors below.")
            return self.form_invalid(form)


class ClubListView(ListView):
    """List all clubs with basic information"""
    model = Club
    template_name = 'matches/clubs.html'
    context_object_name = 'clubs'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add manager and captain info for each club
        for club in context['clubs']:
            clubs_with_info = Club.objects.select_related(
                'manager', 'captain'
            ).prefetch_related('players').get(id=club.id)
            club.manager_info = clubs_with_info.manager
            club.captain_info = clubs_with_info.captain
            club.player_count = clubs_with_info.players.count()
        
        return context


class PlayerListView(ListView):
    """List all players with filtering options"""
    model = Player
    template_name = 'matches/players.html'
    context_object_name = 'players'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Player.objects.select_related('club', 'club__manager', 'club__captain')
        
        # Filter by club
        club_id = self.request.GET.get('club')
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        # Filter by position
        position = self.request.GET.get('position')
        if position:
            queryset = queryset.filter(position=position)
        
        return queryset.order_by('club', 'position', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add clubs for filter dropdown
        context['clubs'] = Club.objects.all().order_by('name')
        context['positions'] = Player.POSITION_CHOICES
        context.update({
            'selected_club': self.request.GET.get('club'),
            'selected_position': self.request.GET.get('position'),
        })
        
        return context


class StatisticsView(TemplateView):
    """Display league statistics and insights"""
    template_name = 'matches/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        table_data = calculate_table()
        
        # Calculate league-wide statistics
        total_matches = sum([club['matches_played'] for club in table_data])
        total_goals = sum([club['goals_for'] for club in table_data])
        avg_goals_per_match = round(total_goals / max(total_matches, 1), 2)
        
        # Top goalscorers
        top_scorers = Goal.objects.values('scorer__first_name', 'scorer__last_name', 'scorer__club__name').annotate(
            goals_count=Count('id')
        ).order_by('-goals_count')[:10]
        
        # Most disciplinary points
        booking_stats = Booking.objects.values('player__club__name').annotate(
            yellow_cards=Count('id', filter=Q(card_type='yellow')),
            red_cards=Count('id', filter=Q(card_type='red')),
            total_cards=Count('id', filter=Q(card_type='yellow')) + 
                      Count('id', filter=Q(card_type='red')) * 3
        ).order_by('-total_cards')[:10]
        
        context.update({
            'total_clubs': len(table_data),
            'total_matches': total_matches,
            'total_goals': total_goals,
            'avg_goals_per_match': avg_goals_per_match,
            'top_scorers': top_scorers,
            'most_disciplined': booking_stats,
            'table_data': table_data,
        })
        
        return context


# API endpoints for dynamic form functionality
def get_fixture_players(request, fixture_id):
    """API endpoint to get players for a specific fixture"""
    try:
        fixture = get_object_or_404(Fixture, id=fixture_id)
        
        # Get players for both teams
        team1_players = Player.objects.filter(club=fixture.team1).values(
            'id', 'first_name', 'last_name', 'position'
        ).order_by('first_name', 'last_name')
        
        team2_players = Player.objects.filter(club=fixture.team2).values(
            'id', 'first_name', 'last_name', 'position'
        ).order_by('first_name', 'last_name')
        
        # Combine all players for general dropdowns
        all_players = Player.objects.filter(
            Q(club=fixture.team1) | Q(club=fixture.team2)
        ).values(
            'id', 'first_name', 'last_name', 'position', 'club__name'
        ).order_by('first_name', 'last_name')
        
        return JsonResponse({
            'team1': {
                'name': fixture.team1.name,
                'players': list(team1_players)
            },
            'team2': {
                'name': fixture.team2.name,
                'players': list(team2_players)
            },
            'all_players': list(all_players)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def get_club_players(request, club_id):
    """API endpoint to get players for a specific club"""
    try:
        club = get_object_or_404(Club, id=club_id)
        players = Player.objects.filter(club=club).values(
            'id', 'first_name', 'last_name', 'position'
        ).order_by('first_name', 'last_name')
        
        return JsonResponse({
            'club_name': club.name,
            'players': list(players)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def validate_form_data(request):
    """API endpoint to validate form submission data on the server side"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract form data
            goals_data = data.get('goals', [])
            bookings_data = data.get('bookings', [])
            fixture_id = data.get('fixture_id')
            
            errors = []
            
            # Validate goals
            for i, goal in enumerate(goals_data):
                if not goal.get('scorer'):
                    errors.append(f"Goal {i+1}: Scorer is required")
                if not goal.get('minute'):
                    errors.append(f"Goal {i+1}: Minute is required")
                elif int(goal.get('minute', 0)) > 120:
                    errors.append(f"Goal {i+1}: Minute cannot be more than 120")
            
            # Validate bookings
            for i, booking in enumerate(bookings_data):
                if not booking.get('player'):
                    errors.append(f"Booking {i+1}: Player is required")
                if not booking.get('minute'):
                    errors.append(f"Booking {i+1}: Minute is required")
                elif int(booking.get('minute', 0)) > 120:
                    errors.append(f"Booking {i+1}: Minute cannot be more than 120")
            
            # Validate fixture exists
            if fixture_id and not Fixture.objects.filter(id=fixture_id).exists():
                errors.append("Invalid fixture selected")
            
            return JsonResponse({
                'valid': len(errors) == 0,
                'errors': errors
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)