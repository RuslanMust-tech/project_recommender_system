import pickle
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

class IndexLoader:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.indices: Dict[str, Any] = {}
        self.source_embeddings: Dict[str, np.ndarray] = {}
        self.sources: list = []

    def load(self) -> 'IndexLoader':
        """Загружает индексы, source_embeddings и список источников."""
        self.indices = joblib.load(self.model_dir / 'indices.pkl')
        self.sources = joblib.load(self.model_dir / 'sources.pkl')
        with open(self.model_dir / 'source_embeddings.pkl', 'rb') as f:
            self.source_embeddings = pickle.load(f)
        return self

    def search(self, source: str, query_emb: np.ndarray, k: int = 5):
        """Поиск в FAISS индексе источника."""
        idx = self.indices.get(source)
        if idx is None:
            return None, None
        return idx.search(query_emb.reshape(1, -1), k)

    def get_retrieved_emb(self, source: str, row_idx: int) -> np.ndarray:
        """Возвращает эмбеддинг retrieved документа по индексу."""
        emb = self.source_embeddings.get(source)
        if emb is not None and 0 <= row_idx < len(emb):
            return emb[row_idx]
        # fallback: нулевой вектор размерности 384 (стандарт для all-MiniLM-L6-v2)
        return np.zeros(384)

    def get_embedding_dim(self) -> int:
        """Возвращает размерность эмбеддингов (из первого источника)."""
        for src in self.sources:
            if src in self.source_embeddings and self.source_embeddings[src] is not None:
                return self.source_embeddings[src].shape[1]
        return 384  # значение по умолчанию