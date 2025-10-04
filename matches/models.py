from django.db import models
from django.contrib.auth.models import User


class Club(models.Model):
    """Represents a football club/team"""
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='clubs/logos/', blank=True, null=True)
    manager = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_club')
    captain = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='captained_club')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Club'
        verbose_name_plural = 'Clubs'
    
    def __str__(self):
        return self.name


class Player(models.Model):
    """Represents a football player"""
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='players')
    
    class Meta:
        ordering = ['club', 'position', 'last_name']
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.club.name})"


class Fixture(models.Model):
    """Represents a scheduled match between two clubs"""
    team1 = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='team1_fixtures')
    team2 = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='team2_fixtures')
    date = models.DateTimeField()
    venue = models.CharField(max_length=200, default="Main Stadium")
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Fixture'
        verbose_name_plural = 'Fixtures'
    
    def __str__(self):
        return f"{self.team1} vs {self.team2} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.team1 == self.team2:
            raise ValidationError("A club cannot play against itself.")
        return super().clean()
    
    def teams_involved(self):
        """Return both teams involved in the fixture"""
        return [self.team1, self.team2]


class MatchResult(models.Model):
    """Represents the result of a completed match"""
    fixture = models.OneToOneField(Fixture, on_delete=models.CASCADE, related_name='result')
    team1_goals = models.PositiveIntegerField(default=0)
    team2_goals = models.PositiveIntegerField(default=0)
    man_of_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Match Result'
        verbose_name_plural = 'Match Results'
    
    def __str__(self):
        return f"{self.fixture.team1} {self.team1_goals} - {self.team2_goals} {self.fixture.team2}"
    
    @property
    def is_completed(self):
        """Returns True if the match has been completed"""
        return self.fixture.date < timezone.now()
    
    @property
    def winner(self):
        """Returns the winning club or None if it's a draw"""
        if self.team1_goals > self.team2_goals:
            return self.fixture.team1
        elif self.team2_goals > self.team1_goals:
            return self.fixture.team2
        return None


class Booking(models.Model):
    """Represents a yellow or red card booking in a match"""
    CARD_CHOICES = [
        ('yellow', 'Yellow Card'),
        ('red', 'Red Card'),
    ]
    
    match = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='bookings')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=6, choices=CARD_CHOICES)
    minute = models.PositiveIntegerField(default=0, help_text="Minute when the booking occurred")
    
    class Meta:
        ordering = ['match', 'minute', 'player']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name} - {self.get_card_type_display()} ({self.minute}')"


class Goal(models.Model):
    """Represents a goal scored in a match"""
    match = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='goals')
    scorer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='goals_scored')
    assist = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='assists_made')
    minute = models.PositiveIntegerField(help_text="Minute when the goal was scored")
    own_goal = models.BooleanField(default=False)
    penalty = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['match', 'minute']
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
    
    def __str__(self):
        goal_type = ""
        if self.own_goal:
            goal_type = " (OG)"
        elif self.penalty:
            goal_type = " (P)"
        
        assist_str = ""
        if self.assist:
            assist_str = f", assisted by {self.assist.first_name} {self.assist.last_name}"
        
        return f"{self.scorer.first_name} {self.scorer.last_name} ({self.minute}'{goal_type}){assist_str}"


# Import timezone at the end to avoid circular imports
from django.utils import timezone