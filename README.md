# IDA Presentation Q&A Bot

Streamlit chatbot that answers attendees' questions during the IDA 2026 presentation.

## Logging questions and answers to Google Sheets

Every question and AI answer is appended to a Google Sheet as `Timestamp | User_Question | AI_Answer` (Singapore time).

1. Open the Google Sheet and go to **Extensions > Apps Script**.
2. Replace the editor contents with [`google_apps_script/Code.gs`](google_apps_script/Code.gs) and save.
3. Click **Deploy > New deployment**, choose type **Web app**, set **Execute as: Me** and **Who has access: Anyone**, then **Deploy** and authorize access when asked.
4. Copy the **Web app URL** (ends in `/exec`).
5. Add it to the Streamlit secrets (Streamlit Cloud: app **Settings > Secrets**; locally: `.streamlit/secrets.toml`):

   ```toml
   GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/XXXX/exec"
   ```

Rows are written to the first tab of the sheet. If the secret is not set, the app runs as before without logging. If you edit `Code.gs` later, redeploy with **Deploy > Manage deployments > Edit > New version** so the same URL keeps working.
