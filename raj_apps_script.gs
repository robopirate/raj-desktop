/**
 * Raj Scheduled Email Sender — Google Apps Script
 * 
 * This script runs on Google's servers (free) and sends Raj-scheduled drafts
 * at the right time, even when your laptop is closed.
 * 
 * SETUP:
 * 1. Go to https://script.google.com
 * 2. Create a new project
 * 3. Paste this entire file into the editor
 * 4. Click the clock icon (Triggers) → Add Trigger
 * 5. Choose function: sendScheduledDrafts
 * 6. Choose deployment: Head
 * 7. Choose event source: Time-driven
 * 8. Choose type: Minutes timer
 * 9. Choose interval: Every 15 minutes
 * 10. Save
 * 
 * The script will now check every 15 minutes for drafts created by Raj
 * and send them when their scheduled time arrives.
 */

const SCHEDULE_PREFIX = '[RAJ-SCHEDULE:';
const SCHEDULE_REGEX = /\[RAJ-SCHEDULE:([^\]]+)\]/;

function sendScheduledDrafts() {
  const now = new Date();
  const drafts = GmailApp.getDrafts();
  let sent = 0;
  let skipped = 0;

  for (const draft of drafts) {
    try {
      const message = draft.getMessage();
      const subject = message.getSubject();

      // Check if this is a Raj scheduled draft
      if (!subject.includes(SCHEDULE_PREFIX)) {
        continue;
      }

      // Extract scheduled time from subject
      const match = subject.match(SCHEDULE_REGEX);
      if (!match) {
        continue;
      }

      const sendAtStr = match[1].trim();
      const sendAt = new Date(sendAtStr);

      // Check if it's time to send
      if (now < sendAt) {
        skipped++;
        continue;
      }

      // Extract original subject (remove the schedule prefix)
      const originalSubject = subject.replace(SCHEDULE_REGEX, '').trim();

      // Get recipient and body
      const to = message.getTo();
      const body = message.getBody();
      const from = message.getFrom();

      // Send the email with the original subject
      GmailApp.sendEmail(to, originalSubject, '', {
        htmlBody: body,
        name: message.getFrom() // preserve sender name if set
      });

      // Delete the draft after sending
      draft.deleteDraft();
      sent++;

    } catch (e) {
      console.error('Error processing draft: ' + e);
    }
  }

  if (sent > 0 || skipped > 0) {
    console.log(`Raj Apps Script: ${sent} sent, ${skipped} pending`);
  }
}

/**
 * Manual test function — run this once after setup to verify it works.
 * It will log how many scheduled drafts are waiting.
 */
function testScheduledDrafts() {
  const drafts = GmailApp.getDrafts();
  let found = 0;

  for (const draft of drafts) {
    const subject = draft.getMessage().getSubject();
    if (subject.includes(SCHEDULE_PREFIX)) {
      const match = subject.match(SCHEDULE_REGEX);
      if (match) {
        console.log(`Found: "${subject}" scheduled for ${match[1]}`);
        found++;
      }
    }
  }

  console.log(`Total Raj scheduled drafts waiting: ${found}`);
}
