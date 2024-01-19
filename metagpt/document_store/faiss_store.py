#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/25 10:20
@Author  : alexanderwu
@File    : faiss_store.py
"""
import asyncio
from pathlib import Path
from typing import Any, Optional

import faiss
from llama_index import VectorStoreIndex, load_index_from_storage
from llama_index.embeddings import BaseEmbedding
from llama_index.schema import Document, QueryBundle, TextNode
from llama_index.storage import StorageContext
from llama_index.vector_stores import FaissVectorStore

from metagpt.document import IndexableDocument
from metagpt.document_store.base_store import LocalStore
from metagpt.logs import logger
from metagpt.utils.embedding import get_embedding


class FaissStore(LocalStore):
    def __init__(
        self, raw_data: Path, cache_dir=None, meta_col="source", content_col="output", embedding: BaseEmbedding = None
    ):
        self.meta_col = meta_col
        self.content_col = content_col
        self.embedding = embedding or get_embedding()
        self.store: VectorStoreIndex
        super().__init__(raw_data, cache_dir)

    def _load(self) -> Optional["VectorStoreIndex"]:
        index_file, store_file = self._get_index_and_store_fname(index_ext=".faiss")  # FAISS using .faiss

        if not (index_file.exists() and store_file.exists()):
            logger.info("Missing at least one of index_file/store_file, load failed and return None")
            return None
        vector_store = FaissVectorStore.from_persist_dir(persist_dir=self.cache_dir)
        storage_context = StorageContext.from_defaults(persist_dir=self.cache_dir, vector_store=vector_store)
        index = load_index_from_storage(storage_context)

        return index

    def _write(self, docs: list[str], metadatas: list[dict[str, Any]]) -> VectorStoreIndex:
        assert len(docs) == len(metadatas)
        texts_embeds = self.embedding.get_text_embedding_batch(docs)
        documents = [Document(text=doc, metadata=metadatas[idx]) for idx, doc in enumerate(docs)]

        [TextNode(embedding=embed, metadata=metadatas[idx]) for idx, embed in enumerate(texts_embeds)]
        # doc_store = SimpleDocumentStore()
        # doc_store.add_documents(nodes)
        vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(1536))
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context)

        return index

    def persist(self):
        self.store.storage_context.persist(self.cache_dir)

    def search(self, query: str, expand_cols=False, sep="\n", *args, k=5, **kwargs):
        retriever = self.store.as_retriever(similarity_top_k=k)
        rsp = retriever.retrieve(QueryBundle(query_str=query, embedding=self.embedding.get_text_embedding(query)))

        logger.debug(rsp)
        if expand_cols:
            return str(sep.join([f"{x.node.text}: {x.node.metadata}" for x in rsp]))
        else:
            return str(sep.join([f"{x.node.text}" for x in rsp]))

    async def asearch(self, *args, **kwargs):
        return await asyncio.to_thread(self.search, *args, **kwargs)

    def write(self):
        """Initialize the index and library based on the Document (JSON / XLSX, etc.) file provided by the user."""
        if not self.raw_data_path.exists():
            raise FileNotFoundError
        doc = IndexableDocument.from_path(self.raw_data_path, self.content_col, self.meta_col)
        docs, metadatas = doc.get_docs_and_metadatas()

        self.store = self._write(docs, metadatas)
        self.persist()
        return self.store

    def add(self, texts: list[str], *args, **kwargs) -> list[str]:
        """FIXME: Currently, the store is not updated after adding."""
        texts_embeds = self.embedding.get_text_embedding_batch(texts)
        nodes = [TextNode(embedding=embed) for embed in texts_embeds]
        self.store.insert_nodes(nodes)

        return []

    def delete(self, *args, **kwargs):
        """Currently, faiss does not provide a delete interface."""
        raise NotImplementedError
