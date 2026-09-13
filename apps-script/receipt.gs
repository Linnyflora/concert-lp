var FORM_ID = '1r1k6c505SjfCFPQoAkrNTBeTsasyPXnXvxaT0jtlhK4';
var EVENT_DATE = '2026年11月15日';
var FOLDER_NAME = '領収書_1曲ひいてみようコンサート';
var SPREADSHEET_ID = '1eLPlTjNVmb2misodki-8bJZIhWHcs9ixqiLmlzcMQy4';

// 領収書に入れるイラストの表示サイズ（pt）。画像データはこのファイルのいちばん下にあります。
var HEADER_IMAGE_WIDTH = 180;
var HEADER_IMAGE_HEIGHT = 121;
var FOOTER_IMAGE_WIDTH = 300;
var FOOTER_IMAGE_HEIGHT = 89;

function setupTrigger() {
var triggers = ScriptApp.getProjectTriggers();
for (var i = 0; i < triggers.length; i++) {
if (triggers[i].getHandlerFunction() === 'onFormSubmit') {
ScriptApp.deleteTrigger(triggers[i]);
}
}
var form = FormApp.openById(FORM_ID);
ScriptApp.newTrigger('onFormSubmit').forForm(form).onFormSubmit().create();
Logger.log('trigger created');
}

function getOrCreateFolder() {
var folders = DriveApp.getFoldersByName(FOLDER_NAME);
if (folders.hasNext()) {
return folders.next();
}
return DriveApp.createFolder(FOLDER_NAME);
}

// チラシと同じ線画イラストを画像として貼り付けます。
function appendCenteredImage(body, base64, name, width, height) {
var blob = Utilities.newBlob(Utilities.base64Decode(base64), 'image/png', name);
var para = body.appendParagraph('');
para.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
var image = para.appendInlineImage(blob);
image.setWidth(width);
image.setHeight(height);
return para;
}

function buildReceiptDoc(studentName, receiptName, driveFolder, issueDateText) {
var doc = DocumentApp.create('領収書_' + studentName);
var body = doc.getBody();
body.setMarginTop(28);
body.setMarginBottom(28);
body.setMarginLeft(50);
body.setMarginRight(50);

// ヘッダー：チラシのピアノのイラスト
appendCenteredImage(body, RECEIPT_HEADER_IMAGE, 'receipt-header.png',
HEADER_IMAGE_WIDTH, HEADER_IMAGE_HEIGHT);

var titleP = body.appendParagraph('♪　領　収　書　♪');
titleP.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
var titleText = titleP.editAsText();
titleText.setFontSize(18);
titleText.setBold(true);
titleText.setForegroundColor('#3b3f5c');

body.appendParagraph('').appendHorizontalRule();

var dateP = body.appendParagraph('発行日：' + issueDateText);
dateP.setAlignment(DocumentApp.HorizontalAlignment.RIGHT);

body.appendParagraph('');

var nameP = body.appendParagraph(receiptName);
nameP.editAsText().setFontSize(18);
nameP.editAsText().setBold(true);
var underlineP = body.appendParagraph('────────────────────');
underlineP.editAsText().setForegroundColor('#999999');

body.appendParagraph('');

body.appendParagraph('件名：1曲ひいてみよう やってみようコンサート　参加費として');

body.appendParagraph('');

var totalP = body.appendParagraph('合計金額　　¥8,800-（税込）');
totalP.editAsText().setFontSize(18);
totalP.editAsText().setBold(true);

body.appendParagraph('上記の金額を正に領収いたしました。');

body.appendParagraph('');

var table = body.appendTable([
['品目', '数量', '単価', '金額'],
['参加費（1曲ひいてみよう やってみようコンサート）', '1', '¥8,000', '¥8,000']
]);
var headerRow = table.getRow(0);
for (var c = 0; c < headerRow.getNumCells(); c++) {
headerRow.getCell(c).setBackgroundColor('#eeedfc');
headerRow.getCell(c).editAsText().setBold(true);
}

body.appendParagraph('');

var sumTable = body.appendTable([
['小計', '¥8,000'],
['消費税（10%）', '¥800'],
['合計', '¥8,800']
]);
sumTable.setBorderWidth(0.5);

body.appendParagraph('');

var issuerLabel = body.appendParagraph('発行者');
issuerLabel.editAsText().setBold(true);
body.appendParagraph('増見麻美');
body.appendParagraph('〒456-0062　愛知県名古屋市熱田区大宝４−１５−２１');
body.appendParagraph('登録番号：T2810958830122');

var thanksP = body.appendParagraph('ご参加いただき、ありがとうございます。');
thanksP.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
var thanksText = thanksP.editAsText();
thanksText.setFontSize(9);
thanksText.setForegroundColor('#5f6368');

// フッター：チラシの客席のイラスト
appendCenteredImage(body, RECEIPT_FOOTER_IMAGE, 'receipt-footer.png',
FOOTER_IMAGE_WIDTH, FOOTER_IMAGE_HEIGHT);

// 新規ドキュメントの先頭にできる空段落を取り除きます。
var first = body.getChild(0);
if (body.getNumChildren() > 1 &&
first.getType() === DocumentApp.ElementType.PARAGRAPH &&
first.asParagraph().getText() === '' &&
first.asParagraph().getNumChildren() === 0) {
body.removeChild(first);
}

doc.saveAndClose();

var file = DriveApp.getFileById(doc.getId());
driveFolder.addFile(file);
DriveApp.getRootFolder().removeFile(file);
return file;
}

