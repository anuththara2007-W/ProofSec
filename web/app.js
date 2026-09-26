document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    handleRoute();

    window.addEventListener('popstate', handleRoute);
    
    document.body.addEventListener('click', e => {
        if (e.target.matches('[data-route]')) {
            e.preventDefault();
            const path = e.target.getAttribute('href');
            window.history.pushState({}, '', path);
            handleRoute();
        }
    });

    document.getElementById('add-evidence-btn').addEventListener('click', () => {
        const wrapper = document.createElement('div');
        wrapper.className = 'evidence-input-wrapper';
        wrapper.innerHTML = `<input type="text" class="evidence-input" placeholder="Additional evidence...">`;
        document.getElementById('evidence-list').appendChild(wrapper);
    });

    document.getElementById('eval-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('evaluate-submit-btn');
        btn.textContent = 'Evaluating...';
        btn.disabled = true;

        const scenario = document.getElementById('scenario').value;
        const context = document.getElementById('context').value;
        const evidenceInputs = document.querySelectorAll('.evidence-input');
        const evidence = Array.from(evidenceInputs).map(i => i.value.trim()).filter(v => v !== '');
        
        const expClass = document.getElementById('expected_classification').value;
        const expState = document.getElementById('expected_evidence_state').value;

        const payload = { scenario, context, evidence };
        if (expClass) payload.expected_classification = expClass;
        if (expState) payload.expected_evidence_state = expState;

        try {
            const res = await fetch('/api/v1/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) {
                let errData;
                try {
                    errData = await res.json();
                } catch (e) {
                    throw new Error("Server error (not JSON)");
                }
                
                if (errData && errData.error) {
                    throw new Error(`${errData.error.code}: ${errData.error.message}\nAction: ${errData.error.action}`);
                } else if (errData && errData.error && typeof errData.error === 'string') {
                    throw new Error(errData.error);
                } else {
                    throw new Error(`HTTP Error ${res.status}`);
                }
            }
            const result = await res.json();
            
            window.history.pushState({}, '', `/evaluation/${result.evaluation_id}`);
            handleRoute();
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
        } else throw new Error();
    } catch {
        statusDot.className = 'dot error';
        statusText.innerHTML = `<span class="dot error"></span> API Offline`;
    }
}

function handleRoute() {
    const path = window.location.pathname;
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    let activeNav = '/';
    let targetPage = 'page-home';

    if (path === '/evaluate') {
        activeNav = '/evaluate';
        targetPage = 'page-evaluate';
        loadHistory();
    } else if (path.startsWith('/evaluation/')) {
        const parts = path.split('/');
        const id = parts[2];
        if (parts[3] === 'compare') {
            targetPage = 'page-compare';
            loadCompare(id); // Actually needs a target_id, simplified for now
        } else {
            targetPage = 'page-evaluation';
            loadEvaluation(id);
        }
    } else if (path === '/benchmark') {
        activeNav = '/benchmark';
        targetPage = 'page-benchmark';
        loadBenchmark();
    } else if (path === '/research') {
        activeNav = '/research';
        targetPage = 'page-research';
        loadResearch();
    } else if (path === '/docs') {
        activeNav = '/docs';
        targetPage = 'page-docs';
    }

    const nav = document.querySelector(`[data-route="${activeNav}"]`);
    if (nav) nav.classList.add('active');
    
    document.getElementById(targetPage).classList.remove('hidden');
}

