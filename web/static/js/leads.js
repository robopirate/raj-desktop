/* leads.js — Lead segments overview on the Leads page.
   Shows one card per segment (sequence) with pool stats and actions:
   import into the segment, create a batch from it, reset for re-campaign. */
const LeadsPage = (() => {
    const els = {
        grid: document.getElementById('segments-grid'),
        importSeq: document.getElementById('import-sequence'),
        importSubPool: document.getElementById('import-sub-pool'),
    };

    const SEGMENT_LABELS = {
        'school': { title: 'School (Private Schools)', icon: '🏫' },
        'csr-wsl-5': { title: 'CSR (Corporate CSR)', icon: '🏢' },
        'leads': { title: 'Generic leads', icon: '📥' },
    };

    function stat(label, value, cls = '') {
        return `<div class="text-center">
            <div class="text-xl font-bold ${cls}">${value}</div>
            <div class="text-[11px] text-[var(--text-muted)]">${label}</div>
        </div>`;
    }

    function card(seq, s) {
        const meta = SEGMENT_LABELS[seq] || { title: seq, icon: '🗂️' };
        const contactable = Math.max(0, s.available - Math.min(s.available, s.blacklisted));
        const canReset = s.contacted > 0;
        return `
        <div class="card rounded-2xl p-5" data-segment="${seq}">
            <div class="flex items-center gap-2 mb-3">
                <span class="text-2xl">${meta.icon}</span>
                <h4 class="font-semibold text-sm">${meta.title}</h4>
            </div>
            <div class="grid grid-cols-4 gap-2 mb-4">
                ${stat('Total', s.total)}
                ${stat('Available', s.available, 'text-emerald-600')}
                ${stat('Contacted', s.contacted, 'text-amber-600')}
                ${stat('Blocked', s.blacklisted, 'text-red-500')}
            </div>
            <div class="flex items-center gap-3 text-sm">
                <button data-action="import" class="text-[var(--accent-teal)] hover:underline font-medium">Import here</button>
                <button data-action="batch" class="text-[var(--accent-teal)] hover:underline font-medium">Create batch</button>
                ${canReset ? `<button data-action="reset" class="text-amber-600 hover:underline font-medium">Reset for re-campaign</button>` : ''}
            </div>
        </div>`;
    }

    async function loadSegments() {
        if (!els.grid) return;
        try {
            const stats = await API.poolStats();
            const order = ['school', 'csr-wsl-5', 'leads'];
            const keys = [...order.filter(k => stats[k]), ...Object.keys(stats).filter(k => !order.includes(k))];
            els.grid.innerHTML = keys.map(k => card(k, stats[k])).join('');
        } catch (e) {
            els.grid.innerHTML = `<p class="text-sm text-red-500">Failed to load segments: ${e.message}</p>`;
        }
    }

    function onAction(e) {
        const btn = e.target.closest('button[data-action]');
        if (!btn) return;
        const cardEl = btn.closest('[data-segment]');
        const seq = cardEl && cardEl.dataset.segment;
        const action = btn.dataset.action;

        if (action === 'import') {
            if (els.importSeq) {
                els.importSeq.value = seq;
                els.importSeq.dispatchEvent(new Event('change'));
            }
            document.getElementById('import-file-form')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            showToast(`Importing into ${(SEGMENT_LABELS[seq] || {}).title || seq}`, 'success');
        }

        if (action === 'batch') {
            try { sessionStorage.setItem('batch_preselect', JSON.stringify({ sequence_id: seq === 'leads' ? null : seq, pull_from: seq })); } catch (_) {}
            const navLink = document.querySelector('a[data-page="batches"]');
            if (navLink) {
                navLink.click();
            } else if (typeof APP !== 'undefined' && typeof APP.showPage === 'function') {
                APP.showPage('batches');
            } else {
                location.hash = '#batches';
            }
        }

        if (action === 'reset') {
            const label = (SEGMENT_LABELS[seq] || {}).title || seq;
            if (!confirm(
                `Reset "${label}" for a new campaign?\n\n` +
                `Everyone except people who replied or are blacklisted becomes available again (batched=0).\n` +
                `Their OLD send history is archived (recoverable), so Day 1 of the new sequence can go out fresh.\n\n` +
                `Continue?`
            )) return;
            btn.disabled = true;
            btn.textContent = 'Resetting…';
            API.resetPool(seq).then(res => {
                showToast(`Reset done: ${res.leads_reset} leads available again (${res.sends_archived} old sends archived)`, 'success');
                loadSegments();
            }).catch(err => {
                showToast(err.message, 'error');
                btn.disabled = false;
                btn.textContent = 'Reset for re-campaign';
            });
        }
    }

    function init() {
        if (!els.grid) return;
        els.grid.addEventListener('click', onAction);
        loadSegments();
    }

    // Reload stats whenever the Leads page is shown
    window.addEventListener('hashchange', () => { if (location.hash === '#import') loadSegments(); });
    document.addEventListener('DOMContentLoaded', init);

    return { loadSegments };
})();
