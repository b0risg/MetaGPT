"""Hybrid retriever."""
from llama_index.schema import QueryType

from metagpt.rag.retrievers.base import RAGRetriever


class SimpleHybridRetriever(RAGRetriever):
    """
    SimpleHybridRetriever is a composite retriever that aggregates search results from multiple retrievers.
    """

    def __init__(self, *retrievers):
        self.retrievers: list[RAGRetriever] = retrievers
        super().__init__()

    async def _aretrieve(self, query: QueryType, **kwargs):
        """
        Asynchronously retrieves and aggregates search results from all configured retrievers.

        This method queries each retriever in the `retrievers` list with the given query and
        additional keyword arguments. It then combines the results, ensuring that each node is
        unique, based on the node's ID.
        """
        all_nodes = []
        for retriever in self.retrievers:
            nodes = await retriever.aretrieve(query, **kwargs)
            all_nodes.extend(nodes)

        # combine all nodes
        result = []
        node_ids = set()
        for n in all_nodes:
            if n.node.node_id not in node_ids:
                result.append(n)
                node_ids.add(n.node.node_id)
        return result
