// State
let tasks = [];
const API_URL = 'http://127.0.0.1:8000/api/tasks/analyze/';

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    // Pre-populate with a sample for easy testing
    const sample = [
        { id: 1, title: "Fix Login Bug", due_date: "2025-01-20", estimated_hours: 3, importance: 9, dependencies: [] },
        { id: 2, title: "Write Documentation", due_date: "2025-02-01", estimated_hours: 2, importance: 5, dependencies: [1] },
        { id: 3, title: "Update Dependencies", due_date: "2024-12-25", estimated_hours: 1, importance: 4, dependencies: [] }
    ];
    document.getElementById('json-input').value = JSON.stringify(sample, null, 2);
});

function switchTab(tab) {
    // ... (rest of the function is unchanged)
    if (tab === 'single') {
        document.getElementById('single-form').classList.remove('hidden');
        document.getElementById('json-form').classList.add('hidden');
    } else {
        document.getElementById('single-form').classList.add('hidden');
        document.getElementById('json-form').classList.remove('hidden');
    }
}

function addTask() {
    const title = document.getElementById('t-title').value;
    const id = parseInt(document.getElementById('t-id').value);
    const date = document.getElementById('t-date').value;
    const hours = parseFloat(document.getElementById('t-hours').value) || 1;
    const imp = parseInt(document.getElementById('t-imp').value);
    const depStr = document.getElementById('t-deps').value;
    
    if (!title || !date || !id) {
        alert("Please fill required fields (ID, Title, Date)");
        return;
    }

    const deps = depStr ? depStr.split(',').map(n => parseInt(n.trim())) : [];

    tasks.push({
        id: id,
        title: title,
        due_date: date,
        estimated_hours: hours,
        importance: imp,
        dependencies: deps
    });

    renderList();
    clearForm();
}

function loadJson() {
    try {
        const raw = document.getElementById('json-input').value;
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
            tasks = parsed;
            renderList();
            // Using a simple inline message instead of alert()
            document.getElementById('task-count').innerHTML += ' <span style="color: var(--success); font-size: 0.8em;">(Loaded!)</span>';
        } else {
            // Using a simple inline message instead of alert()
            document.getElementById('task-count').innerHTML += ' <span style="color: var(--danger); font-size: 0.8em;">(JSON Error!)</span>';
        }
    } catch (e) {
        // Using a simple inline message instead of alert()
        document.getElementById('task-count').innerHTML += ' <span style="color: var(--danger); font-size: 0.8em;">(Invalid JSON!)</span>';
    }
}

function renderList() {
    const list = document.getElementById('task-list');
    document.getElementById('task-count').innerHTML = tasks.length;
    list.innerHTML = '';
    
    tasks.forEach(t => {
        const li = document.createElement('li');
        li.innerText = `${t.title} (ID: ${t.id}, Due: ${t.due_date})`;
        list.appendChild(li);
    });
}

function clearForm() {
    document.getElementById('t-title').value = '';
    document.getElementById('t-id').value = '';
    document.getElementById('t-deps').value = '';
}

// Function to implement exponential backoff retry logic for fetch
async function fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                // Throw error if response status is not OK (e.g., 400, 500)
                const errorBody = await response.json().catch(() => ({}));
                throw new Error(`HTTP Error ${response.status}: ${JSON.stringify(errorBody)}`);
            }
            return response;
        } catch (error) {
            if (i === maxRetries - 1) throw error; // Re-throw if last attempt
            // Exponential backoff delay
            const delay = Math.pow(2, i) * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
            console.warn(`Fetch attempt ${i + 1} failed. Retrying in ${delay / 1000}s...`);
        }
    }
}


async function analyzeTasks() {
    if (tasks.length === 0) {
        // Using a simple message box instead of alert()
        const container = document.getElementById('results-container');
        container.innerHTML = `<p style="color: var(--danger); font-weight: bold;">Please add tasks before analyzing!</p>`;
        return;
    }

    const strategy = document.getElementById('strategy-select').value;
    const container = document.getElementById('results-container');
    const loading = document.getElementById('loading');
    
    container.innerHTML = '';
    loading.classList.remove('hidden');

    try {
        const response = await fetchWithRetry(`${API_URL}?strategy=${strategy}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tasks)
        });

        const sortedTasks = await response.json();
        renderResults(sortedTasks);
        
    } catch (err) {
        console.error("Analysis Error:", err);
        container.innerHTML = `<p style="color:red; font-weight: bold;">Error connecting to backend or invalid task data. Is the Django server running?</p>`;
    } finally {
        loading.classList.add('hidden');
    }
}

function renderResults(sortedTasks) {
    const container = document.getElementById('results-container');
    container.innerHTML = '';

    sortedTasks.forEach(task => {
        let priorityClass = 'priority-low';
        let explText = task.explanation;
        
        // 1. Handle Circular Dependency (Feature implementation)
        if (task.is_circular) {
            priorityClass = 'priority-high';
            explText = `<span style="color: var(--danger); font-weight: bold;">CIRCULAR DEPENDENCY: Cannot be started!</span>`;
        } else if (task.priority_score > 60) {
            priorityClass = 'priority-high';
        } else if (task.priority_score > 30) {
            priorityClass = 'priority-med';
        }

        // 2. Handle Eisenhower Matrix View (Feature implementation)
        if (task.eisenhower_quadrant) {
            // Apply specific coloring for Eisenhower
            const quadrantColors = {
                "Do": "var(--danger)",
                "Decide": "#f59e0b", // Yellow/Orange
                "Delegate": "var(--primary)",
                "Delete": "var(--success)"
            };
            const customStyle = `border-left-color: ${quadrantColors[task.eisenhower_quadrant]};`;
            
            const html = `
                <div class="task-card" style="${customStyle}">
                    <div>
                        <h3>${task.title}</h3>
                        <div class="meta">
                            Due: ${task.due_date} | Effort: ${task.estimated_hours}h | Imp: ${task.importance}
                        </div>
                        <div style="margin-top:5px; font-weight: bold; color: ${quadrantColors[task.eisenhower_quadrant]};">
                            ${task.eisenhower_quadrant}
                        </div>
                    </div>
                    <div class="score-badge" style="background: ${quadrantColors[task.eisenhower_quadrant]};">
                        P: ${task.priority_score}
                    </div>
                </div>
            `;
            container.innerHTML += html;
            return; // Skip default rendering if Eisenhower is active
        }

        // Default Rendering (Smart Balance, Deadline, etc.)
        const html = `
            <div class="task-card ${priorityClass}">
                <div>
                    <h3>${task.title}</h3>
                    <div class="meta">
                        Due: ${task.due_date} | Effort: ${task.estimated_hours}h | Imp: ${task.importance}
                    </div>
                    <div style="margin-top:5px; font-style:italic; color:#4b5563;">
                        Why: ${explText}
                    </div>
                </div>
                <div class="score-badge">
                    Score: ${task.priority_score}
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}