/* analytics.js — Engagement analytics page with CSS-based charts */

const ANALYTICS = {
    async load() {
        const rangeEl = document.getElementById('analytics-range');
        const seqEl = document.getElementById('analytics-seq');
        const days = rangeEl ? parseInt(rangeEl.value, 10) : 14;
        const seq = seqEl ? seqEl.value : '';

        try {
            const [summary, daily, links, activity] = await Promise.all([
                API.analyticsSummary(days, seq),
                API.analyticsDaily(days, seq),
                API.analyticsTopLinks(8),
                API.analyticsActivity(10),
            ]);
            this.renderSummary(summary);
            this.renderDaily(daily);
            this.renderFunnel(summary);
            this.renderTopLinks(links);
            this.renderActivity(activity);
        } catch (e) {
            showToast('Failed to load analytics: ' + e.message, 'error');
        }
    },

    renderSummary(stats) {
        const container = document.getElementById('analytics-summary');
        if (!container) return;
        const specs = [
            { key: 'sent', label: 'Sent', color: 'text-blue-500' },
            { key: 'opened', label: 'Opened', color: 'text-emerald-500' },
            { key: 'clicked', label: 'Clicked', color: 'text-amber-500' },
            { key: 'open_rate', label: 'Open Rate', color: 'text-violet-500', suffix: '%' },
            { key: 'ctr', label: 'CTR', color: 'text-pink-500', suffix: '%' },
        ];
        container.innerHTML = specs.map(s => `
            <div class="card p-4 rounded-2xl">
                <div class="text-xs text-[var(--text-muted)]">${s.label}</div>
                <div class="text-2xl font-bold ${s.color}">${stats[s.key] || 0}${s.suffix || ''}</div>
            </div>
        `).join('');
    },

    renderDaily(data) {
        const container = document.getElementById('analytics-daily-chart');
        if (!container) return;
        if (!data || !data.length) {
            container.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No sends in this range.</p>';
            return;
        }
        const maxSent = Math.max(...data.map(d => d.sent || 0), 1);
        container.innerHTML = `
            <div class="grid grid-cols-[80px_50px_50px_50px_1fr] gap-2 text-xs text-[var(--text-muted)] font-medium mb-2">
                <span>Date</span><span>Sent</span><span>Open</span><span>Click</span><span></span>
            </div>
            ${data.map(row => {
                const pct = row.sent ? Math.round((row.sent / maxSent) * 100) : 0;
                return `
                    <div class="grid grid-cols-[80px_50px_50px_50px_1fr] gap-2 items-center text-sm">
                        <span class="text-[var(--text-muted)]">${row.day || ''}</span>
                        <span class="text-blue-500">${row.sent || 0}</span>
                        <span class="text-emerald-500">${row.opened || 0}</span>
                        <span class="text-amber-500">${row.clicked || 0}</span>
                        <div class="h-2 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500 rounded-full" style="width: ${pct}%"></div>
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    },

    renderFunnel(stats) {
        const container = document.getElementById('analytics-funnel');
        if (!container) return;
        const sent = stats.sent || 0;
        if (!sent) {
            container.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No sends yet.</p>';
            return;
        }
        const stages = [
            { label: 'Sent', value: sent, color: 'bg-blue-500' },
            { label: 'Opened', value: stats.opened || 0, color: 'bg-emerald-500' },
            { label: 'Clicked', value: stats.clicked || 0, color: 'bg-amber-500' },
        ];
        container.innerHTML = stages.map(s => {
            const pct = s.value / sent;
            return `
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span>${s.label}</span>
                        <span class="text-[var(--text-muted)]">${s.value} (${(pct * 100).toFixed(1)}%)</span>
                    </div>
                    <div class="h-4 bg-[var(--bg-primary)] rounded-full overflow-hidden">
                        <div class="h-full ${s.color} rounded-full" style="width: ${Math.max(pct * 100, 1)}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    renderTopLinks(links) {
        const container = document.getElementById('analytics-top-links');
        if (!container) return;
        if (!links || !links.length) {
            container.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No clicks yet.</p>';
            return;
        }
        container.innerHTML = links.map(l => `
            <div class="flex items-start gap-3 text-sm">
                <span class="font-bold text-amber-500 w-6">${l.clicks || 0}</span>
                <a href="${l.url}" target="_blank" class="text-[var(--accent-teal)] hover:underline break-all">${l.url}</a>
            </div>
        `).join('');
    },

    renderActivity(rows) {
        const container = document.getElementById('analytics-activity');
        if (!container) return;
        if (!rows || !rows.length) {
            container.innerHTML = '<p class="text-[var(--text-muted)] text-sm">No recent activity.</p>';
            return;
        }
        container.innerHTML = rows.map(r => `
            <div class="text-sm border-b border-[var(--border)] pb-2 last:border-0">
                <div class="text-xs text-[var(--text-muted)]">${new Date(r.created_at).toLocaleString()}</div>
                <div>${r.message || r.action || ''}</div>
            </div>
        `).join('');
    },
};

document.addEventListener('page:analytics', () => ANALYTICS.load());
document.getElementById('analytics-range')?.addEventListener('change', () => ANALYTICS.load());
document.getElementById('analytics-seq')?.addEventListener('change', () => ANALYTICS.load());
document.getElementById('btn-refresh-analytics')?.addEventListener('click', () => ANALYTICS.load());
