import joblib
import numpy as np
from pathlib import Path
from .embedding import EmbeddingModel
from .index_loader import IndexLoader
from .feature_extractor import FeatureExtractor

class Predictor:
    def __init__(self, model_dir: str, embedding_model: EmbeddingModel):
        model_path = Path(model_dir)
        self.rf = joblib.load(model_path / 'rf_model.pkl')
        self.scaler = joblib.load(model_path / 'scaler.pkl')
        self.label_encoder = joblib.load(model_path / 'label_encoder.pkl')

        self.index_loader = IndexLoader(model_dir).load()
        self.feature_extractor = FeatureExtractor(embedding_model, self.index_loader)

    def predict(self, query_dict: dict) -> list:
        """
        Возвращает список предсказанных товаров (первые top_k, обычно 1-5).
        """
        X = self.feature_extractor.extract(query_dict).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        pred_id = self.rf.predict(X_scaled)[0]
        label = self.label_encoder.inverse_transform([pred_id])[0]
        # Если модель предсказала несколько товаров через разделитель "|"
        return label.split('|') if '|' in label else [label]