// 宛名はフルネームで出します。
// フォームの「領収書の宛名」に姓だけ（例：住田）と書かれていても、
// 保護者様・生徒様のお名前と姓が一致すれば、そのフルネーム（例：住田未来）にします。
// 会社名など、どちらにも当てはまらない場合は書かれたとおりに出します。
function resolveReceiptName(receiptNameRaw, studentName, guardianName) {
// 「住田様」のように敬称つきで書かれていても二重にならないようにします。
var raw = trimName(trimName(receiptNameRaw).replace(/(様|さま|サマ)$/, ''));
if (!raw) {
return '上様';
}
var fullNames = [trimName(guardianName), trimName(studentName)];
for (var i = 0; i < fullNames.length; i++) {
var full = fullNames[i];
if (!full) {
continue;
}
if (compactName(full).length > compactName(raw).length &&
compactName(full).indexOf(compactName(raw)) === 0) {
raw = full;
break;
}
}
return raw + '　様';
}

function trimName(value) {
if (value === null || value === undefined) {
return '';
}
return String(value).replace(/^[\s　]+/, '').replace(/[\s　]+$/, '');
}

function compactName(value) {
return value.replace(/[\s　]/g, '');
}

function onFormSubmit(e) {
var itemResponses = e.response.getItemResponses();
var answers = {};
for (var i = 0; i < itemResponses.length; i++) {
var title = itemResponses[i].getItem().getTitle();
answers[title] = itemResponses[i].getResponse();
}

var studentName = answers['お名前（生徒様）'] || '';
var guardianName = '';
var receiptNameRaw = '';
for (var key in answers) {
if (key.indexOf('領収書の宛名') === 0) {
receiptNameRaw = answers[key];
}
if (key.indexOf('保護者') === 0) {
guardianName = answers[key];
}
}
var receiptName = resolveReceiptName(receiptNameRaw, studentName, guardianName);

var folder = getOrCreateFolder();
var file = buildReceiptDoc(studentName, receiptName, folder, EVENT_DATE);

var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
var sheet = ss.getSheets()[0];
var lastRow = sheet.getLastRow();

var urlCol = getOrAddColumn(sheet, '領収書URL（コンサート当日日付版）');
var dateCol = getOrAddColumn(sheet, '発行日（コンサート当日日付版）');
var doneCol = getOrAddColumn(sheet, 'お渡し済み');

sheet.getRange(lastRow, urlCol).setValue(file.getUrl());
sheet.getRange(lastRow, dateCol).setValue(EVENT_DATE);
sheet.getRange(lastRow, doneCol).insertCheckboxes();
}

function getOrAddColumn(sheet, headerName) {
var lastCol = sheet.getLastColumn();
var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
for (var i = 0; i < headers.length; i++) {
if (headers[i] === headerName) {
return i + 1;
}
}
var newCol = lastCol + 1;
sheet.getRange(1, newCol).setValue(headerName);
return newCol;
}

// 手動で実行する関数です。Apps Scriptエディタ上部の関数選択で
// generateReceiptsWithTodayDate を選んで「実行」ボタンを押してください。
// 印刷しようとしているそのタイミングで、発行日を「今日の日付」にした
// 領収書を、まだ作っていない人の分だけまとめて作成します。
function generateReceiptsWithTodayDate() {
var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
var sheet = ss.getSheets()[0];
var lastRow = sheet.getLastRow();
if (lastRow < 2) {
return;
}
var lastCol = sheet.getLastColumn();
var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];

