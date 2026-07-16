/* templates.js — Template editor with HTML/Plain toggle, day pills, status grid, A/B, lock */

(function () {
    const state = {
        sequences: {},
        currentSeq: 'school',
        currentDay: 1,
        format: 'html', // 'html' or 'plain'
        templates: {}, // cache: 'seq:day' -> {subject, html_body, text_body}
        status: {},
    };

    const els = {
        seqList: document.getElementById('template-seq-list'),
        dayGrid: document.getElementById('template-day-grid'),
        dayStatus: document.getElementById('template-day-status'),
        statusGrid: document.getElementById('template-status-grid'),
        syncStatus: document.getElementById('template-sync-status'),
        formatHtml: document.getElementById('format-html'),
        formatPlain: document.getElementById('format-plain'),
        subject: document.getElementById('template-subject'),
        subjectB: document.getElementById('template-subject-b'),
        abEnabled: document.getElementById('template-ab-enabled'),
        abFields: document.getElementById('template-ab-fields'),
        abSplit: document.getElementById('template-ab-split'),
        abSplitValue: document.getElementById('ab-split-value'),
        body: document.getElementById('template-body'),
        editorLabel: document.getElementById('editor-label'),
        editorHint: document.getElementById('editor-hint'),
        btnPreview: document.getElementById('btn-preview-template'),
        btnSave: document.getElementById('btn-save-template'),
        btnTest: document.getElementById('btn-test-template'),
        btnGenerate: document.getElementById('btn-generate-template'),
        btnLock: document.getElementById('btn-lock-template'),
        btnSync: document.getElementById('btn-sync-templates'),
        btnGenerateMissing: document.getElementById('btn-generate-missing'),
        btnLockAll: document.getElementById('btn-lock-all'),
        trialForm: document.getElementById('trial-form'),
        trialEmail: document.getElementById('trial-email'),
        trialName: document.getElementById('trial-name'),
        trialOrg: document.getElementById('trial-org'),
    };

    function cacheKey() {
        return `${state.currentSeq}:${state.currentDay}`;
    }

    async function loadSequences() {
        try {
            state.sequences = await API.listSequences();
        } catch (e) {
            state.sequences = {};
        }
        renderSequenceList();
        renderDayGrid();
        const ids = Object.keys(state.sequences);
        if (ids.length && !state.sequences[state.currentSeq]) {
            state.currentSeq = ids[0];
        }
        await loadTemplateStatus();
        selectSequence(state.currentSeq, false);
    }

    function renderSequenceList() {
        if (!els.seqList) return;
        const ids = Object.keys(state.sequences);
        if (!ids.length) {
            els.seqList.innerHTML = '<p class="text-sm text-[var(--text-muted)]">No sequences configured.</p>';
            return;
        }
        els.seqList.innerHTML = ids.map(id => `
            <button data-seq="${id}" class="seq-btn w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors ${id === state.currentSeq ? 'bg-[var(--accent-teal)] text-white' : 'hover:bg-[var(--bg-secondary)]'}">
                ${id.toUpperCase()}
            </button>
        `).join('');
    }

    function renderDayGrid() {
        if (!els.dayGrid) return;
        const cfg = state.sequences[state.currentSeq] || { days: [1, 3, 5, 7, 10] };
        const days = cfg.days || [1, 3, 5, 7, 10];
        els.dayGrid.innerHTML = days.map(d => `
            <button data-day="${d}" class="day-btn py-2 rounded-lg text-sm font-medium transition-colors ${d === state.currentDay ? 'bg-[var(--accent-teal)] text-white' : 'bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white'}">
                ${d}
            </button>
        `).join('');
    }

    async function loadTemplateStatus() {
        try {
            const res = await API.listTemplates();
            state.status = (res && res.status) || {};
        } catch (e) {
            state.status = {};
        }
        renderStatusGrid();
    }

    function renderStatusGrid() {
        if (!els.statusGrid) return;
        const seqIds = Object.keys(state.sequences).length ? Object.keys(state.sequences) : ['school', 'csr', 'csr-wsl-5'];
        els.statusGrid.innerHTML = seqIds.map(seq => {
            const days = (state.sequences[seq] && state.sequences[seq].days) || [1, 3, 5, 7, 10];
            return `
                <tr class="border-b border-[var(--border)] last:border-0">
                    <td class="py-2 px-3 font-medium">${seq.toUpperCase()}</td>
                    ${[1, 3, 5, 7, 10].map(d => {
                        const st = (state.status[seq] && state.status[seq][d]) || { exists: false, empty: true, locked: false, ab_test: false };
                        const dayActive = days.includes(d);
                        if (!dayActive) return `<td class="py-2 px-3 text-center text-[var(--text-muted)]">—</td>`;
                        let badge = '';
                        if (st.locked) badge += '🔒';
                        if (st.exists && !st.empty) badge += '✅';
                        else if (st.exists && st.empty) badge += '⚠️';
                        else badge += '⬜';
                        if (st.ab_test) badge += ' A/B';
                        const title = `Source: ${st.source || 'none'}${st.locked ? ' (locked)' : ''}`;
                        return `<td class="py-2 px-3 text-center">
                            <button data-seq="${seq}" data-day="${d}" title="${title}" class="template-status-cell inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${seq === state.currentSeq && d === state.currentDay ? 'bg-[var(--accent-teal)] text-white' : 'bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white'} transition-colors">
                                ${badge}
                            </button>
                        </td>`;
                    }).join('')}
                </tr>
            `;
        }).join('');
    }

    function selectSequence(seq, load = true) {
        state.currentSeq = seq;
        const cfg = state.sequences[seq] || { days: [1, 3, 5, 7, 10] };
        const days = cfg.days || [1, 3, 5, 7, 10];
        if (!days.includes(state.currentDay)) state.currentDay = days[0];
        renderSequenceList();
        renderDayGrid();
        renderStatusGrid();
        if (load) loadTemplate();
    }

    function selectDay(day) {
        state.currentDay = parseInt(day, 10);
        renderDayGrid();
        renderStatusGrid();
        els.dayStatus.textContent = `Day ${state.currentDay}: Loading...`;
        loadTemplate().then(() => {
            els.dayStatus.textContent = `Day ${state.currentDay}: Template loaded`;
        });
    }

    async function loadTemplate() {
        const key = cacheKey();
        if (state.templates[key]) {
            renderTemplate(state.templates[key]);
            return;
        }
        try {
            const tmpl = await API.getTemplate(state.currentSeq, state.currentDay);
            state.templates[key] = tmpl;
            renderTemplate(tmpl);
        } catch (e) {
            renderTemplate({ subject: '', html_body: '', text_body: '', subject_b: '', ab_test: 0, ab_split: 0.5 });
        }
    }

    function renderTemplate(tmpl) {
        tmpl = tmpl || { subject: '', html_body: '', text_body: '', subject_b: '', ab_test: 0, ab_split: 0.5 };
        els.subject.value = tmpl.subject || '';
        els.subjectB.value = tmpl.subject_b || '';
        const abEnabled = !!tmpl.ab_test;
        els.abEnabled.checked = abEnabled;
        toggleABFields(abEnabled);
        const split = tmpl.ab_split != null ? Math.round(tmpl.ab_split * 100) : 50;
        els.abSplit.value = split;
        els.abSplitValue.textContent = split;
        updateLockButton();

        if (state.format === 'html') {
            els.body.value = tmpl.html_body || tmpl.text_body || '';
            els.editorLabel.textContent = 'HTML Editor';
            els.editorHint.textContent = 'HTML tags supported. Use {{name}}, {{org}} for personalization.';
        } else {
            els.body.value = tmpl.text_body || '';
            els.editorLabel.textContent = 'Plain Text Editor';
            els.editorHint.textContent = 'No HTML, just text. Better deliverability.';
        }
    }

    function toggleABFields(show) {
        if (!els.abFields) return;
        if (show) els.abFields.classList.remove('hidden');
        else els.abFields.classList.add('hidden');
    }

    function updateLockButton() {
        if (!els.btnLock) return;
        const st = (state.status[state.currentSeq] && state.status[state.currentSeq][state.currentDay]) || {};
        if (st.locked) {
            els.btnLock.textContent = '🔓 Unlock Template';
            els.btnLock.dataset.locked = 'true';
        } else {
            els.btnLock.textContent = '🔒 Lock Template';
            els.btnLock.dataset.locked = 'false';
        }
    }

    function setFormat(format) {
        state.format = format;
        const active = 'flex-1 py-2 rounded-md text-sm font-medium bg-white shadow-sm text-[var(--text-primary)] transition-all';
        const inactive = 'flex-1 py-2 rounded-md text-sm font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all';
        els.formatHtml.className = format === 'html' ? active : inactive;
        els.formatPlain.className = format === 'plain' ? active : inactive;
        loadTemplate();
    }

    async function openPreview() {
        const body = els.body.value || '';
        const subject = els.subject.value || '';
        if (!body.trim()) {
            showToast('Nothing to preview', 'warning');
            return;
        }
        try {
            await API.openPreview({
                subject: subject,
                body: body,
                format: state.format,
            });
            showToast('Opening preview in your browser...', 'success');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function saveTemplate() {
        const key = cacheKey();
        const cached = state.templates[key] || {};
        const payload = { subject: els.subject.value };

        if (state.format === 'html') {
            payload.html_body = els.body.value;
            if (cached.text_body) payload.text_body = cached.text_body;
        } else {
            payload.text_body = els.body.value;
            if (cached.html_body) payload.html_body = cached.html_body;
        }

        payload.subject_b = els.subjectB.value;
        payload.ab_test = els.abEnabled.checked ? 1 : 0;
        payload.ab_split = parseInt(els.abSplit.value, 10) / 100;
        payload.format = state.format;

        try {
            await API.updateTemplate(state.currentSeq, state.currentDay, payload);
            state.templates[key] = { ...cached, ...payload };
            showToast('Template saved', 'success');
            await loadTemplateStatus();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function testSend() {
        const email = prompt('Send test email to:');
        if (!email) return;
        try {
            await API.testSendTemplate(state.currentSeq, state.currentDay, email);
            showToast('Test email sent', 'success');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function generateTemplate() {
        if (!state.currentSeq) return;
        try {
            const result = await API.generateTemplate(state.currentSeq, state.currentDay, false);
            const key = cacheKey();
            state.templates[key] = result.template || state.templates[key];
            renderTemplate(state.templates[key]);
            showToast('Template generated (no Gmail draft created)', 'success');
            await loadTemplateStatus();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function toggleLock() {
        const st = (state.status[state.currentSeq] && state.status[state.currentSeq][state.currentDay]) || {};
        try {
            if (st.locked) {
                await API.unlockTemplate(state.currentSeq, state.currentDay);
                showToast('Template unlocked', 'success');
            } else {
                await API.lockTemplate(state.currentSeq, state.currentDay);
                showToast('Template locked', 'success');
            }
            await loadTemplateStatus();
            updateLockButton();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function syncTemplates() {
        try {
            els.syncStatus.textContent = 'Syncing...';
            const result = await API.syncTemplates();
            els.syncStatus.textContent = `Loaded ${result.loaded || 0}, skipped ${(result.skipped || []).length}`;
            showToast(`Synced ${result.loaded || 0} templates from Gmail`, 'success');
            state.templates = {};
            await loadTemplateStatus();
            await loadTemplate();
        } catch (e) {
            els.syncStatus.textContent = 'Sync failed';
            showToast(e.message, 'error');
        }
    }

    async function generateMissing() {
        try {
            els.syncStatus.textContent = 'Generating missing templates...';
            const result = await API.generateMissingTemplates();
            els.syncStatus.textContent = `Created ${result.count || 0} drafts`;
            showToast(`Generated ${result.count || 0} missing templates`, 'success');
            state.templates = {};
            await loadTemplateStatus();
            await loadTemplate();
        } catch (e) {
            els.syncStatus.textContent = 'Generate failed';
            showToast(e.message, 'error');
        }
    }

    async function lockAll() {
        if (!confirm('Lock all existing templates? Auto-sync and generate will skip locked templates.')) return;
        try {
            const result = await API.lockAllTemplates();
            showToast(`Locked ${result.locked || 0} templates`, 'success');
            await loadTemplateStatus();
            updateLockButton();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function trialSend(e) {
        e.preventDefault();
        if (!state.currentSeq) return;
        try {
            await API.trialSendSequence(
                state.currentSeq,
                els.trialEmail.value.trim(),
                els.trialName.value.trim(),
                els.trialOrg.value.trim(),
            );
            showToast('Trial sequence sent', 'success');
            els.trialForm.reset();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function init() {
        if (!els.seqList) return;
        loadSequences();

        els.seqList.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-seq]');
            if (btn) selectSequence(btn.dataset.seq);
        });

        els.dayGrid.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-day]');
            if (btn) selectDay(btn.dataset.day);
        });

        if (els.statusGrid) {
            els.statusGrid.addEventListener('click', (e) => {
                const btn = e.target.closest('.template-status-cell');
                if (!btn) return;
                selectSequence(btn.dataset.seq);
                selectDay(btn.dataset.day);
            });
        }

        els.formatHtml.addEventListener('click', () => setFormat('html'));
        els.formatPlain.addEventListener('click', () => setFormat('plain'));

        els.btnPreview.addEventListener('click', openPreview);
        els.btnSave.addEventListener('click', saveTemplate);
        els.btnTest.addEventListener('click', testSend);
        els.btnGenerate.addEventListener('click', generateTemplate);
        if (els.btnLock) els.btnLock.addEventListener('click', toggleLock);
        if (els.btnSync) els.btnSync.addEventListener('click', syncTemplates);
        if (els.btnGenerateMissing) els.btnGenerateMissing.addEventListener('click', generateMissing);
        if (els.btnLockAll) els.btnLockAll.addEventListener('click', lockAll);

        if (els.abEnabled) {
            els.abEnabled.addEventListener('change', () => toggleABFields(els.abEnabled.checked));
        }
        if (els.abSplit) {
            els.abSplit.addEventListener('input', () => {
                els.abSplitValue.textContent = els.abSplit.value;
            });
        }

        els.trialForm.addEventListener('submit', trialSend);

        document.addEventListener('page:templates', () => {
            loadSequences();
        });
    }

    init();
})();
