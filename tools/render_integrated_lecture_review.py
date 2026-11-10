"""Render the integrated slide deck for human visual review.

Requires LibreOffice Impress, pdftoppm (poppler), and Pillow.
Renders only presentation pages and creates contact sheets for QA.
This is a preview, not an AI-generated figure or source slide file.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "slides/lecture_when_can_we_trust_clinical_ai.pptx"
DEST = ROOT / "docs/qa"

def run():
    if shutil.which("libreoffice") is None:
        raise RuntimeError("LibreOffice Impress is needed to render the PPTX")
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm is needed to rasterize the exported PDF")
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="review_mauritius_") as tmp:
        temp = Path(tmp)
        command = [
            "libreoffice", f"-env:UserInstallation=file://{temp}/lo_profile",
            "--headless", "--convert-to", "pdf", "--outdir", str(temp), str(PPTX)
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        pdf = temp / (PPTX.stem + ".pdf")
        if not pdf.exists():
            raise RuntimeError("LibreOffice did not generate the expected PDF")
        subprocess.run([
            "pdftoppm", "-f", "1", "-l", "23", "-r", "90", "-png",
            str(pdf), str(temp / "slide")
        ], check=True, capture_output=True, text=True)
        pages = sorted(temp.glob("slide-*.png"))
        if len(pages) != 23:
            raise AssertionError(f"Expected 23 rendered pages, got {len(pages)}")
        # Three groups of 8 slides make labels legible for manual inspection.
        for group_index, start in enumerate(range(0, len(pages), 8), 1):
            chunk = pages[start:start+8]
            cell_w, cell_h = 640, 380
            canvas = Image.new("RGB", (2 * cell_w, 4 * cell_h), "white")
            draw = ImageDraw.Draw(canvas)
            for j, path in enumerate(chunk):
                slide = Image.open(path).convert("RGB")
                fitted = ImageOps.contain(slide, (620, 350))
                col, row = j % 2, j // 2
                x = col * cell_w + (cell_w - fitted.width)//2
                y = row * cell_h + 13
                canvas.paste(fitted, (x, y))
                draw.text((col*cell_w + 16, row*cell_h + 360),
                          f"Slide {start+j+1}", fill="black")
            out = DEST / f"integrated_lecture_contact_sheet_{group_index}.png"
            canvas.save(out)
            print(f"Rendered contact sheet: {out.relative_to(ROOT)} ({len(chunk)} slides)")
    print("All 23 slides rendered for human visual review.")

if __name__ == "__main__":
    run()
