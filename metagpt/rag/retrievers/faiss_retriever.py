"""FAISS retriever."""
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import BaseNode


class FAISSRetriever(VectorIndexRetriever):
    """FAISS retriever."""

    def add_nodes(self, nodes: list[BaseNode], **kwargs):
        """Support add nodes"""
        self._index.insert_nodes(nodes, **kwargs)
