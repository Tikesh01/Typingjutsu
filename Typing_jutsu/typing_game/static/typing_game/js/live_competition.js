document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const timerElement = document.getElementById('timer');
    const statusElement = document.getElementById('competition-status');
    const countdownOverlay = document.getElementById('countdown-overlay');
    const countdownNumber = document.getElementById('countdown-number');
    const typingContainer = document.getElementById('typing-container');
    const startNowBtn = document.getElementById('start-now-btn');
    
    // Competition state
    let timeLeft = competitionData.timeRemaining;
    let competitionStatus = competitionData.status;
    let timerInterval;
    let startTime = null;
    let timerIntervalTyping = null;
    let elapsedTime = 0;
    let totalKeystrokes = 0;
    let correctKeystrokes = 0;
    let isCompleted = false;
    let repeatCount = 0;
    let originalText = '';
    
    // Initialize based on user role
    if (userRole === 'participant') {
        initParticipantView();
    } else {
        initOrganizerView();
    }
    
    // Start the main timer
    startTimer();
    
    function initParticipantView() {
        // Only initialize if competition is active
        if (competitionStatus !== 'active') return;
        
        const typingInput = document.getElementById('typing-input');
        const wpmElement = document.getElementById('wpm');
        const accuracyElement = document.getElementById('accuracy');
        const timeElement = document.getElementById('time');
        const repeatsElement = document.getElementById('repeats');
        const resetBtn = document.getElementById('reset-btn');
        const submitBtn = document.getElementById('submit-btn');
        
        // Get the original text based on competition type
        if (competitionData.type === 'Jumble-Word') {
            const jumbleWords = document.querySelectorAll('.jumble-word');
            originalText = Array.from(jumbleWords).map(word => word.dataset.answer).join(' ');
        } else {
            originalText = document.getElementById('text-display').textContent.trim();
        }
        
        // For reverse competition, reverse the text
        if (competitionData.type === 'Reverse') {
            originalText = originalText.split('').reverse().join('');
        }
        
        // Add repeat indicator if needed
        addRepeatIndicator();
        
        typingInput.addEventListener('input', function() {
            if (!startTime) {
                startTime = new Date();
                timerIntervalTyping = setInterval(updateTypingStats, 100);
            }
            
            const typedText = typingInput.value;
            totalKeystrokes++;
            
            // Check if we need to repeat the text
            if (typedText.length >= originalText.length && competitionData.type !== 'Jumble-Word') {
                repeatCount++;
                repeatsElement.textContent = repeatCount;
                
                // Reset the input but keep stats
                typingInput.value = '';
                
                // Add visual indicator
                const indicator = document.createElement('div');
                indicator.className = 'repeat-indicator';
                indicator.textContent = `Text repeated (${repeatCount} times)`;
                document.getElementById('text-display').appendChild(indicator);
                
                // Scroll to show the indicator
                indicator.scrollIntoView({ behavior: 'smooth' });
            }
            
            // Check accuracy
            const currentOriginal = getCurrentOriginalText(typedText);
            if (typedText === currentOriginal.substring(0, typedText.length)) {
                correctKeystrokes++;
            }
            
            // Update stats
            updateTypingStats();
            
            // Check if completed (for Jumble-Word only)
            if (competitionData.type === 'Jumble-Word' && typedText === originalText) {
                isCompleted = true;
                clearInterval(timerIntervalTyping);
                submitResults();
            }
        });
        
        resetBtn.addEventListener('click', function() {
            typingInput.value = '';
            startTime = null;
            elapsedTime = 0;
            totalKeystrokes = 0;
            correctKeystrokes = 0;
            isCompleted = false;
            repeatCount = 0;
            clearInterval(timerIntervalTyping);
            
            wpmElement.textContent = '0';
            accuracyElement.textContent = '100%';
            timeElement.textContent = '0s';
            repeatsElement.textContent = '0';
            
            // Remove repeat indicators
            document.querySelectorAll('.repeat-indicator').forEach(el => el.remove());
        });
        
        submitBtn.addEventListener('click', function() {
            if (!isCompleted && competitionData.type === 'Jumble-Word') {
                if (confirm("Are you sure you want to submit? You haven't completed the text yet.")) {
                    submitResults();
                }
            } else {
                submitResults();
            }
        });
        
        // Auto-submit when time runs out
        if (timeLeft <= 0) {
            typingInput.disabled = true;
            submitBtn.disabled = true;
            submitResults();
        }
    }
    
    function initOrganizerView() {
        if (startNowBtn) {
            startNowBtn.addEventListener('click', function() {
                startCompetitionNow();
            });
        }
    }
    
    function startTimer() {
        updateTimerDisplay();
        
        timerInterval = setInterval(function() {
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                timerElement.textContent = "00:00:00";
                
                // Update status to ended
                competitionStatus = 'ended';
                statusElement.innerHTML = '<div class="status-ended">Competition ended</div>';
                
                // Submit results for participants
                if (userRole === 'participant') {
                    const typingInput = document.getElementById('typing-input');
                    const submitBtn = document.getElementById('submit-btn');
                    
                    if (typingInput) {
                        typingInput.disabled = true;
                    }
                    
                    if (submitBtn) {
                        submitBtn.disabled = true;
                    }
                    
                    submitResults();
                }
                
                return;
            }
            
            timeLeft--;
            updateTimerDisplay();
            
            // Update competition status if needed
            if (competitionStatus === 'waiting' && timeLeft <= competitionData.duration) {
                competitionStatus = 'active';
                statusElement.innerHTML = '<div class="status-active">Competition in progress</div>';
                
                if (userRole === 'participant') {
                    // Show countdown for participants
                    showCountdown();
                }
            }
        }, 1000);
    }
    
    function updateTimerDisplay() {
        const hours = Math.floor(timeLeft / 3600);
        const minutes = Math.floor((timeLeft % 3600) / 60);
        const seconds = Math.floor(timeLeft % 60);
        
        timerElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    function showCountdown() {
        countdownOverlay.style.display = 'flex';
        let count = 3;
        
        const countdownInterval = setInterval(function() {
            countdownNumber.textContent = count;
            
            if (count <= 0) {
                clearInterval(countdownInterval);
                countdownOverlay.style.display = 'none';
                
                // Reinitialize participant view after countdown
                if (userRole === 'participant') {
                    initParticipantView();
                }
            }
            
            count--;
        }, 1000);
    }
    
    function updateTypingStats() {
        if (startTime) {
            const currentTime = new Date();
            elapsedTime = (currentTime - startTime) / 1000;
            
            // Calculate WPM
            const words = (totalKeystrokes / 5) + (repeatCount * (originalText.length / 5));
            const minutes = elapsedTime / 60;
            const wpm = minutes > 0 ? words / minutes : 0;
            
            // Calculate accuracy
            const accuracy = totalKeystrokes > 0 ? (correctKeystrokes / totalKeystrokes) * 100 : 100;
            
            // Update UI
            document.getElementById('wpm').textContent = Math.round(wpm);
            document.getElementById('accuracy').textContent = Math.round(accuracy) + '%';
            document.getElementById('time').textContent = Math.round(elapsedTime) + 's';
        }
    }
    
    function getCurrentOriginalText(typedText) {
        if (competitionData.type === 'Jumble-Word') {
            return originalText;
        }
        
        // For repeating text, calculate which segment we're on
        const segmentIndex = Math.floor(typedText.length / originalText.length);
        return originalText.repeat(segmentIndex + 1);
    }
    
    function addRepeatIndicator() {
        if (competitionData.type !== 'Jumble-Word') {
            const indicator = document.createElement('div');
            indicator.className = 'repeat-indicator';
            indicator.textContent = 'Text will repeat when you reach the end';
            indicator.id = 'repeat-indicator';
            document.getElementById('text-display').appendChild(indicator);
        }
    }
    
    function submitResults() {
        if (timerIntervalTyping) {
            clearInterval(timerIntervalTyping);
        }
        
        const wpm = parseFloat(document.getElementById('wpm').textContent);
        const accuracy = parseFloat(document.getElementById('accuracy').textContent);
        
        fetch(competitionData.submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'wpm': wpm,
                'accuracy': accuracy,
                'time_taken': elapsedTime,
                'total_keystrokes': totalKeystrokes,
                'correct_keystrokes': correctKeystrokes,
                'repeat_count': repeatCount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Results submitted successfully');
            } else {
                console.error('Error submitting results:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function startCompetitionNow() {
        fetch(competitionData.startNowUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload the page to reflect changes
                location.reload();
            } else {
                alert('Error starting competition: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while starting the competition.');
        });
    }
    
    // Periodically update competition status
    setInterval(function() {
        fetch(competitionData.updateStatusUrl, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== competitionStatus) {
                // Status changed, reload the page
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error checking competition status:', error);
        });
    }, 5000); // Check every 5 seconds
});