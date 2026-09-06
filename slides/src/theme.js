// Shared visual system for the two healthcare-module lecture decks.
const NAVY = "13293D";
const NAVY_SOFT = "1F3F5C";
const INK = "13293D";
const BODY = "3A4A59";
const MUTED = "7C8794";
const WHITE = "FFFFFF";
const RULE = "DCE1E6";
const TINT = "F2F5F7";

// Validated categorical palette (six checks pass, light and dark surfaces).
const SERIES = ["2E74B5", "DD5A22", "0E8F6E", "9C4BA0"];
const ACCENT = "DD5A22";

const HEAD = "Cambria";
const TEXT = "Calibri";

const W = 13.3;
const H = 7.5;
const M = 0.75;

function titleSlide(pres, { eyebrow, title, subtitle, presenter, meta }) {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText(eyebrow, {
    x: M, y: 1.5, w: W - 2 * M, h: 0.35, isTextBox: true, margin: 0,
    fontFace: TEXT, fontSize: 15, color: ACCENT, bold: true, charSpacing: 2,
  });
  s.addText(title, {
    x: M, y: 2.0, w: W - 2 * M - 0.4, h: 1.9, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 46, color: WHITE, bold: true, lineSpacingMultiple: 1.05,
  });
  s.addText(subtitle, {
    x: M, y: 4.05, w: W - 2 * M - 1.5, h: 0.9, isTextBox: true, margin: 0,
    fontFace: TEXT, fontSize: 19, color: "AFC0D0", lineSpacingMultiple: 1.2,
  });
  s.addShape(pres.ShapeType.rect, { x: M, y: 5.35, w: 1.1, h: 0.035, fill: { color: ACCENT } });
  s.addText(presenter, {
    x: M, y: 5.65, w: W - 2 * M, h: 0.35, isTextBox: true, margin: 0,
    fontFace: TEXT, fontSize: 16, color: WHITE, bold: true,
  });
  s.addText(meta, {
    x: M, y: 6.05, w: W - 2 * M, h: 0.35, isTextBox: true, margin: 0,
    fontFace: TEXT, fontSize: 14, color: "8FA3B8",
  });
  return s;
}

function sectionSlide(pres, { number, title, blurb }) {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape(pres.ShapeType.ellipse, {
    x: M, y: 2.55, w: 1.0, h: 1.0, fill: { color: ACCENT },
  });
  s.addText(String(number), {
    x: M, y: 2.55, w: 1.0, h: 1.0, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 34, color: WHITE, bold: true, align: "center", valign: "middle",
  });
  s.addText(title, {
    x: M + 1.5, y: 2.35, w: W - M - 1.5 - M, h: 1.1, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 38, color: WHITE, bold: true, valign: "middle",
  });
  if (blurb) {
    s.addText(blurb, {
      x: M + 1.5, y: 3.55, w: W - M - 1.5 - M - 1.0, h: 1.0, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 18, color: "AFC0D0", lineSpacingMultiple: 1.25,
    });
  }
  return s;
}

// A light content slide with a heading, and an optional kicker above it.
function contentSlide(pres, heading, kicker) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  let y = 0.55;
  if (kicker) {
    s.addText(kicker, {
      x: M, y, w: W - 2 * M, h: 0.3, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 13, color: ACCENT, bold: true, charSpacing: 1.5,
    });
    y += 0.36;
  }
  s.addText(heading, {
    x: M, y, w: W - 2 * M, h: 0.72, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, color: INK, bold: true, valign: "top",
  });
  return s;
}

// Big single-claim slide.
function statementSlide(pres, { claim, support, dark = false }) {
  const s = pres.addSlide();
  s.background = { color: dark ? NAVY : TINT };
  s.addText(claim, {
    x: M + 0.3, y: 1.9, w: W - 2 * M - 0.6, h: 2.5, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 36, color: dark ? WHITE : INK, bold: true,
    lineSpacingMultiple: 1.12, valign: "middle",
  });
  if (support) {
    s.addShape(pres.ShapeType.rect, { x: M + 0.3, y: 4.62, w: 1.1, h: 0.035, fill: { color: ACCENT } });
    s.addText(support, {
      x: M + 0.3, y: 5.12, w: W - 2 * M - 1.6, h: 1.45, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 18, color: dark ? "AFC0D0" : BODY, lineSpacingMultiple: 1.25,
    });
  }
  return s;
}

