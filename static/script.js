document.addEventListener('DOMContentLoaded', () => {
    const formatBtns = document.querySelectorAll('.format-btn');
    const downloadBtn = document.getElementById('downloadBtn');
    const urlInput = document.getElementById('youtubeUrl');
    const status = document.getElementById('status');
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    let selectedFormat = null;

    const style = document.createElement('style');
    style.textContent = `
        .progress-container {
            display: none;
            margin: 25px 0;
            padding: 20px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049, #4CAF50);
            background-size: 200% 100%;
            width: 0%;
            border-radius: 10px;
            transition: width 1s ease-in-out;
            position: relative;
            animation: gradientMove 2s linear infinite;
        }
        .progress-glow {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 80px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: glow 1.5s infinite;
        }
        .progress-text {
            text-align: center;
            margin: 15px 0;
            color: #444;
            font-size: 15px;
            font-weight: 500;
            text-shadow: 0 1px 1px rgba(255,255,255,0.8);
        }
        .progress-percentage {
            position: absolute;
            right: 10px;
            top: -25px;
            color: #2E7D32;
            font-weight: bold;
            font-size: 16px;
            text-shadow: 0 1px 1px rgba(255,255,255,0.8);
        }
        .progress-steps {
            display: flex;
            justify-content: space-between;
            margin-top: 25px;
            position: relative;
            padding: 0 10px;
        }
        .step {
            background: #fff;
            border: 3px solid #ddd;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            position: relative;
            z-index: 1;
            transition: all 0.5s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .step.active {
            border-color: #4CAF50;
            background: #4CAF50;
            transform: scale(1.1);
            box-shadow: 0 0 15px rgba(76,175,80,0.5);
        }
        .step-text {
            position: absolute;
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 13px;
            color: #555;
            white-space: nowrap;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .step.active + .step-text {
            color: #2E7D32;
        }
        .steps-line {
            position: absolute;
            top: 11px;
            left: 25px;
            right: 25px;
            height: 3px;
            background: #ddd;
            z-index: 0;
            border-radius: 3px;
        }
        @keyframes glow {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(200%); }
        }
        @keyframes gradientMove {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            background: #f8f9fa;
            color: #444;
            text-align: center;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .status.error {
            background: #ffebee;
            color: #c62828;
        }
        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
    `;
    document.head.appendChild(style);

    // Create progress UI
    progressContainer.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill">
                <div class="progress-glow"></div>
            </div>
            <div class="progress-percentage">0%</div>
        </div>
        <div class="progress-text">Initializing...</div>
        <div class="progress-steps">
            <div class="steps-line"></div>
            <div class="step" data-step="1"><span class="step-text">Starting</span></div>
            <div class="step" data-step="2"><span class="step-text">Processing</span></div>
            <div class="step" data-step="3"><span class="step-text">Converting</span></div>
            <div class="step" data-step="4"><span class="step-text">Completing</span></div>
        </div>
    `;
    status.parentNode.insertBefore(progressContainer, status.nextSibling);

    const progressFill = progressContainer.querySelector('.progress-fill');
    const progressText = progressContainer.querySelector('.progress-text');
    const progressPercentage = progressContainer.querySelector('.progress-percentage');
    const steps = progressContainer.querySelectorAll('.step');

    function updateProgress(percent, text) {
        progressFill.style.width = `${percent}%`;
        progressPercentage.textContent = `${Math.round(percent)}%`;
        if (text) progressText.textContent = text;
        
        // Update steps based on percentage
        steps.forEach((step, index) => {
            if (percent >= (index + 1) * 25) {
                step.classList.add('active');
            }
        });
    }

    async function simulateProgress(startPercent, endPercent, duration, text) {
        const step = 1;
        const interval = duration / ((endPercent - startPercent) / step);
        let currentPercent = startPercent;

        return new Promise(resolve => {
            const timer = setInterval(() => {
                currentPercent += step;
                updateProgress(currentPercent, text);
                
                if (currentPercent >= endPercent) {
                    clearInterval(timer);
                    resolve();
                }
            }, interval);
        });
    }

    formatBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            formatBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedFormat = btn.dataset.format;
            status.textContent = '';
        });
    });

    downloadBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        
        if (!selectedFormat) {
            status.textContent = 'Please select a format (MP3 or MP4) before downloading';
            status.className = 'status error';
            return;
        }

        if (!url) {
            status.textContent = 'Please enter a valid YouTube URL';
            status.className = 'status error';
            return;
        }

        try {
            status.textContent = 'Starting download...';
            status.className = 'status';
            progressContainer.style.display = 'block';
            downloadBtn.disabled = true;
            steps.forEach(step => step.classList.remove('active'));
            updateProgress(0, 'Initializing...');

            // Stage 1: Initialization
            await simulateProgress(0, 25, 1000, 'Fetching video information...');

            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format: selectedFormat })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Download failed');
            }

            // Stage 2: Processing
            await simulateProgress(25, 50, 1000, 'Processing content...');

            // Stage 3: Converting
            await simulateProgress(50, 75, 1000, 'Converting format...');

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `download.${selectedFormat}`;
            document.body.appendChild(a);

            // Stage 4: Completing
            await simulateProgress(75, 100, 1000, 'Completing download...');
            
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
            status.textContent = 'Download completed successfully!';
            
            // Keep progress visible for a moment
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 2000);

        } catch (error) {
            status.textContent = `Error: ${error.message}`;
            progressText.textContent = 'Download failed';
            progressFill.style.background = '#ff4444';
        } finally {
            downloadBtn.disabled = false;
        }
    });
}); 