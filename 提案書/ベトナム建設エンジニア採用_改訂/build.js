const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.author = "ESUHAI Technology CO., LTD.";
pres.title = "ベトナム優秀建設エンジニア 採用プログラム ご提案（改訂版）";

const W = 13.333, H = 7.5, M = 0.6, CW = W - 2 * M;

// ---- palette (ESUTECH brand: navy / red) ----
const NAVY = "0E2244";
const NAVY_MID = "1C3D6B";
const RED = "C8102E";
const RED_SOFT = "F3D6DB";
const INK = "1A2230";
const MUTED = "5C6878";
const LINE = "DFE5EC";
const CARD = "F7F9FC";
const WHITE = "FFFFFF";

const JP = "Meiryo";

const sh = () => ({ type: "outer", color: "0E2244", blur: 8, offset: 1, angle: 90, opacity: 0.08 });

function slide() {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  return s;
}

// eyebrow + big title, no rule line
function header(s, eyebrow, title) {
  s.addText(eyebrow, {
    x: M, y: 0.34, w: CW, h: 0.26, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 10.5, bold: true, color: RED, charSpacing: 2,
  });
  s.addText(title, {
    x: M, y: 0.62, w: CW, h: 0.62, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 28, bold: true, color: NAVY, valign: "top",
  });
}

// light hero band with a one-line lead sentence
function lead(s, text, y, h, opts = {}) {
  s.addShape(pres.ShapeType.rect, {
    x: M, y, w: CW, h, fill: { color: opts.dark ? NAVY : "EEF2F7" },
  });
  s.addText(text, {
    x: M + 0.35, y, w: CW - 0.7, h, isTextBox: true, margin: 0, valign: "middle",
    fontFace: JP, fontSize: opts.size || 15, bold: true,
    color: opts.dark ? WHITE : NAVY, lineSpacing: (opts.size || 15) * 1.45,
  });
}

function card(s, x, y, w, h, opts = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.05,
    fill: { color: opts.fill || CARD },
    line: { color: opts.line || LINE, width: 1 },
    shadow: sh(),
  });
}

// navy numbered badge — the deck's repeating motif
function badge(s, x, y, num, opts = {}) {
  const sz = opts.size || 0.3;
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w: sz, h: sz, rectRadius: 0.03,
    fill: { color: opts.color || NAVY }, line: { color: opts.color || NAVY, width: 1 },
  });
  s.addText(num, {
    x, y, w: sz, h: sz, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: "Arial", fontSize: opts.fs || 10, bold: true, color: WHITE,
  });
}

// small right-pointing arrow drawn as a shape (avoids emoji-font substitution of "\u25B6")
function arrow(s, x, y, w, h, color) {
  s.addShape(pres.ShapeType.rightArrow, {
    x, y, w, h, fill: { color }, line: { color, width: 0 },
  });
}

function body(s, text, x, y, w, h, opts = {}) {
  s.addText(text, {
    x, y, w, h, isTextBox: true, margin: 0, valign: opts.valign || "top",
    fontFace: JP, fontSize: opts.size || 10.5, color: opts.color || MUTED,
    lineSpacing: (opts.size || 10.5) * 1.6, bold: !!opts.bold, align: opts.align || "left",
  });
}

function bullets(s, items, x, y, w, h, opts = {}) {
  const fs = opts.size || 10.5;
  s.addText(
    items.map((t, i) => ({
      text: t,
      options: { bullet: { code: "25AA" }, breakLine: i !== items.length - 1 },
    })),
    {
      x, y, w, h, isTextBox: true, margin: 0, valign: "top",
      fontFace: JP, fontSize: fs, color: opts.color || MUTED,
      lineSpacing: fs * 1.55, paraSpaceAfter: opts.gap === undefined ? 6 : opts.gap,
    }
  );
}

/* ============================================================
   1. 表紙
   ============================================================ */
{
  const s = slide();
  s.background = { color: NAVY };

  s.addShape(pres.ShapeType.rect, { x: 8.55, y: 0, w: 4.783, h: H, fill: { color: NAVY_MID } });
  s.addShape(pres.ShapeType.rect, { x: 9.6, y: 0, w: 3.733, h: H, fill: { color: "254B80" } });
  s.addShape(pres.ShapeType.rect, { x: 10.75, y: 0, w: 2.583, h: H, fill: { color: NAVY_MID } });
  s.addShape(pres.ShapeType.rect, { x: 12.0, y: 0, w: 1.333, h: H, fill: { color: "2E5B96" } });

  s.addText("ESUTECH", {
    x: 10.6, y: 0.42, w: 2.2, h: 0.36, isTextBox: true, margin: 0, align: "right",
    fontFace: "Arial", fontSize: 19, bold: true, color: WHITE, charSpacing: 1,
  });

  s.addText("RECIPIENT", {
    x: M, y: 0.75, w: 3, h: 0.24, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 10, bold: true, color: "9BB2CE", charSpacing: 3,
  });
  s.addText("御中", {
    x: M, y: 1.02, w: 5, h: 0.4, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 16, color: WHITE,
  });

  s.addShape(pres.ShapeType.rect, { x: M, y: 1.62, w: 2.55, h: 0.32, fill: { color: RED } });
  s.addText("REVISED PROPOSAL  v2.0", {
    x: M, y: 1.62, w: 2.55, h: 0.32, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: "Arial", fontSize: 9.5, bold: true, color: WHITE, charSpacing: 1,
  });

  s.addText("ベトナム優秀建設エンジニア\n採用プログラム ご提案", {
    x: M, y: 2.15, w: 7.6, h: 2.1, isTextBox: true, margin: 0, valign: "top",
    fontFace: JP, fontSize: 40, bold: true, color: WHITE, lineSpacing: 56,
  });

  s.addText(
    "「合同イベントで集めた学生をご紹介する」方式を取りやめ、\n" +
      "貴社専用の大学説明会から母集団を形成するモデルへ見直しました。\n" +
      "奨学金・生活支援金のスキームは従来どおり継続します。",
    {
      x: M, y: 4.55, w: 7.5, h: 1.3, isTextBox: true, margin: 0,
      fontFace: JP, fontSize: 13, color: "C9D8EA", lineSpacing: 24,
    }
  );

  s.addText("PROJECT CODE", {
    x: M, y: 6.42, w: 2.2, h: 0.22, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 8.5, bold: true, color: "8FA8C6", charSpacing: 2,
  });
  s.addText("VN-RECRUIT-2026 / REV.2", {
    x: M, y: 6.66, w: 2.6, h: 0.28, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 11, color: WHITE,
  });
  s.addText("SERVICE PROVIDER", {
    x: 3.5, y: 6.42, w: 3, h: 0.22, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 8.5, bold: true, color: "8FA8C6", charSpacing: 2,
  });
  s.addText("ESUHAI Technology CO., LTD.", {
    x: 3.5, y: 6.66, w: 4, h: 0.28, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 11, color: WHITE,
  });

  s.addNotes(
    "改訂版の趣旨説明。前回提案（合同イベントの残余候補者をご紹介する方式）が" +
      "志望動機のミスマッチで機能しなかったことを率直に認め、" +
      "貴社専用の大学説明会を起点とするモデルへ切り替えたことを冒頭で伝える。"
  );
}