// Full-width figure with a one-line reading underneath.
function figureSlide(pres, { heading, kicker, image, reading, imgY = 1.55, imgH = 4.35 }) {
  const s = contentSlide(pres, heading, kicker);
  s.addImage({ path: image, x: 2.05, y: imgY, w: 9.2, h: imgH, sizing: { type: "contain", w: 9.2, h: imgH } });
  if (reading) {
    s.addShape(pres.ShapeType.rect, { x: M, y: 6.15, w: W - 2 * M, h: 0.9, fill: { color: TINT } });
    s.addText(reading, {
      x: M + 0.3, y: 6.15, w: W - 2 * M - 0.6, h: 0.9, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 15.5, color: BODY, valign: "middle", lineSpacingMultiple: 1.15,
    });
  }
  return s;
}

// Figure on the left, commentary blocks on the right.
function figureWithNotes(pres, { heading, kicker, image, blocks }) {
  const s = contentSlide(pres, heading, kicker);
  s.addImage({ path: image, x: M, y: 1.75, w: 7.5, h: 4.2, sizing: { type: "contain", w: 7.5, h: 4.2 } });
  let y = 1.9;
  blocks.forEach((b, i) => {
    s.addShape(pres.ShapeType.ellipse, { x: 8.55, y: y + 0.03, w: 0.34, h: 0.34, fill: { color: SERIES[i % SERIES.length] } });
    s.addText(String(i + 1), {
      x: 8.55, y: y + 0.03, w: 0.34, h: 0.34, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 13, color: WHITE, bold: true, align: "center", valign: "middle",
    });
    s.addText(b.title, {
      x: 9.05, y: y - 0.02, w: W - M - 9.05, h: 0.34, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 15.5, color: INK, bold: true, valign: "middle",
    });
    s.addText(b.body, {
      x: 9.05, y: y + 0.34, w: W - M - 9.05, h: 1.05, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 13.5, color: BODY, lineSpacingMultiple: 1.16, valign: "top",
    });
    y += 1.52;
  });
  return s;
}

// Numbered rows with a coloured chip - used for roadmaps and takeaways.
function listSlide(pres, { heading, kicker, items, twoColumn = false }) {
  const s = contentSlide(pres, heading, kicker);
  const colWidth = twoColumn ? (W - 2 * M - 0.7) / 2 : W - 2 * M - 0.6;
  const perCol = twoColumn ? Math.ceil(items.length / 2) : items.length;
  items.forEach((item, i) => {
    const col = twoColumn ? Math.floor(i / perCol) : 0;
    const row = twoColumn ? i % perCol : i;
    const x = M + col * (colWidth + 0.7);
    const y = 1.75 + row * (twoColumn ? 1.02 : 0.86);
    s.addShape(pres.ShapeType.ellipse, {
      x, y: y + 0.04, w: 0.38, h: 0.38, fill: { color: SERIES[i % SERIES.length] },
    });
    s.addText(String(i + 1), {
      x, y: y + 0.04, w: 0.38, h: 0.38, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 14, color: WHITE, bold: true, align: "center", valign: "middle",
    });
    s.addText(item.title, {
      x: x + 0.56, y, w: colWidth - 0.56, h: 0.36, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 17, color: INK, bold: true,
    });
    if (item.body) {
      s.addText(item.body, {
        x: x + 0.56, y: y + 0.35, w: colWidth - 0.56, h: 0.62, isTextBox: true, margin: 0,
        fontFace: TEXT, fontSize: 14.5, color: BODY, lineSpacingMultiple: 1.14,
      });
    }
  });
  return s;
}

