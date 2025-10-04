from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from matches.models import Club, Player, Fixture


class Command(BaseCommand):
    help = 'Initialize clubs and players data for Wasl Village Premier League Season 3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before adding new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Player.objects.all().delete()
            Club.objects.all().delete()
            Fixture.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        with transaction.atomic():
            self.create_clubs_and_players()
            self.create_fixtures()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized clubs, players, and fixtures data!')
        )

    def create_clubs_and_players(self):
        """Create clubs and players based on the provided data"""
        
        # Team data from the image
        teams_data = [
            {
                'name': 'Time & Cost',
                'players': [
                    {'name': 'Rasheed', 'position': 'DEF'},
                    {'name': 'Midhul', 'position': 'DEF'},
                    {'name': 'Ravi', 'position': 'GK'},
                    {'name': 'Raees', 'position': 'MID'},
                    {'name': 'Naheem', 'position': 'FWD'},
                    {'name': 'Jabbar', 'position': 'FWD'},
                    {'name': 'Sukesh', 'position': 'MID'},
                    {'name': 'Jabir', 'position': 'FWD'},
                    {'name': 'Saif', 'position': 'FWD'},
                    {'name': 'Sharaz', 'position': 'DEF'}
                ]
            },
            {
                'name': 'Wehbe Warriors',
                'players': [
                    {'name': 'Husaif', 'position': 'DEF'},
                    {'name': 'Murthusha', 'position': 'DEF'},
                    {'name': 'Aneesh', 'position': 'MID'},
                    {'name': 'Fasalu', 'position': 'DEF'},
                    {'name': 'Azeem', 'position': 'GK'},
                    {'name': 'Ajesh', 'position': 'DEF'},
                    {'name': 'Shafeeq', 'position': 'FWD'},
                    {'name': 'Stebin', 'position': 'FWD'},
                    {'name': 'Aju', 'position': 'FWD'},
                    {'name': 'Sahad', 'position': 'DEF'}
                ]
            },
            {
                'name': 'Fenix Cobalt',
                'players': [
                    {'name': 'Vinod', 'position': 'MID'},
                    {'name': 'Nahas', 'position': 'DEF'},
                    {'name': 'Sreejith', 'position': 'FWD'},
                    {'name': 'Sinto', 'position': 'GK'},
                    {'name': 'Unni', 'position': 'MID'},
                    {'name': 'Jojo', 'position': 'DEF'},
                    {'name': 'Sajir', 'position': 'MID'},
                    {'name': 'Jaasim', 'position': 'FWD'},
                    {'name': 'Ramees CP', 'position': 'GK'},
                    {'name': 'Lazar', 'position': 'FWD'}
                ]
            },
            {
                'name': 'Arabzone Tigers',
                'players': [
                    {'name': 'Kaseer', 'position': 'MID'},
                    {'name': 'Iqbal', 'position': 'FWD'},
                    {'name': 'Saddam', 'position': 'DEF'},
                    {'name': 'Dibbu', 'position': 'MID'},
                    {'name': 'Vinod Kumar', 'position': 'DEF'},
                    {'name': 'Sagar', 'position': 'DEF'},
                    {'name': 'Gidhin', 'position': 'GK'},
                    {'name': 'Ramize', 'position': 'MID'},
                    {'name': 'Sharad', 'position': 'DEF'},
                    {'name': 'Delwin', 'position': 'MID'}
                ]
            }
        ]

        for team_data in teams_data:
            # Create club
            club = Club.objects.create(name=team_data['name'])
            self.stdout.write(f'Created club: {club.name}')

            # Create players
            players = []
            for i, player_data in enumerate(team_data['players']):
                # Split name into first and last name
                name_parts = player_data['name'].split()
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                
                # Get position from the dictionary
                position = player_data['position']

                player = Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    position=position,
                    club=club
                )
                players.append(player)
                self.stdout.write(f'  Created player: {player.first_name} {player.last_name} ({position})')

            # Set first player as captain and manager
            captain_manager = players[0]
            club.captain = captain_manager
            club.manager = captain_manager
            club.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Set {captain_manager.first_name} as captain and manager for {club.name}')
            )

        self.stdout.write(f'\nCreated {len(teams_data)} clubs with {sum(len(team["players"]) for team in teams_data)} total players')

    def create_fixtures(self):
        """Create fixtures based on the schedule from the image"""
        
        # Map old team names to new club names
        team_name_mapping = {
            'Team Husaif': 'Wehbe Warriors',
            'Team Rasheed': 'Time & Cost', 
            'Team Kaseer': 'Arabzone Tigers',
            'Team Vinod': 'Fenix Cobalt'
        }
        
        # Fixture data from the schedule image
        fixtures_data = [
            {
                'match_no': 1,
                'date': '2025-10-05',
                'time': '06:00',
                'team1': 'Team Husaif',
                'team2': 'Team Rasheed'
            },
            {
                'match_no': 2,
                'date': '2025-10-05', 
                'time': '06:45',
                'team1': 'Team Kaseer',
                'team2': 'Team Vinod'
            },
            {
                'match_no': 3,
                'date': '2025-10-12',
                'time': '06:00',
                'team1': 'Team Vinod',
                'team2': 'Team Rasheed'
            },
            {
                'match_no': 4,
                'date': '2025-10-12',
                'time': '06:45',
                'team1': 'Team Husaif',
                'team2': 'Team Kaseer'
            },
            {
                'match_no': 5,
                'date': '2025-10-19',
                'time': '06:00',
                'team1': 'Team Husaif',
                'team2': 'Team Vinod'
            },
            {
                'match_no': 6,
                'date': '2025-10-19',
                'time': '06:45',
                'team1': 'Team Kaseer',
                'team2': 'Team Rasheed'
            },
            {
                'match_no': 7,
                'date': '2025-11-02',
                'time': '06:00',
                'team1': 'Team Kaseer',
                'team2': 'Team Vinod'
            },
            {
                'match_no': 8,
                'date': '2025-11-02',
                'time': '06:45',
                'team1': 'Team Husaif',
                'team2': 'Team Rasheed'
            }
        ]
        
        self.stdout.write('\nCreating fixtures...')
        
        for fixture_data in fixtures_data:
            # Map team names to actual club names
            team1_name = team_name_mapping[fixture_data['team1']]
            team2_name = team_name_mapping[fixture_data['team2']]
            
            # Get club objects
            try:
                team1 = Club.objects.get(name=team1_name)
                team2 = Club.objects.get(name=team2_name)
            except Club.DoesNotExist as e:
                self.stdout.write(
                    self.style.ERROR(f'Club not found: {e}')
                )
                continue
            
            # Parse date and time
            date_str = fixture_data['date']
            time_str = fixture_data['time']
            datetime_str = f"{date_str} {time_str}:00"
            
            try:
                match_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                # Make timezone aware
                match_datetime = timezone.make_aware(match_datetime)
            except ValueError as e:
                self.stdout.write(
                    self.style.ERROR(f'Invalid datetime format: {e}')
                )
                continue
            
            # Create fixture
            fixture = Fixture.objects.create(
                team1=team1,
                team2=team2,
                date=match_datetime,
                venue="Talented Sports Academy, Qusais"
            )
            
            self.stdout.write(
                f'  Created Match {fixture_data["match_no"]}: {team1.name} vs {team2.name} '
                f'on {match_datetime.strftime("%Y-%m-%d %H:%M")}'
            )
        
        self.stdout.write(f'\nCreated {len(fixtures_data)} fixtures')
