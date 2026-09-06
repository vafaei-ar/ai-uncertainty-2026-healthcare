"""Execute a notebook headlessly and report cell timings.

    python tools/run_notebook.py notebooks/01_..._instructor.ipynb
"""
import sys, time, warnings
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import nbformat
from nbclient import NotebookClient

warnings.filterwarnings("ignore")

path = Path(sys.argv[1])
nb = nbformat.read(path, as_version=4)
client = NotebookClient(nb, timeout=900, kernel_name="python3",
                        resources={"metadata": {"path": str(Path.cwd())}})
start = time.time()
client.execute()
print(f"OK  {path.name}  {len(nb.cells)} cells  {time.time() - start:.1f}s")
