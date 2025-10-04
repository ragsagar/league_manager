// Enhanced Dynamic Form Management System
class MatchFormManager {
    constructor() {
        this.goalCount = 0;
        this.bookingCount = 0;
        this.formValidators = [];
        this.playerData = this.loadPlayerData();
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.setupRealTimeValidation();
    }
    
    loadPlayerData() {
        // Get player data from Django context
        return {
            team1: [],
            team2: []
        };
    }
    
    bindEvents() {
        // Add Goal button
        document.getElementById('add-goal-btn').addEventListener('click', () => {
            this.goalCount++;
            this.addGoal(this.goalCount);
            this.playSound('add');
            this.showNotification('Goal entry added!', 'success');
        });
        
        // Add Booking button
        document.getElementById('add-booking-btn').addEventListener('click', () => {
            this.bookingCount++;
            this.addBooking(this.bookingCount);
            this.playSound('add');
            this.showNotification('Booking entry added!', 'info');
        });
        
        // Form submission
        document.getElementById('dynamic-result-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission();
        });
        
        // Real-time goal validation
        document.addEventListener('input', (e) => {
            if (e.target.name === 'team1_goals' || e.target.name === 'team2_goals') {
                this.validateGoalRange(e.target);
            }
        });
    }
    
    addGoal(number) {
        const template = document.getElementById('goal-template').content.cloneNode(true);
        template.querySelector('.goal-number').textContent = number;
        
        const form = document.getElementById('goals-container');
        form.appendChild(template);
        
        const goalForm = form.lastElementChild;
        this.setupGoalEventListeners(goalForm);
        this.populateGoalPlayers(goalForm);
        
        // Smooth animation
        goalForm.style.opacity = '0';
        goalForm.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            goalForm.style.transition = 'all 0.3s ease';
            goalForm.style.opacity = '1';
            goalForm.style.transform = 'translateY(0)';
        }, 10);
    }
    
    addBooking(number) {
        const template = document.getElementById('booking-template').content.cloneNode(true);
        template.querySelector('.booking-number').textContent = number;
        
        const container = document.getElementById('bookings-container');
        container.appendChild(template);
        
        const bookingForm = container.lastElementChild;
        this.setupBookingEventListeners(bookingForm);
        this.populateBookingPlayers(bookingForm);
        
        // Smooth animation
        bookingForm.style.opacity = '0';
        bookingForm.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            bookingForm.style.transition = 'all 0.3s ease';
            bookingForm.style.opacity = '1';
            bookingForm.style.transform = 'translateY(0)';
        }, 10);
    }
    
    setupGoalEventListeners(goalForm) {
        // Remove functionality
        const removeBtn = goalForm.querySelector('.remove-goal');
        removeBtn.addEventListener('click', () => {
            this.removeGoal(goalForm);
        });
        
        // Team selection change
        const teamSelect = goalForm.querySelector('.goal-team-select');
        teamSelect.addEventListener('change', () => {
            this.updateGoalPlayers(goalForm);
        });
        
        // Own goal toggle
        const ownGoalCheck = goalForm.querySelector('.own-goal-check');
        const penaltyCheck = goalForm.querySelector('.penalty-check');
        
        ownGoalCheck.addEventListener('change', () => {
            if (ownGoalCheck.checked) {
                penaltyCheck.disabled = true;
                penaltyCheck.checked = false;
            } else {
                penaltyCheck.disabled = false;
            }
        });
        
        penaltyCheck.addEventListener('change', () => {
            if (penaltyCheck.checked) {
                ownGoalCheck.disabled = true;
                ownGoalCheck.checked = false;
            } else {
                ownGoalCheck.disabled = false;
            }
        });
    }
    
    setupBookingEventListeners(bookingForm) {
        // Remove functionality
        const removeBtn = bookingForm.querySelector('.remove-booking');
        removeBtn.addEventListener('click', () => {
            this.removeBooking(bookingForm);
        });
        
        // Team selection change
        const teamSelect = bookingForm.querySelector('.booking-team-select');
        teamSelect.addEventListener('change', () => {
            this.updateBookingPlayers(bookingForm);
        });
        
        // Card type change with visual feedback
        const cardSelect = bookingForm.querySelector('.booking-card-select');
        cardSelect.addEventListener('change', () => {
            const cardType = cardSelect.value;
            if (cardType === 'yellow') {
                cardSelect.classList.add('bg-yellow-100');
                cardSelect.classList.remove('bg-red-100');
            } else if (cardType === 'red') {
                cardSelect.classList.add('bg-red-100');
               卡 select.classList.remove('bg-yellow-100');
            }
        });
    }
    
    removeGoal(goalForm) {
        goalForm.style.transition = 'all 0.3s ease';
        goalForm.style.opacity = '0';
        goalForm.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            goalForm.remove();
            this.playSound('remove');
            this.showNotification('Goal entry removed!', 'warning');
        }, 300);
    }
    
    removeBooking(bookingForm) {
        bookingForm.style.transition = 'all 0.3s ease';
        bookingForm.style.opacity = '0';
        bookingForm.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            bookingForm.remove();
            this.playSound('remove');
            this.showNotification('Booking entry removed!', 'warning');
        }, 300);
    }
    
    populateGoalPlayers(goalForm) {
        this.updateGoalPlayers(goalForm);
    }
    
    populateBookingPlayers(bookingForm) {
        this.updateBookingPlayers(bookingForm);
    }
    
    updateGoalPlayers(goalForm) {
        const team = goalForm.querySelector('.goal-team-select').value;
        const scorerSelect = goalForm.querySelector('.goal-scorer-select');
        const assistSelect = goalForm.querySelector('.goal-assist-select');
        
        // Clear existing options
        scorerSelect.innerHTML = '<option value="">Select Scorer</option>';
        assistSelect.innerHTML = '<option value="">Select Assist (Optional)</option>';
        
        // Add team players (simplified for demo)
        const players = team === 'team1' 
            ? [
                { id: 1, name: 'Team 1 Player A' }, 
                { id: 2, name: 'Team 1 Player B' },
                { id: 3, name: 'Team 1 Player C' }
              ]
            : [
                { id: 4, name: 'Team 2 Player A' }, 
                { id: 5, name: 'Team 2 Player B' },
                { id: 6, name: 'Team 2 Player C' }
            ];
        
        players.forEach(player => {
            const option1 = document.createElement('option');
            option1.value = player.id;
            option1.textContent = player.name;
            scorerSelect.appendChild(option1.cloneNode(true));
            assistSelect.appendChild(option1);
        });
    }
    
    updateBookingPlayers(bookingForm) {
        const team = bookingForm.querySelector('.booking-team-select').value;
        const playerSelect = bookingForm.querySelector('.booking-player-select');
        
        // Clear existing options
        playerSelect.innerHTML = '<option value="">Select Player</option>';
        
        // Add team players (simplified for demo)
        const players = team === 'team1' 
            ? [
                { id: 1, name: 'Team 1 Player A' }, 
                { id: 2, name: 'Team 1 Player B' },
                { id: 3, name: 'Team 1 Player C' }
              ]
            : [
                { id: 4, name: 'Team 2 Player A' }, 
                { id: 5, name: 'Team 2 Player B' },
                { id: 6, name: 'Team 2 Player C' }
              ];
        
        players.forEach(player => {
            const option = document.createElement('option');
            option.value = player.id;
            option.textContent = player.name;
            playerSelect.appendChild(option);
        });
    }
    
    validateGoalRange(input) {
        const value = parseInt(input.value);
        const maxGoals = 10; // Reasonable max
        
        if (value > maxGoals) {
            input.value = maxGoals;
            this.showNotification(`Maximum ${maxGoals} goals allowed`, 'warning');
        }
        
        if (value < 0) {
            input.value = 0;
        }
    }
    
    setupFormValidation() {
        this.formValidators.push({
            name: 'required_fields',
            validate: () => {
                const team1Goals = document.querySelector('input[name="team1_goals"]');
                const team2Goals = document.querySelector('input[name="team2_goals"]');
                
                if (!team1Goals.value.trim()) {
                    throw new Error('Team 1 goals are required');
                }
                
                if (!team2Goals.value.trim()) {
                    throw new Error('Team 2 goals are required');
                }
                
                return true;
            }
        });
        
        this.formValidators.push({
            name: 'goal_consistency',
            validate: () => {
                const team1Goals = parseInt(document.querySelector('input[name="team1_goals"]').value || 0);
                const team2Goals = parseInt(document.querySelector('input[name="team2_goals"]').value || 0);
                const goalCount = document.querySelectorAll('#goals-container .goal-form').length;
                
                if (goalCount > (team1Goals + team2Goals)) {
                    throw new Error('More goal entries than total goals scored');
                }
                
                return true;
            }
        });
    }
    
    setupRealTimeValidation() {
        // Real-time validation feedback
        document.addEventListener('input', () => {
            this.validateForm();
        });
    }
    
    validateForm() {
        const errors = [];
        
        this.formValidators.forEach(validator => {
            try {
                validator.validate();
            } catch (error) {
                errors.push(`❌ ${error.message}`);
            }
        });
        
        if (errors.length === 0) {
            this.showValidationStatus('✅ Form is valid', 'success');
            return true;
        } else {
            this.showValidationStatus(errors.join('<br>'), 'error');
            return false;
        }
    }
    
    handleFormSubmission() {
        if (!this.validateForm()) {
            this.showNotification('Please fix errors before submitting', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = document.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="mr-2">⏳</span>Saving...';
        submitBtn.disabled = true;
        
        // Process and serialize dynamic data
        this.processFormData();
        
        // Submit the form
        setTimeout(() => {
            document.getElementById('dynamic-result-form').submit();
        }, 500);
    }
    
    processFormData() {
        const formData = new FormData();
        
        // Process goals
        document.querySelectorAll('#goals-container .goal-form').forEach((goalForm, index) => {
            const goalData = {
                team: goalForm.querySelector('.goal-team-select').value,
                scorer: goalForm.querySelector('.goal-scorer-select').value,
                assist: goalForm.querySelector('.goal-assist-select').value,
                minute: goalForm.querySelector('input[name="goal-minute"]').value,
                own_goal: goalForm.querySelector('.own-goal-check').checked,
                penalty: goalForm.querySelector('.penalty-check').checked
            };
            
            Object.keys(goalData).forEach(key => {
                formData.append(`goal_${index}_${key}`, goalData[key]);
            });
        });
        
        // Process bookings
        document.querySelectorAll('#bookings-container .booking-form').forEach((bookingForm, index) => {
            const bookingData = {
                team: bookingForm.querySelector('.booking-team-select').value,
                player: bookingForm.querySelector('.booking-player-select').value,
                card_type: bookingForm.querySelector('.booking-card-select').value,
                minute: bookingForm.querySelector('input[name="booking-minute"]').value
            };
            
            Object.keys(bookingData).forEach(key => {
                formData.append(`booking_${index}_${key}`, bookingData[key]);
            });
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-black',
            info: 'bg-blue-500 text-white'
        };
        
        notification.className += ` ${colors[type]}`;
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        // Slide in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Slide out after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    showValidationStatus(message, type) {
        let statusDiv = document.getElementById('validation-status');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'validation-status';
            statusDiv.className = 'fixed bottom-4 right-4 max-w-md p-4 rounded-lg shadow-lg z-50';
            document.body.appendChild(statusDiv);
        }
        
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white'
        };
        
        statusDiv.className = `fixed bottom-4 right-4 max-w-md p-4 rounded-lg shadow-lg z-50 ${colors[type]}`;
        statusDiv.innerHTML = message;
    }
    
    playSound(type) {
        // Simple sound feedback (web audio API)
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            if (type === 'add') {
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            } else if (type === 'remove') {
                oscillator.frequency.setValueAtTime(400, audioContext.currentTime)}}
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.log('Audio not supported:', error);
        }
    }
}

