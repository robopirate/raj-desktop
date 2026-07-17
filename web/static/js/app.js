/* app.js — shell: routing, theme, engine controls, toasts */

const APP = {
    currentPage: 'dashboard',
    state: null,
    heartbeatTimer: null,

    async init() {
        await this.loadState();
        this.initTheme();
        this.initRouter();
        this.initEngineControls();
        this.initHeaderButtons();
        this.initKeyboardShortcuts();
        this.initHeartbeat();
        this.initPolling();
        this.initShutdownSignal();
        this.initSettings();
        if (typeof DASHBOARD !== 'undefined') DASHBOARD.init();
        const startPage = this.state?.page || 'dashboard';
        this.showPage(startPage);
        this.updateEngineStatus();
    },

    // ── Theme ────────────────────────────────────────────────────────────────
    initTheme() {
        const saved = localStorage.getItem('raj-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = saved || (prefersDark ? 'dark' : 'light');
        this.setTheme(theme);

        document.getElementById('theme-toggle').addEventListener('click', () => {
            const html = document.documentElement;
            const next = html.classList.contains('dark') ? 'light' : 'dark';
            this.setTheme(next);
        });
    },

    setTheme(theme, persist = true) {
        const html = document.documentElement;
        if (theme === 'dark') {
            html.classList.add('dark');
            html.setAttribute('data-theme', 'dark');
            document.getElementById('theme-icon').textContent = '☀️';
            document.getElementById('theme-label').textContent = 'Light mode';
        } else {
            html.classList.remove('dark');
            html.setAttribute('data-theme', 'light');
            document.getElementById('theme-icon').textContent = '🌙';
            document.getElementById('theme-label').textContent = 'Dark mode';
        }
        localStorage.setItem('raj-theme', theme);
        if (persist && this.state) {
            this.state.theme = theme;
            this.saveState();
        }
    },

    // ── Router ───────────────────────────────────────────────────────────────
    initRouter() {
        document.querySelectorAll('#sidebar-nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.showPage(page);
            });
        });
    },

    showPage(page) {
        this.currentPage = page;
        if (this.state && this.state.page !== page) {
            this.state.page = page;
            this.saveState();
        }

        // Sidebar active state
        document.querySelectorAll('#sidebar-nav a').forEach(link => {
            if (link.dataset.page === page) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Show/hide sections
        document.querySelectorAll('.page-section').forEach(section => {
            section.classList.add('hidden');
        });
        const target = document.getElementById(`page-${page}`);
        if (target) {
            target.classList.remove('hidden');
            target.classList.add('animate-fade-in');
        }

        // Header titles
        const titles = {
            dashboard: ['Dashboard', 'Overview of your email campaigns'],
            analytics: ['Analytics', 'Engagement and conversion insights'],
            batches: ['Batches', 'Create and manage campaign batches'],
            templates: ['Templates', 'Edit email templates'],
            import: ['Import', 'Import leads into pools'],
            replies: ['Replies', 'Manage recipient replies'],
            integrations: ['Integrations', 'Calendar and Drive management'],
            blacklist: ['Blacklist', 'Blocked email addresses'],
            settings: ['Settings', 'App configuration and connections'],
        };
        const [title, subtitle] = titles[page] || [page, ''];
        document.getElementById('page-title').textContent = title;
        document.getElementById('page-subtitle').textContent = subtitle;

        // Trigger page-specific load
        if (page === 'dashboard' && typeof DASHBOARD !== 'undefined') {
            DASHBOARD.load();
        }
        document.dispatchEvent(new CustomEvent(`page:${page}`));
    },

    // ── State persistence ────────────────────────────────────────────────────
    async loadState() {
        try {
            this.state = await API.getState();
            if (this.state.theme) this.setTheme(this.state.theme, false);
        } catch (e) {
            this.state = { page: 'dashboard', theme: 'light', desktop: {} };
        }
    },

    saveState() {
        if (!this.state) return;
        API.setState(this.state).catch(() => {});
    },

    // ── Engine controls ──────────────────────────────────────────────────────
    initEngineControls() {
        const pauseBtn = document.getElementById('btn-pause');
        pauseBtn.addEventListener('click', async () => {
            try {
                const status = await API.engineStatus();
                if (!status.running) {
                    this.toast('Engine is stopped. Start it first.', 'warning');
                    return;
                }
                if (status.paused) {
                    await API.resumeEngine();
                    this.toast('Engine resumed', 'success');
                } else {
                    await API.pauseEngine();
                    this.toast('Engine paused', 'warning');
                }
                this.updateEngineStatus();
            } catch (err) {
                this.toast(err.message || 'Engine control failed', 'error');
            }
        });

        const startBtn = document.getElementById('btn-engine-start');
        const stopBtn = document.getElementById('btn-engine-stop');
        if (startBtn) {
            startBtn.addEventListener('click', async () => {
                try {
                    await API.startEngine();
                    this.toast('Engine started', 'success');
                    this.updateEngineStatus();
                } catch (e) {
                    this.toast(e.message || 'Failed to start engine', 'error');
                }
            });
        }
        if (stopBtn) {
            stopBtn.addEventListener('click', async () => {
                try {
                    await API.stopEngine();
                    this.toast('Engine stopped', 'warning');
                    this.updateEngineStatus();
                } catch (e) {
                    this.toast(e.message || 'Failed to stop engine', 'error');
                }
            });
        }

        document.getElementById('btn-scan').addEventListener('click', async () => {
            try {
                const result = await API.scanBounces(15);
                this.toast(`Bounce scan: ${result.blacklisted || 0} blacklisted`, 'success');
            } catch (e) {
                this.toast(e.message || 'Bounce scan failed', 'error');
            }
        });
    },

    async updateEngineStatus() {
        try {
            const status = await API.engineStatus();
            const dot = document.getElementById('status-dot');
            const text = document.getElementById('status-text');
            const pauseBtn = document.getElementById('btn-pause');

            if (!status.running) {
                dot.className = 'w-2.5 h-2.5 rounded-full bg-[var(--danger)]';
                text.textContent = 'Stopped';
                if (pauseBtn) {
                    pauseBtn.textContent = '▶';
                    pauseBtn.title = 'Start engine from settings';
                }
                return;
            }

            if (status.paused) {
                dot.className = 'w-2.5 h-2.5 rounded-full bg-[var(--warning)]';
                text.textContent = 'Paused';
                if (pauseBtn) {
                    pauseBtn.textContent = '▶';
                    pauseBtn.title = 'Resume engine';
                }
            } else {
                dot.className = 'w-2.5 h-2.5 rounded-full bg-[var(--success)]';
                text.textContent = 'Running';
                if (pauseBtn) {
                    pauseBtn.textContent = '⏸';
                    pauseBtn.title = 'Pause engine';
                }
            }
        } catch (err) {
            document.getElementById('status-dot').className = 'w-2.5 h-2.5 rounded-full bg-[var(--danger)]';
            document.getElementById('status-text').textContent = 'Unknown';
        }
    },

    // ── Keyboard shortcuts ─────────────────────────────────────────────────
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (!e.ctrlKey) return;
            const key = e.key.toLowerCase();
            if (e.shiftKey && key === 'r') {
                e.preventDefault();
                if (typeof DASHBOARD !== 'undefined') DASHBOARD.load();
                this.toast('Dashboard refreshed', 'success');
            } else if (e.shiftKey && key === 'p') {
                e.preventDefault();
                document.getElementById('btn-pause').click();
            } else if (e.shiftKey && key === 'n') {
                e.preventDefault();
                this.showPage('batches');
            } else if (e.shiftKey && key === 'd') {
                e.preventDefault();
                this.showPage('dashboard');
            } else if (e.shiftKey && key === 't') {
                e.preventDefault();
                const html = document.documentElement;
                const next = html.classList.contains('dark') ? 'light' : 'dark';
                this.setTheme(next);
            } else if (key === 'q') {
                e.preventDefault();
                if (confirm('Quit Raj?')) {
                    navigator.sendBeacon?.('/api/shutdown');
                    setTimeout(() => window.close(), 150);
                }
            }
        });
    },

    // ── Heartbeat / offline overlay ──────────────────────────────────────────
    initHeartbeat() {
        if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
        this.heartbeatTimer = setInterval(() => this._heartbeat(), 30000);
        this._heartbeat();
    },

    initPolling() {
        const pollPages = ['dashboard', 'batches', 'replies', 'analytics', 'integrations', 'blacklist'];
        setInterval(() => {
            if (document.hidden) return;
            if (pollPages.includes(this.currentPage)) {
                document.dispatchEvent(new CustomEvent(`page:${this.currentPage}`));
            }
        }, 30000);
    },

    async _heartbeat() {
        try {
            await API.health();
            this._setOffline(false);
        } catch (e) {
            this._setOffline(true);
        }
    },

    _setOffline(offline) {
        let overlay = document.getElementById('offline-overlay');
        if (offline) {
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'offline-overlay';
                overlay.className = 'fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm';
                overlay.innerHTML = `
                    <div class="bg-[var(--bg-card)] p-8 rounded-2xl shadow-xl text-center max-w-sm mx-4">
                        <div class="text-4xl mb-3">🔌</div>
                        <h3 class="text-lg font-semibold mb-2">Reconnecting…</h3>
                        <p class="text-sm text-[var(--text-muted)] mb-4">Raj lost contact with the backend.</p>
                        <button id="retry-connection" class="btn-primary px-4 py-2 rounded-xl text-sm font-medium">Retry now</button>
                    </div>
                `;
                document.body.appendChild(overlay);
                overlay.querySelector('#retry-connection').addEventListener('click', () => this._heartbeat());
            }
        } else if (overlay) {
            overlay.remove();
        }
    },

    // ── Graceful shutdown signal ─────────────────────────────────────────────
    initShutdownSignal() {
        window.addEventListener('beforeunload', () => {
            navigator.sendBeacon?.('/api/shutdown');
        });
    },

    // ── Header buttons ───────────────────────────────────────────────────────
    initHeaderButtons() {
        const refreshBtn = document.getElementById('header-refresh');
        const exportBtn = document.getElementById('header-export');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                if (typeof DASHBOARD !== 'undefined') {
                    DASHBOARD.loaded = false;
                    DASHBOARD.load();
                }
                document.dispatchEvent(new CustomEvent(`page:${this.currentPage}`));
                this.toast('Refreshed', 'success');
            });
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', async () => {
                try {
                    const result = await API.exportCampaign();
                    this.toast(`Exported to ${result.file || 'campaign_state.md'}`, 'success');
                } catch (e) {
                    this.toast(e.message || 'Export failed', 'error');
                }
            });
        }
    },

    // ── Settings page ────────────────────────────────────────────────────────
    initSettings() {
        const trayBox = document.getElementById('setting-tray');
        const startBox = document.getElementById('setting-autostart');
        const notifyBox = document.getElementById('setting-notify');
        const ds = this.state?.desktop || {};

        if (trayBox) {
            trayBox.checked = ds.minimize_to_tray !== false;
            trayBox.addEventListener('change', () => {
                this.state.desktop.minimize_to_tray = trayBox.checked;
                this.saveState();
            });
        }
        if (startBox) {
            startBox.checked = !!ds.start_on_boot;
            startBox.addEventListener('change', async () => {
                this.state.desktop.start_on_boot = startBox.checked;
                this.saveState();
                try {
                    await API.setAutostart(startBox.checked);
                } catch (e) {
                    this.toast('Could not update startup shortcut', 'error');
                }
            });
        }
        if (notifyBox) {
            notifyBox.checked = ds.notifications !== false;
            notifyBox.addEventListener('change', () => {
                this.state.desktop.notifications = notifyBox.checked;
                this.saveState();
            });
        }
    },

    // ── Toast notifications ──────────────────────────────────────────────────
    toast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('hiding');
            toast.addEventListener('animationend', () => toast.remove());
        }, duration);
    },
};

window.showToast = (message, type = 'info', duration = 3000) => APP.toast(message, type, duration);

document.addEventListener('DOMContentLoaded', () => APP.init());
