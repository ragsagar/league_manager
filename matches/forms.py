from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Fieldset, Div
from crispy_forms.bootstrap import Accordion, AccordionGroup
from .models import Club, Player, Fixture, MatchResult, Booking, Goal


class FixtureForm(forms.ModelForm):
    """Form for creating and editing fixtures"""
    
    class Meta:
        model = Fixture
        fields = ['team1', 'team2', 'date', 'venue']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'placeholder': 'Enter match venue'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Fieldset(
                'Fixture Details',
                Row(
                    Column('team1', css_class='form-group col-md-6 mb-3'),
                    Column('team2', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('date', css_class='form-group col-md-6 mb-3'),
                    Column('venue', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Submit('submit', 'Save Fixture', css_class='btn btn-primary btn-lg')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get('team1')
        team2 = cleaned_data.get('team2')
        
        if team1 and team2:
            if team1 == team2:
                raise forms.ValidationError("A club cannot play against itself.")
        
        return cleaned_data


class MatchResultForm(forms.ModelForm):
    """Traditional match result form for compatibility"""
    
    class Meta:
        model = MatchResult
        fields = ['team1_goals', 'team2_goals', 'man_of_match']
        widgets = {
            'team1_goals': forms.NumberInput(attrs={
                'min': '0', 'max': '20', 'class': 'form-control'
            }),
            'team2_goals': forms.NumberInput(attrs={
                'min': '0', 'max': '20', 'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        fixture_id = kwargs.pop('fixture_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Filter players for man of match based on the fixture teams
        if fixture_id:
            fixture = Fixture.objects.get(id=fixture_id)
            from django.db.models import Q
            man_of_match_players = Player.objects.filter(
                Q(club=fixture.team1) | Q(club=fixture.team2)
            ).order_by('first_name', 'last_name')
            self.fields['man_of_match'].queryset = man_of_match_players
        
        self.helper.layout = Layout(
            Fieldset(
                'Match Result',
                Row(
                    Column('team1_goals', css_class='form-group col-md-6 mb-3'),
                    Column('team2_goals', css_class='form-group col-md-6 mb-3'),
                ),
                'man_of_match',
            ),
            Submit('submit', 'Save Result', css_class='btn btn-success btn-lg mr-3'),
            HTML('<a href="{% url "matches:fixtures" %}" class="btn btn-secondary btn-lg">Cancel</a>')
        )


class DynamicMatchResultForm(forms.ModelForm):
    """Dynamic match result form with enhanced UX"""
    
    class Meta:
        model = MatchResult
        fields = ['team1_goals', 'team2_goals', 'man_of_match']
        widgets = {
            'team1_goals': forms.NumberInput(attrs={
                'min': '0', 'max': '30', 'class': 'form-control form-control-lg text-center',
                'id': 'team1-goals'
            }),
            'team2_goals': forms.NumberInput(attrs={
                'min': '0', 'max': '30', 'class': 'form-control form-control-lg text-center',
                'id': 'team2-goals'
            }),
        }
    
    def __init__(self, fixture=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixture = fixture
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.form_id = 'match-result-form'
        
        # Filter players for man of match based on the fixture teams
        if fixture:
            from django.db.models import Q
            man_of_match_players = Player.objects.filter(
                Q(club=fixture.team1) | Q(club=fixture.team2)
            ).order_by('first_name', 'last_name')
            self.fields['man_of_match'].queryset = man_of_match_players
            self.fields['man_of_match'].widget = forms.Select(
                attrs={'class': 'form-control', 'id': 'man-of-match-select'}
            )
        
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div(
                        HTML('<h4 class="text-center mb-3">{{ team1.name }}</h4>'),
                        Column('team1_goals', css_class='col-4 mx-auto'),
                        css_class='col-6 border-right'
                    ),
                    Div(
                        HTML('<h4 class="text-center mb-3">{{ team2.name }}</h4>'),
                        Column('team2_goals', css_class='col-4 mx-auto'),
                        css_class='col-6'
                    ),
                    css_class='row justify-content-center align-items-center py-4 bg-light rounded mb-4'
                ),
                Row(
                    Column('man_of_match', css_class='form-group col-md-12 mb-3'),
                ),
            )
        )


class DynamicGoalForm(forms.ModelForm):
    """Dynamic goal form with enhanced features"""
    
    # Dynamic team selection
    TEAM_CHOICES = [
        ('team1', 'Team 1'),
        ('team2', 'Team 2'),
    ]
    
    team = forms.ChoiceField(
        choices=TEAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control goal-team-select'})
    )
    
    class Meta:
        model = Goal
        fields = ['scorer', 'minute', 'own_goal', 'penalty', 'assist']
        widgets = {
            'scorer': forms.Select(attrs={'class': 'form-control goal-scorer-select'}),
            'minute': forms.NumberInput(attrs={
                'min': '0', 'max': '120', 'class': 'form-control',
                'placeholder': 'Minute scored'
            }),
            'own_goal': forms.CheckboxInput(attrs={'class': 'form-check-input own-goal-check'}),
            'penalty': forms.CheckboxInput(attrs={'class': 'form-check-input penalty-check'}),
            'assist': forms.Select(attrs={'class': 'form-control goal-assist-select'}),
        }
    
    def __init__(self, fixture=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixture = fixture
        
        # If edit mode and we have an instance, set the team
        if kwargs.get('instance') and self.fixture:
            instance = kwargs['instance']
            if instance.scorer:
                if instance.scorer.club == self.fixture.team1:
                    self.fields['team'].initial = 'team1'
                else:
                    self.fields['team'].initial = 'team2'
        
        # Initialize player choices based on fixture
        if fixture:
            team1_players = Player.objects.filter(club=fixture.team1).order_by('first_name', 'last_name')
            team2_players = Player.objects.filter(club=fixture.team2).order_by('first_name', 'last_name')
            
            # All fixture players for scorer dropdown
            from django.db.models import Q
            all_players = Player.objects.filter(
                Q(club=fixture.team1) | Q(club=fixture.team2)
            ).order_by('first_name', 'last_name')
            
            self.fields['scorer'].queryset = all_players
            self.fields['assist'].queryset = all_players
        
        self.helper = FormHelper()
        self.helper.form_tag = False  # We'll handle form submission manually
        self.helper.layout = Layout(
            Row(
                Column('team', css_class='col-md-2'),
                Column('scorer', css_class='col-md-4'),
                Column('assist', css_class='col-md-4'),
                Column('minute', css_class='col-md-2'),
            ),
            Row(
                Column(
                    Div(
                        HTML('<div class="form-check">'),
                        HTML('<input type="checkbox" class="form-check-input" id="goal-own-{{ forloop.counter }}" name="goal-{{ forloop.counter }}-own_goal">'),
                        HTML('<label class="form-check-label" for="goal-own-{{ forloop.counter }}">Own Goal</label>'),
                        HTML('</div>'),
                        css_class='col-md-6'
                    )
                ),
                Column(
                    Div(
                        HTML('<div class="form-check">'),
                        HTML('<input type="checkbox" class="form-check-input" id="goal-penalty-{{ forloop.counter }}" name="goal-{{ forloop.counter }}-penalty">'),
                        HTML('<label class="form-check-label" for="goal-penalty-{{ forloop.counter }}">Penalty</label>'),
                        HTML('</div>'),
                        css_class='col-md-6'
                    )
                ),
            ),
        )


class DynamicBookingForm(forms.ModelForm):
    """Dynamic booking form with enhanced features"""
    
    # Dynamic team selection
    TEAM_CHOICES = [
        ('team1', 'Team 1'),
        ('team2', 'Team 2'),
    ]
    
    team = forms.ChoiceField(
        choices=TEAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control booking-team-select'})
    )
    
    class Meta:
        model = Booking
        fields = ['player', 'card_type', 'minute']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control booking-player-select'}),
            'card_type': forms.Select(attrs={'class': 'form-control booking-card-select'}),
            'minute': forms.NumberInput(attrs={
                'min': '0', 'max': '120', 'class': 'form-control',
                'placeholder': 'Minute'
            }),
        }
    
    def __init__(self, fixture=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixture = fixture
        
        # If edit mode and we have an instance, set the team
        if kwargs.get('instance') and self.fixture:
            instance = kwargs['instance']
            if instance.player:
                if instance.player.club == self.fixture.team1:
                    self.fields['team'].initial = 'team1'
                else:
                    self.fields['team'].initial = 'team2'
        
        # Initialize player choices based on fixture
        if fixture:
            from django.db.models import Q
            all_players = Player.objects.filter(
                Q(club=fixture.team1) | Q(club=fixture.team2)
            ).order_by('first_name', 'last_name')
            
            self.fields['player'].queryset = all_players
        
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('team', css_class='col-md-3'),
                Column('player', css_class='col-md-4'),
                Column('card_type', css_class='col-md-3'),
                Column('minute', css_class='col-md-2'),
            ),
        )


# Create enhanced formsets
class DynamicGoalFormSet(forms.BaseFormSet):
    form = DynamicGoalForm
    
    def __init__(self, fixture=None, *args, **kwargs):
        self.fixture = fixture
        super().__init__(*args, **kwargs)
    
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['fixture'] = self.fixture
        return kwargs


class DynamicBookingFormSet(forms.BaseFormSet):
    form = DynamicBookingForm
    
    def __init__(self, fixture=None, *args, **kwargs):
        self.fixture = fixture
        super().__init__(*args, **kwargs)
    
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['fixture'] = self.fixture
        return kwargs


# Traditional formsets for compatibility
BookingFormSet = forms.inlineformset_factory(
    MatchResult,
    Booking,
    fields=['player', 'card_type', 'minute'],
    extra=3,
    can_delete=True,
    widgets={
        'minute': forms.NumberInput(attrs={'min': '1', 'max': '120', 'class': 'form-control'}),
        'card_type': forms.Select(attrs={'class': 'form-control'}),
    }
)

GoalFormSet = forms.inlineformset_factory(
    MatchResult,
    Goal,
    fields=['scorer', 'minute', 'own_goal', 'penalty'],
    extra=5,
    can_delete=True,
    widgets={
        'minute': forms.NumberInput(attrs={'min': '1', 'max': '120', 'class': 'form-control'}),
        'own_goal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'penalty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)


class ClubForm(forms.ModelForm):
    """Form for creating and editing clubs"""
    
    class Meta:
        model = Club
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter club name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Club Information',
                'name',
                'logo',
            ),
            Submit('submit', 'Save Club', css_class='btn btn-primary btn-lg')
        )


class PlayerForm(forms.ModelForm):
    """Form for creating and editing players"""
    
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'position', 'club']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('position', css_class='form-group col-md-6 mb-3'),
                Column('club', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Save Player', css_class='btn btn-primary btn-lg')
        )


class UserRegistrationForm(UserCreationForm):
    """Enhanced user registration form"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Create Account',
                Row(
                    Column('username', css_class='form-group col-md-6 mb-3'),
                    Column('email', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-3'),
                    Column('last_name', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('password1', css_class='form-group col-md-6 mb-3'),
                    Column('password2', css_class='form-group col-md-6 mb-3'),
                ),
            ),
            Submit('submit', 'Register', css_class='btn btn-primary btn-lg')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user