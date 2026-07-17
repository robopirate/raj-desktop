/* integrations.js — Google Calendar and Drive management */

(function () {
    const els = {
        calendarStatus: document.getElementById('calendar-status'),
        calendarConnectPrompt: document.getElementById('calendar-connect-prompt'),
        btnConnectCal: document.getElementById('btn-connect-calendar'),
        calForm: document.getElementById('calendar-create-form'),
        calEmail: document.getElementById('cal-email'),
        calName: document.getElementById('cal-name'),
        calSubject: document.getElementById('cal-subject'),
        calDuration: document.getElementById('cal-duration'),
        calDays: document.getElementById('cal-days'),
        calTime: document.getElementById('cal-time'),
        calDesc: document.getElementById('cal-desc'),
        calEvents: document.getElementById('calendar-events'),

        driveStatus: document.getElementById('drive-status'),
        driveConnectPrompt: document.getElementById('drive-connect-prompt'),
        btnConnectDrive: document.getElementById('btn-connect-drive'),
        driveUploadForm: document.getElementById('drive-upload-form'),
        driveFile: document.getElementById('drive-file'),
        driveFileLabel: document.getElementById('drive-file-label'),
        driveSearch: document.getElementById('drive-search'),
        btnDriveSearch: document.getElementById('btn-drive-search'),
        driveFiles: document.getElementById('drive-files'),
    };

    async function loadAuthStatus() {
        updateConnectionUI('calendar', null);
        updateConnectionUI('drive', null);
        try {
            const status = await API.authStatus();
            updateConnectionUI('calendar', !!status.calendar);
            updateConnectionUI('drive', !!status.drive);
            const err = status.last_error || {};
            ['calendar', 'drive'].forEach(svc => {
                const info = err[svc];
                if (info && info.success === false && info.error) {
                    showToast(`${svc} connect failed: ${info.error}`, 'error');
                    // prevent repeated toasts
                    info.reported = true;
                }
            });
        } catch (e) {
            updateConnectionUI('calendar', false);
            updateConnectionUI('drive', false);
        }
    }

    function updateConnectionUI(service, connected, waiting = false) {
        const statusEl = els[`${service}Status`];
        const promptEl = els[`${service}ConnectPrompt`];
        if (statusEl) {
            if (waiting) {
                statusEl.textContent = 'Waiting for browser approval...';
                statusEl.className = 'text-xs text-amber-600 font-medium';
            } else if (connected === null) {
                statusEl.textContent = 'Checking...';
                statusEl.className = 'text-xs text-[var(--text-muted)]';
            } else {
                statusEl.textContent = connected ? 'Connected' : 'Not connected';
                statusEl.className = `text-xs ${connected ? 'text-emerald-600 font-medium' : 'text-red-500'}`;
            }
        }
        if (promptEl) {
            if (connected === true) promptEl.classList.add('hidden');
            else promptEl.classList.remove('hidden');
        }
    }

    let pollTimer = null;

    async function connect(service) {
        try {
            updateConnectionUI(service, null, true);
            await API.connectService(service);
            showToast(`${service} connect started — approve in your browser`, 'info');
            startPolling();
        } catch (e) {
            updateConnectionUI(service, false);
            showToast(e.message, 'error');
        }
    }

    function startPolling() {
        if (pollTimer) return;
        pollTimer = setInterval(loadAuthStatus, 4000);
        setTimeout(stopPolling, 120000);
    }

    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    // ── Calendar ─────────────────────────────────────────────────────────────
    function escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    async function loadCalendarEvents() {
        if (!els.calEvents) return;
        try {
            const events = await API.listCalendarEvents(20);
            if (!events || !events.length) {
                els.calEvents.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No upcoming meetings.</p>';
                return;
            }
            els.calEvents.innerHTML = events.map(ev => {
                const start = ev.start && (ev.start.dateTime || ev.start.date);
                const when = start ? new Date(start).toLocaleString() : 'No date';
                return `
                    <div class="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-secondary)] text-sm">
                        <div class="min-w-0">
                            <div class="font-medium truncate">${escapeHtml(ev.summary) || '(no title)'}</div>
                            <div class="text-xs text-[var(--text-muted)]">${escapeHtml(when)}</div>
                        </div>
                        <div class="flex gap-2 shrink-0 ml-2">
                            <a href="${escapeHtml(ev.htmlLink || '#')}" target="_blank" class="text-[var(--accent-teal)] hover:underline text-xs">Open</a>
                            <button data-event-id="${escapeHtml(ev.id)}" class="cal-cancel text-red-600 hover:underline text-xs">Cancel</button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (e) {
            els.calEvents.innerHTML = `<p class="text-red-500 text-sm">${escapeHtml(e.message)}</p>`;
        }
    }

    async function createMeeting(e) {
        e.preventDefault();
        const [hour, minute] = els.calTime.value.split(':').map(Number);
        const payload = {
            email: els.calEmail.value.trim(),
            name: els.calName.value.trim(),
            subject: els.calSubject.value.trim(),
            duration: parseInt(els.calDuration.value, 10),
            days_from_now: parseInt(els.calDays.value, 10),
            hour,
            minute,
            description: els.calDesc.value.trim(),
        };
        try {
            await API.createCalendarEvent(payload);
            showToast('Meeting created', 'success');
            els.calForm.reset();
            els.calDuration.value = 30;
            els.calDays.value = 2;
            els.calTime.value = '10:00';
            await loadCalendarEvents();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function cancelMeeting(id) {
        if (!confirm('Cancel this meeting?')) return;
        try {
            await API.cancelCalendarEvent(id);
            showToast('Meeting cancelled', 'success');
            await loadCalendarEvents();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    // ── Drive ─────────────────────────────────────────────────────────────────
    async function loadDriveFiles(query = '') {
        if (!els.driveFiles) return;
        try {
            const files = await API.listDriveFiles(null, query || null);
            if (!files || !files.length) {
                els.driveFiles.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No files found.</p>';
                return;
            }
            els.driveFiles.innerHTML = files.map(f => `
                <div class="flex items-center justify-between p-3 rounded-xl bg-[var(--bg-secondary)] text-sm">
                    <div class="min-w-0">
                        <div class="font-medium truncate">${escapeHtml(f.name)}</div>
                        <div class="text-xs text-[var(--text-muted)]">${escapeHtml(f.mimeType || '')}</div>
                    </div>
                    <div class="flex gap-2 shrink-0 ml-2">
                        <a href="${escapeHtml(f.webViewLink || '#')}" target="_blank" class="text-[var(--accent-teal)] hover:underline text-xs">Open</a>
                        <button data-file-id="${escapeHtml(f.id)}" class="drive-validate text-[var(--text-muted)] hover:underline text-xs">Validate</button>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            els.driveFiles.innerHTML = `<p class="text-red-500 text-sm">${escapeHtml(e.message)}</p>`;
        }
    }

    async function uploadDrive(e) {
        e.preventDefault();
        const file = els.driveFile.files[0];
        if (!file) {
            showToast('Select a file first', 'warning');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        try {
            const result = await API.uploadDriveFile(formData);
            showToast(`Uploaded: ${result.name}`, 'success');
            els.driveFile.value = '';
            els.driveFileLabel.textContent = '📄 Click to upload file';
            await loadDriveFiles(els.driveSearch.value.trim());
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function validateFile(id, btn) {
        try {
            const result = await API.validateDriveFile(id);
            btn.textContent = result.valid ? 'Valid' : 'Invalid';
            btn.className = result.valid ? 'text-emerald-600 text-xs' : 'text-red-600 text-xs';
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function init() {
        if (!els.calEvents && !els.driveFiles) return;

        loadAuthStatus();
        loadCalendarEvents();
        loadDriveFiles();

        els.btnConnectCal?.addEventListener('click', () => connect('calendar'));
        els.btnConnectDrive?.addEventListener('click', () => connect('drive'));

        els.calForm?.addEventListener('submit', createMeeting);
        els.calEvents?.addEventListener('click', (e) => {
            const btn = e.target.closest('.cal-cancel');
            if (btn) cancelMeeting(btn.dataset.eventId);
        });

        els.driveFile?.addEventListener('change', () => {
            const file = els.driveFile.files[0];
            if (file) els.driveFileLabel.textContent = file.name;
        });
        els.driveUploadForm?.addEventListener('submit', uploadDrive);
        els.btnDriveSearch?.addEventListener('click', () => loadDriveFiles(els.driveSearch.value.trim()));
        els.driveSearch?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') loadDriveFiles(els.driveSearch.value.trim());
        });
        els.driveFiles?.addEventListener('click', (e) => {
            const btn = e.target.closest('.drive-validate');
            if (btn) validateFile(btn.dataset.fileId, btn);
        });

        document.addEventListener('page:integrations', () => {
            loadAuthStatus();
            loadCalendarEvents();
            loadDriveFiles();
        });
    }

    init();
})();