// Initialize the form manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.matchFormManager = new MatchFormManager();
});

// Smooth scrolling utility
function scrollToSection(elementId) {
    document.getElementById(elementId).scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.querySelector('button[type="submit"]').click();
    }
    
    // Ctrl/Cmd + G to add goal
    if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
        e.preventDefault();
        document.getElementById('add-goal-btn').click();
    }
    
    // Ctrl/Cmd + B to add booking
    if ((e.ctrlKey || e.metaKeys) && e.key === 'b') {
        e.preventDefault();
        document.getElementById('add-booking-btn').click();
    }
});

// Auto-save functionality (optional)
function autoSaveForm() {
    const formData = new FormData(document.getElementById('dynamic-result-form'));
    localStorage.setItem('matchResultDraft', JSON.stringify(Object.fromEntries(formData)));
}

// Load draft on page load
window.addEventListener('load', function() {
    const saved = localStorage.getItem('matchResultDraft');
    if (saved && confirm('Load previously saved draft?')) {
        const data = JSON.parse(saved);
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`[name="${key}"]`);
            if (element && element.type !== 'checkbox') {
                element.value = data[key];
            } else if (element && element.type === 'checkbox') {
           元素.checked = data[key] === 'true';
            }
        });
    }
});

// Auto-save on input change
document.addEventListener('input', autoSaveForm);
</script>

