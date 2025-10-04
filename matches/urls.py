from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('table/', views.TableView.as_view(), name='table'),
    path('fixtures/', views.FixtureListView.as_view(), name='fixtures'),
    path('match/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('clubs/', views.ClubListView.as_view(), name='clubs'),
    path('players/list/', views.PlayerListView.as_view(), name='players'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # Authentication URLs
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # API endpoints for dynamic forms
    path('api/fixture/<int:fixture_id>/players/', views.get_fixture_players, name='fixture_players_api'),
    path('api/club/<int:club_id>/players/', views.get_club_players, name='club_players_api'),
    path('api/validate-form/', views.validate_form_data, name='validate_form_api'),
    
]
