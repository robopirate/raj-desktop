/* batches.js — Batch creation and family pipeline management */

(function () {
    const state = {
        sequences: [],
        subPools: [],
        pipelines: [],
        expandedFamilies: new Set(),
    };

    const els = {
        form: document.getElementById('batch-create-form'),
        name: document.getElementById('batch-name'),
        sequence: document.getElementById('batch-sequence'),
        pullFrom: document.getElementById('batch-pull-from'),
        subPool: document.getElementById('batch-sub-pool'),
        size: document.getElementById('batch-size'),
        offset: document.getElementById('batch-offset'),
        schedule: document.getElementById('batch-schedule'),
        poolCount: document.getElementById('pool-count'),
        filterSeq: document.getElementById('batch-filter-seq'),
        body: document.getElementById('batches-body'),
    };

    async function loadSequences() {
        try {
            const seqObj = await API.listSequences();
            state.sequences = Object.keys(seqObj);
        } catch (e) {
            state.sequences = ['school', 'csr', 'csr-wsl-5'];
        }
        const allOptions = ['leads', ...state.sequences];
        populateSelect(els.pullFrom, allOptions, false);
        populateSelect(els.sequence, state.sequences, false);
        populateSelect(els.filterSeq, state.sequences, true);

        if (allOptions.includes('leads')) els.pullFrom.value = 'leads';
        if (state.sequences.includes('school')) els.sequence.value = 'school';

        await loadSubPools(els.pullFrom.value);
        await updatePoolCount();
    }

    function populateSelect(select, items, includeAll) {
        if (!select) return;
        const current = select.value;
        select.innerHTML = '';
        if (includeAll) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = '— All —';
            select.appendChild(opt);
        }
        items.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item;
            opt.textContent = item === 'leads' ? 'Generic leads pool' : item.toUpperCase();
            select.appendChild(opt);
        });
        if (current && Array.from(select.options).some(o => o.value === current)) select.value = current;
    }

    async function loadSubPools(seq) {
        try {
            const res = await API.listPools(seq);
            state.subPools = (res && res.pools) ? res.pools : [];
        } catch (e) {
            state.subPools = [];
        }
        const current = els.subPool.value;
        els.subPool.innerHTML = '<option value="">— All leads —</option>';
        state.subPools.forEach(sp => {
            const opt = document.createElement('option');
            opt.value = sp.name || sp;
            opt.textContent = `${sp.name || sp}${sp.count != null ? ` (${sp.count})` : ''}`;
            els.subPool.appendChild(opt);
        });
        if (current && Array.from(els.subPool.options).some(o => o.value === current)) {
            els.subPool.value = current;
        }
    }

    async function updatePoolCount() {
        const seq = els.pullFrom.value || 'leads';
        const sub = els.subPool.value || null;
        try {
            const count = await API.poolCount(seq, sub);
            els.poolCount.textContent = count;
        } catch (e) {
            els.poolCount.textContent = '—';
        }
    }

    async function loadPipelines() {
        const seq = els.filterSeq ? els.filterSeq.value : '';
        try {
            state.pipelines = await API.listPipelines(seq);
        } catch (e) {
            state.pipelines = [];
            showToast('Failed to load pipelines: ' + e.message, 'error');
        }
        renderPipelines();
    }

    function statusBadge(status) {
        const map = {
            running: 'bg-emerald-100 text-emerald-700',
            paused: 'bg-amber-100 text-amber-700',
            scheduled: 'bg-blue-100 text-blue-700',
            completed: 'bg-gray-100 text-gray-600',
            draft: 'bg-purple-100 text-purple-700',
            failed: 'bg-red-100 text-red-700',
        };
        const cls = map[status] || 'bg-gray-100 text-gray-600';
        return `<span class="px-2 py-1 rounded-full text-xs font-medium ${cls}">${status || 'unknown'}</span>`;
    }

    function dayBadge(day, batch) {
        const total = batch ? batch.total_recipients || 0 : 0;
        const sent = batch ? batch.sent || 0 : 0;
        const status = batch ? batch.status : 'draft';
        const pct = total > 0 ? Math.round((sent / total) * 100) : 0;
        const cls = batch ? 'bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white' : 'opacity-50 bg-[var(--bg-secondary)]';
        return `
            <div class="day-pill flex-1 min-w-[80px] p-2 rounded-xl border border-[var(--border)] ${cls} transition-colors cursor-pointer" data-day="${day}">
                <div class="text-xs font-semibold mb-1">D${day}</div>
                <div class="text-[10px] text-opacity-90">${sent}/${total}</div>
                <div class="w-full h-1 bg-black/10 rounded-full mt-1 overflow-hidden">
                    <div class="h-full bg-current rounded-full" style="width: ${pct}%"></div>
                </div>
                <div class="mt-1">${batch ? statusBadge(status) : '<span class="text-[10px] text-[var(--text-muted)]">empty</span>'}</div>
            </div>
        `;
    }

    function renderPipelines() {
        if (!state.pipelines.length) {
            els.body.innerHTML = '<p class="text-[var(--text-muted)] text-sm text-center py-8">No campaign families yet. Create a batch to start.</p>';
            return;
        }

        els.body.innerHTML = state.pipelines.map(pipe => {
            const root = pipe.batches && pipe.batches[0] ? pipe.batches[0] : {};
            const days = [1, 3, 5, 7, 10];
            const batchesByDay = {};
            (pipe.batches || []).forEach(b => { batchesByDay[b.day_offset] = b; });

            const total = pipe.family_total_leads || (pipe.batches || []).reduce((sum, b) => sum + (b.total_recipients || 0), 0);
            const sent = pipe.family_sent_leads || (pipe.batches || []).reduce((sum, b) => sum + (b.sent || 0), 0);
            const pct = total > 0 ? Math.round((sent / total) * 100) : 0;
            const isExpanded = state.expandedFamilies.has(pipe.root_batch_id);

            return `
                <div class="card rounded-2xl p-5 family-card" data-root="${pipe.root_batch_id}">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
                        <div class="flex items-center gap-3">
                            <h4 class="font-semibold text-[var(--text-primary)]">${pipe.root_name || root.name || 'Unknown'}</h4>
                            <span class="badge badge-teal">${(pipe.sequence_id || root.sequence_id || '').toUpperCase()}</span>
                        </div>
                        <div class="flex items-center gap-3 text-sm text-[var(--text-muted)]">
                            <span>${sent}/${total}</span>
                            <div class="w-24 h-1.5 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                                <div class="h-full bg-[var(--accent-teal)] rounded-full" style="width: ${pct}%"></div>
                            </div>
                            <span>${pct}%</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <button data-action="start-family" data-root="${pipe.root_batch_id}" class="action-btn text-emerald-600 hover:bg-emerald-50" title="Start family">▶</button>
                            <button data-action="pause-family" data-root="${pipe.root_batch_id}" class="action-btn text-amber-600 hover:bg-amber-50" title="Pause family">⏸</button>
                            <button data-action="clone-family" data-root="${pipe.root_batch_id}" class="action-btn text-blue-600 hover:bg-blue-50" title="Clone family">📋</button>
                            <button data-action="delete-family" data-root="${pipe.root_batch_id}" class="action-btn text-red-600 hover:bg-red-50" title="Delete family">🗑</button>
                            <button data-action="expand-family" data-root="${pipe.root_batch_id}" class="action-btn text-[var(--text-muted)] hover:bg-[var(--bg-secondary)]" title="Toggle details">${isExpanded ? '▲' : '▼'}</button>
                        </div>
                    </div>

                    <div class="flex flex-wrap gap-2 mb-2">
                        ${days.map(d => dayBadge(d, batchesByDay[d])).join('')}
                    </div>

                    ${isExpanded ? renderFamilyDetails(pipe, batchesByDay) : ''}
                </div>
            `;
        }).join('');
    }

    function renderFamilyDetails(pipe, batchesByDay) {
        const days = [1, 3, 5, 7, 10];
        return `
            <div class="mt-4 pt-4 border-t border-[var(--border)]">
                <div class="grid grid-cols-1 md:grid-cols-5 gap-2">
                    ${days.map(d => {
                        const b = batchesByDay[d];
                        if (!b) return `<div class="p-3 rounded-xl bg-[var(--bg-secondary)] text-[var(--text-muted)] text-xs text-center">D${d}<br>No batch</div>`;
                        return `
                            <div class="p-3 rounded-xl bg-[var(--bg-secondary)] text-xs">
                                <div class="font-semibold mb-2">D${d}</div>
                                <div class="space-y-1 text-[var(--text-secondary)]">
                                    <div class="flex justify-between"><span>Total</span><span>${b.total_recipients || 0}</span></div>
                                    <div class="flex justify-between"><span>Sent</span><span>${b.sent || 0}</span></div>
                                    ${Object.entries(b.counts || {}).filter(([k]) => k !== 'sent').map(([k, v]) => `<div class="flex justify-between"><span>${k}</span><span>${v}</span></div>`).join('')}
                                </div>
                                <div class="flex gap-2 mt-3">
                                    ${b.status !== 'running' ? `<button data-action="start" data-id="${b.id}" class="text-emerald-600 hover:underline">Start</button>` : ''}
                                    ${b.status === 'running' ? `<button data-action="pause" data-id="${b.id}" class="text-amber-600 hover:underline">Pause</button>` : ''}
                                    <button data-action="report" data-id="${b.id}" class="text-[var(--text-muted)] hover:underline">Report</button>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    async function createBatch(e) {
        e.preventDefault();
        const body = {
            name: els.name.value.trim(),
            pull_from: els.pullFrom.value || 'leads',
            sequence_id: els.sequence.value || null,
            sub_pool: els.subPool.value || null,
            batch_size: parseInt(els.size.value, 10),
            day_offset: parseInt(els.offset.value, 10),
            scheduled_at: els.schedule.value || null,
        };
        try {
            const result = await API.createBatch(body);
            showToast(`Batch created with ${result.size || 0} recipients`, 'success');
            els.form.reset();
            els.size.value = 10;
            els.offset.value = '1';
            if (state.sequences.includes('school')) els.sequence.value = 'school';
            if (els.pullFrom) els.pullFrom.value = 'leads';
            await updatePoolCount();
            await loadPipelines();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function startFamily(rootId) {
        const pipe = state.pipelines.find(p => p.root_batch_id == rootId);
        if (!pipe) return;
        let started = 0;
        for (const b of pipe.batches || []) {
            if (b.status === 'running') continue;
            if (b.status === 'scheduled') {
                // scheduled batches will auto-start at their time
                continue;
            }
            try {
                await API.startBatch(b.id, b.sequence_id);
                started++;
            } catch (e) { console.error(e); }
        }
        showToast(`Started ${started} day batch${started === 1 ? '' : 'es'}`, 'success');
        await loadPipelines();
    }

    async function pauseFamily(rootId) {
        const pipe = state.pipelines.find(p => p.root_batch_id == rootId);
        if (!pipe) return;
        let paused = 0;
        for (const b of pipe.batches || []) {
            if (b.status === 'running') {
                try {
                    await API.pauseBatch(b.id);
                    paused++;
                } catch (e) { console.error(e); }
            }
        }
        showToast(`Paused ${paused} day batch${paused === 1 ? '' : 'es'}`, 'success');
        await loadPipelines();
    }

    async function cloneFamily(rootId) {
        const pipe = state.pipelines.find(p => p.root_batch_id == rootId);
        if (!pipe || !pipe.batches || !pipe.batches.length) return;
        const first = pipe.batches[0];
        const newName = prompt('New family name:', `${pipe.root_name || first.name}_copy`);
        if (!newName) return;
        try {
            await API.cloneBatch(first.id, newName, first.sub_pool);
            showToast('Family cloned', 'success');
            await loadPipelines();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function deleteFamily(rootId) {
        if (!confirm('Delete this campaign family? All leads will return to the pool.')) return;
        try {
            await API.deleteFamily(rootId);
            showToast('Family deleted', 'success');
            await loadPipelines();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function onBatchAction(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const action = btn.dataset.action;

        if (action === 'start-family' || action === 'pause-family' || action === 'clone-family' || action === 'delete-family' || action === 'expand-family') {
            const rootId = btn.dataset.root;
            if (action === 'start-family') return startFamily(rootId);
            if (action === 'pause-family') return pauseFamily(rootId);
            if (action === 'clone-family') return cloneFamily(rootId);
            if (action === 'delete-family') return deleteFamily(rootId);
            if (action === 'expand-family') {
                if (state.expandedFamilies.has(rootId)) state.expandedFamilies.delete(rootId);
                else state.expandedFamilies.add(rootId);
                renderPipelines();
            }
            return;
        }

        const id = parseInt(btn.dataset.id, 10);
        if (action === 'start') {
            try {
                const batch = findBatch(id);
                await API.startBatch(id, batch?.sequence_id);
                showToast('Batch started', 'success');
                await loadPipelines();
            } catch (err) { showToast(err.message, 'error'); }
        } else if (action === 'pause') {
            try {
                await API.pauseBatch(id);
                showToast('Batch paused', 'success');
                await loadPipelines();
            } catch (err) { showToast(err.message, 'error'); }
        } else if (action === 'report') {
            try {
                const report = await API.batchReport(id);
                alert(JSON.stringify(report, null, 2));
            } catch (err) { showToast(err.message, 'error'); }
        }
    }

    function findBatch(id) {
        for (const pipe of state.pipelines) {
            for (const b of pipe.batches || []) {
                if (b.id === id) return b;
            }
        }
        return null;
    }

    function init() {
        if (!els.form) return;
        loadSequences();
        loadPipelines();

        els.form.addEventListener('submit', createBatch);
        els.pullFrom.addEventListener('change', async () => {
            await loadSubPools(els.pullFrom.value);
            await updatePoolCount();
        });
        els.subPool.addEventListener('change', updatePoolCount);
        if (els.filterSeq) els.filterSeq.addEventListener('change', loadPipelines);
        els.body.addEventListener('click', onBatchAction);

        document.addEventListener('page:batches', () => {
            loadSequences();
            loadPipelines();
        });
    }

    init();
})();