var nameColIdx = headers.indexOf('お名前（生徒様）');
var receiptColIdx = -1;
var guardianColIdx = -1;
for (var i = 0; i < headers.length; i++) {
if (headers[i].indexOf('領収書の宛名') === 0) {
receiptColIdx = i;
}
if (headers[i].indexOf('保護者') === 0) {
guardianColIdx = i;
}
}

var todayUrlCol = getOrAddColumn(sheet, '領収書URL（発行日=作成日版）');
var todayDateCol = getOrAddColumn(sheet, '発行日（発行日=作成日版）');
var doneCol = getOrAddColumn(sheet, 'お渡し済み');

var today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy年M月d日');
var folder = getOrCreateFolder();

lastCol = sheet.getLastColumn();
var data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();

for (var r = 0; r < data.length; r++) {
var rowNum = r + 2;
var alreadyDone = sheet.getRange(rowNum, todayUrlCol).getValue();
if (alreadyDone) {
continue;
}

var studentName = data[r][nameColIdx] || '';
if (!studentName) {
continue;
}
var receiptNameRaw = receiptColIdx >= 0 ? data[r][receiptColIdx] : '';
var guardianName = guardianColIdx >= 0 ? data[r][guardianColIdx] : '';
var receiptName = resolveReceiptName(receiptNameRaw, studentName, guardianName);

var file = buildReceiptDoc(studentName, receiptName, folder, today);

sheet.getRange(rowNum, todayUrlCol).setValue(file.getUrl());
sheet.getRange(rowNum, todayDateCol).setValue(today);

var doneCell = sheet.getRange(rowNum, doneCol);
if (!doneCell.getDataValidation()) {
doneCell.insertCheckboxes();
}
}
}

// 一時的に使う関数です。レイアウト修正（イラストの追加など）を
// 反映するため、既存の領収書（当日版・今日版）をいったんゴミ箱に入れ、
// 作り直します。実行後にこの関数は削除して構いません。
function regenerateAllReceiptsFixedLayout() {
var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
var sheet = ss.getSheets()[0];
var lastRow = sheet.getLastRow();
if (lastRow < 2) {
return;
}
var lastCol = sheet.getLastColumn();
var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];

var nameColIdx = headers.indexOf('お名前（生徒様）');
var receiptColIdx = -1;
var guardianColIdx = -1;
for (var i = 0; i < headers.length; i++) {
if (headers[i].indexOf('領収書の宛名') === 0) {
receiptColIdx = i;
}
if (headers[i].indexOf('保護者') === 0) {
guardianColIdx = i;
}
}

var todayUrlCol = getOrAddColumn(sheet, '領収書URL（発行日=作成日版）');
var todayDateCol = getOrAddColumn(sheet, '発行日（発行日=作成日版）');
var eventUrlCol = getOrAddColumn(sheet, '領収書URL（コンサート当日日付版）');
var eventDateCol = getOrAddColumn(sheet, '発行日（コンサート当日日付版）');

var today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy年M月d日');
var folder = getOrCreateFolder();

var data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();

for (var r = 0; r < data.length; r++) {
var rowNum = r + 2;
var studentName = data[r][nameColIdx] || '';
if (!studentName) {
continue;
}
var receiptNameRaw = receiptColIdx >= 0 ? data[r][receiptColIdx] : '';
var guardianName = guardianColIdx >= 0 ? data[r][guardianColIdx] : '';
var receiptName = resolveReceiptName(receiptNameRaw, studentName, guardianName);

var oldTodayUrl = sheet.getRange(rowNum, todayUrlCol).getValue();
if (oldTodayUrl) {
trashFileByUrl(oldTodayUrl);
}
var oldEventUrl = sheet.getRange(rowNum, eventUrlCol).getValue();
if (oldEventUrl) {
trashFileByUrl(oldEventUrl);
}

var todayFile = buildReceiptDoc(studentName, receiptName, folder, today);
sheet.getRange(rowNum, todayUrlCol).setValue(todayFile.getUrl());
sheet.getRange(rowNum, todayDateCol).setValue(today);

var eventFile = buildReceiptDoc(studentName, receiptName, folder, EVENT_DATE);
sheet.getRange(rowNum, eventUrlCol).setValue(eventFile.getUrl());
sheet.getRange(rowNum, eventDateCol).setValue(EVENT_DATE);
}
}

function trashFileByUrl(url) {
var match = url.match(/[-\w]{25,}/);
if (!match) {
return;
}
try {
var file = DriveApp.getFileById(match[0]);
file.setTrashed(true);
} catch (e) {
// 既に削除済み等の場合は無視します
}
}
