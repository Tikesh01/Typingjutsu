document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const timerElement = document.getElementById('timer');
    const statusElement = document.getElementById('competition-status');
    const countdownOverlay = document.getElementById('countdown-overlay');
    const countdownNumber = document.getElementById('countdown-number');
    const typingContainer = document.getElementById('typing-container');
    const startNowBtn = document.getElementById('start-now-btn');
    const stopCompetitionBtn = document.getElementById('stop-competition-btn');
    const restartCompetitionBtn = document.getElementById('restart-competition-btn');
    
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
    let currentWpm = 0;
    let currentAccuracy = 100;
    let resultsUpdateInterval;
    let participantPosition = 0;
    let allResults = [];

    // Initialize based on user role
    if (userRole === 'participant') {
        initParticipantView();
    } else {
        initOrganizerView();
    }
    
    // Start the main timer
    startTimer();
    
    // Start periodic results updates
    startResultsUpdates();

    function initParticipantView() {
        // Only initialize if competition is active
        if (competitionStatus !== 'active') return;
        
        const typingInput = document.getElementById('typing-input');
        const wpmElement = document.getElementById('wpm');
        const accuracyElement = document.getElementById('accuracy');
        const timeElement = document.getElementById('time');
        const repeatsElement = document.getElementById('repeats');
        const resetBtn = document.getElementById('reset-btn');
        
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
        
        // Auto-submit when time runs out
        if (timeLeft <= 0) {
            typingInput.disabled = true;
            submitResults();
        }
    }
    
    function initOrganizerView() {
        if (startNowBtn) {
            startNowBtn.addEventListener('click', function() {
                startCompetitionNow();
            });
        }
        
        if (stopCompetitionBtn) {
            stopCompetitionBtn.addEventListener('click', function() {
                stopCompetition();
            });
        }
        
        if (restartCompetitionBtn) {
            restartCompetitionBtn.addEventListener('click', function() {
                restartCompetition();
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
                    
                    if (typingInput) {
                        typingInput.disabled = true;
                    }
                    
                    submitResults();
                    
                    // Show final results
                    showFinalResults();
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
            currentWpm = minutes > 0 ? words / minutes : 0;
            
            // Calculate accuracy
            currentAccuracy = totalKeystrokes > 0 ? (correctKeystrokes / totalKeystrokes) * 100 : 100;
            
            // Update UI
            document.getElementById('wpm').textContent = Math.round(currentWpm);
            document.getElementById('accuracy').textContent = Math.round(currentAccuracy) + '%';
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
        
        fetch(competitionData.submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'wpm': currentWpm,
                'accuracy': currentAccuracy,
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
    
    function showFinalResults() {
        // Fetch final results
        fetch(competitionData.getResultsUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI with final results
                document.getElementById('final-wpm').textContent = Math.round(currentWpm);
                document.getElementById('final-accuracy').textContent = Math.round(currentAccuracy) + '%';
                
                // Find participant position
                const sortedResults = data.results.sort((a, b) => b.wpm - a.wpm);
                const position = sortedResults.findIndex(r => r.participant_id == userId) + 1;
                document.getElementById('final-position').textContent = position;
                
                // Populate results table
                const resultsBody = document.getElementById('results-body');
                resultsBody.innerHTML = '';
                
                sortedResults.forEach((result, index) => {
                    const row = document.createElement('tr');
                    if (result.participant_id == userId) {
                        row.style.fontWeight = 'bold';
                    }
                    
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${result.participant_name}</td>
                        <td>${Math.round(result.wpm)}</td>
                        <td>${Math.round(result.accuracy)}%</td>
                    `;
                    
                    resultsBody.appendChild(row);
                });
                
                // Render final racetrack
                renderMiniRacetrack(sortedResults, true);
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
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
    
    function stopCompetition() {
        if (confirm('Are you sure you want to stop the competition? All participants will be notified.')) {
            fetch(competitionData.stopCompetitionUrl, {
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
                    alert('Error stopping competition: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while stopping the competition.');
            });
        }
    }
    
    function restartCompetition() {
        if (confirm('Are you sure you want to restart the competition? All current results will be cleared.')) {
            fetch(competitionData.restartCompetitionUrl, {
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
                    alert('Error restarting competition: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while restarting the competition.');
            });
        }
    }
    
    function startResultsUpdates() {
        // Update results immediately
        updateResults();
        
        // Set up periodic updates
        resultsUpdateInterval = setInterval(updateResults, 3000);
    }
    
    function updateResults() {
        fetch(competitionData.getResultsUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allResults = data.results;
                
                if (userRole === 'organizer') {
                    renderRacetrack(allResults);
                    updateLeaderboard(allResults);
                } else if (userRole === 'participant' && competitionStatus === 'active') {
                    renderMiniRacetrack(allResults);
                    updateParticipantPosition(allResults);
                }
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
        });
    }
    
    function renderRacetrack(results) {
        const racetrack = document.getElementById('racetrack');
        racetrack.innerHTML = '';
        
        // Sort results by WPM
        const sortedResults = results.sort((a, b) => b.wpm - a.wpm);
        const maxWpm = sortedResults.length > 0 ? Math.max(...sortedResults.map(r => r.wpm)) : 1;
        
        sortedResults.forEach((result, index) => {
            const positionPercentage = maxWpm > 0 ? (result.wpm / maxWpm) * 85 : 0;
            
            const racer = document.createElement('div');
            racer.className = 'racer';
            racer.style.left = `${positionPercentage}%`;
            racer.style.top = `${20 + (index % 5) * 35}px`;
            racer.style.backgroundColor = index === 0 ? '#ffc107' : '#007bff';
            
            const name = document.createElement('div');
            name.className = 'racer-name';
            name.textContent = result.participant_name;
            
            const wpm = document.createElement('div');
            wpm.className = 'racer-wpm';
            wpm.textContent = `${Math.round(result.wpm)} WPM`;
            
            racer.appendChild(name);
            racer.appendChild(wpm);
            racetrack.appendChild(racer);
        });
    }
    
    function renderMiniRacetrack(results, isFinal = false) {
        const racetrackElement = isFinal ? 
            document.getElementById('final-racetrack') : 
            document.getElementById('mini-racetrack');
            
        racetrackElement.innerHTML = '';
        
        // Sort results by WPM and take top 5
        const sortedResults = results.sort((a, b) => b.wpm - a.wpm).slice(0, 5);
        const maxWpm = sortedResults.length > 0 ? Math.max(...sortedResults.map(r => r.wpm)) : 1;
        
        sortedResults.forEach((result, index) => {
            const positionPercentage = maxWpm > 0 ? (result.wpm / maxWpm) * 85 : 0;
            
            const racer = document.createElement('div');
            racer.className = 'mini-racer';
            if (result.participant_id == userId) {
                racer.classList.add('current');
            }
            racer.style.left = `${positionPercentage}%`;
            racer.style.top = `${20 + index * 15}px`;
            
            racetrackElement.appendChild(racer);
        });
    }
    
    function updateParticipantPosition(results) {
        const sortedResults = results.sort((a, b) => b.wpm - a.wpm);
        const position = sortedResults.findIndex(r => r.participant_id == userId) + 1;
        
        if (position > 0) {
            document.getElementById('participant-position').textContent = `Your position: ${position} / ${results.length}`;
            participantPosition = position;
        }
    }
    
    function updateLeaderboard(results) {
        // This would update the leaderboard table if needed
        // Implementation depends on your specific requirements
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