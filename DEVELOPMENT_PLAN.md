# League Table & Match Management - Development Plan

## Project Overview
A Django web application for managing football league tables and match results with a beautiful, responsive UI using Tailwind CSS, ready for deployment to Coolify.

## Phase 1: Project Setup & Configuration

### Step 1.1: Create Django App
```bash
python manage.py startapp matches
```

### Step 1.2: Install Dependencies
Add to `requirements.txt`:
```
Django>=4.2
Pillow>=10.0.0
django-crispy-forms>=2.0
crispy-tailwind>=0.5.0
```

### Step 1.3: Update Settings
In `league_manager/settings.py`:
- Add 'matches' to INSTALLED_APPS
- Configure Crispy Forms with Tailwind
- Set MEDIA settings for uploads
- Configure TIME_ZONE

## Phase 2: Database Models (`matches/models.py`)

### Step 2.1: Player Model
```python
class Player(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=[
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ])
    club = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='players')
    
    class Meta:
        ordering = ['club', 'position', 'last_name']
```

### Step 2.2: Club Model
```python
class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='clubs/logos/', blank=True, null=True)
    manager = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_club')
    captain = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='captained_club')
    
    class Meta:
        ordering = ['name']
```

### Step 2.3: Fixture Model
```python
class Fixture(models.Model):
    home_team = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey('Club', on_delete=models.CASCADE, related_name='away_fixtures')
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    
    class Meta:
        ordering = ['-date']
```

### Step 2.4: MatchResult Model
```python
class MatchResult(models.Model):
    fixture = models.OneToOneField('Fixture', on_delete=models.CASCADE, related_name='result')
    home_goals = models.PositiveIntegerField(default=0)
    away_goals = models.PositiveIntegerField(default=0)
    man_of_match = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.fixture.home_team} {self.home_goals} - {self.away_goals} {self.fixture.away_team}"
```

### Step 2.5: Booking Model
```python
class Booking(models.Model):
    CARD_CHOICES = [
        ('yellow', 'Yellow Card'),
        ('red', 'Red Card'),
    ]
    
    match = models.ForeignKey('MatchResult', on_delete=models.CASCADE, related_name='bookings')
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    card_type = models.CharField(max_length=6, choices=CARD_CHOICES)
    
    class Meta:
        ordering = ['match', 'player', 'card_type']
```

### Step 2.6: Goal Model
```python
class Goal(models.Model):
    match = models.ForeignKey('MatchResult', on_delete=models.CASCADE, related_name='goals')
    scorer = models.ForeignKey('Player', on_delete=models.CASCADE)
    minute = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['match', 'minute']
        unique_together = ('match', 'minute')  # Assuming max 1 goal per minute
```

## Phase 3: Scoring & Table Logic (`matches/utils.py`)

### Step 3.1: Calculate Table Function
```python
def calculate_table():
    """
    Calculate league table with proper tiebreaker logic:
    1. Points (3 for win, 1 for draw, 0 for loss)
    2. Goal difference
    3. Goals scored
    4. Head-to-head record
    5. Disciplinary (fewer cards better)
    6. Random (coin toss simulation)
    """
    
    # Initialize club stats dictionary
    club_stats = {}
    
    # Loop through completed match results
    # Calculate points, goals for/against, bookings
    # Store in club_stats dictionary
    
    # Sort based on tiebreakers
    # Return sorted list of club standings
    
    return sorted_table
```

### Step 3.2: Helper Functions
- `get_head_to_head_record(club1, club2)` - Calculate head-to-head results
- `get_club_disciplinary_points(club)` - Count yellow/red cards
- `apply_tiebreakers(sorted_clubs)` - Implement complete tiebreaker hierarchy

## Phase 4: Admin Interface (`matches/admin.py`)

### Step 4.1: Model Registration
```python
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'captain']
    search_fields = ['name']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'position', 'club']
    list_filter = ['club', 'position']
    search_fields = ['first_name', 'last_name']
```

### Step 4.2: Inline Formsets
```python
class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1

class GoalInline(admin.TabularInline):
    model = Goal
    extra = 1

@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    inlines = [GoalInline, BookingInline]
```

## Phase 5: Forms (`matches/forms.py`)

### Step 5.1: Result Entry Formset
```python
class MatchResultForm(forms.ModelForm):
    class Meta:
        model = MatchResult
        fields = ['home_goals', 'away_goals', 'man_of_match']

BookingFormSet = forms.inlineformset_factory(
    MatchResult, Booking, fields='__all__', extra=3
)

GoalFormSet = forms.inlineformset_factory(
    MatchResult, Goal, fields='__all__', extra=5
)
```

## Phase 6: Views (`matches/views.py`)

### Step 6.1: Table View
```python
class TableView(TemplateView):
    template_name = 'matches/league_table.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_data'] = calculate_table()
        return context
```

### Step 6.2: Fixtures List View
```python
class FixtureListView(ListView):
    model = Fixture
    template_name = 'matches/fixtures.html'
    
    def get_queryset(self):
        return Fixture.objects.filter(date__gte=timezone.now()).order_by('date')
```

