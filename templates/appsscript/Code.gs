/**
 * 워크시트 제출 수신용 Apps Script.
 * 여러 워크시트가 하나의 스프레드시트로 제출할 수 있고,
 * 워크시트별(ws 값)로 시트 탭이 자동 분리됩니다.
 *
 * 설치: README.md 참고. SHEET_ID 만 본인 스프레드시트 ID 로 바꾸면 됩니다.
 */

// [바꾸기] 응답을 저장할 Google Sheets 의 ID (URL 의 /d/ 와 /edit 사이 문자열)
const SHEET_ID = 'PASTE_YOUR_SPREADSHEET_ID_HERE';

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const p = (e && e.parameter) || {};
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const name = (p.ws || '응답').toString().slice(0, 90);
    let sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);

    // a1, a2, ... 형태의 답변을 순서대로 수집
    const answers = [];
    let i = 1;
    while (p['a' + i] !== undefined) { answers.push(p['a' + i]); i++; }

    // 헤더가 없으면 생성
    if (sh.getLastRow() === 0) {
      const head = ['제출시각', '반', '모둠', '모둠원'];
      for (let j = 1; j <= answers.length; j++) head.push('답변' + j);
      sh.appendRow(head);
    }

    const row = [new Date(), p.cls || '', p.grp || '', p.members || ''].concat(answers);
    sh.appendRow(row);

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// 웹앱이 살아있는지 확인용
function doGet() {
  return ContentService.createTextOutput('OK · 제출 수신 준비됨');
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
