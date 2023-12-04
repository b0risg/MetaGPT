#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/8 14:03
@Author  : alexanderwu
@File    : document.py
"""
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from langchain.document_loaders import (
    TextLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import CharacterTextSplitter
from pydantic import BaseModel, Field
from tqdm import tqdm

from metagpt.config import CONFIG
from metagpt.logs import logger
from metagpt.repo_parser import RepoParser


def validate_cols(content_col: str, df: pd.DataFrame):
    if content_col not in df.columns:
        raise ValueError("Content column not found in DataFrame.")


def read_data(data_path: Path):
    suffix = data_path.suffix
    if ".xlsx" == suffix:
        data = pd.read_excel(data_path)
    elif ".csv" == suffix:
        data = pd.read_csv(data_path)
    elif ".json" == suffix:
        data = pd.read_json(data_path)
    elif suffix in (".docx", ".doc"):
        data = UnstructuredWordDocumentLoader(str(data_path), mode="elements").load()
    elif ".txt" == suffix:
        data = TextLoader(str(data_path)).load()
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=256, chunk_overlap=0)
        texts = text_splitter.split_documents(data)
        data = texts
    elif ".pdf" == suffix:
        data = UnstructuredPDFLoader(str(data_path), mode="elements").load()
    else:
        raise NotImplementedError("File format not supported.")
    return data


class DocumentStatus(Enum):
    """Indicates document status, a mechanism similar to RFC/PEP"""

    DRAFT = "draft"
    UNDERREVIEW = "underreview"
    APPROVED = "approved"
    DONE = "done"


class Document(BaseModel):
    """
    Document: Handles operations related to document files.
    """

    path: Path = Field(default=None)
    name: str = Field(default="")
    content: str = Field(default="")

    # metadata? in content perhaps.
    author: str = Field(default="")
    status: DocumentStatus = Field(default=DocumentStatus.DRAFT)
    reviews: list = Field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path):
        """
        Create a Document instance from a file path.
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found.")
        content = path.read_text()
        return cls(content=content, path=path)

    @classmethod
    def from_text(cls, text: str, path: Optional[Path] = None):
        """
        Create a Document from a text string.
        """
        return cls(content=text, path=path)

    def to_path(self, path: Optional[Path] = None):
        """
        Save content to the specified file path.
        """
        if path is not None:
            self.path = path

        if self.path is None:
            raise ValueError("File path is not set.")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.content, encoding="utf-8")

    def persist(self):
        """
        Persist document to disk.
        """
        return self.to_path()


class IndexableDocument(Document):
    """
    Advanced document handling: For vector databases or search engines.
    """

    data: Union[pd.DataFrame, list]
    content_col: Optional[str] = Field(default="")
    meta_col: Optional[str] = Field(default="")

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_path(cls, data_path: Path, content_col="content", meta_col="metadata"):
        if not data_path.exists():
            raise FileNotFoundError(f"File {data_path} not found.")
        data = read_data(data_path)
        content = data_path.read_text()
        if isinstance(data, pd.DataFrame):
            validate_cols(content_col, data)
        return cls(data=data, content=content, content_col=content_col, meta_col=meta_col)

    def _get_docs_and_metadatas_by_df(self) -> (list, list):
        df = self.data
        docs = []
        metadatas = []
        for i in tqdm(range(len(df))):
            docs.append(df[self.content_col].iloc[i])
            if self.meta_col:
                metadatas.append({self.meta_col: df[self.meta_col].iloc[i]})
            else:
                metadatas.append({})
        return docs, metadatas

    def _get_docs_and_metadatas_by_langchain(self) -> (list, list):
        data = self.data
        docs = [i.page_content for i in data]
        metadatas = [i.metadata for i in data]
        return docs, metadatas

    def get_docs_and_metadatas(self) -> (list, list):
        if isinstance(self.data, pd.DataFrame):
            return self._get_docs_and_metadatas_by_df()
        elif isinstance(self.data, list):
            return self._get_docs_and_metadatas_by_langchain()
        else:
            raise NotImplementedError("Data type not supported for metadata extraction.")


class RepoMetadata(BaseModel):
    name: str = Field(default="")
    n_docs: int = Field(default=0)
    n_chars: int = Field(default=0)
    symbols: list = Field(default_factory=list)


class Repo(BaseModel):
    # Name of this repo.
    name: str = Field(default="")
    # metadata: RepoMetadata = Field(default=RepoMetadata)
    docs: dict[Path, Document] = Field(default_factory=dict)
    codes: dict[Path, Document] = Field(default_factory=dict)
    assets: dict[Path, Document] = Field(default_factory=dict)
    path: Path = Field(default=None)

    def _path(self, filename):
        return self.path / filename

    @classmethod
    def from_path(cls, path: Path):
        """Load documents, code, and assets from a repository path."""
        path.mkdir(parents=True, exist_ok=True)
        repo = Repo(path=path, name=path.name)
        for file_path in path.rglob("*"):
            # FIXME: These judgments are difficult to support multiple programming languages and need to be more general
            if file_path.is_file() and file_path.suffix in [".json", ".txt", ".md", ".py", ".js", ".css", ".html"]:
                repo._set(file_path.read_text(), file_path)
        return repo

    def to_path(self):
        """Persist all documents, code, and assets to the given repository path."""
        for doc in self.docs.values():
            doc.to_path()
        for code in self.codes.values():
            code.to_path()
        for asset in self.assets.values():
            asset.to_path()

    def _set(self, content: str, path: Path):
        """Add a document to the appropriate category based on its file extension."""
        suffix = path.suffix
        doc = Document(content=content, path=path, name=str(path.relative_to(self.path)))

        # FIXME: These judgments are difficult to support multiple programming languages and need to be more general
        if suffix.lower() == ".md":
            self.docs[path] = doc
        elif suffix.lower() in [".py", ".js", ".css", ".html"]:
            self.codes[path] = doc
        else:
            self.assets[path] = doc
        return doc

    def set(self, content: str, filename: str):
        """Set a document and persist it to disk."""
        path = self._path(filename)
        doc = self._set(content, path)
        doc.to_path()

    def get(self, filename: str) -> Optional[Document]:
        """Get a document by its filename."""
        path = self._path(filename)
        return self.docs.get(path) or self.codes.get(path) or self.assets.get(path)

    def get_text_documents(self) -> list[Document]:
        return list(self.docs.values()) + list(self.codes.values())

    def eda(self) -> RepoMetadata:
        n_docs = sum(len(i) for i in [self.docs, self.codes, self.assets])
        n_chars = sum(sum(len(j.content) for j in i.values()) for i in [self.docs, self.codes, self.assets])
        symbols = RepoParser(base_directory=self.path).generate_symbols()
        return RepoMetadata(name=self.name, n_docs=n_docs, n_chars=n_chars, symbols=symbols)


def set_existing_repo(path=CONFIG.workspace_path / "t1"):
    repo1 = Repo.from_path(path)
    repo1.set("wtf content", "doc/wtf_file.md")
    repo1.set("wtf code", "code/wtf_file.py")
    logger.info(repo1)  # check doc


def load_existing_repo(path=CONFIG.workspace_path / "web_tetris"):
    repo = Repo.from_path(path)
    logger.info(repo)
    logger.info(repo.eda())


def main():
    load_existing_repo()


if __name__ == "__main__":
    main()
