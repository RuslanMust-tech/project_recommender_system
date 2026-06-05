import pickle
import joblib
import numpy as np
from pathlib import Path

# Папка с файлами модели
model_dir = Path("rag_order_model_custom")

# Загружаем модель и трансформеры
rf_model = joblib.load(model_dir / "rf_model.pkl")
scaler = joblib.load(model_dir / "scaler.pkl")
label_encoder = joblib.load(model_dir / "label_encoder.pkl")

# Загружаем эмбеддинги (матрицы)
emb_user = np.load(model_dir / "emb_user_data.npy")
emb_prev_orders = np.load(model_dir / "emb_previous_orders.npy")
emb_context = np.load(model_dir / "emb_current_context.npy")
emb_cart = np.load(model_dir / "emb_cart.npy")
emb_calendar = np.load(model_dir / "emb_calendar.npy")

# Вспомогательные маппинги
with open(model_dir / "source_embeddings.pkl", "rb") as f:
    source_embeddings = pickle.load(f)
with open(model_dir / "indices.pkl", "rb") as f:
    indices = pickle.load(f)
with open(model_dir / "sources.pkl", "rb") as f:
    sources = pickle.load(f)

print("Все компоненты модели успешно загружены.")

# Какое количество признаков ожидает модель?
n_features = rf_model.n_features_in_
print(f"Модель ожидает {n_features} признаков")

# А сколько признаков у scaler?
print(f"Scaler обучен на {scaler.mean_.shape[0]} признаках")

print("\n--- sources ---")
print(type(sources))
if isinstance(sources, dict):
    print("Ключи:", list(sources.keys())[:5])
    print("Пример значения:", list(sources.values())[:2])
else:
    print(sources[:5] if hasattr(sources, '__getitem__') else sources)

print("\n--- indices ---")
print(type(indices))
if isinstance(indices, dict):
    print("Ключи:", list(indices.keys())[:10])

print("\n--- source_embeddings ---")
print(type(source_embeddings))
if isinstance(source_embeddings, dict):
    first_key = list(source_embeddings.keys())[0]
    print(f"Пример ключа: {first_key}")
    print(f"Форма эмбеддинга: {source_embeddings[first_key].shape}")

print("\nРазмерности эмбеддингов по источникам:")
total = 0
for src in sources:
    emb_mat = source_embeddings[src]
    print(f"{src}: {emb_mat.shape}")
    total += emb_mat.shape[1]
print(f"\nСуммарная размерность (без доп. признаков): {total}")
print(f"Ожидаемая моделью: {rf_model.n_features_in_}")
print(f"Разница: {rf_model.n_features_in_ - total} (возможно, это склярные признаки)")