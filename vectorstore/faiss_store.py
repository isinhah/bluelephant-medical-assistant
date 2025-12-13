import faiss
import numpy as np
import pickle
import os

VECTOR_DIM = 100

class VectorStore:
    def __init__(self, file_path=".faiss_index"):
        self.file_path = file_path
        self.id_to_name = {}  # mapeia índice -> nome oficial do tipo
        self.index = faiss.IndexFlatL2(VECTOR_DIM)

        if os.path.exists(file_path):
            self.load()

    def simple_embedding(self, text: str):
        vec = np.zeros(VECTOR_DIM, dtype=np.float32)
        for i, c in enumerate(text[:VECTOR_DIM]):
            vec[i] = ord(c) / 100
        return vec

    def add_consult_type(self, name: str, synonyms=None):
        if synonyms is None:
            synonyms = []
        for term in [name] + synonyms:
            vec = self.simple_embedding(term).reshape(1, -1).astype(np.float32)
            self.index.add(vec)
            idx = self.index.ntotal - 1
            self.id_to_name[idx] = name

        self.save()

    def query_consult_type(self, query: str, top_k=1):
        vec = self.simple_embedding(query).reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(vec, top_k)
        if len(indices[0]) > 0:
            return self.id_to_name[indices[0][0]]
        return None

    def save(self):
        faiss.write_index(self.index, self.file_path)
        with open(self.file_path + ".pkl", "wb") as f:
            pickle.dump(self.id_to_name, f)

    def load(self):
        self.index = faiss.read_index(self.file_path)
        with open(self.file_path + ".pkl", "rb") as f:
            self.id_to_name = pickle.load(f)
