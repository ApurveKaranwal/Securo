const API_BASE = "http://127.0.0.1:8000";

// --- SYSTEM & INITIALIZATION ---
lucide.createIcons();

async function checkHealth() {
    const dot = document.getElementById('healthDot');
    const text = document.getElementById('healthText');
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            dot.style.color = "var(--success)";
            dot.style.backgroundColor = "var(--success)";
            text.innerText = "System: Secure";
        }
    } catch {
        dot.style.color = "var(--error)";
        dot.style.backgroundColor = "var(--error)";
        text.innerText = "System: Offline";
    }
}

// --- NAVIGATION ---
function showSection(sectionId) {
    document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
    document.getElementById(`${sectionId}-section`).style.display = 'block';
    document.getElementById(`tab-${sectionId}`).classList.add('active');
    if (sectionId === 'vault') fetchVault();
}

// --- MASTER AUTH FLOW ---
function openAuthWindow(title, onVerified) {
    const modal = document.getElementById('authModal');
    const input = document.getElementById('authMasterInput');
    const btn = document.getElementById('authConfirmBtn');
    
    document.getElementById('authTitle').innerText = title;
    input.value = "";
    modal.style.display = 'flex';
    input.focus();

    btn.onclick = async () => {
        const pass = input.value;
        if (!pass) return;
        closeModal('authModal');
        onVerified(pass);
    };
}

// --- VAULT CORE ---
async function fetchVault() {
    const res = await fetch(`${API_BASE}/list`);
    const data = await res.json();
    renderGrid(data);
}

function renderGrid(items) {
    const grid = document.getElementById('passwordGrid');
    grid.innerHTML = items.map(item => `
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:15px">
                <div>
                    <h3 style="margin:0; color:var(--accent)">${item.service}</h3>
                    <small style="opacity:0.5">${item.email}</small>
                </div>
                <button class="btn-rotate-small" onclick="handleRotate('${item.service}')">Rotate</button>
            </div>
            <div style="font-size:0.7rem; opacity:0.3; margin-bottom:15px">
                Last Sync: ${item.updated_at ? new Date(item.updated_at).toLocaleTimeString() : 'Initial'}
            </div>
            <div class="modal-actions" style="justify-content: flex-start">
                <button class="btn-primary" style="flex:1" onclick="handleRetrieve('${item.service}')">Reveal</button>
                <button class="btn-secondary" onclick="handleDelete('${item.service}')">
                    <i data-lucide="trash-2" size="16"></i>
                </button>
            </div>
        </div>
    `).join('');
    lucide.createIcons();
}

// --- ACTIONS ---
async function handleAddPassword() {
    const payload = {
        service: document.getElementById('addService').value,
        email: document.getElementById('addEmail').value,
        length: parseInt(document.getElementById('addLength').value)
    };
    const res = await fetch(`${API_BASE}/add`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    if (res.ok) {
        const data = await res.json();
        closeModal('addModal');
        alert(`Record Saved!\nPassword: ${data.password}`);
        fetchVault();
    }
}

function handleRetrieve(service) {
    openAuthWindow(`Retrieve ${service}`, async (pass) => {
        const res = await fetch(`${API_BASE}/retrieve?service=${encodeURIComponent(service)}&master_password=${encodeURIComponent(pass)}`);
        const data = await res.json();
        if (res.ok) alert(`Service: ${data.service}\nPassword: ${data.password}`);
        else alert("Unauthorized: " + data.detail);
    });
}

function handleRotate(service) {
    openAuthWindow(`Rotate ${service}`, async (pass) => {
        const res = await fetch(`${API_BASE}/rotate?service=${encodeURIComponent(service)}&master_password=${encodeURIComponent(pass)}`, {method: 'PUT'});
        const data = await res.json();
        if (res.ok) alert(`New Password Generated: ${data.new_password}`);
        else alert("Error: " + data.detail);
        fetchVault();
    });
}

function handleDelete(service) {
    openAuthWindow(`Delete ${service}?`, async (pass) => {
        const res = await fetch(`${API_BASE}/delete?service=${encodeURIComponent(service)}&master_password=${encodeURIComponent(pass)}`, {method: 'DELETE'});
        if (res.ok) fetchVault();
        else alert("Delete Failed");
    });
}

async function handleSearch() {
    const q = document.getElementById('searchInput').value;
    const res = await fetch(`${API_BASE}/search?query=${q}`);
    const data = await res.json();
    renderGrid(data);
}

function handleExport() {
    openAuthWindow("Authorize Vault Export", async (pass) => {
        const res = await fetch(`${API_BASE}/export?master_password=${encodeURIComponent(pass)}`);
        if (res.ok) {
            const data = await res.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "vault_export.json";
            a.click();
        } else alert("Export Failed");
    });
}

// --- GENERATOR TAB ---
function updateLenLabel(v) { document.getElementById('lenLabel').innerText = v; }
function quickGenerate() {
    const len = document.getElementById('genRange').value;
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*()";
    let res = "";
    for(let i=0; i<len; i++) res += chars.charAt(Math.floor(Math.random()*chars.length));
    document.getElementById('genDisplay').innerText = res;
}

async function setMasterPassword() {
    const password = document.getElementById('masterSetupInput').value;
    const res = await fetch(`${API_BASE}/set-master`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ password })
    });
    const data = await res.json();
    alert(data.message || data.detail);
}

// --- HELPERS ---
function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

// Init
setInterval(checkHealth, 10000);
checkHealth();
fetchVault();
quickGenerate();