async function loadHistory() {
    const tbody = document.getElementById('history-body');
    try {
        const res = await fetch('/api/v1/evaluations');
        if (!res.ok) return;
        const data = await res.json();
        tbody.innerHTML = data.evaluations.map(e => `
            <tr>
                <td style="font-family: monospace;">${e.evaluation_id}</td>
                <td><span class="badge ${e.classification === 'Vulnerable' ? 'vulnerable' : 'not-vulnerable'}">${e.classification}</span></td>
                <td>${e.evidence_state}</td>
                <td>${new Date(e.created_at).toLocaleString()}</td>
                <td><a href="/evaluation/${e.evaluation_id}" class="btn btn-secondary btn-sm" data-route="/evaluation/${e.evaluation_id}">View</a></td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5">Error loading history</td></tr>';
    }
}

async function loadEvaluation(id) {
    document.getElementById('eval-header-id').textContent = id;
    const content = document.getElementById('evaluation-content');
    content.innerHTML = 'Loading...';
    try {
        const res = await fetch(`/api/v1/evaluations/${id}`);
        if (!res.ok) throw new Error('Evaluation not found');
        const data = await res.json();
        
        let html = `
            <div class="card glass">
                <div class="result-header">
                    <div>
                        <h2>${data.classification}</h2>
                    </div>
                    <span class="badge ${data.evidence_state.toLowerCase()}">${data.evidence_state}</span>
                </div>
                <p><strong>Provider:</strong> ${data.provider} (${data.model})</p>
                <p><strong>Summary:</strong> ${data.summary}</p>
                <p><strong>Reasoning:</strong> ${data.reasoning}</p>
        `;
        
        if (data.metrics && data.metrics.status !== "Ground truth not provided") {
            html += `<div style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.1); border-radius: 4px;">
                <h4>Metrics vs Ground Truth</h4>
                <p>Classification Correct: ${data.metrics.classification_correct}</p>
                <p>Evidence State Correct: ${data.metrics.evidence_state_correct}</p>
            </div>`;
        }

        html += `</div>`;
        content.innerHTML = html;

        // Load timeline
        loadTimeline(id);

        // Setup revision btn
        const revBtn = document.getElementById('revise-btn');
        revBtn.onclick = async () => {
            const ev = document.getElementById('revision-evidence').value;
            if(!ev) return;
            revBtn.disabled = true;
            try {
                const res = await fetch(`/api/v1/evaluations/${id}/revise`, {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({evidence: [ev]})
                });
                if(!res.ok) throw new Error("Revise failed");
                const result = await res.json();
                window.history.pushState({}, '', `/evaluation/${result.evaluation_id}`);
                handleRoute();
            } catch(e) {
                alert(e.message);
            } finally {
                revBtn.disabled = false;
            }
        };

    } catch (e) {
        content.innerHTML = `<p style="color:red">${e.message}</p>`;
    }
}

async function loadTimeline(id) {
    const tl = document.getElementById('evaluation-timeline');
    try {
        const res = await fetch(`/api/v1/evaluations/${id}/revisions`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.revisions.length <= 1) {
            tl.innerHTML = '';
            return;
        }
        
        tl.innerHTML = `<h2>Revision Timeline</h2>` + data.revisions.map(r => `
            <div class="card glass" style="margin-bottom: 1rem;">
                <h4>${r.evaluation_id}</h4>
                <p><span class="badge ${r.classification === 'Vulnerable'?'vulnerable':'not-vulnerable'}">${r.classification}</span> | ${r.evidence_state}</p>
            </div>
        `).join('');
    } catch (e) { }
}

async function loadBenchmark() {
    const content = document.getElementById('benchmark-content');
    try {
        const res = await fetch('/api/v1/benchmark');
        const data = await res.json();
        const hashRes = await fetch('/api/v1/benchmark/hash');
        const hashData = await hashRes.json();
        
        content.innerHTML = `
            <h2>Version: ${data.version}</h2>
            <p><strong>Tasks:</strong> ${data.tasks}</p>
            <p><strong>Integrity SHA256:</strong> <code>${hashData.hash}</code></p>
            <p>The ProofSec frozen benchmark contains highly rigorous security reasoning tasks isolated from user inputs.</p>
        `;
    } catch(e) {}
}

async function loadResearch() {
    const content = document.getElementById('research-content');
    try {
        const res = await fetch('/api/v1/research/metrics');
        const data = await res.json();
        content.innerHTML = `
            <h2>${data.experiment}</h2>
            <p>Status: <strong>${data.status}</strong> (${data.completed}/${data.total})</p>
            <ul>
                <li>Accuracy: ${data.metrics.accuracy}</li>
                <li>PVR: ${data.metrics.pvr}</li>
                <li>Flip Miss Rate: ${data.metrics.flip_miss_rate}</li>
            </ul>
        `;
    } catch(e) {}
}
