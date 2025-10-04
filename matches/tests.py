from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Club, Player, Fixture, MatchResult, Booking, Goal
from .utils import calculate_table


class BasicTableCalculationTestCase(TestCase):
    """Test basic league table calculation logic"""
    
    def setUp(self):
        # Create test clubs
        self.club1 = Club.objects.create(name="Team A")
        self.club2 = Club.objects.create(name="Team B")
        
        # Create test player
        self.player1 = Player.objects.create(
            first_name="John", last_name="Doe", 
            position="FWD", club=self.club1
        )
        
        # Create fixture in the past
        past_date = timezone.now() - timedelta(days=1)
        
        self.fixture = Fixture.objects.create(
            home_team=self.club1,
            away_team=self.club2,
            date=past_date,
            venue="Test Stadium"
        )
    
    def test_basic_points_calculation(self):
        """Test basic win/loss point calculation"""
        # Team A beats Team B 2-1
        MatchResult.objects.create(
            fixture=self.fixture,
            home_goals=2,
            away_goals=1
        )
        
        table_data = calculate_table()
        
        # Find clubs in table
        team_a_data = next(c for c in table_data if c['club'].name == "Team A")
        team_b_data = next(c for c in table_data if c['club'].name == "Team B")
        
        # Team A: 1 win = 3 points
        self.assertEqual(team_a_data['points'], 3)
        self.assertEqual(team_a_data['wins'], 1)
        self.assertEqual(team_a_data['losses'], 0)
        
        # Team B: 1 loss = 0 points
        self.assertEqual(team_b_data['points'], 0)
        self.assertEqual(team_b_data['wins'], 0)
        self.assertEqual(team_b_data['losses'], 1)
    
    def test_goal_difference_calculation(self):
        """Test goal difference calculation"""
        # Team A wins 3-0
        MatchResult.objects.create(
            fixture=self.fixture,
            home_goals=3,
            away_goals=0
        )
        
        table_data = calculate_table()
        team_a_data = next(c for c in table_data if c['club'].name == "Team A")
        
        # Should have +3 goal difference
        self.assertEqual(team_a_data['goal_difference'], 3)
        self.assertEqual(team_a_data['goals_for'], 3)
        self.assertEqual(team_a_data['goals_against'], 0)


class ModelValidationTestCase(TestCase):
    """Test model validation and creation"""
    
    def test_club_creation(self):
        """Test club model creation"""
        club = Club.objects.create(name="Test Club")
        self.assertEqual(club.name, "Test Club")
        self.assertEqual(str(club), "Test Club")
    
    def test_player_creation(self):
        """Test player model creation"""
        club = Club.objects.create(name="Test Club")
        player = Player.objects.create(
            first_name="John", last_name="Doe",
            position="FWD", club=club
        )
        
        self.assertEqual(player.first_name, "John")
        self.assertEqual(player.club, club)
        self.assertIn("John Doe", str(player))
    
    def test_fixture_validation(self):
        """Test fixture validation for same team"""
        club = Club.objects.create(name="Test Club")
        
        # Should raise error if same team plays against itself
        with self.assertRaises(ValidationError):
            fixture = Fixture(
                home_team=club,
                away_team=club,
                date=timezone.now(),
                venue="Test Stadium"
            )
            fixture.clean()


class EmptyTableTestCase(TestCase):
    """Test edge cases with empty tables"""
    
    def test_empty_table_calculation(self):
        """Test table calculation with no matches"""
        # Create clubs but no matches
        Club.objects.create(name="No Matches Team")
        
        table_data = calculate_table()
        
        # Should return empty list as no matches played
        self.assertEqual(len(table_data), 0)