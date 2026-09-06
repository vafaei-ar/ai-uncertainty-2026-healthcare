"""Minimal notebook builder.

Notebooks are authored once as Python source under ``notebooks/source`` and
emitted in two variants: a student copy with exercises left open, and an
instructor copy with worked solutions and teaching notes. Keeping one source
means the two can never drift apart.
"""

from __future__ import annotations

import json
from pathlib import Path

STUDENT = "student"
INSTRUCTOR = "instructor"

_DEFAULT_STUB = "# Your turn.\n"


class Notebook:
    """Collects cells, then writes the two variants."""

    def __init__(self, title: str, colab_setup: bool = True):
        self.title = title
        self.cells: list[dict] = []
        if colab_setup:
            self._add_colab_setup()

    # -- authoring API ----------------------------------------------------
    def md(self, text: str, only: str | None = None) -> "Notebook":
        self.cells.append({"kind": "markdown", "source": text.strip("\n"), "only": only})
        return self

    def code(self, text: str, only: str | None = None) -> "Notebook":
        self.cells.append({"kind": "code", "source": text.strip("\n"), "only": only})
        return self

    def exercise(self, prompt: str, solution: str, stub: str | None = None) -> "Notebook":
        """A task students attempt and instructors demonstrate."""
        self.md(prompt)
        self.cells.append(
            {
                "kind": "code",
                "source": solution.strip("\n"),
                "only": None,
                "stub": (stub or _DEFAULT_STUB).strip("\n"),
            }
        )
        return self

    def note(self, text: str) -> "Notebook":
        """Teaching note that only appears in the instructor copy."""
        return self.md(f"> **Teaching note.** {text.strip()}", only=INSTRUCTOR)

    # -- rendering --------------------------------------------------------
    def _render(self, variant: str) -> dict:
        cells = []
        for cell in self.cells:
            if cell.get("only") not in (None, variant):
                continue
            source = cell["source"]
            if variant == STUDENT and "stub" in cell:
                source = cell["stub"]
            cells.append(_nb_cell(cell["kind"], source))
        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.10"},
                "colab": {"provenance": [], "toc_visible": True},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    def write(self, directory: Path, stem: str, variants=(STUDENT, INSTRUCTOR)) -> list[Path]:
        """Emit one file per variant. Pass ``variants=None`` for a single copy."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        if variants is None:
            path = directory / f"{stem}.ipynb"
            path.write_text(json.dumps(self._render(STUDENT), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            return [path]
        written = []
        for variant in variants:
            path = directory / f"{stem}_{variant}.ipynb"
            path.write_text(json.dumps(self._render(variant), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(path)
        return written

    def _add_colab_setup(self) -> None:
        self.md(
            "<a href=\"https://colab.research.google.com/github/vafaei-ar/"
            "ai-uncertainty-2026-healthcare/blob/main/notebooks/\" target=\"_parent\">"
            "Open in Colab</a>\n\n"
            "---\n\n"
            "**Setup.** Run this first. It fetches the teaching utilities and pins the\n"
            "handful of packages the notebook needs. On a fresh Colab runtime it takes\n"
            "about twenty seconds."
        )
        self.code(
            """
import importlib.util, subprocess, sys, os

REPO = "https://github.com/vafaei-ar/ai-uncertainty-2026-healthcare.git"

if importlib.util.find_spec("medsim") is None:
    if not os.path.isdir("ai-uncertainty-2026-healthcare"):
        subprocess.run(["git", "clone", "--depth", "1", REPO], check=True)
    sys.path.insert(0, os.path.abspath("ai-uncertainty-2026-healthcare"))

import medsim
print("medsim", medsim.__version__, "ready")
"""
        )


def _nb_cell(kind: str, source: str) -> dict:
    lines = source.split("\n")
    payload = [line + "\n" for line in lines[:-1]] + [lines[-1]]
    cell = {"cell_type": kind, "metadata": {}, "source": payload}
    if kind == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell


PLOT_STYLE = """
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.figsize": (7.2, 4.4),
    "figure.dpi": 110,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})
"""
