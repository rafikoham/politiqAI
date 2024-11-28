import os
import numpy as np
import fasttext
import faiss
from typing import List, Union
import pickle

class VectorManager:
    def __init__(self, model_path: str, vector_dim: int = 300):
        self.model = fasttext.load_model(model_path)
        self.vector_dim = vector_dim
        self.index = faiss.IndexFlatL2(vector_dim)

    def text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to FastText vector"""
        return self.model.get_sentence_vector(text)

    def batch_to_vectors(self, texts: List[str]) -> np.ndarray:
        """Convert batch of texts to vectors"""
        vectors = [self.text_to_vector(text) for text in texts]
        return np.array(vectors).astype('float32')

    def add_to_index(self, vectors: np.ndarray):
        """Add vectors to FAISS index"""
        if vectors.shape[1] != self.vector_dim:
            raise ValueError(f"Vector dimension mismatch. Expected {self.vector_dim}, got {vectors.shape[1]}")
        self.index.add(vectors)

    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors"""
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        return distances[0], indices[0]

    def save_index(self, path: str):
        """Save FAISS index to disk"""
        faiss.write_index(self.index, path)

    def load_index(self, path: str):
        """Load FAISS index from disk"""
        self.index = faiss.read_index(path)

    def save_metadata(self, metadata: dict, path: str):
        """Save metadata (e.g., mapping between vector indices and original texts)"""
        with open(path, 'wb') as f:
            pickle.dump(metadata, f)

    def load_metadata(self, path: str) -> dict:
        """Load metadata"""
        with open(path, 'rb') as f:
            return pickle.load(f)

class VectorizeResult:
    def __init__(self, text_id: str, vector: np.ndarray, metadata: dict = None):
        self.text_id = text_id
        self.vector = vector
        self.metadata = metadata or {}
