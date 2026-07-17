/* dashboard.js — dashboard data fetching and rendering */

function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

const DASHBOARD = {
    async load() {
        await Promise.allSettled([
            this.loadSummary(),
            this.loadPipeline(),
            this.loadCampaigns(),
        ]);
    },

    init() {
        document.addEventListener('page:dashboard', () => this.load());
    },

    setError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<p class="text-red-500 text-sm">${escapeHtml(message)}</p>`;
        }
    },

    // ── Summary cards ────────────────────────────────────────────────────────
    async loadSummary() {
        const container = document.getElementById('summary-cards');
        try {
            const data = await API.dashboardSummary();
            const global = data.global || {};
            const sequences = data.sequences || {};

            const cards = [
                { label: 'Total Leads', value: global.total_recipients || 0, icon: '📧' },
                { label: 'School Leads', value: (sequences.school || {}).recipients || 0, icon: '🏫' },
                { label: 'CSR Leads', value: ((sequences.csr || {}).recipients || 0) + ((sequences['csr-wsl-5'] || {}).recipients || 0), icon: '🤝' },
                { label: 'Blocked', value: global.blacklist_count || 0, icon: '🚫' },
            ];

            container.innerHTML = cards.map(card => `
                <div class="card p-6 rounded-2xl">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-2xl">${card.icon}</span>
                    </div>
                    <div class="text-3xl font-bold text-[var(--text-primary)]">${Number(card.value).toLocaleString()}</div>
                    <div class="text-sm text-[var(--text-muted)] mt-1">${card.label}</div>
                </div>
            `).join('');
        } catch (err) {
            this.setError('summary-cards', 'Could not load summary');
        }
    },

    // ── Pipeline table ───────────────────────────────────────────────────────
    async loadPipeline() {
        const tbody = document.getElementById('pipeline-body');
        try {
            const data = await API.dashboardPipeline();
            tbody.innerHTML = '';

            const dayTotals = {};
            [1, 3, 5, 7, 10].forEach(day => {
                dayTotals[day] = { total: 0, sent: 0, bounced: 0, replied: 0 };
            });

            Object.values(data.day_wise || {}).forEach(seqDays => {
                Object.entries(seqDays || {}).forEach(([day, row]) => {
                    day = parseInt(day, 10);
                    if (!dayTotals[day]) return;
                    dayTotals[day].total += row.total || 0;
                    dayTotals[day].sent += row.sent || 0;
                    dayTotals[day].bounced += row.bounced || 0;
                    dayTotals[day].replied += row.replied || 0;
                });
            });

            [1, 3, 5, 7, 10].forEach(day => {
                const stats = dayTotals[day];
                const status = stats.sent >= stats.total && stats.total > 0
                    ? '<span class="badge badge-success">✅ Done</span>'
                    : stats.sent > 0
                        ? '<span class="badge badge-teal">⏳ Sending</span>'
                        : '<span class="badge badge-gray">⏸ Pending</span>';

                const tr = document.createElement('tr');
                tr.className = 'border-b border-[var(--border)] last:border-0';
                tr.innerHTML = `
                    <td class="py-3 px-4 font-medium">Day ${day}</td>
                    <td class="py-3 px-4">${stats.total}</td>
                    <td class="py-3 px-4">${stats.sent}</td>
                    <td class="py-3 px-4">${stats.bounced}</td>
                    <td class="py-3 px-4">${stats.replied}</td>
                    <td class="py-3 px-4">${status}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-red-500">Could not load pipeline</td></tr>`;
        }
    },

    // ── Active campaigns ─────────────────────────────────────────────────────
    async loadCampaigns() {
        const container = document.getElementById('active-campaigns');
        try {
            const data = await API.dashboardBatches();
            container.innerHTML = '';

            const running = data.running || [];
            if (running.length === 0) {
                container.innerHTML = `<p class="text-[var(--text-muted)] text-sm">No active campaigns right now.</p>`;
                return;
            }

            for (const batch of running) {
                const counts = await API.getBatch(batch.id).catch(() => ({ counts: {} }));
                const sent = (counts.counts || {}).sent || 0;
                const total = Object.values(counts.counts || {}).reduce((a, b) => a + b, 0) || batch.total || 0;
                const pct = total > 0 ? Math.round((sent / total) * 100) : 0;

                const el = document.createElement('div');
                el.className = 'card rounded-2xl p-5';
                el.innerHTML = `
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-3">
                            <h4 class="font-semibold text-[var(--text-primary)]">${escapeHtml(batch.name)}</h4>
                            <span class="badge badge-teal">${escapeHtml((batch.sequence_id || '').toUpperCase())}</span>
                        </div>
                        <div class="flex items-center gap-3 text-sm text-[var(--text-muted)]">
                            <span>${sent}/${total}</span>
                            <div class="w-24 h-1.5 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                                <div class="h-full bg-[var(--accent-teal)] rounded-full" style="width: ${pct}%"></div>
                            </div>
                            <span>${pct}%</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        ${[1, 3, 5, 7, 10].map(d => {
                            const label = batch.day_offset === d ? 'Sending' : 'Queue';
                            const cls = batch.day_offset === d ? 'badge-teal' : 'badge-gray';
                            return `<span class="badge ${cls}">D${d} ${label}</span>`;
                        }).join('')}
                    </div>
                `;
                container.appendChild(el);
            }
        } catch (err) {
            this.setError('active-campaigns', 'Could not load active campaigns');
        }
    },
};
