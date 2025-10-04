from django.db import models
from django.utils import timezone
from collections import defaultdict
import random
from .models import Club, MatchResult, Goal, Booking


def calculate_table():
    """
    Calculate league table with proper tiebreaker logic:
    1. Points (3 for win, 1 for draw, 0 for loss)
    2. Goal difference
    3. Goals scored
    4. Head-to-head record
    5. Disciplinary (fewer cards better)
    6. Random (coin toss simulation for final tiebreaker)
    
    Returns a list of dictionaries with club standings
    """
    
    # Initialize club stats dictionary
    club_stats = defaultdict(lambda: {
        'club': None,
        'matches_played': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'goals_for': 0,
        'goals_against': 0,
        'goal_difference': 0,
        'points': 0,
        'yellow_cards': 0,
        'red_cards': 0,
        'total_cards': 0,
    })
    
    # Get all completed match results
    completed_results = MatchResult.objects.select_related('fixture__team1', 'fixture__team2')
    
    # Loop through completed match results
    for result in completed_results:
        team1_club = result.fixture.team1
        team2_club = result.fixture.team2
        
        # Initialize club entries
        club_stats[team1_club.id]['club'] = team1_club
        club_stats[team2_club.id]['club'] = team2_club
        
        # Update match stats
        club_stats[team1_club.id]['matches_played'] += 1
        club_stats[team2_club.id]['matches_played'] += 1
        
        club_stats[team1_club.id]['goals_for'] += result.team1_goals
        club_stats[team1_club.id]['goals_against'] += result.team2_goals
        
        club_stats[team2_club.id]['goals_for'] += result.team2_goals
        club_stats[team2_club.id]['goals_against'] += result.team1_goals
        
        # Calculate results and points
        if result.team1_goals > result.team2_goals:
            # Team1 win
            club_stats[team1_club.id]['wins'] += 1
            club_stats[team2_club.id]['losses'] += 1
            club_stats[team1_club.id]['points'] += 3
        elif result.team2_goals > result.team1_goals:
            # Team2 win
            club_stats[team2_club.id]['wins'] += 1
            club_stats[team1_club.id]['losses'] += 1
            club_stats[team2_club.id]['points'] += 3
        else:
            # Draw
            club_stats[team1_club.id]['draws'] += 1
            club_stats[team2_club.id]['draws'] += 1
            club_stats[team1_club.id]['points'] += 1
            club_stats[team2_club.id]['points'] += 1
        
        # Calculate goal differences
        club_stats[team1_club.id]['goal_difference'] = (
            club_stats[team1_club.id]['goals_for'] - club_stats[team1_club.id]['goals_against']
        )
        club_stats[team2_club.id]['goal_difference'] = (
            club_stats[team2_club.id]['goals_for'] - club_stats[team2_club.id]['goals_against']
        )
    
    # Calculate disciplinary points (yellow=1, red=3)
    bookings = Booking.objects.select_related('match__fixture__team1', 'match__fixture__team2', 'player__club')
    
    for booking in bookings:
        club = booking.player.club
        if booking.card_type == 'yellow':
            club_stats[club.id]['yellow_cards'] += 1
            club_stats[club.id]['total_cards'] += 1
        elif booking.card_type == 'red':
            club_stats[club.id]['red_cards'] += 1
            club_stats[club.id]['total_cards'] += 3  # Red card = 3 points
    
    # Convert to list and remove clubs with no matches
    table_data = []
    for club_id, stats in club_stats.items():
        if stats['club'] and stats['matches_played'] > 0:
            table_data.append(stats)
    
    # Sort using tiebreaker logic
    sorted_table = apply_tiebreakers(table_data)
    
    # Add position
    for i, club_data in enumerate(sorted_table, 1):
        club_data['position'] = i
    
    return sorted_table


