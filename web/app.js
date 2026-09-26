document.addEventListener('DOMContentLoaded', () => {
    // Check API Health
    checkHealth();

    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const targetId = e.target.dataset.target;
            document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');

            if (targetId === 'history-view') {
                loadHistory();
            }
        });
    });

    // Evidence fields logic
    document.getElementById('add-evidence-btn').addEventListener('click', () => {
        const wrapper = document.createElement('div');
        wrapper.className = 'evidence-input-wrapper';
        wrapper.innerHTML = `<input type="text" class="evidence-input" placeholder="Additional evidence...">`;
        document.getElementById('evidence-list').appendChild(wrapper);
    });

    // Evaluation submission
    document.getElementById('eval-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('evaluate-submit-btn');
        btn.textContent = 'Evaluating...';
        btn.disabled = true;

        const scenario = document.getElementById('scenario').value;
        const provider = document.getElementById('provider').value;
        const evidenceInputs = document.querySelectorAll('.evidence-input');
        const evidence = Array.from(evidenceInputs).map(i => i.value.trim()).filter(v => v !== '');

        try {
            // Need to set provider in backend somehow if not globally configured.
            // Actually, we should probably pass provider in the request, but our schema doesn't accept provider.
            // The API doesn't take provider in payload yet, it relies on env. 
            // We'll leave it as is for MVP, assuming Kaggle or Mock is set globally.
            
            const res = await fetch('/api/v1/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario, evidence })
            });
            
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Evaluation failed');
            }

            const result = await res.json();
            displayResult(result);
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            btn.textContent = 'Evaluate Scenario';
            btn.disabled = false;
        }
    });
});

async function checkHealth() {
    const statusDot = document.querySelector('.dot');
    const statusText = document.getElementById('api-status');
    try {
        const res = await fetch('/api/v1/health');
        if (res.ok) {
            statusDot.className = 'dot online';
            const data = await res.json();
            statusText.innerHTML = `<span class="dot online"></span> ${data.provider} (${data.status})`;
        } else {
            throw new Error();
        }
    } catch {
        statusDot.className = 'dot error';
        statusText.innerHTML = `<span class="dot error"></span> API Offline`;
    }
}

function displayResult(result) {
    const container = document.getElementById('result-container');
    container.classList.remove('hidden');

    let badgeClass = 'insufficient';
    if (result.classification === 'Vulnerable') badgeClass = 'vulnerable';
    if (result.classification === 'Not Vulnerable') badgeClass = 'not-vulnerable';

    let stateClass = result.evidence_state.toLowerCase();

    let html = `
        <div class="card glass">
            <div class="result-header">
                <div>
                    <h2>Evaluation Result</h2>
                    <p style="color: var(--text-secondary); font-size: 0.875rem;">ID: ${result.evaluation_id} | ${result.provider} (${result.model})</p>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <span class="badge ${badgeClass}">${result.classification}</span>
                    <span class="badge ${stateClass}">${result.evidence_state}</span>
                </div>
            </div>

            <div class="result-section">
                <h3>Summary</h3>
                <p>${result.summary || 'N/A'}</p>
            </div>

            <div class="result-section">
                <h3>Reasoning</h3>
                <p>${result.reasoning}</p>
            </div>
    `;

    if (result.supporting_evidence && result.supporting_evidence.length > 0) {
        html += `
            <div class="result-section">
                <h3>Supporting Evidence</h3>
                <ul class="result-list">
                    ${result.supporting_evidence.map(e => `<li>${e}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (result.missing_evidence && result.missing_evidence.length > 0) {
        html += `
            <div class="result-section">
                <h3>Missing Evidence</h3>
                <ul class="result-list">
                    ${result.missing_evidence.map(e => `<li>${e}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    html += `</div>`;
    
    // Check for timeline (if there is a previous evaluation ID)
    if (result.previous_evaluation_id) {
        html += `
            <div class="card glass">
                <h2>Proof Timeline</h2>
                <div class="timeline">
                    <div class="timeline-item">
                        <div class="timeline-content">
                            <h4>Original Evaluation</h4>
                            <p>ID: ${result.previous_evaluation_id}</p>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-content">
                            <h4>Revised with new Evidence</h4>
                            <p><span class="badge ${badgeClass}">${result.classification}</span></p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

async function loadHistory() {
    const tbody = document.getElementById('history-body');
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

    try {
        const res = await fetch('/api/v1/evaluations');
        if (!res.ok) throw new Error('Failed to load history');
        
        const data = await res.json();
        
        if (data.evaluations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No evaluations found.</td></tr>';
            return;
        }

        tbody.innerHTML = data.evaluations.map(e => `
            <tr>
                <td style="font-family: monospace;">${e.evaluation_id}</td>
                <td><span class="badge ${e.classification === 'Vulnerable' ? 'vulnerable' : (e.classification === 'Not Vulnerable' ? 'not-vulnerable' : 'insufficient')}">${e.classification}</span></td>
                <td>${e.evidence_state}</td>
                <td>${new Date(e.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="viewEvaluation('${e.evaluation_id}')">View</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" style="color: var(--danger);">Error loading history: ${error.message}</td></tr>`;
    }
}

window.viewEvaluation = async function(id) {
    try {
        const res = await fetch(`/api/v1/evaluations/${id}`);
        if (!res.ok) throw new Error('Failed to load evaluation');
        const data = await res.json();
        
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('[data-target="evaluate-view"]').classList.add('active');
        
        document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));
        document.getElementById('evaluate-view').classList.remove('hidden');

        displayResult(data);
    } catch (error) {
        alert(error.message);
    }
};
