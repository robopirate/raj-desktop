# Raj Web UI — Complete Feature Fix Spec
## For: Kimi Code Implementation

---

## PROBLEMS FOUND

The current web UI has these missing/broken features that the user NEEDS:

### 1. Templates Page — CRITICAL ISSUES

**Issue A: No HTML/Plain Text Toggle**
- The user explicitly asked for HTML and Plain Text email options
- Backend supports both `html_body` and `text_body` (db.py, gmail.py, engine.py all updated)
- Frontend only has ONE textarea that saves to `text_body`
- Need: Toggle switch "HTML" ↔ "Plain Text" with two separate editors

**Issue B: No Email Preview**
- User can't see how the email looks before sending
- Need: Side-by-side preview pane showing rendered HTML or plain text

**Issue C: Only Saves text_body**
- `templates.js` line 91: only sends `text_body`
- When in HTML mode, should save to `html_body`
- When in Plain Text mode, should save to `text_body`

**Issue D: No 5-Day Template View**
- User wants to see all 5 days at once (Day 1, 3, 5, 7, 10)
- Currently only has a dropdown `<select>` for day
- Need: Visual day pills/buttons showing all 5 days with status indicators

### 2. Replies Page — EMPTY PLACEHOLDER
- Currently shows: "Reply inbox coming in Phase 2"
- Need: Real reply list with search, filter, and AI response generation

### 3. Blacklist Page — EMPTY PLACEHOLDER
- Currently shows: "Blacklist management coming in Phase 2"
- Need: List of blacklisted emails, add/remove, import from CSV

---

## REQUIRED FIXES

### Fix 1: Templates Page — Complete Rewrite

#### New HTML Structure (index.html)

Replace the entire `<section id="page-templates">` with:

```html
<section id="page-templates" class="page-section hidden max-w-[1400px] mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left sidebar: Sequences + Days -->
        <div class="lg:col-span-3 space-y-6">
            <!-- Sequence selector -->
            <div class="card rounded-2xl p-5">
                <h3 class="text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-3">Sequence</h3>
                <div id="template-seq-list" class="space-y-1">
                    <button class="seq-btn w-full text-left px-3 py-2 rounded-lg text-sm font-medium bg-[var(--accent-teal)] text-white">SCHOOL</button>
                    <button class="seq-btn w-full text-left px-3 py-2 rounded-lg text-sm font-medium hover:bg-[var(--bg-secondary)]">CSR</button>
                    <button class="seq-btn w-full text-left px-3 py-2 rounded-lg text-sm font-medium hover:bg-[var(--bg-secondary)]">CSR-WSL-5</button>
                </div>
            </div>
            
            <!-- Day selector -->
            <div class="card rounded-2xl p-5">
                <h3 class="text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-3">Day</h3>
                <div class="grid grid-cols-5 gap-2" id="template-day-grid">
                    <button data-day="1" class="day-btn py-2 rounded-lg text-sm font-medium bg-[var(--accent-teal)] text-white">1</button>
                    <button data-day="3" class="day-btn py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white transition-colors">3</button>
                    <button data-day="5" class="day-btn py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white transition-colors">5</button>
                    <button data-day="7" class="day-btn py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white transition-colors">7</button>
                    <button data-day="10" class="day-btn py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white transition-colors">10</button>
                </div>
                <div class="mt-3 text-xs text-[var(--text-muted)]" id="template-day-status">
                    Day 1: Template loaded
                </div>
            </div>
            
            <!-- Format toggle -->
            <div class="card rounded-2xl p-5">
                <h3 class="text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-3">Format</h3>
                <div class="flex bg-[var(--bg-secondary)] rounded-lg p-1">
                    <button id="format-html" class="flex-1 py-2 rounded-md text-sm font-medium bg-white shadow-sm text-[var(--text-primary)] transition-all">HTML</button>
                    <button id="format-plain" class="flex-1 py-2 rounded-md text-sm font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all">Plain Text</button>
                </div>
                <p class="text-xs text-[var(--text-muted)] mt-2">
                    HTML: Rich formatting with images and links<br>
                    Plain Text: Simple text, better deliverability
                </p>
            </div>
            
            <!-- Actions -->
            <div class="card rounded-2xl p-5 space-y-3">
                <button id="btn-preview-template" class="btn-secondary w-full py-2.5 rounded-xl text-sm font-medium">👁 Preview Email</button>
                <button id="btn-test-template" class="btn-secondary w-full py-2.5 rounded-xl text-sm font-medium">🧪 Test Send</button>
                <button id="btn-generate-template" class="btn-secondary w-full py-2.5 rounded-xl text-sm font-medium">✨ Auto-Generate</button>
                <button id="btn-save-template" class="btn-primary w-full py-2.5 rounded-xl text-sm font-medium">💾 Save Template</button>
            </div>
        </div>
        
        <!-- Main editor area -->
        <div class="lg:col-span-9 space-y-6">
            <!-- Subject line -->
            <div class="card rounded-2xl p-6">
                <label class="block text-xs font-medium text-[var(--text-muted)] mb-2">Subject Line</label>
                <input type="text" id="template-subject" class="input w-full rounded-xl px-4 py-3 text-sm font-medium" placeholder="Enter subject line...">
                <p class="text-xs text-[var(--text-muted)] mt-2">Use {{name}}, {{org}} for personalization</p>
            </div>
            
            <!-- Editor + Preview -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Editor -->
                <div class="card rounded-2xl p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-sm font-semibold" id="editor-label">HTML Editor</h3>
                        <span class="text-xs text-[var(--text-muted)]" id="editor-hint">HTML tags supported</span>
                    </div>
                    <textarea id="template-body" rows="20" class="input w-full rounded-xl px-4 py-3 text-sm font-mono" placeholder="Enter email content..."></textarea>
                </div>
                
                <!-- Preview -->
                <div class="card rounded-2xl p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-sm font-semibold">Preview</h3>
                        <span class="text-xs text-[var(--text-muted)]">How recipients will see it</span>
                    </div>
                    <div id="template-preview" class="bg-white rounded-xl border border-[var(--border)] p-4 min-h-[400px] overflow-auto">
                        <p class="text-[var(--text-muted)] text-sm">Click "Preview Email" to see how it looks</p>
                    </div>
                </div>
            </div>
            
            <!-- Trial send -->
            <div class="card rounded-2xl p-6">
                <h3 class="text-sm font-semibold mb-4">🧪 Trial Send (All 5 Days)</h3>
                <p class="text-xs text-[var(--text-muted)] mb-4">Send the complete sequence to your email to test</p>
                <form id="trial-form" class="flex flex-wrap gap-3 items-end">
                    <div class="flex-1 min-w-[200px]">
                        <label class="block text-xs text-[var(--text-muted)] mb-1">Your Email</label>
                        <input type="email" id="trial-email" class="input w-full rounded-xl px-4 py-2 text-sm" placeholder="you@example.com" required>
                    </div>
                    <div class="min-w-[150px]">
                        <label class="block text-xs text-[var(--text-muted)] mb-1">Your Name</label>
                        <input type="text" id="trial-name" class="input w-full rounded-xl px-4 py-2 text-sm" placeholder="John Doe">
                    </div>
                    <div class="min-w-[150px]">
                        <label class="block text-xs text-[var(--text-muted)] mb-1">Organization</label>
                        <input type="text" id="trial-org" class="input w-full rounded-xl px-4 py-2 text-sm" placeholder="Company">
                    </div>
                    <button type="submit" class="btn-primary px-6 py-2 rounded-xl text-sm font-medium">Send Trial</button>
                </form>
            </div>
        </div>
    </div>
</section>
```

