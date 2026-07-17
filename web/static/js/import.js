/* import.js — Lead import: file upload and paste preview/confirm */

(function () {
    const els = {
        fileForm: document.getElementById('import-file-form'),
        fileInput: document.getElementById('import-file'),
        fileLabel: document.getElementById('file-label'),
        pasteForm: document.getElementById('import-paste-form'),
        pasteInput: document.getElementById('import-paste'),
        previewCard: document.getElementById('import-preview-card'),
        previewCount: document.getElementById('preview-count'),
        previewHead: document.getElementById('preview-head'),
        previewBody: document.getElementById('preview-body'),
        btnCancel: document.getElementById('import-cancel'),
        btnConfirm: document.getElementById('import-confirm'),
        seqSelect: document.getElementById('import-sequence'),
        subPoolInput: document.getElementById('import-sub-pool'),
    };

    let pendingImport = null; // { source: 'file'|'paste', payload, rows }

    function getSequenceId() {
        return els.seqSelect ? els.seqSelect.value : 'leads';
    }

    function getSubPool() {
        return els.subPoolInput ? els.subPoolInput.value.trim() : '';
    }

    function escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    function showPreview(rows, columns) {
        if (!rows || rows.length === 0) {
            showToast('No rows to preview', 'warning');
            return;
        }
        pendingImport = rows;
        els.previewCount.textContent = rows.length;
        els.previewCard.classList.remove('hidden');

        const cols = columns || Object.keys(rows[0]);
        els.previewHead.innerHTML = `<tr class="text-left text-[var(--text-muted)] border-b border-[var(--border)]">${cols.map(c => `<th class="py-2 px-3 font-medium uppercase text-xs">${escapeHtml(c)}</th>`).join('')}</tr>`;
        els.previewBody.innerHTML = rows.slice(0, 50).map(row => {
            return `<tr class="border-b border-[var(--border)]">${cols.map(c => `<td class="py-2 px-3">${escapeHtml(row[c] ?? '')}</td>`).join('')}</tr>`;
        }).join('');
        if (rows.length > 50) {
            els.previewBody.innerHTML += `<tr><td colspan="${cols.length}" class="py-2 px-3 text-[var(--text-muted)] text-xs">...and ${rows.length - 50} more rows</td></tr>`;
        }
    }

    function hidePreview() {
        pendingImport = null;
        els.previewCard.classList.add('hidden');
        els.previewHead.innerHTML = '';
        els.previewBody.innerHTML = '';
    }

    async function handleFile(e) {
        e.preventDefault();
        const file = els.fileInput.files[0];
        if (!file) {
            showToast('Please select a file', 'warning');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        formData.append('preview', 'true');
        formData.append('sequence_id', getSequenceId());
        formData.append('sub_pool', getSubPool());
        try {
            const data = await API.uploadLeads(formData);
            showPreview(data.rows, data.columns);
            pendingImport = { source: 'file', payload: file, rows: data.rows, columns: data.columns };
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function handlePaste(e) {
        e.preventDefault();
        const text = els.pasteInput.value.trim();
        if (!text) {
            showToast('Please paste some leads', 'warning');
            return;
        }
        try {
            const data = await API.previewPasteLeads({ 
                text, 
                sequence_id: getSequenceId(),
                sub_pool: getSubPool()
            });
            showPreview(data.rows, data.columns);
            pendingImport = { source: 'paste', payload: text, rows: data.rows, columns: data.columns };
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    async function confirmImport() {
        if (!pendingImport || !pendingImport.rows) return;
        try {
            if (pendingImport.source === 'paste') {
                const result = await API.confirmPasteLeads({ 
                    rows: pendingImport.rows, 
                    sequence_id: getSequenceId(),
                    sub_pool: getSubPool()
                });
                showToast(`Imported ${result.imported} leads`, 'success');
            } else {
                const formData = new FormData();
                formData.append('file', pendingImport.payload);
                formData.append('sequence_id', getSequenceId());
                formData.append('sub_pool', getSubPool());
                const result = await API.uploadLeads(formData);
                showToast(`Imported ${result.imported} leads`, 'success');
            }
            hidePreview();
            els.pasteInput.value = '';
            els.fileInput.value = '';
            els.fileLabel.textContent = 'Click to select CSV or Excel';
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    function init() {
        if (!els.fileForm) return;

        els.fileInput.addEventListener('change', () => {
            const file = els.fileInput.files[0];
            els.fileLabel.textContent = file ? file.name : 'Click to select CSV or Excel';
        });

        els.fileForm.addEventListener('submit', handleFile);
        els.pasteForm.addEventListener('submit', handlePaste);
        els.btnCancel.addEventListener('click', hidePreview);
        els.btnConfirm.addEventListener('click', confirmImport);
    }

    init();
})();
