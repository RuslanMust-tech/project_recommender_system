import numpy as np
from .embedding import EmbeddingModel
from .index_loader import IndexLoader

class FeatureExtractor:
    def __init__(self, embedding_model: EmbeddingModel, index_loader: IndexLoader, k: int = 5):
        self.emb_model = embedding_model
        self.index_loader = index_loader
        self.k = k
        self.emb_dim = embedding_model.dim

    def extract(self, query_dict: dict) -> np.ndarray:
        """
        Строит вектор признаков для одного запроса.
        query_dict: словарь с ключами из sources (previous_orders, current_context, ...)
        Возвращает: вектор длины len(sources) * (emb_dim + 2 + emb_dim) = 5 * 770 = 3850
        """
        features = []
        for src in self.index_loader.sources:
            text = query_dict.get(src, '')
            if not text or src not in self.index_loader.indices or self.index_loader.indices[src] is None:
                # заглушка: нули для всего блока
                features.extend([0.0] * (self.emb_dim + 2 + self.emb_dim))
                continue

            # эмбеддинг запроса
            query_emb = self.emb_model.encode([text])[0].astype('float32')

            # поиск в FAISS
            sims, ret_idx = self.index_loader.search(src, query_emb, self.k)
            if sims is None:
                max_sim = mean_sim = 0.0
                retrieved_emb = np.zeros(self.emb_dim)
            else:
                valid_sims = sims[0][sims[0] > -1]
                max_sim = valid_sims.max() if len(valid_sims) else 0.0
                mean_sim = valid_sims.mean() if len(valid_sims) else 0.0
                retrieved_idx = ret_idx[0][0] if ret_idx[0][0] != -1 else -1
                if retrieved_idx != -1:
                    retrieved_emb = self.index_loader.get_retrieved_emb(src, retrieved_idx)
                else:
                    retrieved_emb = np.zeros(self.emb_dim)

            feat = np.concatenate([query_emb, [max_sim, mean_sim], retrieved_emb])
            features.extend(feat)

        return np.array(features)