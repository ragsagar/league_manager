# League Manager ⚽

A professional Django web application for managing football league tables, fixtures, and match results with a beautiful, responsive UI built using Tailwind CSS.

## Features

🏆 **League Table Management**
- Automated league table calculation with proper tiebreaker logic
- Real-time standings updates after match results
- Comprehensive statistics tracking (wins, draws, losses, goals, cards)

⚽ **Match Management**
- Fixture scheduling and management
- Match result entry with detailed goal and booking tracking
- Man of the match selection
- Detailed match reports with timeline views

📊 **Statistics & Analytics**
- Top goalscorers tracking
- Disciplinary records by team
- Player position filtering
- Club performance analytics

🎨 **Modern UI/UX**
- Responsive design with Tailwind CSS
- Mobile-first approach
- Beautiful gradient themes and animations
- Professional admin interface

## Project Structure

```
league_manager/
├── manage.py
├── requirements.txt
├── Dockerfile
├── DEVELOPMENT_PLAN.md
├── league_manager/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── matches/
│   ├── models.py          # Club, Player, Fixture, MatchResult, Booking, Goal
│   ├── views.py           # TableView, FixtureListView, ResultEntryView, etc.
│   ├── forms.py           # ModelForms with inline formsets
│   ├── utils.py           # League table calculation logic
│   ├── admin.py           # Admin interface configuration
│   ├── urls.py            # URL patterns
│   └── tests.py           # Unit tests
└── templates/
    └── matches/
        ├── base.html
        ├── home.html
        ├── league_table.html
        ├── fixtures.html
        ├── match_detail.html
        ├── clubs.html
        ├── players.html
        └── statistics.html
```

## Getting Started

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd league_manager
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run Development Server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://localhost:8000` to access the application.

### Admin Access

Visit `/admin/` to access the Django admin interface where you can:
- Add clubs and players
- Schedule fixtures
- Enter match results
- Add goals and bookings

## Coolify Deployment

This application is ready for deployment to Coolify with the following configuration:

### Environment Variables

Set these in your Coolify environment:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

### Docker Configuration

The application includes:
- **Dockerfile**: Production-ready with Gunicorn
- **.dockerignore**: Optimized for faster builds
- **Gunicorn**: WSGI server for production
- **Static file handling**: Configured for production

### Database

For production, use PostgreSQL:
```bash
# Add to requirements.txt for production
psycopg2-binary>=2.9.0
```

## Model Overview

### Core Models

- **Club**: Team information with logo, manager, captain
- **Player**: Player details with position and club association
- **Fixture**: Match scheduling between clubs
- **MatchResult**: Match outcomes with scores and MOTM
- **Goal**: Individual goal tracking with scorer and timing
- **Booking**: Yellow/red card disciplinary records

### Relationship Structure

```
Club (1) ←→ (N) Player (Manager/Captain self-references)
Club (1) ←→ (N) Fixture (home/away team)
Fixture (1) ←→ (1) MatchResult
MatchResult (1) ←→ (N) Goal/Booking
```

## League Table Logic

The application implements FIFA-standard tiebreaker rules:

1. **Points**: 3 for win, 1 for draw, 0 for loss
2. **Goal Difference**: Goals scored minus goals conceded
3. **Goals Scored**: Total goals in favor
4. **Head-to-Head**: Direct match results between tied teams
5. **Disciplinary**: Fewer cards preferred (yellow=1pt, red=3pts)
6. **Random**: Stable randomization for final tiebreaker

## Templates & Styling

### Design System

- **Colors**: Soccer-themed green gradients with professional palettes
- **Typography**: Poppins font family for modern look
- **Components**: Card-based layouts with hover effects
- **Responsive**: Mobile-first design with breakpoint optimization

### Key Templates

- `base.html`: Main layout with navigation and theme configuration
- `league_table.html`: Comprehensive table view with tiebreaker indicators
- `fixtures.html`: Timeline view of matches with filtering
- `match_detail.html`: Detailed match information with goals/goals timeline

## Testing

Run the test suite:
```bash
python manage.py test matches.tests
```

Tests cover:
- Basic model creation and validation
- League table calculation logic
- Edge cases and tiebreaker scenarios
- Integration workflows

## API & Extensions

The codebase is designed for easy extension:
- **REST API**: Add Django REST Framework for mobile apps
- **Real-time**: Integrate WebSockets for live score updates
- **Mobile**: Responsive design works on mobile browsers
- **Data Export**: Easily add CSV/Excel export functionality

## Performance Considerations

- **Database**: Optimized queries with select_related/prefetch_related
- **Caching**: Django caching framework integration ready
- **Static Files**: CDN-ready media file handling
- **Migrations**: Safe database schema changes

## Contributing

1. Follow Django best practices
2. Add tests for new functionality
3. Use Black for code formatting
4. Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For deployment issues or questions:
1. Check the `DEVELOPMENT_PLAN.md` for detailed implementation notes
2. Review Django documentation for framework-specific issues
3. Test locally before deploying to production

---

**Built with ❤️ using Django + Tailwind CSS**

