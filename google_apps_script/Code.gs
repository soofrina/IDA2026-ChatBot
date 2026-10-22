/**
 * Receives each attendee question and AI answer from the Streamlit app
 * and appends it as a new row: Timestamp | User_Question | AI_Answer.
 *
 * Setup: in the Google Sheet, open Extensions > Apps Script, paste this file,
 * then Deploy > New deployment > Web app (Execute as: Me, Who has access: Anyone).
 */
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  sheet.appendRow([
    data.timestamp || new Date(),
    data.question || "",
    data.answer || ""
  ]);
  return ContentService
    .createTextOutput(JSON.stringify({ status: "ok" }))
    .setMimeType(ContentService.MimeType.JSON);
}
