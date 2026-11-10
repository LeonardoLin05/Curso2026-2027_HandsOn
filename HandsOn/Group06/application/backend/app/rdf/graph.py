
from pathlib import Path

from rdflib import Graph

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BACKEND_DIR / "datasets" / "madrid-culture-with-links.ttl"

def load_graph() -> Graph:
    """
    Carga el dataset RDF de bibliotecas y museos.
    """
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"No se ha encontrado el dataset: {DATASET_PATH}"
        )

    graph = Graph()
    graph.parse(str(DATASET_PATH), format="turtle")

    return graph