#### New templates.js Logic

```javascript
// State
const state = {
    sequences: {},
    currentSeq: 'school',
    currentDay: 1,
    format: 'html', // 'html' or 'plain'
    templates: {}, // Cache: { 'school:1': {subject, html_body, text_body} }
};

// Load template for current seq+day
async function loadTemplate() {
    const key = `${state.currentSeq}:${state.currentDay}`;
    
    // Try cache first
    if (state.templates[key]) {
        renderTemplate(state.templates[key]);
        return;
    }
    
    // Fetch from API
    try {
        const tmpl = await API.getTemplate(state.currentSeq, state.currentDay);
        state.templates[key] = tmpl;
        renderTemplate(tmpl);
    } catch (e) {
        // No template yet — show empty
        renderTemplate({ subject: '', html_body: '', text_body: '' });
    }
}

// Render template into editor
function renderTemplate(tmpl) {
    els.subject.value = tmpl.subject || '';
    
    if (state.format === 'html') {
        els.body.value = tmpl.html_body || tmpl.text_body || '';
        els.editorLabel.textContent = 'HTML Editor';
        els.editorHint.textContent = 'HTML tags supported';
    } else {
        els.body.value = tmpl.text_body || '';
        els.editorLabel.textContent = 'Plain Text Editor';
        els.editorHint.textContent = 'No HTML, just text';
    }
    
    // Update preview if we have content
    if (tmpl.html_body || tmpl.text_body) {
        updatePreview();
    }
}

// Save template
async function saveTemplate() {
    const key = `${state.currentSeq}:${state.currentDay}`;
    const payload = {
        subject: els.subject.value,
    };
    
    if (state.format === 'html') {
        payload.html_body = els.body.value;
        // Keep existing text_body if we have it
        if (state.templates[key]?.text_body) {
            payload.text_body = state.templates[key].text_body;
        }
    } else {
        payload.text_body = els.body.value;
        // Keep existing html_body if we have it
        if (state.templates[key]?.html_body) {
            payload.html_body = state.templates[key].html_body;
        }
    }
    
    try {
        await API.updateTemplate(state.currentSeq, state.currentDay, payload);
        // Update cache
        state.templates[key] = { ...state.templates[key], ...payload };
        showToast('Template saved', 'success');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// Preview
function updatePreview() {
    const body = els.body.value;
    const previewEl = document.getElementById('template-preview');
    
    if (state.format === 'html') {
        // Render HTML directly
        previewEl.innerHTML = body || '<p class="text-[var(--text-muted)]">No content to preview</p>';
    } else {
        // Escape HTML and show as plain text
        previewEl.innerHTML = `<pre class="whitespace-pre-wrap font-sans text-sm">${escapeHtml(body)}</pre>`;
    }
}

// Format toggle
function setFormat(format) {
    state.format = format;
    
    // Update toggle buttons
    document.getElementById('format-html').className = format === 'html' 
        ? 'flex-1 py-2 rounded-md text-sm font-medium bg-white shadow-sm text-[var(--text-primary)] transition-all'
        : 'flex-1 py-2 rounded-md text-sm font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all';
    document.getElementById('format-plain').className = format === 'plain'
        ? 'flex-1 py-2 rounded-md text-sm font-medium bg-white shadow-sm text-[var(--text-primary)] transition-all'
        : 'flex-1 py-2 rounded-md text-sm font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all';
    
    // Reload template in new format
    loadTemplate();
}

// Day selection (visual pills)
function selectDay(day) {
    state.currentDay = day;
    
    // Update visual state
    document.querySelectorAll('.day-btn').forEach(btn => {
        const btnDay = parseInt(btn.dataset.day);
        if (btnDay === day) {
            btn.className = 'day-btn py-2 rounded-lg text-sm font-medium bg-[var(--accent-teal)] text-white';
        } else {
            btn.className = 'day-btn py-2 rounded-lg text-sm font-medium bg-[var(--bg-secondary)] hover:bg-[var(--accent-teal)] hover:text-white transition-colors';
        }
    });
    
    document.getElementById('template-day-status').textContent = `Day ${day}: Loading...`;
    
    loadTemplate().then(() => {
        document.getElementById('template-day-status').textContent = `Day ${day}: Template loaded`;
    });
}
```