/* ============================================================
   2. 前回モデルの振り返り
   ============================================================ */
{
  const s = slide();
  header(s, "LESSONS LEARNED", "前回モデルの振り返りと、見直しの理由");
  lead(
    s,
    "前回は「大手ゼネコン向けイベントの合格枠から漏れた学生」を他社様へご紹介する設計でした。この前提が成立しませんでした。",
    1.4, 0.72, { size: 13.5 }
  );

  const cw = (CW - 0.35) / 2;

  // 前回の設計
  card(s, M, 2.5, cw, 2.72, { fill: "F2F4F7" });
  badge(s, M + 0.3, 2.82, "01", { color: "8A97A8" });
  body(s, "前回の設計", M + 0.72, 2.82, cw - 1.0, 0.3, { size: 13, bold: true, color: INK, valign: "middle" });
  bullets(
    s,
    [
      "大手ゼネコン向けの採用イベントで建設系大学生を集客（参加 56名）",
      "先行企業の合格枠は最大 4名",
      "枠から漏れた 50〜60名を、他の建設会社様へご紹介する想定",
    ],
    M + 0.32, 3.42, cw - 0.64, 1.6, { size: 11 }
  );

  // 実際に起きたこと
  card(s, M + cw + 0.35, 2.5, cw, 2.72, { fill: WHITE, line: RED_SOFT });
  badge(s, M + cw + 0.65, 2.82, "02", { color: RED });
  body(s, "実際に起きたこと", M + cw + 1.07, 2.82, cw - 1.0, 0.3, { size: 13, bold: true, color: RED, valign: "middle" });
  bullets(
    s,
    [
      "学生の応募動機が「大手ゼネコンで働くこと」に強く紐づいていた",
      "企業名・事業規模が変わると志望度が続かず、面接まで進まなかった",
      "「選ばれなかった学生の受け皿」という位置づけが、学生の納得感を損ねた",
    ],
    M + cw + 0.67, 3.42, cw - 0.64, 1.7, { size: 11 }
  );

  lead(
    s,
    "結論：母集団は「余った学生」から集めるのではなく、はじめから貴社を志望する学生として形成する必要があります。",
    5.62, 1.05, { dark: true, size: 15 }
  );

  s.addNotes(
    "反省点を隠さず先に出すスライド。数字（56名・4名・50〜60名）は前回提案書の記載をそのまま引用している。"
  );
}

/* ============================================================
   3. Before / After
   ============================================================ */
{
  const s = slide();
  header(s, "MODEL SHIFT", "集客の起点を「イベント」から「貴社説明会」へ");

  const rowH = 1.78;

  // ---- BEFORE ----
  s.addText("BEFORE ／ 前回モデル", {
    x: M, y: 1.5, w: 4, h: 0.28, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 11.5, bold: true, color: MUTED, charSpacing: 1,
  });
  const bSteps = [
    ["合同イベントで集客", "大手ゼネコン主催の\nイベントに学生が集まる"],
    ["先行企業が選考", "合格枠は最大4名"],
    ["不合格者がプール化", "50〜60名が待機"],
    ["他社様へご紹介", "志望動機が接続せず\nマッチングに至らない"],
  ];
  const bw = (CW - 3 * 0.42) / 4;
  bSteps.forEach((st, i) => {
    const x = M + i * (bw + 0.42);
    card(s, x, 1.84, bw, rowH, { fill: "F2F4F7", line: "E4E8EE" });
    body(s, st[0], x + 0.24, 2.08, bw - 0.48, 0.3, { size: 12, bold: true, color: i === 3 ? RED : "6B7787" });
    body(s, st[1], x + 0.24, 2.5, bw - 0.48, 1.0, { size: 10, color: "8A97A8" });
    if (i < 3) arrow(s, x + bw + 0.09, 1.84 + rowH / 2 - 0.09, 0.24, 0.18, "B9C3CF");
  });
  s.addText("✕　母集団の志望動機が、紹介先の企業に引き継がれなかった", {
    x: M, y: 3.82, w: CW, h: 0.3, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 11.5, bold: true, color: RED,
  });

  // ---- AFTER ----
  s.addText("AFTER ／ 今回のご提案", {
    x: M, y: 4.32, w: 4, h: 0.28, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 11.5, bold: true, color: NAVY, charSpacing: 1,
  });
  const aSteps = [
    ["貴社専用説明会", "提携大学のキャンパスで\n貴社単独で開催"],
    ["志望学生がエントリー", "事前エントリー制で\n志望理由を提出"],
    ["選考・最終面接", "貴社が直接面接し\n内定を通知"],
    ["内定・支援開始", "奨学金・生活支援金で\n学習期間を支える"],
    ["来日・入社", "志望動機が\n入社まで途切れない"],
  ];
  const aw = (CW - 4 * 0.3) / 5;
  aSteps.forEach((st, i) => {
    const x = M + i * (aw + 0.3);
    const isLast = i === 4;
    card(s, x, 4.62, aw, rowH, { fill: isLast ? NAVY : WHITE, line: isLast ? NAVY : "CBD6E4" });
    badge(s, x + 0.2, 4.84, "0" + (i + 1), { size: 0.26, fs: 9, color: isLast ? RED : NAVY });
    body(s, st[0], x + 0.2, 5.22, aw - 0.4, 0.34, { size: 11.5, bold: true, color: isLast ? WHITE : NAVY });
    body(s, st[1], x + 0.2, 5.62, aw - 0.4, 0.95, { size: 10, color: isLast ? "C9D8EA" : MUTED });
    if (!isLast) arrow(s, x + aw + 0.03, 4.62 + rowH / 2 - 0.09, 0.24, 0.18, NAVY);
  });
  s.addText("○　「貴社で働きたい」という動機を持つ学生だけが、選考から入社まで進みます", {
    x: M, y: 6.62, w: CW, h: 0.3, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 11.5, bold: true, color: NAVY,
  });

  s.addNotes("前回モデルとの違いを一枚で示す。差分は「誰のために集めるか」の一点であることを強調する。");
}