def apply_tiebreakers(table_data):
    """
    Apply comprehensive tiebreaker logic to league table
    """
    
    def tiebreaker_key(club_data):
        club = club_data['club']
        
        # Primary: Points (descending)
        points = club_data['points']
        
        # Secondary: Goal difference (descending)
        goal_diff = club_data['goal_difference']
        
        # Tertiary: Goals for (descending)
        goals_for = club_data['goals_for']
        
        # Quaternary: Head-to-head record
        h2h_points, h2h_gd = get_head_to_head_record(club, table_data)
        
        # Quinary: Fewer disciplinary points (ascending)
        disciplinary_points = club_data['total_cards']
        
        # Senary: Random value for final tiebreaker (stable seed based on club name)
        random.seed(hash(club.name))
        random_value = random.random()
        
        return (-points, -goal_diff, -goals_for, -h2h_points, -h2h_gd, disciplinary_points, random_value)
    
    return sorted(table_data, key=tiebreaker_key)


def get_head_to_head_record(club, table_data):
    """
    Calculate head-to-head record for a specific club
    Returns (points, goal_difference)
    """
    home_wins = 0
    away_wins = 0
    home_draws = 0
    away_draws = 0
    home_goal_diff = 0
    away_goal_diff = 0
    
    # Get all head-to-head matches
    for opponent_data in table_data:
        opponent = opponent_data['club']
        if opponent.id == club.id:
            continue
            
        # Get results where these two teams played each other
        from .models import MatchResult, Fixture
        
        h2h_results = MatchResult.objects.filter(
            models.Q(fixture__team1=club, fixture__team2=opponent) |
            models.Q(fixture__team1=opponent, fixture__team2=club)
        ).select_related('fixture')
        
        for result in h2h_results:
            if result.fixture.team1 == club:
                # Club is team1
                if result.team1_goals > result.team2_goals:
                    home_wins += 1
                    home_goal_diff += (result.team1_goals - result.team2_goals)
                elif result.team1_goals == result.team2_goals:
                    home_draws += 1
                else:
                    home_goal_diff += (result.team1_goals - result.team2_goals)
            else:
                # Club is team2
                if result.team2_goals > result.team1_goals:
                    away_wins += 1
                    away_goal_diff += (result.team2_goals - result.team1_goals)
                elif result.team2_goals == result.team1_goals:
                    away_draws += 1
                else:
                    away_goal_diff += (result.team2_goals - result.team1_goals)
    
    # Calculate total points and goal difference
    total_points = (home_wins + away_wins) * 3 + (home_draws + away_draws) * 1
    total_goal_diff = home_goal_diff + away_goal_diff
    
    return total_points, total_goal_diff


def get_recent_form(club, num_matches=5):
    """
    Get recent form for a club (last N matches)
    Returns a string like "WWDLW" or "DDLWL" showing only actual matches played
    """
    recent_results = MatchResult.objects.filter(
        models.Q(fixture__team1=club) | models.Q(fixture__team2=club)
    ).select_related('fixture').order_by('-fixture__date')[:num_matches]
    
    form = ""
    for result in recent_results:
        if result.winner == club:
            form += "W"  # Win
        elif result.fixture.team1 == club:
            if result.team1_goals > result.team2_goals:
                form += "W"
            elif result.team1_goals == result.team2_goals:
                form += "D"
            else:
                form += "L"
        else:  # team2
            if result.team2_goals > result.team1_goals:
                form += "W"
            elif result.team2_goals == result.team1_goals:
                form += "D"
            else:
                form += "L"
    
    # Return only actual matches played, no padding
    return form


def get_club_statistics(club_data):
    """
    Get comprehensive statistics for a club
    """
    return {
        'avg_goals_per_match': round(club_data['goals_for'] / max(club_data['matches_played'], 1), 2),
        'avg_conceded_per_match': round(club_data['goals_against'] / max(club_data['matches_played'], 1), 2),
        'win_percentage': round((club_data['wins'] / max(club_data['matches_played'], 1)) * 100, 1),
    }