#### API Changes (api.js)

Add these methods if missing:

```javascript
// Get template (already exists, verify it returns html_body + text_body)
getTemplate: (seq, day) => fetch(`${BASE}/templates/${seq}/${day}`).then(r => r.json()).then(j => j.data),

// Update template (already exists, verify it accepts html_body + text_body)
updateTemplate: (seq, day, data) => fetch(`${BASE}/templates/${seq}/${day}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
}).then(r => r.json()),

// List sequences (already exists)
listSequences: () => fetch(`${BASE}/sequences`).then(r => r.json()).then(j => j.data),

// Test send (already exists)
testSendTemplate: (seq, day, email) => fetch(`${BASE}/templates/${seq}/${day}/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
}).then(r => r.json()),

// Generate template (already exists)
generateTemplate: (seq, day) => fetch(`${BASE}/templates/${seq}/${day}/generate`, {
    method: 'POST'
}).then(r => r.json()),

// Trial send (already exists)
trialSendSequence: (seq, email, name, org) => fetch(`${BASE}/templates/${seq}/trial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name, org })
}).then(r => r.json()),
```

### Fix 2: Replies Page — Real Implementation

Replace the placeholder `<section id="page-replies">` with:

```html
<section id="page-replies" class="page-section hidden max-w-[1400px] mx-auto">
    <div class="card rounded-2xl p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold">💬 Replies</h3>
            <div class="flex items-center gap-3">
                <input type="text" id="reply-search" class="input rounded-xl px-4 py-2 text-sm" placeholder="Search replies...">
                <select id="reply-filter" class="input rounded-xl px-3 py-2 text-sm">
                    <option value="all">All</option>
                    <option value="unread">Unread</option>
                    <option value="replied">Replied</option>
                </select>
                <button id="btn-fetch-replies" class="btn-primary px-4 py-2 rounded-xl text-sm font-medium">🔄 Fetch</button>
            </div>
        </div>
        <div id="replies-list" class="space-y-3">
            <p class="text-[var(--text-muted)] text-sm">Click "Fetch" to load replies from Gmail</p>
        </div>
    </div>
</section>
```

Backend endpoint needed:
```python
@app.route("/api/replies", methods=["GET"])
def get_replies():
    # Fetch from Gmail API or local DB
    # Return list of replies with: id, from, subject, snippet, date, thread_id, status
    pass