/* ============================================================
   4. 進め方サマリー（6W2H）
   ============================================================ */
{
  const s = slide();
  header(s, "6W2H FRAMEWORK", "進め方サマリー");
  lead(
    s,
    "建設系大卒の優秀層を、貴社を志望する母集団から選考し、ESUHAIグループの伴走で「育成型正社員」として採用します。",
    1.4, 0.78, { size: 13.5 }
  );

  const items = [
    ["WHO", "誰を", "建設系（建築・土木・道路）の大卒／卒業予定者。優秀大学、実務経験不問の人材。"],
    ["WHAT", "何を", "技術系正社員（施工管理者／設計者等）として採用。来日前にESUHAIグループで徹底育成。"],
    ["WHEN", "いつ", "貴社説明会の開催から約2ヶ月で内定。内定の約1ヶ月後にJPCへ入学します。"],
    ["WHERE", "どこで", "説明会・選考は提携大学のキャンパス（ダナン／ホーチミン）。就業は日本国内の貴社。"],
    ["WHY", "なぜ", "建設人材不足の解消と、志望動機に裏づけられた定着する即戦力の確保のため。"],
    ["HOW", "どうやって", "ESUTECHが大学調整・集客・広告・通訳・選考運営からCoE申請、来日、定着まで伴走。"],
  ];

  const w4 = (CW - 3 * 0.26) / 4;
  items.slice(0, 4).forEach((it, i) => {
    const x = M + i * (w4 + 0.26);
    card(s, x, 2.32, w4, 1.82);
    s.addShape(pres.ShapeType.rect, { x: x + 0.24, y: 2.54, w: 0.78, h: 0.24, fill: { color: NAVY } });
    s.addText(it[0], {
      x: x + 0.24, y: 2.54, w: 0.78, h: 0.24, isTextBox: true, margin: 0, align: "center", valign: "middle",
      fontFace: "Arial", fontSize: 8, bold: true, color: WHITE, charSpacing: 1,
    });
    body(s, it[1], x + 1.08, 2.54, w4 - 1.3, 0.26, { size: 12, bold: true, color: INK, valign: "middle" });
    body(s, it[2], x + 0.24, 2.94, w4 - 0.48, 1.05, { size: 10 });
  });

  const w2 = (CW - 2 * 0.26) / 4;
  items.slice(4).forEach((it, i) => {
    const x = M + i * (w2 + 0.26);
    card(s, x, 4.34, w2, 1.92);
    s.addShape(pres.ShapeType.rect, { x: x + 0.24, y: 4.56, w: 0.78, h: 0.24, fill: { color: NAVY } });
    s.addText(it[0], {
      x: x + 0.24, y: 4.56, w: 0.78, h: 0.24, isTextBox: true, margin: 0, align: "center", valign: "middle",
      fontFace: "Arial", fontSize: 8, bold: true, color: WHITE, charSpacing: 1,
    });
    body(s, it[1], x + 1.08, 4.56, w2 - 1.3, 0.26, { size: 12, bold: true, color: INK, valign: "middle" });
    body(s, it[2], x + 0.24, 4.96, w2 - 0.48, 1.15, { size: 10 });
  });

  const hx = M + 2 * (w2 + 0.26);
  const hw = CW - 2 * (w2 + 0.26);
  card(s, hx, 4.34, hw, 1.92, { fill: WHITE, line: "CBD6E4" });
  s.addShape(pres.ShapeType.rect, { x: hx + 0.28, y: 4.56, w: 1.16, h: 0.24, fill: { color: RED } });
  s.addText("HOW MUCH", {
    x: hx + 0.28, y: 4.56, w: 1.16, h: 0.24, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: "Arial", fontSize: 8, bold: true, color: WHITE, charSpacing: 1,
  });
  body(s, "いくら", hx + 1.5, 4.56, 1.5, 0.26, { size: 12, bold: true, color: INK, valign: "middle" });
  s.addText(
    [
      { text: "ご契約の人材採用コンサルティング料／人材紹介料", options: { color: INK, bold: true, breakLine: true } },
      { text: "＋ 学費支援 ＋ 生活支援金。", options: { color: RED, bold: true } },
    ],
    {
      x: hx + 0.28, y: 4.96, w: hw - 0.56, h: 0.62, isTextBox: true, margin: 0,
      fontFace: JP, fontSize: 14, lineSpacing: 22,
    }
  );
  body(
    s,
    "※ 募集・選考にかかる弊社職員のホーチミン市外への出張費（旅費交通費）の実費ご負担はお願いいたします。",
    hx + 0.28, 5.66, hw - 0.56, 0.5, { size: 9.5 }
  );

  s.addNotes("前回提案の6W2Hを、説明会起点モデルに合わせて WHEN / WHERE / WHY / HOW を書き換えたもの。");
}

/* ============================================================
   5. 貴社専用説明会の実施設計（新規・中核）
   ============================================================ */
{
  const s = slide();
  header(s, "CAMPUS BRIEFING DESIGN", "貴社専用説明会の実施設計");
  lead(
    s,
    "「どの企業の説明会か」を明示したうえで集客します。母集団づくりがこのモデルの中核です。",
    1.4, 0.68, { size: 13.5 }
  );

  // 左：対象大学
  const lw = 3.5;
  card(s, M, 2.32, lw, 4.54, { fill: NAVY, line: NAVY });
  s.addText("TARGET UNIVERSITIES", {
    x: M + 0.3, y: 2.6, w: lw - 0.6, h: 0.24, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 8.5, bold: true, color: "9BB2CE", charSpacing: 2,
  });
  body(s, "提携大学（実績校）", M + 0.3, 2.9, lw - 0.6, 0.3, { size: 13, bold: true, color: WHITE });
  bullets(
    s,
    [
      "ダナン工科大学",
      "ダナン技術師範大学",
      "ホーチミン工科大学",
      "ホーチミン技術師範大学",
      "HUTECH大学",
    ],
    M + 0.32, 3.4, lw - 0.64, 2.1, { size: 11.5, color: "D6E2F0", gap: 11 }
  );
  body(
    s,
    "実施校は貴社の採用人数・勤務地・求める専攻に応じて選定し、\n必要に応じて追加校もご提案します。",
    M + 0.3, 5.72, lw - 0.6, 0.9, { size: 10, color: "9BB2CE" }
  );

  // 右：4ステップ
  const rx = M + lw + 0.36;
  const rw = CW - lw - 0.36;
  const stepW = (rw - 0.28) / 2;
  const steps = [
    ["01", "大学との日程調整・会場確保", "ESUTECHが各大学の就職支援部門と交渉し、教室と実施枠を確保します。貴社にお手間は発生しません。"],
    ["02", "貴社単独での告知（3週間）", "貴社の企業情報・職務内容・待遇を明記した募集広告を、学内掲示・SNS・学科経由で展開します。"],
    ["03", "事前エントリー制", "申込時に志望理由と専攻を提出いただきます。動機のある学生を事前に可視化し、当日の面談精度を上げます。"],
    ["04", "説明会当日（貴社ご登壇）", "貴社採用責任者にご登壇いただき、その場で個別質問・一次面談まで実施します。通訳は弊社が手配します。"],
  ];
  steps.forEach((st, i) => {
    const x = rx + (i % 2) * (stepW + 0.28);
    const y = 2.32 + Math.floor(i / 2) * (1.78 + 0.14);
    card(s, x, y, stepW, 1.78);
    badge(s, x + 0.26, y + 0.26, st[0]);
    body(s, st[1], x + 0.68, y + 0.26, stepW - 0.94, 0.3, { size: 12, bold: true, color: INK, valign: "middle" });
    body(s, st[2], x + 0.26, y + 0.7, stepW - 0.52, 0.95, { size: 10 });
  });

  card(s, rx, 6.08, rw, 0.78, { fill: "EEF2F7", line: "DBE3EC" });
  s.addText(
    [
      { text: "想定規模（目安）：", options: { bold: true, color: NAVY } },
      { text: "1校あたり参加 30〜50名 を目安に、2〜3校で母集団を形成します。", options: { color: NAVY } },
    ],
    { x: rx + 0.28, y: 6.2, w: rw - 0.56, h: 0.28, isTextBox: true, margin: 0, fontFace: JP, fontSize: 11.5 }
  );
  body(
    s,
    "※ 参加人数は大学・実施時期・貴社の募集条件により変動します。確定値ではなく計画上の目安としてご覧ください。",
    rx + 0.28, 6.52, rw - 0.56, 0.28, { size: 9 }
  );

  s.addNotes(
    "本提案の中核スライド。1校あたり30〜50名は計画上の目安であり、実績値ではない点を口頭でも明示すること。"
  );
}