### Step 6.3: Result Entry View
```python
class ResultEntryView(CreateView):
    model = MatchResult
    template_name = 'matches/result_entry.html'
    form_class = MatchResultForm
    # Handle formsets for goals and bookings
```

### Step 6.4: Match Detail View
```python
class MatchDetailView(DetailView):
    model = MatchResult
    template_name = 'matches/match_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goals'] = self.object.goals.all()
        context['bookings'] = self.object.bookings.all()
        return context
```

## Phase 7: Templates with Tailwind CSS

### Step 7.1: Base Template (`templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}League Manager{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Custom Tailwind config for football theme -->
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <!-- Main content with responsive grid -->
</body>
</html>
```

### Step 7.2: League Table Template
- Responsive table design
- Color-coded standings
- Mobile-friendly card layout
- Sortable columns

### Step 7.3: Fixtures Template
- Calendar-style layout
- Upcoming vs past fixtures
- Search and filter functionality

### Step 7.4: Results Template
- Match cards with detailed information
- Goal scorers and timing
- Booking records
- Man of the match highlights

## Phase 8: URL Configuration

### Step 8.1: App URLs (`matches/urls.py`)
```python
app_name = 'matches'
urlpatterns = [
    path('table/', TableView.as_view(), name='table'),
    path('fixtures/', FixtureListView.as_view(), path='fixtures'),
    path('results/entry/<int:fixture_id>/', ResultEntryView.as_view(), name='result_entry'),
    path('match/<int:pk>/', MatchDetailView.as_view(), name='match_detail'),
]
```

### Step 8.2: Project URLs (`league_manager/urls.py`)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matches.urls')),
    path('media/', serve, {'document_root': settings.MEDIA_ROOT}),
]
```

## Phase 9: Testing (`tests/`)

### Step 9.1: Unit Tests for calculate_table()
```python
class CalculateTableTestCase(TestCase):
    def setUp(self):
        # Create test clubs, players, fixtures, results
        pass
    
    def test_points_calculation(self):
        # Test win=3, draw=1, loss=0
        pass
    
    def test_goal_difference_tiebreaker(self):
        # Test when points are equal
        pass
    
    def test_head_to_head_tiebreaker(self):
        # Test complex tiebreaker scenarios
        pass
    
    def test_disciplinary_tiebreaker(self):
        # Test card counting logic
        pass
```

### Step 9.2: View Tests
- Test all views render correctly
- Test form submissions
- Test permissions and access

## Phase 10: Data Migration & Sample Data

### Step 10.1: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 10.2: Create Sample Data
Create management command to populate with:
- 8-10 clubs with logos
- Players for each club
- Sample fixtures and results
- Goals and bookings

## Phase 11: Deployment Preparation

### Step 11.1: Coolify Requirements
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Step 11.2: Environment Configuration
- SECRET_KEY environment variable
- DEBUG=False for production
- Database configuration
- Media file handling
- Static file serving

### Step 11.3: Coolify Deployment Checklist
- [ ] Dockerfile in root directory
- [ ] Environment variables set
- [ ] Database migration on deployment
- [ ] Media files backup strategy
- [ ] Static files collection
- [ ] SSL certificate setup

## Phase 12: Final Testing & Launch

### Step 12.1: Pre-deployment Testing
```bash
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
```

### Step 12.2: Local Development Server
```bash
python manage.py runserver
```

### Step 12.3: Coolify Deployment
1. Connect GitHub repository to Coolify
2. Configure build settings
3. Set environment variables
4. Deploy and monitor

## File Structure Summary
```
league_manager/
├── manage.py
├── requirements.txt
├── Dockerfile
├── league_manager/
│   ├── settings.py
│   ├── urls.py
│   � └── wsgi.py
└── matches/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── forms.py
    ├── utils.py
    ├── tests.py
    └── migrations/
└── templates/
    └── matches/
        ├── base.html
        ├── league_table.html
        ├── fixtures.html
        ├── results.html
        └── match_detail.html
```

## Success Criteria
- [ ] Responsive design works on mobile and desktop
- [ ] League table updates correctly after match results
- [ ] All tiebreaker scenarios function properly
- [ ] Admin interface allows easy data management
- [ ] Tests achieve 90%+ coverage
- [ ] Application deploys successfully to Coolify
- [ ] Performance is acceptable under load

## Estimated Timeline
- Phase 1-2: 2 hours (Setup & Models)
- Phase 3: 3 hours (Scoring Logic)
- Phase 4-5: 2 hours (Admin & Forms)
- Phase 6: 2 hours (Views)
- Phase 7: 4 hours (Templates & Styling)
- Phase 8: 1 hour (URLs)
- Phase 9: 2 hours (Testing)
- Phase 10: 1 hour (Migration & Data)
- Phase 11: 1 hour (Deployment Prep)
- Phase 12: 1 hour (Final Testing)

**Total Estimated Time: 19 hours**

This plan provides a comprehensive roadmap for building a professional-grade league management system with modern UI and deployment readiness.
