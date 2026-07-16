/* replies.js — Reply inbox with search, filter, draft reply actions, and Gmail fetch */

(function () {
    const els = {
        list: document.getElementById('replies-list'),
        search: document.getElementById('reply-search'),
        filter: document.getElementById('reply-filter'),
        sentiment: document.getElementById('reply-sentiment'),
        fetchBtn: document.getElementById('btn-fetch-replies'),
        navBadge: document.getElementById('nav-replies-badge'),
        modal: document.getElementById('reply-draft-modal'),
        modalClose: document.getElementById('reply-modal-close'),
        modalCancel: document.getElementById('reply-modal-cancel'),
        modalSend: document.getElementById('reply-modal-send'),
        modalMeta: document.getElementById('reply-modal-meta'),
        modalBody: document.getElementById('reply-modal-body'),
    };

    let replies = [];
    let modalReplyId = null;

    function statusBadge(status) {
        const map = {
            pending: 'bg-amber-100 text-amber-700',
            handled: 'bg-emerald-100 text-emerald-700',
            drafted: 'bg-blue-100 text-blue-700',
        };
        const cls = map[status] || 'bg-gray-100 text-gray-600';
        const label = status === 'pending' ? 'Unread' : status === 'drafted' ? 'Draft Reply' : status;
        return `<span class="px-2 py-1 rounded-full text-xs font-medium ${cls}">${label}</span>`;
    }

    function sentimentBadge(sentiment) {
        if (!sentiment) return '';
        const map = {
            positive: 'bg-emerald-100 text-emerald-700',
            neutral: 'bg-blue-100 text-blue-700',
            hostile: 'bg-red-100 text-red-700',
            unsubscribe: 'bg-gray-100 text-gray-600',
        };
        const cls = map[sentiment] || 'bg-gray-100 text-gray-600';
        return `<span class="px-2 py-0.5 rounded text-xs font-medium ${cls} ml-2">${sentiment}</span>`;
    }

    function formatDate(iso) {
        if (!iso) return '—';
        return new Date(iso).toLocaleString();
    }

    function renderReplies() {
        if (!replies.length) {
            els.list.innerHTML = '<p class="text-[var(--text-muted)] text-sm text-center py-8">No replies found. Click Fetch to scan Gmail.</p>';
            return;
        }
        els.list.innerHTML = replies.map(r => `
            <div class="card rounded-xl p-4 hover:bg-[var(--bg-secondary)] transition-colors" data-reply-id="${r.id}">
                <div class="flex items-start justify-between gap-4">
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1 flex-wrap">
                            <span class="font-semibold text-sm">${r.from_addr || r.email || 'Unknown'}</span>
                            ${r.name ? `<span class="text-xs text-[var(--text-muted)]">(${r.name})</span>` : ''}
                            ${statusBadge(r.status)}
                            ${sentimentBadge(r.sentiment)}
                        </div>
                        <p class="text-sm font-medium text-[var(--text-primary)] mb-1 truncate">${r.subject || '(no subject)'}</p>
                        ${r.summary ? `<p class="text-xs text-[var(--text-secondary)] mb-1 italic">💡 ${escapeHtml(r.summary)}</p>` : ''}
                        <p class="text-xs text-[var(--text-muted)] line-clamp-2">${r.snippet || r.body || ''}</p>
                        <p class="text-[10px] text-[var(--text-muted)] mt-2">${formatDate(r.received_at || r.date)}</p>
                    </div>
                    <div class="flex flex-col gap-2 shrink-0">
                        ${r.status === 'pending' ? `
                            <button data-action="draft-reply" data-id="${r.id}" class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">📝 Generate Draft</button>
                            <button data-action="handled" data-id="${r.id}" class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">Mark handled</button>
                            <button data-action="blacklist" data-id="${r.id}" class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 hover:bg-red-50">🚫 Blacklist</button>
                        ` : r.status === 'drafted' ? `
                            <button data-action="edit-draft" data-id="${r.id}" class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">✏️ Edit / Send</button>
                            <button data-action="handled" data-id="${r.id}" class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">Mark handled</button>
                        ` : `
                            <span class="text-xs text-emerald-600 font-medium">✓ Handled</span>
                        `}
                    </div>
                </div>
            </div>
        `).join('');
    }

    async function loadReplies(refresh = false) {
        els.list.innerHTML = '<p class="text-[var(--text-muted)] text-sm text-center py-8">Loading replies...</p>';
        try {
            replies = await API.getReplies(refresh, els.filter.value, els.sentiment?.value, els.search.value.trim());
            renderReplies();
            await updateBadge();
        } catch (e) {
            showToast(e.message, 'error');
            els.list.innerHTML = '<p class="text-red-500 text-sm text-center py-8">Failed to load replies.</p>';
        }
    }

    async function updateBadge() {
        try {
            const counts = await API.getRepliesCount();
            const pending = counts.pending || 0;
            if (els.navBadge) {
                els.navBadge.textContent = pending;
                if (pending > 0) els.navBadge.classList.remove('hidden');
                else els.navBadge.classList.add('hidden');
            }
        } catch (e) {
            console.error('Failed to load reply counts', e);
        }
    }

    async function markHandled(id) {
        try {
            await API.markReplyHandled(id);
            showToast('Reply marked handled', 'success');
            await loadReplies(false);
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function draftReply(id) {
        try {
            const result = await API.draftReply(id);
            showToast('Draft reply created', 'success');
            await loadReplies(false);
            openModal(id, result.draft_html || '');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async function sendDraft(id, body) {
        if (!confirm('Send the drafted reply to this recipient?')) return;
        try {
            await API.updateDraftReply(id, body);
            await API.sendDraftReply(id);
            showToast('Draft reply sent', 'success');
            closeModal();
            await loadReplies(false);
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function openModal(id, body) {
        const reply = replies.find(r => r.id === id);
        if (!reply) return;
        modalReplyId = id;
        els.modalBody.value = stripHtml(body) || '';
        els.modalMeta.textContent = `${reply.from_addr || reply.email || 'Unknown'} — ${reply.subject || '(no subject)'}`;
        els.modal.classList.remove('hidden');
    }

    function closeModal() {
        modalReplyId = null;
        els.modal.classList.add('hidden');
    }

    async function blacklistSender(id) {
        if (!confirm('Blacklist this sender and mark the reply handled?')) return;
        try {
            await API.blacklistFromReply(id);
            showToast('Sender blacklisted', 'success');
            await loadReplies(false);
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    function stripHtml(html) {
        if (!html) return '';
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || '';
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function onAction(e) {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        const id = parseInt(btn.dataset.id, 10);
        const action = btn.dataset.action;
        
        switch (action) {
            case 'handled':
                markHandled(id);
                break;
            case 'draft-reply':
                draftReply(id);
                break;
            case 'edit-draft':
                const reply = replies.find(r => r.id === id);
                if (reply) openModal(id, reply.draft_html || '');
                break;
            case 'blacklist':
                blacklistSender(id);
                break;
        }
    }

    function init() {
        if (!els.list) return;

        els.fetchBtn.addEventListener('click', () => loadReplies(true));
        els.search.addEventListener('input', debounce(() => loadReplies(false), 400));
        els.filter.addEventListener('change', () => loadReplies(false));
        if (els.sentiment) els.sentiment.addEventListener('change', () => loadReplies(false));
        els.list.addEventListener('click', onAction);

        els.modalClose.addEventListener('click', closeModal);
        els.modalCancel.addEventListener('click', closeModal);
        els.modalSend.addEventListener('click', () => {
            if (modalReplyId !== null) sendDraft(modalReplyId, els.modalBody.value);
        });
        els.modal.addEventListener('click', (e) => {
            if (e.target === els.modal) closeModal();
        });

        document.addEventListener('page:replies', () => loadReplies(false));
        updateBadge();
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