/* ============================================================
   6. 説明会で伝えるべきこと
   ============================================================ */
{
  const s = slide();
  header(s, "BRIEFING STRATEGY", "説明会で伝えるべきこと");
  lead(
    s,
    "「出稼ぎ」ではなく「日本でのキャリア形成」をイメージさせる、具体的な年収とビジョンの提示が不可欠です。",
    1.4, 0.72, { size: 14 }
  );

  const cw = (CW - 3 * 0.24) / 4;
  const y0 = 2.4, ch = 3.5;

  // 01
  let x = M;
  card(s, x, y0, cw, ch);
  badge(s, x + 0.24, y0 + 0.26, "01");
  body(s, "会社・職務紹介", x + 0.66, y0 + 0.26, cw - 0.9, 0.3, { size: 12, bold: true, color: INK, valign: "middle" });
  bullets(
    s,
    ["事業内容と業界内での立ち位置", "誇れる施工実績の視覚的提示", "施工管理（安全・品質・工程等）の具体的な業務フロー"],
    x + 0.26, y0 + 0.74, cw - 0.52, 2.0, { size: 10 }
  );

  // 02 (priority)
  x = M + cw + 0.24;
  card(s, x, y0, cw, ch, { fill: WHITE, line: RED });
  s.addShape(pres.ShapeType.rect, { x: x + cw - 1.05, y: y0 - 0.14, w: 0.9, h: 0.26, fill: { color: RED } });
  s.addText("PRIORITY", {
    x: x + cw - 1.05, y: y0 - 0.14, w: 0.9, h: 0.26, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: "Arial", fontSize: 7.5, bold: true, color: WHITE, charSpacing: 1,
  });
  badge(s, x + 0.24, y0 + 0.26, "02", { color: RED });
  body(s, "待遇の提示（例）", x + 0.66, y0 + 0.26, cw - 0.9, 0.3, { size: 12, bold: true, color: INK, valign: "middle" });
  s.addShape(pres.ShapeType.rect, { x: x + 0.26, y: y0 + 0.74, w: cw - 0.52, h: 1.16, fill: { color: "F7F9FC" } });
  body(s, "モデル年収例", x + 0.38, y0 + 0.84, cw - 0.76, 0.24, { size: 8.5 });
  [["30歳", "530〜720", 1.12], ["40歳", "800〜1,100", 1.5]].forEach((r) => {
    body(s, r[0], x + 0.38, y0 + r[2], 0.6, 0.3, { size: 10, color: INK, valign: "middle" });
    s.addText(
      [
        { text: r[1], options: { fontSize: 13.5, bold: true, color: RED } },
        { text: " 万円", options: { fontSize: 8.5, color: INK } },
      ],
      {
        x: x + 0.9, y: y0 + r[2], w: cw - 1.28, h: 0.3, isTextBox: true, margin: 0,
        align: "right", valign: "middle", fontFace: JP,
      }
    );
  });
  bullets(s, ["賞与・昇給制度の明確化", "奨学金返済支援等の独自制度"], x + 0.26, y0 + 2.06, cw - 0.52, 1.2, { size: 10 });

  // 03
  x = M + 2 * (cw + 0.24);
  card(s, x, y0, cw, ch);
  badge(s, x + 0.24, y0 + 0.26, "03");
  body(s, "キャリアプラン", x + 0.66, y0 + 0.26, cw - 0.9, 0.3, { size: 12, bold: true, color: INK, valign: "middle" });
  body(s, "取得目標資格", x + 0.26, y0 + 0.78, cw - 0.52, 0.22, { size: 8.5 });
  body(s, "施工管理技士等の国家資格取得を全面的にバックアップ", x + 0.26, y0 + 1.04, cw - 0.52, 0.7, { size: 10 });
  body(s, "キャリアパス", x + 0.26, y0 + 1.82, cw - 0.52, 0.22, { size: 8.5 });
  s.addText(
    [
      { text: "5年後：", options: { bold: true, color: RED } },
      { text: "現場主任・リーダー", options: { color: INK, breakLine: true } },
      { text: "10年後：", options: { bold: true, color: RED } },
      { text: "現場所長・管理職", options: { color: INK } },
    ],
    { x: x + 0.26, y: y0 + 2.08, w: cw - 0.52, h: 1.1, isTextBox: true, margin: 0, fontFace: JP, fontSize: 10.5, lineSpacing: 20 }
  );

  // 04
  x = M + 3 * (cw + 0.24);
  card(s, x, y0, cw, ch, { fill: NAVY, line: NAVY });
  badge(s, x + 0.24, y0 + 0.26, "04", { color: RED });
  body(s, "支援制度の提示", x + 0.66, y0 + 0.26, cw - 0.9, 0.3, { size: 12, bold: true, color: WHITE, valign: "middle" });
  body(
    s,
    "学費支援・生活支援金を、貴社の制度としてご説明ください。",
    x + 0.26, y0 + 0.78, cw - 0.52, 0.7, { size: 10.5, color: "D6E2F0" }
  );
  body(
    s,
    "「入社前から投資してくれる会社」という事実が、企業規模の差を超えて志望度を決定づけます。",
    x + 0.26, y0 + 1.6, cw - 0.52, 1.6, { size: 11, color: WHITE, bold: true }
  );

  s.addShape(pres.ShapeType.rect, { x: M, y: 6.16, w: CW, h: 0.72, fill: { color: NAVY } });
  s.addText(
    [
      { text: "メッセージ　", options: { bold: true, color: RED_SOFT } },
      { text: "単なる労働力ではなく「共に歩むパートナー」として。企業の真摯な姿勢が、定着率の向上に直結します。", options: { color: WHITE } },
    ],
    { x: M + 0.34, y: 6.16, w: CW - 0.68, h: 0.72, isTextBox: true, margin: 0, valign: "middle", fontFace: JP, fontSize: 12 }
  );

  s.addNotes("旧提案のブリーフィング構成を踏襲しつつ、04として支援制度の訴求を追加した。");
}

