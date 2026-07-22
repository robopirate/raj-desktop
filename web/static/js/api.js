/* api.js — thin fetch wrapper for the Raj Flask backend */

const API = {
    baseUrl: '',

    async request(method, path, body = null, timeoutMs = 30000) {
        const url = `${this.baseUrl}${path}`;
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), timeoutMs);
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal,
        };
        if (body !== null) {
            options.body = JSON.stringify(body);
        }

        try {
            const res = await fetch(url, options);
            clearTimeout(timeout);
            const json = await res.json().catch(() => ({ success: false, error: 'Invalid JSON response' }));
            if (!res.ok || !json.success) {
                throw new Error(json.error || `HTTP ${res.status}`);
            }
            return json.data;
        } catch (err) {
            clearTimeout(timeout);
            if (err.name === 'AbortError') {
                throw new Error(`Request timeout: ${method} ${path}`);
            }
            console.error(`API ${method} ${path} failed:`, err);
            throw err;
        }
    },

    get(path)  { return this.request('GET', path); },
    post(path, body = {}) { return this.request('POST', path, body); },
    put(path, body = {})  { return this.request('PUT', path, body); },
    delete(path) { return this.request('DELETE', path); },

    // Desktop / state
    health()        { return this.get('/api/health'); },
    getState()      { return this.get('/api/state'); },
    setState(body)  { return this.post('/api/state', body); },
    setAutostart(enabled) { return this.post('/api/settings/autostart', { enabled }); },

    // Health / status
    engineStatus()  { return this.get('/api/engine/status'); },
    startEngine()   { return this.post('/api/engine/start'); },
    stopEngine()    { return this.post('/api/engine/stop'); },
    pauseEngine()   { return this.post('/api/engine/pause'); },
    resumeEngine()  { return this.post('/api/engine/resume'); },
    triggerBrief()  { return this.post('/api/brief'); },
    emergency(action, target = 'all') { return this.post('/api/emergency', { action, target }); },
    getAuditLog(limit = 50) { return this.get(`/api/audit-log?limit=${limit}`); },
    authStatus()    { return this.get('/api/auth/status'); },

    // Dashboard
    dashboardSummary()  { return this.get('/api/dashboard/summary'); },
    dashboardPipeline() { return this.get('/api/dashboard/pipeline'); },
    dashboardBatches()  { return this.get('/api/dashboard/batches'); },

    // Analytics
    analyticsSummary(days = 30, seq = '') { return this.get(`/api/analytics/summary?days=${days}${seq ? '&sequence_id=' + encodeURIComponent(seq) : ''}`); },
    analyticsDaily(days = 14, seq = '') { return this.get(`/api/analytics/daily?days=${days}${seq ? '&sequence_id=' + encodeURIComponent(seq) : ''}`); },
    analyticsTopLinks(limit = 8) { return this.get(`/api/analytics/top-links?limit=${limit}`); },
    analyticsActivity(limit = 10) { return this.get(`/api/analytics/activity?limit=${limit}`); },

    // Batches
    listBatches(seq) {
        const q = seq ? `?sequence_id=${encodeURIComponent(seq)}` : '';
        return this.get(`/api/batches${q}`);
    },
    getBatch(id) { return this.get(`/api/batches/${id}`); },
    listPipelines(seq) {
        const q = seq ? `?sequence_id=${encodeURIComponent(seq)}` : '';
        return this.get(`/api/batches/pipelines${q}`);
    },
    getPipeline(batchId) { return this.get(`/api/batches/${batchId}/pipeline`); },
    deleteFamily(batchId) { return this.delete(`/api/batches/${batchId}/family`); },

    // Pools
    listPools(seq) { return this.get(`/api/pools?sequence_id=${encodeURIComponent(seq)}`); },
    poolCount(seq, sub) {
        const q = sub ? `&sub_pool=${encodeURIComponent(sub)}` : '';
        return this.get(`/api/pools/count?sequence_id=${encodeURIComponent(seq)}${q}`);
    },

    // Batches (mutations)
    createBatch(body) { return this.post('/api/batches', body); },
    startBatch(id, sequence_id) { return this.post(`/api/batches/${id}/start`, { sequence_id }); },
    pauseBatch(id) { return this.post(`/api/batches/${id}/pause`); },
    cloneBatch(id, newName, subPool) { return this.post(`/api/batches/${id}/clone`, { new_name: newName, sub_pool: subPool }); },
    deleteBatch(id) { return this.delete(`/api/batches/${id}`); },
    batchReport(id) { return this.get(`/api/batches/${id}/report`); },

    // Leads / Import
    uploadLeads(formData) {
        return fetch(`${this.baseUrl}/api/leads/import/file`, {
            method: 'POST',
            body: formData,
        }).then(r => r.json()).then(j => {
            if (!j.success) throw new Error(j.error || 'Upload failed');
            return j.data;
        });
    },
    previewPasteLeads(body) { return this.post('/api/leads/import/paste', body); },
    confirmPasteLeads(body) { return this.post('/api/leads/import/confirm', body); },

    // Templates
    listSequences() { return this.get('/api/sequences'); },
    listTemplates() { return this.get('/api/templates'); },
    getTemplate(seq, day) { return this.get(`/api/templates/${seq}/${day}`); },
    updateTemplate(seq, day, body) { return this.put(`/api/templates/${seq}/${day}`, body); },
    testSendTemplate(seq, day, email, extra = {}) { return this.post(`/api/templates/${seq}/${day}/test`, { email, ...extra }); },
    trialSendSequence(seq, email, name, org, format) { return this.post(`/api/templates/${seq}/trial`, { email, name, org, format }); },
    generateTemplate(seq, day, createDraft = true) { return this.post(`/api/templates/${seq}/${day}/generate`, { create_draft: createDraft }); },
    syncTemplates() { return this.post('/api/templates/sync'); },
    generateMissingTemplates() { return this.post('/api/templates/generate-missing'); },
    lockTemplate(seq, day) { return this.post(`/api/templates/${seq}/${day}/lock`); },
    unlockTemplate(seq, day) { return this.delete(`/api/templates/${seq}/${day}/lock`); },
    lockAllTemplates() { return this.post('/api/templates/lock-all'); },
    openPreview(body) { return this.post('/api/preview', body); },

    // Reports
    exportCampaign() { return this.post('/api/export'); },
    getCampaignSettings() { return this.get('/api/settings/campaign'); },
    updateCampaignSettings(body) { return this.post('/api/settings/campaign', body); },

    // Google auth
    connectService(service) { return this.post(`/api/connect/${service}`); },

    // Calendar
    listCalendarEvents(max = 10) { return this.get(`/api/calendar/events?max=${max}`); },
    createCalendarEvent(body) { return this.post('/api/calendar/events', body); },
    cancelCalendarEvent(id) { return this.delete(`/api/calendar/events/${encodeURIComponent(id)}`); },

    // Drive
    listDriveFiles(folderId, query) {
        const q = new URLSearchParams();
        if (folderId) q.set('folder_id', folderId);
        if (query) q.set('query', query);
        const qs = q.toString();
        return this.get(`/api/drive/files${qs ? '?' + qs : ''}`);
    },
    getDriveFile(id) { return this.get(`/api/drive/files/${encodeURIComponent(id)}`); },
    validateDriveFile(id) { return this.get(`/api/drive/files/${encodeURIComponent(id)}/validate`); },
    uploadDriveFile(formData) {
        return fetch(`${this.baseUrl}/api/drive/upload`, {
            method: 'POST',
            body: formData,
        }).then(r => r.json()).then(j => {
            if (!j.success) throw new Error(j.error || 'Upload failed');
            return j.data;
        });
    },

    // Replies
    getReplies(refresh = false, status = '', sentiment = '', search = '') {
        const q = new URLSearchParams();
        if (refresh) q.set('refresh', '1');
        if (status && status !== 'all') q.set('status', status);
        if (sentiment && sentiment !== 'all') q.set('sentiment', sentiment);
        if (search) q.set('search', search);
        const qs = q.toString();
        return this.get(`/api/replies${qs ? '?' + qs : ''}`);
    },
    getRepliesCount() { return this.get('/api/replies/count'); },
    markReplyHandled(id) { return this.post(`/api/replies/${id}/handled`); },
    draftReply(id) { return this.post(`/api/replies/${id}/draft`); },
    sendDraftReply(id) { return this.post(`/api/replies/${id}/send-draft`); },
    updateDraftReply(id, body) { return this.post(`/api/replies/${id}/update-draft`, { body }); },
    blacklistFromReply(id) { return this.post(`/api/replies/${id}/blacklist`); },

    // Blacklist
    getBlacklist() { return this.get('/api/blacklist'); },
    addBlacklist(emails, reason = 'manual') { return this.post('/api/blacklist', { emails, reason }); },
    removeBlacklist(email) { return this.delete(`/api/blacklist/${encodeURIComponent(email)}`); },
    scanBounces(days = 15) { return this.post('/api/blacklist/scan', { days }); },
    importBlacklist(formData) {
        return fetch(`${this.baseUrl}/api/blacklist/import`, {
            method: 'POST',
            body: formData,
        }).then(r => r.json()).then(j => {
            if (!j.success) throw new Error(j.error || 'Import failed');
            return j.data;
        });
    },
};