```

### Fix 3: Blacklist Page — Real Implementation

Replace the placeholder `<section id="page-blacklist">` with:

```html
<section id="page-blacklist" class="page-section hidden max-w-[1400px] mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Add to blacklist -->
        <div class="lg:col-span-1">
            <div class="card rounded-2xl p-6 space-y-4">
                <h3 class="text-lg font-semibold">🚫 Add to Blacklist</h3>
                <textarea id="blacklist-input" rows="6" class="input w-full rounded-xl px-4 py-3 text-sm font-mono" placeholder="Enter emails to blacklist, one per line..."></textarea>
                <button id="btn-blacklist-add" class="btn-primary w-full py-2.5 rounded-xl text-sm font-medium">Add to Blacklist</button>
                <div class="border-t border-[var(--border)] pt-4">
                    <p class="text-xs text-[var(--text-muted)] mb-2">Or upload CSV:</p>
                    <input type="file" id="blacklist-file" accept=".csv" class="hidden">
                    <label for="blacklist-file" class="block border-2 border-dashed border-[var(--border)] rounded-xl p-4 text-center cursor-pointer hover:border-[var(--accent-teal)] transition-colors">
                        <span class="text-sm">📄 Click to upload CSV</span>
                    </label>
                </div>
            </div>
        </div>
        
        <!-- Blacklist list -->
        <div class="lg:col-span-2">
            <div class="card rounded-2xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">Blacklisted Emails</h3>
                    <span class="text-sm text-[var(--text-muted)]" id="blacklist-count">0 emails</span>
                </div>
                <div class="overflow-x-auto max-h-[600px] overflow-y-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-left text-[var(--text-muted)] border-b border-[var(--border)]">
                                <th class="py-3 px-4 font-medium uppercase text-xs">Email</th>
                                <th class="py-3 px-4 font-medium uppercase text-xs">Added</th>
                                <th class="py-3 px-4 font-medium uppercase text-xs">Reason</th>
                                <th class="py-3 px-4 font-medium uppercase text-xs">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="blacklist-body">
                            <tr><td colspan="4" class="py-8 text-center text-[var(--text-muted)]">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</section>
```

Backend endpoints needed:
```python
@app.route("/api/blacklist", methods=["GET"])
def get_blacklist():
    # Return paginated list of blacklisted emails
    pass

@app.route("/api/blacklist", methods=["POST"])
def add_to_blacklist():
    # Add emails to blacklist
    pass

@app.route("/api/blacklist/<email>", methods=["DELETE"])
def remove_from_blacklist(email):
    # Remove email from blacklist
    pass
```

---

## IMPLEMENTATION CHECKLIST

### templates.js — Rewrite Required
- [ ] Add format state (html/plain)
- [ ] Add HTML/Plain Text toggle UI
- [ ] Add separate preview pane
- [ ] Save to correct field (html_body vs text_body)
- [ ] Visual day pills (1,3,5,7,10) instead of dropdown
- [ ] Cache templates to avoid re-fetching
- [ ] Update preview on input change (debounced)

### index.html — Update Required
- [ ] Replace templates section with new layout
- [ ] Replace replies placeholder with real UI
- [ ] Replace blacklist placeholder with real UI

### api.js — Verify/Add
- [ ] Verify getTemplate returns both html_body and text_body
- [ ] Verify updateTemplate accepts both fields
- [ ] Add getReplies endpoint
- [ ] Add getBlacklist endpoint
- [ ] Add addBlacklist endpoint
- [ ] Add removeBlacklist endpoint

### app.py — Add Endpoints
- [ ] GET /api/replies
- [ ] GET /api/blacklist
- [ ] POST /api/blacklist
- [ ] DELETE /api/blacklist/<email>
- [ ] Verify GET /api/templates/<seq>/<day> returns html_body + text_body
- [ ] Verify PUT /api/templates/<seq>/<day> accepts html_body + text_body

---

## TESTING

1. Open Templates page
2. Select "CSR-WSL-5" sequence
3. Click Day 1, 3, 5, 7, 10 — each should load different template
4. Toggle "HTML" ↔ "Plain Text" — content should switch
5. Edit HTML body, save, reload — should persist
6. Edit Plain Text body, save, reload — should persist
7. Click "Preview" — should show rendered HTML or escaped plain text
8. Click "Test Send" — should send to entered email
9. Go to Replies page — should show list (or "Fetch" button)
10. Go to Blacklist page — should show table, add/remove works

---

## NOTES

- The backend ALREADY supports html_body and text_body (db.py, engine.py, gmail.py all updated)
- The frontend just needs to USE both fields properly
- Keep existing dashboard, batches, import pages working
- Don't break any existing functionality
