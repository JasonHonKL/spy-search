import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from chromadb.config import Settings


class VectorSearch:
    def __init__(
        self,
        model: str = "nomic-embed-text:latest",
        name="new_collection",
        path: str = "./db",
    ):
        self.name = name
        self.client = chromadb.PersistentClient(
            path=path, settings=Settings(allow_reset=True)
        )
        self.embedding = OllamaEmbeddingFunction(
            url="http://localhost:11434", model_name=model
        )
        try:
            self.collection = self.client.get_collection(name=name)
        except:
            self.collection = self.client.create_collection(
                name=name, embedding_function=self.embedding
            )

    def add_document(self, documents: str, id: str, metadatas: None = None):
        if metadatas == None:
            self.collection.add(documents=documents, ids=id)
        else:
            self.collection.add(documents=documents, ids=id, metadatas=metadatas)

    def query(self, query: str, k: int):
        return self.collection.query(query_texts=query, n_results=k)

    def reset(self):
        self.client.reset()
        self.collection = self.client.create_collection(
            name=self.name, embedding_function=self.embedding
        )
