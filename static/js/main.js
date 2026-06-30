/* ─────────────────────────────────────────────────────
   Menstrual Tracker — main.js
   Shared utilities loaded on every page via base.html
───────────────────────────────────────────────────── */

/* ── Toast Notification ── */
function showToast(message, icon = '✅', duration = 3000) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.innerHTML = `<span class="toast-icon"></span><span class="toast-msg"></span>`;
        document.body.appendChild(toast);
    }
    toast.querySelector('.toast-icon').textContent = icon;
    toast.querySelector('.toast-msg').textContent = message;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

/* ── Mobile Sidebar Toggle ── */
function initMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Create overlay if not exists
    let overlay = document.getElementById('sidebarOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'sidebarOverlay';
        overlay.className = 'sidebar-overlay';
        overlay.onclick = closeSidebar;
        document.body.appendChild(overlay);
    }

    // Inject hamburger into topbar if not exists
    const topbar = document.querySelector('.topbar');
    if (topbar && !topbar.querySelector('.hamburger')) {
        const ham = document.createElement('button');
        ham.className = 'hamburger';
        ham.innerHTML = '☰';
        ham.onclick = openSidebar;
        topbar.insertBefore(ham, topbar.firstChild);
    }
}

function openSidebar() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebarOverlay').classList.add('show');
}
function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    const o = document.getElementById('sidebarOverlay');
    if (o) o.classList.remove('show');
}

/* ── Format date to readable ── */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

/* ── Days until a date ── */
function daysUntil(dateStr) {
    if (!dateStr || dateStr === 'N/A') return null;
    const parts = dateStr.split(' ');
    // Handle "DD Mon YYYY"
    const target = new Date(dateStr);
    const today = new Date();
    today.setHours(0,0,0,0);
    return Math.round((target - today) / 86400000);
}

/* ── Capitalize ── */
function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

/* ── Debounce ── */
function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

/* ── Confirm delete with custom dialog ── */
function confirmDelete(url, message) {
    if (confirm(message || 'Are you sure you want to delete this record?')) {
        window.location.href = url;
    }
}

/* ── Chart default colors ── */
const CHART_COLORS = {
    pink:      '#E75480',
    pinkLight: '#FF85A1',
    pinkPale:  'rgba(231,84,128,0.12)',
    mauve:     '#7B3F6E',
    border:    '#FFAAC8',
    muted:     '#9E7A9A',
    green:     '#4CAF50',
    blue:      '#2196F3',
    yellow:    '#FFC107',
};

/* Chart.js global defaults */
if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#9E7A9A';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.pointStyleWidth = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = '#2D1B2E';
    Chart.defaults.plugins.tooltip.titleColor = '#FF85A1';
    Chart.defaults.plugins.tooltip.bodyColor = '#fff';
    Chart.defaults.plugins.tooltip.cornerRadius = 10;
    Chart.defaults.plugins.tooltip.padding = 10;
}

/* ── Active nav highlight (fallback) ── */
function highlightNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(a => {
        const href = a.getAttribute('href');
        if (href && path.startsWith(href) && href !== '/') {
            a.classList.add('active');
        }
    });
}

/* ── Animate number counter ── */
function animateCount(el, target, suffix = '', duration = 800) {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
        start += step;
        if (start >= target) { start = target; clearInterval(timer); }
        el.textContent = Math.floor(start) + suffix;
    }, 16);
}

/* ── Init on DOM ready ── */
document.addEventListener('DOMContentLoaded', () => {
    initMobileSidebar();

    // Auto-dismiss alerts after 5s
    document.querySelectorAll('.alert').forEach(a => {
        setTimeout(() => { a.style.transition = 'opacity 0.5s'; a.style.opacity = '0'; setTimeout(() => a.remove(), 500); }, 5000);
    });

    // Set max date for date inputs to today
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(inp => {
        if (!inp.max) inp.max = today;
    });

    // Animate stat values
    document.querySelectorAll('.stat-value[data-count]').forEach(el => {
        const val = parseInt(el.dataset.count);
        if (!isNaN(val)) animateCount(el, val);
    });
});