/* ============================================================
   7. スケジュール
   ============================================================ */
{
  const s = slide();
  header(s, "SCHEDULE PROPOSAL", "スケジュール（貴社説明会 起点）");
  lead(
    s,
    "起点は貴社にて実施条件をご確定いただいた時点です。以下は 2026年10月に着手した場合の例です。",
    1.4, 0.68, { size: 13.5 }
  );

  const steps = [
    ["STEP 01", "起点〜2週間", "例：2026年10月", "実施条件の確定・大学調整", "採用人数・待遇・支援条件を確定し、ESUTECHが対象大学と実施日程を調整します。", false],
    ["STEP 02", "調整完了後 3週間", "例：2026年11月", "貴社単独の告知・エントリー受付", "貴社名を前面に出した募集広告を展開し、志望理由つきの事前エントリーを受け付けます。", false],
    ["STEP 03", "告知から3週間後", "例：2026年12月上旬", "貴社説明会（大学キャンパス）", "対象校を巡回して実施。来越が難しい場合はオンライン開催も可能です。", false],
    ["STEP 04", "説明会から1週間前後", "例：2026年12月中旬", "選考・最終面接", "最終面接を実施し、即日または数日以内に内定通知を行います。", false],
    ["STEP 05", "内定から約1ヶ月", "例：2027年1〜2月", "内定式・契約 → JPC入学・開講", "JPC（KAIZEN）へ入学。日本語・技術教育を開始し、支援金の支給もスタートします。", false],
    ["STEP 06", "入学から約15ヶ月", "例：2028年4〜5月", "N3合格・CoE申請 → 来日・入社", "高度な日本語学習（N3）と在留資格申請を経て、日本でのキャリアがスタートします。", true],
  ];

  const cw = (CW - 2 * 0.26) / 3;
  steps.forEach((st, i) => {
    const x = M + (i % 3) * (cw + 0.26);
    const y = 2.3 + Math.floor(i / 3) * (2.05 + 0.2);
    const dark = st[5];
    card(s, x, y, cw, 2.05, { fill: dark ? NAVY : CARD, line: dark ? NAVY : LINE });
    s.addText(st[0], {
      x: x + 0.26, y: y + 0.22, w: 1.1, h: 0.22, isTextBox: true, margin: 0,
      fontFace: "Arial", fontSize: 8.5, bold: true, color: dark ? RED_SOFT : RED, charSpacing: 1,
    });
    body(s, st[1], x + 1.36, y + 0.2, cw - 1.62, 0.26, { size: 10.5, bold: true, color: dark ? WHITE : NAVY, align: "right" });
    body(s, st[2], x + 0.26, y + 0.5, cw - 0.52, 0.24, { size: 9, color: dark ? "9BB2CE" : "8A97A8" });
    body(s, st[3], x + 0.26, y + 0.8, cw - 0.52, 0.42, { size: 12, bold: true, color: dark ? WHITE : INK });
    body(s, st[4], x + 0.26, y + 1.3, cw - 0.52, 0.68, { size: 9.5, color: dark ? "C9D8EA" : MUTED });
  });

  body(
    s,
    "※ 学習期間（約15ヶ月）と支援金額は前回提案から変更ありません。ベトナムの学事日程・卒業時期により、対象学年と実施月は調整が必要です。",
    M, 6.72, CW, 0.4, { size: 9 }
  );

  s.addNotes(
    "前回提案のスケジュールは2026年9〜10月のJPC入学を前提としており、既に時期を過ぎている。" +
      "そのため起点からの相対日程に組み替え、2026年10月着手の場合の例示を併記した。"
  );
}

/* ============================================================
   8. 奨学金・生活支援金
   ============================================================ */
{
  const s = slide();
  header(s, "FINANCIAL SUPPORT SCHEME", "奨学金・生活支援金の仕組み（案）");

  const lw = 4.3;
  body(
    s,
    "学生の学習意欲を維持し、確実な来日へ繋げるための経済的支援スキームです。",
    M, 1.5, lw, 0.6, { size: 11.5 }
  );
  card(s, M, 2.24, lw, 2.4, { fill: "EEF2F7", line: "DBE3EC" });
  s.addText(
    [
      { text: "N3合格・CoE発行を条件とした", options: { color: NAVY } },
      { text: "学費支援", options: { color: RED, bold: true } },
      { text: "と", options: { color: NAVY }, breakLine: true },
      { text: "月々の生活支援", options: { color: RED, bold: true } },
      { text: "により、学生のコミットメントを高めます。", options: { color: NAVY } },
    ],
    { x: M + 0.32, y: 2.5, w: lw - 0.64, h: 1.9, isTextBox: true, margin: 0, fontFace: JP, fontSize: 14.5, bold: true, lineSpacing: 30 }
  );
  card(s, M, 4.84, lw, 1.06, { fill: WHITE, line: "CBD6E4" });
  body(s, "本スキームは前回提案から\n一切変更しておりません。", M + 0.32, 5.02, lw - 0.64, 0.7, { size: 12, bold: true, color: NAVY });
  body(
    s,
    "※ 金額・期間は標準モデルです。最終的な条件は貴社にてご決定いただきます。",
    M, 6.1, lw, 0.7, { size: 9 }
  );

  const rx = M + lw + 0.4;
  const rw = CW - lw - 0.4;

  card(s, rx, 1.5, rw, 1.86);
  body(s, "SUPPORT 01", rx + 0.3, 1.72, 1.6, 0.24, { size: 8.5, bold: true, color: RED });
  body(s, "学費一部支援", rx + 0.3, 2.0, 2.4, 0.36, { size: 16, bold: true, color: INK });
  s.addText(
    [
      { text: "30,000,000〜60,000,000", options: { fontSize: 17.5, bold: true, color: NAVY } },
      { text: " VND / 人", options: { fontSize: 10, color: MUTED } },
    ],
    { x: rx + 2.6, y: 1.96, w: rw - 2.9, h: 0.44, isTextBox: true, margin: 0, align: "right", valign: "middle", fontFace: JP }
  );
  s.addShape(pres.ShapeType.rect, { x: rx + 0.3, y: 2.56, w: rw - 0.6, h: 0.56, fill: { color: "EEF2F7" } });
  body(
    s,
    "✓　JLPT N3合格およびCoE発行後に、ESUHAIへお振り込みいただきます。",
    rx + 0.5, 2.56, rw - 1.0, 0.56, { size: 10.5, color: NAVY, valign: "middle" }
  );

  card(s, rx, 3.5, rw, 1.9);
  body(s, "SUPPORT 02", rx + 0.3, 3.72, 1.6, 0.24, { size: 8.5, bold: true, color: RED });
  body(s, "生活支援金", rx + 0.3, 4.0, 2.4, 0.36, { size: 16, bold: true, color: INK });
  s.addText(
    [
      { text: "2,000,000", options: { fontSize: 21, bold: true, color: NAVY } },
      { text: " VND / 月", options: { fontSize: 10, color: MUTED } },
    ],
    { x: rx + 2.9, y: 3.96, w: rw - 3.2, h: 0.44, isTextBox: true, margin: 0, align: "right", valign: "middle", fontFace: JP }
  );
  body(s, "DURATION", rx + 0.3, 4.6, 2.2, 0.22, { size: 8.5 });
  body(s, "学習期間中（約15ヶ月）", rx + 0.3, 4.86, 2.6, 0.3, { size: 11.5, color: INK });
  body(s, "PAYMENT FLOW", rx + 3.2, 4.6, 2.4, 0.22, { size: 8.5 });
  body(s, "四半期毎前払い → 現金支給", rx + 3.2, 4.86, 3.0, 0.3, { size: 11.5, color: INK });

  card(s, rx, 5.56, rw, 1.24, { fill: NAVY, line: NAVY });
  body(s, "TOTAL INVESTMENT", rx + 0.34, 5.78, 2.6, 0.24, { size: 8.5, color: "9BB2CE" });
  body(s, "1人あたり総額目安（案）", rx + 0.34, 6.06, 3.0, 0.34, { size: 13, color: WHITE });
  s.addText(
    [
      { text: "34万〜54万", options: { fontSize: 30, bold: true, color: WHITE } },
      { text: " 円 JPY", options: { fontSize: 12, color: "C9D8EA" } },
    ],
    { x: rx + 3.6, y: 5.86, w: rw - 3.94, h: 0.64, isTextBox: true, margin: 0, align: "right", valign: "middle", fontFace: JP }
  );

  s.addNotes("支援金額は前回提案から一切変更していない。ご要望どおり継続する点を明言する。");
}

