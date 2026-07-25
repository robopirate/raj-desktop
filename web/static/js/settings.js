/* settings.js — Google auth, campaign settings, automation controls, audit log */

(function () {
    const services = ['gmail', 'calendar', 'drive'];
    let pollTimer = null;

    async function loadAuthStatus() {
        try {
            const status = await API.authStatus();
            renderStatus(status);
            if (services.every(s => status[s])) {
                stopPolling();
            }
        } catch (e) {
            services.forEach(s => renderService(s, false, 'Unknown'));
        }
    }

    function renderStatus(status) {
        services.forEach(s => renderService(s, !!status[s], status[s] ? 'Connected' : 'Not connected'));
    }

    function renderService(service, connected, text) {
        const dot = document.getElementById(`status-dot-${service}`);
        const label = document.getElementById(`status-text-${service}`);
        if (dot) {
            dot.className = `w-2.5 h-2.5 rounded-full ${connected ? 'bg-emerald-500' : 'bg-red-400'}`;
        }
        if (label) {
            label.textContent = text;
            label.className = `text-xs ${connected ? 'text-emerald-600 font-medium' : 'text-[var(--text-muted)]'}`;
        }
    }

    async function connect(service) {
        renderService(service, false, 'Connecting...');
        try {
            await API.connectService(service);
            showToast(`${service} connect started — approve in your browser`, 'info');
            startPolling();
        } catch (e) {
            showToast(e.message, 'error');
            loadAuthStatus();
        }
    }

    function startPolling() {
        if (pollTimer) return;
        pollTimer = setInterval(() => loadAuthStatus(), 5000);
        setTimeout(stopPolling, 120000);
    }

    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    async function loadDeliverability() {
        const box = document.getElementById('deliverability-checks');
        if (!box) return;
        box.innerHTML = '<p class="text-[var(--text-muted)]">Checking…</p>';
        try {
            const res = await API.deliverability();
            box.innerHTML = res.checks.map(c => `
                <div class="flex items-start gap-2">
                    <span class="${c.ok ? 'text-emerald-600' : 'text-red-500'} font-bold">${c.ok ? '✓' : '✗'}</span>
                    <div>
                        <div class="font-medium">${c.name} <span class="text-xs ${c.ok ? 'text-emerald-600' : 'text-red-500'}">${c.ok ? 'OK' : 'MISSING'}</span></div>
                        ${c.ok ? '' : `<div class="text-xs text-[var(--text-muted)]">${c.fix}</div>`}
                    </div>
                </div>`).join('') +
                `<p class="text-xs text-[var(--text-muted)] pt-2 border-t border-[var(--border)]">${res.all_ok ? '✅ All records present — emails are authenticated.' : 'Fix the missing records in your DNS (Squarespace), wait 1–24h, then re-check.'}</p>`;
        } catch (e) {
            box.innerHTML = `<p class="text-red-500 text-sm">DNS check failed: ${e.message}</p>`;
        }
    }

    async function loadCampaignSettings() {
        try {
            const s = await API.getCampaignSettings();
            const emailEl = document.getElementById('setting-brief-email');
            if (emailEl) emailEl.value = s.brief_email || '';
            const senderEl = document.getElementById('setting-default-sender');
            if (senderEl) senderEl.value = s.default_sender || 'om@robopirate.in';
            const pauseSchool = document.getElementById('setting-pause-school');
            if (pauseSchool) pauseSchool.checked = !!s.pause_school;
            const pauseCsr = document.getElementById('setting-pause-csr');
            if (pauseCsr) pauseCsr.checked = !!s.pause_csr;
            const pauseCsrWsl = document.getElementById('setting-pause-csrwsl');
            if (pauseCsrWsl) pauseCsrWsl.checked = !!s.pause_csr_wsl_5;
            const gapEl = document.getElementById('setting-send-gap');
            if (gapEl) gapEl.value = s.send_gap_seconds || 45;
            const capEl = document.getElementById('setting-daily-cap');
            if (capEl) capEl.value = s.daily_send_cap ?? 100;
        } catch (e) {
            console.error('Failed to load campaign settings', e);
        }
    }

    async function saveCampaignSettings() {
        const payload = {
            brief_email: document.getElementById('setting-brief-email')?.value.trim() || '',
            default_sender: document.getElementById('setting-default-sender')?.value.trim() || 'om@robopirate.in',
            pause_school: document.getElementById('setting-pause-school')?.checked || false,
            pause_csr: document.getElementById('setting-pause-csr')?.checked || false,
            pause_csr_wsl_5: document.getElementById('setting-pause-csrwsl')?.checked || false,
            send_gap_seconds: Math.max(30, parseInt(document.getElementById('setting-send-gap')?.value, 10) || 45),
            daily_send_cap: Math.max(0, parseInt(document.getElementById('setting-daily-cap')?.value, 10) ?? 100),
        };
        try {
            await API.updateCampaignSettings(payload);
            showToast('Campaign settings saved', 'success');
        } catch (e) {
            showToast(e.message || 'Failed to save settings', 'error');
        }
    }

    async function loadAutomationSettings() {
        try {
            const state = await API.getState();
            const autoBox = document.getElementById('setting-engine-autostart');
            if (autoBox) autoBox.checked = !!(state.desktop && state.desktop.engine_autostart);
        } catch (e) {
            console.error('Failed to load automation settings', e);
        }
    }

    async function toggleEngineAutostart(enabled) {
        try {
            const state = await API.getState();
            if (!state.desktop) state.desktop = {};
            state.desktop.engine_autostart = enabled;
            await API.setState(state);
        } catch (e) {
            showToast('Failed to save autostart setting', 'error');
        }
    }

    async function sendBrief() {
        try {
            const result = await API.triggerBrief();
            showToast(result.sent ? 'Morning brief sent' : 'Morning brief generated (email not configured)', 'success');
        } catch (e) {
            showToast(e.message || 'Brief failed', 'error');
        }
    }

    async function emergency(action, target) {
        try {
            await API.emergency(action, target);
            showToast(`${action.toUpperCase()} ${target.toUpperCase()} executed`, 'success');
        } catch (e) {
            showToast(e.message || 'Emergency command failed', 'error');
        }
    }

    async function loadAuditLog() {
        const tbody = document.getElementById('audit-log-body');
        if (!tbody) return;
        try {
            const rows = await API.getAuditLog(50);
            if (!rows.length) {
                tbody.innerHTML = '<tr><td colspan="4" class="py-8 text-center text-[var(--text-muted)]">No audit log entries.</td></tr>';
                return;
            }
            tbody.innerHTML = rows.map(r => `
                <tr class="border-b border-[var(--border)]">
                    <td class="py-2 px-3 text-xs text-[var(--text-muted)]">${new Date(r.created_at).toLocaleString()}</td>
                    <td class="py-2 px-3 text-xs font-medium">${r.action || ''}</td>
                    <td class="py-2 px-3 text-xs">${r.user || 'system'}</td>
                    <td class="py-2 px-3 text-xs text-[var(--text-muted)]">${r.details || ''}</td>
                </tr>
            `).join('');
        } catch (e) {
            tbody.innerHTML = '<tr><td colspan="4" class="py-8 text-center text-red-500">Failed to load audit log.</td></tr>';
        }
    }

    function init() {
        const container = document.getElementById('google-connections');
        if (!container) return;

        loadAuthStatus();
        loadCampaignSettings();
        loadAutomationSettings();
        loadAuditLog();
        loadDeliverability();
        document.getElementById('btn-recheck-deliverability')?.addEventListener('click', loadDeliverability);

        container.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-connect]');
            if (btn) connect(btn.dataset.connect);
        });

        const saveBtn = document.getElementById('btn-save-campaign-settings');
        if (saveBtn) saveBtn.addEventListener('click', saveCampaignSettings);

        const autoBox = document.getElementById('setting-engine-autostart');
        if (autoBox) autoBox.addEventListener('change', () => toggleEngineAutostart(autoBox.checked));

        const briefBtn = document.getElementById('btn-trigger-brief');
        if (briefBtn) briefBtn.addEventListener('click', sendBrief);

        document.getElementById('btn-emergency-stop-all')?.addEventListener('click', () => emergency('stop', 'all'));
        document.getElementById('btn-emergency-resume')?.addEventListener('click', () => emergency('resume', 'all'));
        document.getElementById('btn-emergency-stop-school')?.addEventListener('click', () => emergency('stop', 'school'));
        document.getElementById('btn-emergency-stop-csr')?.addEventListener('click', () => emergency('stop', 'csr'));
        document.getElementById('btn-refresh-audit')?.addEventListener('click', loadAuditLog);

        document.addEventListener('page:settings', () => {
            loadAuthStatus();
            loadCampaignSettings();
            loadAutomationSettings();
            loadAuditLog();
            startPolling();
        });
    }

    init();
})();
