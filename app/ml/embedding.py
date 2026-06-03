from abc import ABC, abstractmethod
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingModel(ABC):
    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

class SentenceTransformerEmbedding(EmbeddingModel):
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self._model = SentenceTransformer(model_name)
        self._dim = self._model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts, normalize_embeddings=True)

    @property
    def dim(self) -> int:
        return self._dim