/* ============================================================
   9. 費用と企業リスクの限定
   ============================================================ */
{
  const s = slide();
  header(s, "COST & RISK MANAGEMENT", "費用と企業リスクの限定");
  lead(
    s,
    "企業の投資リスクを最小化し、追加費用の発生しない安全な設計となっています。",
    1.4, 0.68, { size: 14 }
  );

  const lw = 6.95;
  card(s, M, 2.32, lw, 1.86);
  body(s, "負担項目の明確化", M + 0.3, 2.54, lw - 0.6, 0.32, { size: 14, bold: true, color: INK });
  bullets(
    s,
    ["貴社負担：「学費支援」「生活支援金」「渡航・申請実費」のみ", "紹介料等の追加費用は一切不要です。"],
    M + 0.32, 3.0, lw - 0.64, 0.7, { size: 11.5, color: INK }
  );
  body(
    s,
    "※ 募集・選考にかかる弊社職員のホーチミン市外への出張費（旅費交通費）の実費ご負担はお願いいたします。",
    M + 0.32, 3.72, lw - 0.64, 0.34, { size: 9 }
  );

  card(s, M, 4.36, lw, 2.3);
  body(s, "リスク回避の仕組み", M + 0.3, 4.58, lw - 0.6, 0.32, { size: 14, bold: true, color: INK });
  s.addShape(pres.ShapeType.rect, { x: M + 0.32, y: 5.04, w: lw - 0.64, h: 0.82, fill: { color: "EEF2F7" } });
  body(s, "TRIGGER", M + 0.65, 5.14, 2.4, 0.22, { size: 8, align: "center" });
  s.addShape(pres.ShapeType.rect, { x: M + 0.65, y: 5.38, w: 2.4, h: 0.36, fill: { color: WHITE }, line: { color: LINE, width: 1 } });
  body(s, "N3合格", M + 0.65, 5.38, 2.4, 0.36, { size: 12, bold: true, color: INK, align: "center", valign: "middle" });
  arrow(s, M + 3.16, 5.47, 0.28, 0.2, "B9C3CF");
  body(s, "ACTION", M + 3.6, 5.14, 2.4, 0.22, { size: 8, align: "center" });
  s.addShape(pres.ShapeType.rect, { x: M + 3.6, y: 5.38, w: 2.4, h: 0.36, fill: { color: WHITE }, line: { color: RED, width: 1 } });
  body(s, "学費支援発生", M + 3.6, 5.38, 2.4, 0.36, { size: 12, bold: true, color: RED, align: "center", valign: "middle" });
  body(
    s,
    "学生が途中で学習を断念したり不合格となった場合、学費は学生本人の負担となり、企業側の金銭的損失は発生しません。",
    M + 0.32, 6.02, lw - 0.64, 0.5, { size: 10 }
  );

  const rx = M + lw + 0.4;
  const rw = CW - lw - 0.4;
  card(s, rx, 2.32, rw, 4.34, { fill: NAVY, line: NAVY });
  s.addText("“", {
    x: rx + 0.34, y: 2.4, w: 0.8, h: 0.8, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 46, bold: true, color: "3A5F91",
  });
  s.addText("「学生が途中で折れたら\nどうなるか」というリスクを、\n企業が背負わない設計。", {
    x: rx + 0.4, y: 3.18, w: rw - 0.8, h: 1.8, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 16, bold: true, color: WHITE, lineSpacing: 32,
  });
  s.addText("CONCLUSION: SECURED INVESTMENT", {
    x: rx + 0.4, y: 5.16, w: rw - 0.8, h: 0.26, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 9.5, bold: true, color: "9BB2CE", charSpacing: 1.5,
  });
  body(
    s,
    "説明会起点に変更しても、この費用構造とリスク設計は変わりません。",
    rx + 0.4, 5.64, rw - 0.8, 0.85, { size: 10.5, color: "C9D8EA" }
  );

  s.addNotes("費用・リスクの考え方は前回提案を維持。モデル変更による追加費用がないことを明言する。");
}