// A row of large numbers.
function statsSlide(pres, { heading, kicker, stats, footnote }) {
  const s = contentSlide(pres, heading, kicker);
  const n = stats.length;
  const gap = 0.35;
  const cardW = (W - 2 * M - gap * (n - 1)) / n;
  stats.forEach((stat, i) => {
    const x = M + i * (cardW + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.0, w: cardW, h: 2.75, fill: { color: TINT }, rectRadius: 0.08,
    });
    s.addText(stat.value, {
      x: x + 0.2, y: 2.3, w: cardW - 0.4, h: 1.1, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: stat.value.length > 6 ? 34 : 46,
      color: stat.color || SERIES[i % SERIES.length], bold: true, align: "center", valign: "middle",
    });
    s.addText(stat.label, {
      x: x + 0.2, y: 3.45, w: cardW - 0.4, h: 1.15, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 15, color: BODY, align: "center", valign: "top", lineSpacingMultiple: 1.18,
    });
  });
  if (footnote) {
    s.addText(footnote, {
      x: M, y: 5.25, w: W - 2 * M, h: 1.4, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 17, color: BODY, lineSpacingMultiple: 1.28,
    });
  }
  return s;
}

// Two labelled cards side by side.
function compareSlide(pres, { heading, kicker, left, right, footnote }) {
  const s = contentSlide(pres, heading, kicker);
  const cardW = (W - 2 * M - 0.5) / 2;
  [left, right].forEach((card, i) => {
    const x = M + i * (cardW + 0.5);
    const h = footnote ? 4.05 : 4.6;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 1.72, w: cardW, h, fill: { color: TINT }, rectRadius: 0.08,
    });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.35, y: 2.0, w: 0.4, h: 0.4, fill: { color: SERIES[i] } });
    s.addText(card.title, {
      x: x + 0.92, y: 1.96, w: cardW - 1.27, h: 0.48, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 19, color: INK, bold: true, valign: "middle",
    });
    s.addText(card.body, {
      x: x + 0.35, y: 2.6, w: cardW - 0.7, h: h - 1.05, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 14.5, color: BODY, lineSpacingMultiple: 1.22, valign: "top",
    });
  });
  if (footnote) {
    s.addText(footnote, {
      x: M, y: 6.0, w: W - 2 * M, h: 1.0, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 16.5, color: INK, bold: true, lineSpacingMultiple: 1.2,
    });
  }
  return s;
}

// A simple table with a heading row.
function tableSlide(pres, { heading, kicker, columns, rows, widths, footnote }) {
  const s = contentSlide(pres, heading, kicker);
  const header = columns.map((c) => ({
    text: c,
    options: { bold: true, color: WHITE, fill: { color: NAVY_SOFT }, fontSize: 15, fontFace: TEXT },
  }));
  const body = rows.map((r, ri) =>
    r.map((cell, ci) => ({
      text: cell,
      options: {
        fontSize: 14.5, fontFace: TEXT, color: ci === 0 ? INK : BODY, bold: ci === 0,
        fill: { color: ri % 2 === 0 ? WHITE : TINT },
      },
    }))
  );
  s.addTable([header, ...body], {
    x: M, y: 1.8, w: W - 2 * M, colW: widths,
    border: { type: "solid", color: RULE, pt: 1 },
    rowH: 0.52, valign: "middle", margin: 0.09,
  });
  if (footnote) {
    s.addText(footnote, {
      x: M, y: 6.15, w: W - 2 * M, h: 0.9, isTextBox: true, margin: 0,
      fontFace: TEXT, fontSize: 15.5, color: BODY, lineSpacingMultiple: 1.2,
    });
  }
  return s;
}

module.exports = {
  NAVY, NAVY_SOFT, INK, BODY, MUTED, WHITE, RULE, TINT, SERIES, ACCENT, HEAD, TEXT, W, H, M,
  titleSlide, sectionSlide, contentSlide, statementSlide, figureSlide, figureWithNotes,
  listSlide, statsSlide, compareSlide, tableSlide,
};
