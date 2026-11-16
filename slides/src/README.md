# Slide generator sources: historical lecture builds and optional references

The lecture decks are generated, not hand-built, so the figures and the
numbers quoted on the slides stay tied to the code that produced them.

```bash
python slides/make_figures.py     # render figures/ from medsim (run from the repo root)
cd slides/src
npm install pptxgenjs             # only if it is not already available
node deck1.js
node deck2.js       # optional reference
node one_lecture.js # earlier lecture build (not the reviewed PDF)
```

- `theme.js` - the shared visual system: palette, type, and the seven slide
  layouts (title, section, statement, figure, figure-with-notes, list, stats,
  compare, table).
- `deck1.js` / `deck2.js` - the content of each lecture, including speaker notes.

The four-colour series palette is validated for colour-vision deficiency and for
contrast against both light and dark surfaces. If you change it, re-check it
rather than eyeballing it.

- `one_lecture.js` produces an earlier version of the 23-slide lecture. It has not yet been reconciled with the reviewed PDF distributed for Tuesday. Do not claim it regenerates the official presentation without checking fidelity.
- `deck1.js` and `deck2.js` remain as self-paced references, not as two scheduled lecture slots.
- The linked project and presenter guide live under `project/THREE_DAY_RESEARCH_PROJECT.md` and `docs/ONE_LECTURE_PRESENTER_GUIDE.md`.

The GitHub Actions workflow builds temporary PPTX files to verify geometry and notes. The repository distributes only the reviewed PDFs under `slides/`; generated PPTX files should not be committed. When revising the official Tuesday PDF, first reconcile the slide source and verify the updated output.