/* ============================================================
   10. 役割分担
   ============================================================ */
{
  const s = slide();
  header(s, "ROLES & RESPONSIBILITY", "各イベントへの参加と役割分担");
  lead(
    s,
    "実務運営はESUTECHが担当し、貴社には学生と直接向き合う場面にご参加いただきます。",
    1.4, 0.68, { size: 14 }
  );

  const cw = (CW - 0.4) / 2;

  // 貴社
  s.addShape(pres.ShapeType.rect, { x: M, y: 2.32, w: cw, h: 0.5, fill: { color: NAVY } });
  body(s, "貴社にご参加いただく行事", M + 0.3, 2.32, cw - 0.6, 0.5, { size: 13, bold: true, color: WHITE, valign: "middle" });
  card(s, M, 2.82, cw, 3.4, { fill: WHITE, line: LINE });

  const co = [
    ["会社説明会・選考面接", "採用責任者・審査員のご出席。原則として来越をお願いしておりますが、オンラインでの実施も可能です。"],
    ["実施条件のご決定", "採用人数・待遇・支援条件・対象大学の最終決定をお願いします。告知内容の根拠となります。"],
    ["内定式・開講式", "任意参加。社長・役員様のご臨席は、学生のモチベーションと志望度を劇的に高める重要な機会となります。"],
  ];
  co.forEach((it, i) => {
    const y = 3.06 + i * 1.06;
    s.addShape(pres.ShapeType.ellipse, { x: M + 0.32, y: y + 0.06, w: 0.14, h: 0.14, fill: { color: RED } });
    body(s, it[0], M + 0.6, y, cw - 0.9, 0.3, { size: 12, bold: true, color: INK });
    body(s, it[1], M + 0.6, y + 0.34, cw - 0.9, 0.66, { size: 10 });
  });

  // ESUTECH
  const rx = M + cw + 0.4;
  s.addShape(pres.ShapeType.rect, { x: rx, y: 2.32, w: cw, h: 0.5, fill: { color: NAVY_MID } });
  body(s, "ESUTECHがサポートする業務", rx + 0.3, 2.32, cw - 0.6, 0.5, { size: 13, bold: true, color: WHITE, valign: "middle" });
  card(s, rx, 2.82, cw, 3.4, { fill: WHITE, line: LINE });
  body(s, "全面的な運営バックアップ", rx + 0.3, 3.02, cw - 0.6, 0.28, { size: 10.5, color: NAVY_MID, bold: true });

  const tasks = [
    ["提携大学との交渉・会場確保・日程調整", true],
    ["貴社単独の募集広告の作成・展開", false],
    ["学内告知・エントリー管理・参加者集客", true],
    ["専門通訳者の手配", false],
    ["選考運営・CoE申請・来日・定着までの伴走", false],
  ];
  tasks.forEach((t, i) => {
    const y = 3.44 + i * 0.54;
    s.addShape(pres.ShapeType.rect, { x: rx + 0.3, y, w: cw - 0.6, h: 0.44, fill: { color: "F7F9FC" } });
    body(s, t[0], rx + 0.5, y, cw - 1.6, 0.44, { size: 10.5, color: INK, valign: "middle" });
    if (t[1]) {
      s.addShape(pres.ShapeType.rect, { x: rx + cw - 1.06, y: y + 0.11, w: 0.72, h: 0.22, fill: { color: RED } });
      s.addText("NEW", {
        x: rx + cw - 1.06, y: y + 0.11, w: 0.72, h: 0.22, isTextBox: true, margin: 0, align: "center", valign: "middle",
        fontFace: "Arial", fontSize: 7.5, bold: true, color: WHITE, charSpacing: 1,
      });
    }
  });

  s.addShape(pres.ShapeType.rect, { x: M, y: 6.42, w: CW, h: 0.62, fill: { color: NAVY } });
  s.addShape(pres.ShapeType.rect, { x: M + 0.24, y: 6.58, w: 1.85, h: 0.3, fill: { color: RED } });
  s.addText("FLEXIBLE SUPPORT", {
    x: M + 0.24, y: 6.58, w: 1.85, h: 0.3, isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: "Arial", fontSize: 8.5, bold: true, color: WHITE, charSpacing: 1,
  });
  body(
    s,
    "来越が難しい場合でも、説明会から選考までオンラインのみで完結させることが可能です。",
    M + 2.3, 6.42, CW - 2.6, 0.62, { size: 11.5, color: WHITE, valign: "middle" }
  );

  s.addNotes("大学との交渉・学内集客がESUTECH側の新規業務として増える点（NEWバッジ）を説明する。");
}

/* ============================================================
   11. 採用要件・対象学生
   ============================================================ */
{
  const s = slide();
  header(s, "在留資格「技術・人文知識・国際業務」要件", "採用要件・対象学生の詳細");
  body(
    s,
    "法的な在留資格要件を満たしつつ、日本で即戦力として活躍できる教育基盤を持つ人材を対象とします。",
    M, 1.44, CW, 0.4, { size: 11.5 }
  );

  const lw = 6.9;
  body(s, "選考基準・プロファイル", M, 2.02, lw, 0.34, { size: 15, bold: true, color: NAVY });
  const crit = [
    ["学歴・専攻分野", "建築・土木・道路等の建設分野の大卒者（エンジニア候補）"],
    ["学業成績・実務経験", "優秀大学。実務経験は不問とし、ポテンシャルを重視した採用を行います。"],
    ["既卒・卒業条件", "理系4年制大卒者（在学中の卒業予定者を含む）"],
    ["志望動機", "貴社説明会にエントリーし、志望理由を提出した学生に限定します。"],
  ];
  crit.forEach((c, i) => {
    const y = 2.52 + i * 1.06;
    card(s, M, y, lw, 0.92);
    body(s, c[0], M + 0.3, y + 0.14, lw - 0.6, 0.28, { size: 11.5, bold: true, color: i === 3 ? RED : INK });
    body(s, c[1], M + 0.3, y + 0.46, lw - 0.6, 0.36, { size: 10.5 });
  });

  const rx = M + lw + 0.44;
  const rw = CW - lw - 0.44;
  body(s, "必須条件・法的義務", rx, 2.02, rw, 0.34, { size: 15, bold: true, color: NAVY });

  card(s, rx, 2.52, rw, 1.5);
  body(s, "言語能力要件", rx + 0.3, 2.72, rw - 0.6, 0.24, { size: 9 });
  s.addText(
    [
      { text: "JLPT N3", options: { fontSize: 22, bold: true, color: INK } },
      { text: "  または  ", options: { fontSize: 11, color: MUTED } },
      { text: "NAT-TEST 3級", options: { fontSize: 16, bold: true, color: INK } },
    ],
    { x: rx + 0.3, y: 3.0, w: rw - 0.6, h: 0.44, isTextBox: true, margin: 0, valign: "middle", fontFace: JP }
  );
  body(s, "※ 来日前の取得を必須条件とします", rx + 0.3, 3.54, rw - 0.6, 0.28, { size: 10, color: RED });

  card(s, rx, 4.2, rw, 1.72, { fill: "EEF2F7", line: "DBE3EC" });
  body(s, "重要：給与水準に関する規定", rx + 0.34, 4.42, rw - 0.68, 0.26, { size: 9.5, color: MUTED });
  s.addText("在留資格の要件上、日本人大卒者と同等以上の給与提示が法的義務となります。", {
    x: rx + 0.34, y: 4.76, w: rw - 0.68, h: 1.0, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 14, bold: true, color: NAVY, lineSpacing: 26,
  });

  body(
    s,
    "※「技術・人文知識・国際業務」の在留資格申請にあたっては、専攻内容と従事する業務内容の整合性が厳格に審査されます。",
    rx, 6.1, rw, 0.6, { size: 9 }
  );

  s.addNotes("採用要件は前回提案から実質変更なし。志望動機の項目のみ、説明会起点モデルに合わせて追加した。");
}

