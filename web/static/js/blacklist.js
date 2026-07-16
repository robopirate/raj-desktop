/* blacklist.js — Blacklist management: add, remove, search, CSV import, bulk actions */

(function () {
    const els = {
        input: document.getElementById('blacklist-input'),
        addBtn: document.getElementById('btn-blacklist-add'),
        fileInput: document.getElementById('blacklist-file'),
        fileLabel: document.getElementById('blacklist-file-label'),
        count: document.getElementById('blacklist-count'),
        total: document.getElementById('blacklist-total'),
        bounced: document.getElementById('blacklist-bounced'),
        manual: document.getElementById('blacklist-manual'),
        hostile: document.getElementById('blacklist-hostile'),
        tbody: document.getElementById('blacklist-body'),
        search: document.getElementById('blacklist-search'),
        btnBulkRemove: document.getElementById('btn-bulk-remove'),
        selectAll: document.getElementById('blacklist-select-all'),
        scanBtn: document.getElementById('btn-bounce-scan'),
        scanRange: document.getElementById('bounce-scan-range'),
        scanResults: document.getElementById('bounce-scan-results'),
    };

    let emails = [];
    let filteredEmails = [];
    let selectedEmails = new Set();

    function updateSummary() {
        const total = emails.length;
        const bounced = emails.filter(e => (e.reason || '').toLowerCase().includes('bounce')).length;
        const manual = emails.filter(e => (e.source || '').toLowerCase() === 'manual' || (e.reason || '').toLowerCase() === 'manual').length;
        const hostile = emails.filter(e => ['hostile', 'unsubscribe', 'sentiment:hostile', 'sentiment:unsubscribe'].some(k => (e.reason || '').toLowerCase().includes(k))).length;
        if (els.total) els.total.textContent = total;
        if (els.bounced) els.bounced.textContent = bounced;
        if (els.manual) els.manual.textContent = manual;
        if (els.hostile) els.hostile.textContent = hostile;
    }

    function render() {
        const displayEmails = filteredEmails.length > 0 || els.search?.value ? filteredEmails : emails;
        updateSummary();
        els.count.textContent = `${displayEmails.length} email${displayEmails.length === 1 ? '' : 's'}`;
        if (!displayEmails.length) {
            els.tbody.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-[var(--text-muted)]">No blacklisted emails.</td></tr>';
            return;
        }
        els.tbody.innerHTML = displayEmails.map(e => `
            <tr class="border-b border-[var(--border)] hover:bg-[var(--bg-secondary)]">
                <td class="py-3 px-4">
                    <input type="checkbox" class="blacklist-checkbox rounded" data-email="${e.email}" ${selectedEmails.has(e.email) ? 'checked' : ''}>
                </td>
                <td class="py-3 px-4 font-medium">${e.email}</td>
                <td class="py-3 px-4 text-[var(--text-muted)]">${formatDate(e.added_at)}</td>
                <td class="py-3 px-4 text-[var(--text-muted)]">${e.reason || '—'}</td>
                <td class="py-3 px-4">
                    <button data-email="${e.email}" class="action-btn text-red-600 hover:bg-red-50" title="Remove">🗑</button>
                </td>
            </tr>
        `).join('');
        
        // Update select all checkbox
        if (els.selectAll) {
            const allSelected = displayEmails.length > 0 && displayEmails.every(e => selectedEmails.has(e.email));
            els.selectAll.checked = allSelected;
            els.selectAll.indeterminate = !allSelected && displayEmails.some(e => selectedEmails.has(e.email));
        }
        
        // Update bulk remove button
        if (els.btnBulkRemove) {
            els.btnBulkRemove.textContent = `Remove Selected (${selectedEmails.size})`;
            els.btnBulkRemove.disabled = selectedEmails.size === 0;
            els.btnBulkRemove.style.opacity = selectedEmails.size === 0 ? '0.5' : '1';
        }
    }

    function formatDate(iso) {
        if (!iso) return '—';
        return new Date(iso).toLocaleString();
    }

    async function load() {
        try {
            emails = await API.getBlacklist();
            filterEmails();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function filterEmails() {
        const query = els.search ? els.search.value.trim().toLowerCase() : '';
        if (!query) {
            filteredEmails = [];
        } else {
            filteredEmails = emails.filter(e => 
                e.email.toLowerCase().includes(query) || 
                (e.reason && e.reason.toLowerCase().includes(query))
            );
        }
        render();
    }

    async function addEmails() {
        const raw = els.input.value;
        if (!raw.trim()) return;
        const list = raw.split('\n').map(s => s.trim()).filter(Boolean);
        if (!list.length) return;
        try {
            const result = await API.addBlacklist(list, 'manual');
            showToast(`Added ${result.added} emails`, 'success');
            els.input.value = '';
            selectedEmails.clear();
            await load();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function removeEmail(email) {
        if (!confirm(`Remove ${email} from blacklist?`)) return;
        try {
            await API.removeBlacklist(email);
            selectedEmails.delete(email);
            showToast('Removed', 'success');
            await load();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function bulkRemove() {
        if (selectedEmails.size === 0) return;
        if (!confirm(`Remove ${selectedEmails.size} emails from blacklist?`)) return;
        let removed = 0;
        for (const email of selectedEmails) {
            try {
                await API.removeBlacklist(email);
                removed++;
            } catch (e) {
                console.error(`Failed to remove ${email}:`, e);
            }
        }
        selectedEmails.clear();
        showToast(`Removed ${removed} emails`, 'success');
        await load();
    }

    async function runBounceScan(days) {
        if (els.scanResults) {
            els.scanResults.classList.remove('hidden');
            els.scanResults.innerHTML = '<p class="text-[var(--text-muted)]">Scanning Gmail for bounces…</p>';
        }
        try {
            const result = await API.scanBounces(days);
            if (els.scanResults) {
                const lines = [
                    `<strong>Found:</strong> ${result.found || 0}`,
                    `<strong>Blacklisted:</strong> ${result.blacklisted || 0}`,
                    `<strong>Protected:</strong> ${result.protected || 0}`,
                ];
                if (result.details && result.details.length) {
                    lines.push('<ul class="mt-2 space-y-1 max-h-40 overflow-y-auto">' +
                        result.details.map(d => `<li class="text-xs">${d.email} — ${d.action}</li>`).join('') +
                        '</ul>');
                }
                els.scanResults.innerHTML = lines.join('<br>');
            }
            showToast(`Bounce scan complete: ${result.blacklisted || 0} blacklisted`, 'success');
            await load();
        } catch (e) {
            if (els.scanResults) {
                els.scanResults.innerHTML = `<p class="text-red-600">${e.message || 'Scan failed'}</p>`;
            }
            showToast(e.message, 'error');
        }
    }

    async function importCSV(file) {
        const formData = new FormData();
        formData.append('file', file);
        try {
            const result = await API.importBlacklist(formData);
            showToast(`Imported ${result.added} emails`, 'success');
            els.fileInput.value = '';
            els.fileLabel.textContent = '📄 Click to upload CSV';
            await load();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function onTableClick(e) {
        const btn = e.target.closest('[data-email]');
        if (btn && btn.tagName === 'BUTTON') {
            removeEmail(btn.dataset.email);
            return;
        }
        
        const checkbox = e.target.closest('.blacklist-checkbox');
        if (checkbox) {
            const email = checkbox.dataset.email;
            if (checkbox.checked) {
                selectedEmails.add(email);
            } else {
                selectedEmails.delete(email);
            }
            render();
        }
    }

    function onSelectAll() {
        const displayEmails = filteredEmails.length > 0 || els.search?.value ? filteredEmails : emails;
        if (els.selectAll.checked) {
            displayEmails.forEach(e => selectedEmails.add(e.email));
        } else {
            displayEmails.forEach(e => selectedEmails.delete(e.email));
        }
        render();
    }

    function init() {
        if (!els.tbody) return;

        els.addBtn.addEventListener('click', addEmails);
        els.tbody.addEventListener('click', onTableClick);
        els.fileInput.addEventListener('change', () => {
            const file = els.fileInput.files[0];
            if (file) {
                els.fileLabel.textContent = file.name;
                importCSV(file);
            }
        });
        
        if (els.search) {
            els.search.addEventListener('input', debounce(() => {
                filterEmails();
            }, 300));
        }
        
        if (els.selectAll) {
            els.selectAll.addEventListener('change', onSelectAll);
        }
        
        if (els.btnBulkRemove) {
            els.btnBulkRemove.addEventListener('click', bulkRemove);
        }

        if (els.scanBtn) {
            els.scanBtn.addEventListener('click', () => {
                const days = parseInt(els.scanRange?.value || '15', 10);
                runBounceScan(days);
            });
        }

        document.addEventListener('page:blacklist', () => load());
        load();
    }

    function debounce(fn, ms) {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn(...args), ms);
        };
    }

    init();
})();
