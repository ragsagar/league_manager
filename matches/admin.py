from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Club, Player, Fixture, MatchResult, Booking, Goal


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 1
    fields = ['first_name', 'last_name', 'position']
    ordering = ['position', 'last_name']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'captain', 'logo_preview', 'player_count']
    list_filter = ['name']
    search_fields = ['name']
    inlines = [PlayerInline]
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%; object-fit: cover;" />',
                obj.logo.url
            )
        return "No logo"
    logo_preview.short_description = "Logo"
    
    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Players"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position', 'club', 'full_name']
    list_filter = ['club', 'position']
    search_fields = ['first_name', 'last_name', 'club__name']
    ordering = ['club', 'position', 'last_name']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Full Name"


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 3
    fields = ['player', 'card_type', 'minute']
    ordering = ['minute']


class GoalInline(admin.TabularInline):
    model = Goal
    extra = 5
    fields = ['scorer', 'minute', 'own_goal', 'penalty']
    ordering = ['minute']


class MatchResultInline(admin.StackedInline):
    model = MatchResult
    extra = 0
    can_delete = False
    fields = ['team1_goals', 'team2_goals', 'man_of_match']
    inlines = [GoalInline, BookingInline]


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ['team1', 'vs_display', 'team2', 'date', 'venue', 'has_result']
    list_filter = ['date', 'team1', 'team2']
    search_fields = ['team1__name', 'team2__name', 'venue']
    ordering = ['-date']
    inlines = [MatchResultInline]
    
    fieldsets = (
        ('Match Details', {
            'fields': ('team1', 'team2', 'date', 'venue')
        }),
    )
    
    def vs_display(self, obj):
        return "vs"
    vs_display.short_description = ""
    
    def has_result(self, obj):
        return obj.result is not None
    has_result.boolean = True
    has_result.short_description = "Result"


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['fixture', 'score_display', 'winner_display', 'man_of_match']
    list_filter = ['fixture__date']
    search_fields = ['fixture__team1__name', 'fixture__team2__name']
    inlines = [GoalInline, BookingInline]
    
    fieldsets = (
        ('Match Result', {
            'fields': ('fixture', 'team1_goals', 'team2_goals', 'man_of_match')
        }),
    )
    
    def score_display(self, obj):
        return f"{obj.team1_goals} - {obj.team2_goals}"
    score_display.short_description = "Score"
    
    def winner_display(self, obj):
        winner = obj.winner
        return winner.name if winner else "Draw"
    winner_display.short_description = "Winner"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['fixture']  # Make fixture read-only after creation
        return []


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['get_match', 'player', 'card_type', 'minute', 'card_colored']
    list_filter = ['card_type', 'match__fixture__team1', 'match__fixture__team2']
    search_fields = ['player__first_name', 'player__last_name', 'player__club__name']
    ordering = ['-match__fixture__date', 'minute']
    
    def get_match(self, obj):
        return obj.match.fixture.__str__()
    get_match.short_description = "Match"
    
    def card_colored(self, obj):
        if obj.card_type == 'red':
            return format_html('<span style="color: red;">♦</span>')
        else:
            return format_html('<span style="color: yellow;">♦</span>')
    card_colored.short_description = "Card"


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['get_match', 'scorer', 'minute', 'goal_type', 'scorer_club']
    list_filter = ['own_goal', 'penalty', 'match__fixture__team1', 'match__fixture__team2']
    search_fields = ['scorer__first_name', 'scorer__last_name', 'scorer__club__name']
    ordering = ['-match__fixture__date', 'minute']
    
    def get_match(self, obj):
        return obj.match.fixture.__str__()
    get_match.short_description = "Match"
    
    def goal_type(self, obj):
        types = []
        if obj.own_goal:
            types.append("OG")
        if obj.penalty:
            types.append("P")
        return ", ".join(types) or "Normal"
    goal_type.short_description = "Type"
    
    def scorer_club(self, obj):
        return obj.scorer.club.name
    scorer_club.short_description = "Club"


# Customize admin site
admin.site.site_header = "League Manager Administration"
admin.site.site_title = "League Manager Admin"
admin.site.index_title = "Welcome to League Manager Admin"