/* ============================================================
   12. 企業様にご決定いただく項目
   ============================================================ */
{
  const s = slide();
  header(s, "PLANNING PHASE", "企業様にご決定いただく項目");
  lead(
    s,
    "プログラムを開始するために、以下の6つの基本条件を貴社にてご確定いただく必要があります。",
    1.4, 0.68, { size: 14 }
  );

  const items = [
    ["01", "採用規模", ["採用人数", "配属職種（施工管理等）", "勤務地／転勤の有無"], false],
    ["02", "給与・待遇", ["月給／モデル年収／賞与", "各種手当", "※日本人同等水準"], false],
    ["03", "支援条件", ["学費支援額", "生活支援金の月額", "支給期間の確定"], false],
    ["04", "説明会の実施条件", ["対象大学と実施校数", "希望日程", "対面／オンラインの選択", "ご登壇者"], true],
    ["05", "選考形式", ["選考ステップ", "内定通知のタイミング", "式典への参列者選定"], false],
    ["06", "人材像", ["求める専攻分野", "語学水準の下限", "評価の優先順位"], false],
  ];

  const cw = (CW - 2 * 0.26) / 3;
  items.forEach((it, i) => {
    const x = M + (i % 3) * (cw + 0.26);
    const y = 2.3 + Math.floor(i / 3) * (1.9 + 0.18);
    card(s, x, y, cw, 1.9, { fill: it[3] ? WHITE : CARD, line: it[3] ? RED : LINE });
    s.addText(it[0], {
      x: x + 0.28, y: y + 0.2, w: 0.5, h: 0.32, isTextBox: true, margin: 0,
      fontFace: "Arial", fontSize: 15, bold: true, color: RED,
    });
    body(s, it[1], x + 0.82, y + 0.2, cw - 1.1, 0.32, { size: 13, bold: true, color: INK, valign: "middle" });
    if (it[3]) {
      s.addShape(pres.ShapeType.rect, { x: x + cw - 0.98, y: y - 0.14, w: 0.72, h: 0.26, fill: { color: RED } });
      s.addText("NEW", {
        x: x + cw - 0.98, y: y - 0.14, w: 0.72, h: 0.26, isTextBox: true, margin: 0, align: "center", valign: "middle",
        fontFace: "Arial", fontSize: 7.5, bold: true, color: WHITE, charSpacing: 1,
      });
    }
    bullets(s, it[2], x + 0.3, y + 0.66, cw - 0.6, 1.1, { size: 10.5, color: MUTED, gap: 3 });
  });

  s.addShape(pres.ShapeType.rect, { x: M, y: 6.6, w: CW, h: 0.6, fill: { color: NAVY } });
  s.addText(
    [
      { text: "ネクストステップ　", options: { bold: true, color: WHITE } },
      { text: "これらが決まり次第、大学との日程調整と求人票・募集広告の作成フェーズへ即座に移行します。", options: { color: "C9D8EA" } },
    ],
    { x: M + 0.34, y: 6.6, w: CW - 0.68, h: 0.6, isTextBox: true, margin: 0, valign: "middle", fontFace: JP, fontSize: 11.5 }
  );

  s.addNotes("前回提案の5項目に「04 説明会の実施条件」を追加して6項目とした。");
}

/* ============================================================
   13. クロージング
   ============================================================ */
{
  const s = slide();
  s.background = { color: NAVY };

  s.addText("WHY THIS WORKS", {
    x: M, y: 0.7, w: CW, h: 0.26, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 10.5, bold: true, color: RED_SOFT, charSpacing: 2,
  });
  s.addText("志望動機からつくる採用へ", {
    x: M, y: 1.0, w: CW, h: 0.7, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 32, bold: true, color: WHITE,
  });
  s.addText("同じ支援制度でも、「誰のために集めた母集団か」で結果が変わります。", {
    x: M, y: 1.86, w: CW, h: 0.4, isTextBox: true, margin: 0,
    fontFace: JP, fontSize: 14, color: "C9D8EA",
  });

  const pts = [
    ["01", "母集団の質", "貴社を志望して集まった学生だけが選考に進むため、面接の通過率と内定承諾率が安定します。"],
    ["02", "学習期間の完走率", "約15ヶ月の学習を支えるのは志望動機です。行き先が明確な学生は途中離脱しにくくなります。"],
    ["03", "入社後の定着", "説明会で聞いた仕事・待遇・キャリアが入社後の現実と一致するため、早期離職を防ぎます。"],
  ];
  const cw = (CW - 2 * 0.34) / 3;
  pts.forEach((p, i) => {
    const x = M + i * (cw + 0.34);
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.7, w: cw, h: 2.3, rectRadius: 0.05,
      fill: { color: NAVY_MID }, line: { color: "2E5B96", width: 1 },
    });
    badge(s, x + 0.32, 2.98, p[0], { color: RED });
    body(s, p[1], x + 0.32, 3.46, cw - 0.64, 0.36, { size: 15, bold: true, color: WHITE });
    body(s, p[2], x + 0.32, 3.94, cw - 0.64, 0.9, { size: 10.5, color: "C9D8EA" });
  });

  s.addShape(pres.ShapeType.rect, { x: M, y: 5.44, w: CW, h: 0.86, fill: { color: "2E5B96" } });
  s.addText("まずは対象大学と実施時期のご相談から、始めさせてください。", {
    x: M + 0.4, y: 5.44, w: CW - 0.8, h: 0.86, isTextBox: true, margin: 0, valign: "middle",
    fontFace: JP, fontSize: 17, bold: true, color: WHITE,
  });

  s.addText("ESUHAI Technology CO., LTD.　／　VN-RECRUIT-2026 REV.2", {
    x: M, y: 6.62, w: CW, h: 0.3, isTextBox: true, margin: 0,
    fontFace: "Arial", fontSize: 10, color: "8FA8C6",
  });

  s.addNotes("クロージング。支援制度は据え置き、変えたのは母集団形成の方法だけ、というメッセージで締める。");
}

pres.writeFile({ fileName: "ベトナム建設エンジニア採用プログラム_改訂提案書.pptx" }).then((f) =>
  console.log("written:", f)
);