<script>
// Enhanced Dynamic Form Management System
class MatchFormManager {
    constructor() {
        this.goalCount = 0;
        this.bookingCount = 0;
        this.formValidators = [];
        this.playerData = this.loadPlayerData();
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.setupRealTimeValidation();
    }
    
    loadPlayerData() {
        // Get player data from Django context
        return {
            team1: [],
            team2: []
        };
    }
    
    bindEvents() {
        // Add Goal button
        document.getElementById('add-goal-btn').addEventListener('click', () => {
            this.goalCount++;
            this.addGoal(this.goalCount);
            this.playSound('add');
            this.showNotification('Goal entry added!', 'success');
        });
        
        // Add Booking button
        document.getElementById('add-booking-btn').addEventListener('click', () => {
            this.bookingCount++;
            this.addBooking(this.bookingCount);
            this.playSound('add');
            this.showNotification('Booking entry added!', 'info');
        });
        
        // Form submission
        document.getElementById('dynamic-result-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission();
        });
        
        // Real-time goal validation
        document.addEventListener('input', (e) => {
            if (e.target.name === 'team1_goals' || e.target.name === 'team2_goals') {
                this.validateGoalRange(e.target);
            }
        });
    }
    
    addGoal(number) {
        const template = document.getElementById('goal-template').content.cloneNode(true);
        template.querySelector('.goal-number').textContent = number;
        
        const form = document.getElementById('goals-container');
        form.appendChild(template);
        
        const goalForm = form.lastElementChild;
        this.setupGoalEventListeners(goalForm);
        this.populateGoalPlayers(goalForm);
        
        // Smooth animation
        goalForm.style.opacity = '0';
        goalForm.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            goalForm.style.transition = 'all 0.3s ease';
            goalForm.style.opacity = '1';
            goalForm.style.transform = 'translateY(0)';
        }, 10);
    }
    
    addBooking(number) {
        const template = document.getElementById('booking-template').content.cloneNode(true);
        template.querySelector('.booking-number').textContent = number;
        
        const container = document.getElementById('bookings-container');
        container.appendChild(template);
        
        const bookingForm = container.lastElementChild;
        this.setupBookingEventListeners(bookingForm);
        this.populateBookingPlayers(bookingForm);
        
        // Smooth animation
        bookingForm.style.opacity = '0';
        bookingForm.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            bookingForm.style.transition = 'all 0.3s ease';
            bookingForm.style.opacity = '1';
            bookingForm.style.transform = 'translateY(0)';
        }, 10);
    }
    
    setupGoalEventListeners(goalForm) {
        // Remove functionality
        const removeBtn = goalForm.querySelector('.remove-goal');
        removeBtn.addEventListener('click', () => {
            this.removeGoal(goalForm);
        });
        
        // Team selection change
        const teamSelect = goalForm.querySelector('.goal-team-select');
        teamSelect.addEventListener('change', () => {
            this.updateGoalPlayers(goalForm);
        });
        
        // Own goal toggle
        const ownGoalCheck = goalForm.querySelector('.own-goal-check');
        const penaltyCheck = goalForm.querySelector('.penalty-check');
        
        ownGoalCheck.addEventListener('change', () => {
            if (ownGoalCheck.checked) {
                penaltyCheck.disabled = true;
                penaltyCheck.checked = false;
            } else {
                penaltyCheck.disabled = false;
            }
        });
        
        penaltyCheck.addEventListener('change', () => {
            if (penaltyCheck.checked) {
                ownGoalCheck.disabled = true;
                ownGoalCheck.checked = false;
            } else {
                ownGoalCheck.disabled = false;
            }
        });
    }
    
    setupBookingEventListeners(bookingForm) {
        // Remove functionality
        const removeBtn = bookingForm.querySelector('.remove-booking');
        removeBtn.addEventListener('click', () => {
            this.removeBooking(bookingForm);
        });
        
        // Team selection change
        const teamSelect = bookingForm.querySelector('.booking-team-select');
        teamSelect.addEventListener('change', () => {
            this.updateBookingPlayers(bookingForm);
        });
    }
    
    removeGoal(goalForm) {
        goalForm.style.transition = 'all 0.3s ease';
        goalForm.style.opacity = '0';
        goalForm.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            goalForm.remove();
            this.playSound('remove');
            this.showNotification('Goal entry removed!', 'warning');
        }, 300);
    }
    
    removeBooking(bookingForm) {
        bookingForm.style.transition = 'all 0.3s ease';
        bookingForm.style.opacity = '0';
        bookingForm.style.transform = 'translateX(-100%)';
        
        setTimeout(() => {
            bookingForm.remove();
            this.playSound('remove');
            this.showNotification('Booking entry removed!', 'warning');
        }, 300);
    }
    
    populateGoalPlayers(goalForm) {
        this.updateGoalPlayers(goalForm);
    }
    
    populateBookingPlayers(bookingForm) {
        this.updateBookingPlayers(bookingForm);
    }
    
    updateGoalPlayers(goalForm) {
        const team = goalForm.querySelector('.goal-team-select').value;
        const scorerSelect = goalForm.querySelector('.goal-scorer-select')[;
        const assistSelect = goalForm.querySelector('.goal-assist-select');
        
        // Clear existing options
        scorerSelect.innerHTML = '<option value="">Select Scorer</option>';
        assistSelect.innerHTML = '<option value="">Select Assist (Optional)</option>';
        
        // Add team players (simplified for demo)
        const players = team === 'team1' 
            ? [
                { id: 1, name: 'Team 1 Player A' }, 
                { id: 2, name: 'Team 1 Player B' },
                { id: 3, name: 'Team 1 Player C' }
              ]
            : [
                { id: 4, name: 'Team 2 Player A' }, 
                { id: 5, name: 'Team 2 Player B' },
                { id: 6, name: 'Team 2 Player C' }
              ];
        
        players.forEach(player => {
            const option1 = document.createElement('option');
            option1.value = player.id;
            option1.textContent = player.name;
            scorerSelect.appendChild(option1.cloneNode(true));
            assistSelect.appendChild(option1);
        });
    }
    
    updateBookingPlayers(bookingForm) {
        const team = bookingForm.querySelector('.booking-team-select').value;
        const playerSelect = bookingForm.querySelector('.booking-player-select');
        
        // Clear existing options
        playerSelect.innerHTML = '<option value="">Select Player</option>';
        
        // Add team players (simplified for demo)
        const players = team === 'team1' 
            ? [
                { id: 1, name: 'Team 1 Player A' }, 
                { id: 2, name: 'Team 1 Player B' },
                { id: 3, name: 'Team 1 Player C' }
              ]
            : [
                { id: 4, name: 'Team 2 Player A' }, 
                { id: 5, name: 'Team 2 Player B' },
                { id: 6, name: 'Team 2 Player C' }
              ];
        
        players.forEach(player => {
            const option = document.createElement('option');
            option.value = player.id;
            option.textContent = player.name;
            playerSelect.appendChild(option);
        });
    }
    
    validateGoalRange(input) {
        const value = parseInt(input.value);
        const maxGoals = 10; // Reasonable max
        
        if (value > maxGoals) {
            input.value = maxGoals;
            this.showNotification(`Maximum ${maxGoals} goals allowed`, 'warning');
        }
        
        if (value < 0) {
            input.value = 0;
        }
    }
    
    setupFormValidation() {
        this.formValidators.push({
            name: 'required_fields',
            validate: () => {
                const team1Goals = document.querySelector('input[name="team1_goals"]');
                const team2Goals = document.querySelector('input[name="team2_goals"]');
                
                if (!team1Goals.value.trim()) {
                    throw new Error('Team 1 goals are required');
                }
                
                if (!team2Goals.value.trim()) {
                    throw new Error('Team 2 goals are required');
                }
                
                return true;
            }
        });
        
        this.formValidators.push({
            name: 'goal_consistency',
            validate: () => {
                const team1Goals = parseInt(document.querySelector('input[name="team1_goals"]').value || 0);
                const team2Goals = parseInt(document.querySelector('input[name="team2_goals"]').value || 0);
                const goalCount = document.querySelectorAll('#goals-container .goal-form').length;
                
                if (goalCount > (team1Goals + team2Goals)) {
                    throw new Error('More goal entries than total goals scored');
                }
                
                return true;
            }
        });
    }
    
    setupRealTimeValidation() {
        // Real-time validation feedback
        document.addEventListener('input', () => {
            this.validateForm();
        });
    }
    
    validateForm() {
        const errors = [];
        
        this.formValidators.forEach(validator => {
            try {
                validator.validate();
            } catch (error) {
                errors.push(`❌ ${error.message}`);
            }
        });
        
        if (errors.length === 0) {
            this.showValidationStatus('✅ Form is valid', 'success');
            return true;
        } else {
            this.showValidationStatus(errors.join('<br>'), 'error');
            return false;
        }
    }
    
    handleFormSubmission() {
        if (!this.validateForm()) {
            this.showNotification('Please fix errors before submitting', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = document.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="mr-2">⏳</span>Saving...';
        submitBtn.disabled = true;
        
        // Process and serialize dynamic data
        this.processFormData();
        
        // Submit the form
        setTimeout(() => {
            document.getElementById('dynamic-result-form').submit();
        }, 500);
    }
    
    processFormData() {
        const formData = new FormData();
        
        // Process goals
        document.querySelectorAll('#goals-container .goal-form').forEach((goalForm, index) => {
            const goalData = {
                team: goalForm.querySelector('.goal-team-select').value,
                scorer: goalForm.querySelector('.goal-scorer-select').value,
                assist: goalForm.querySelector('.goal-assist-select').value,
                minute: goalForm.querySelector('input[name="goal-minute"]').value;
                own_goal: goalForm.querySelector('.own-goal-check').checked,
                penalty: goalForm.querySelector('.penalty-check').checked
            };
            
            Object.keys(goalData).forEach(key => {
                formData.append(`goal_${index}_${key}`, goalData[key]);
            });
        });
        
        // Process bookings
        document.querySelectorAll('#bookings-container .booking-form').forEach((bookingForm, index) => {
            const bookingData = {
                team: bookingForm.querySelector('.booking-team-select').value,
                player: bookingForm.querySelector('.booking-player-select').value,
                card_type: bookingForm.querySelector('.booking-card-select').value,
                minute: bookingForm.querySelector('input[name="booking-minute"]').value
            };
            
            Object.keys(bookingData).forEach(key => {
                formData.append(`booking_${index}_${key}`, bookingData[key]);
            });
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-black',
            info: 'bg-blue-500 text-white'
        };
        
        notification.className += ` ${colors[type]}`;
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        // Slide in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Slide out after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    showValidationStatus(message, type) {
        let statusDiv = document.getElementById('validation-status');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'validation-status';
            statusDiv.className = 'fixed bottom-4 right-4 max-w-md p-4 rounded-lg shadow-lg z-50';
            document.body.appendChild(statusDiv);
        }
        
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white'
        };
        
        statusDiv.className = `fixed bottom-4 right-4 max-w-md p-4 rounded-lg shadow-lg z-50 ${colors[type]}`;
        statusDiv.innerHTML = message;
    }
    
    playSound(type) {
        // Simple sound feedback
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            if (type === 'add') {
                oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            } else if (type === 'remove') {
                oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
            }
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.log('Audio not supported:', error);
        }
    }
}

// Initialize the form manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.matchFormManager = new MatchFormManager();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.querySelector('button[type="submit"]').click();
    }
    
    // Ctrl/Cmd + G to add goal
    if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
        e.preventDefault();
        document.getElementById('add-goal-btn').click();
    }
    
    // Ctrl/Cmd + B to add booking
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        document.getElementById('add-booking-btn').click();
    }
});
</script>
