#!/usr/bin/env python3
import sys
import pandas as pd
from pathlib import Path

# Добавляем путь к модулям (если run.py лежит в папке ml, то можно просто from .embedding import ...)
# Для удобства сделаем импорт относительно текущего пакета
from .embedding import SentenceTransformerEmbedding
from .predictor import Predictor
from .pipeline import PredictionPipeline

def main(input_csv: str, output_csv: str = "predictions.csv", model_dir: str = "rag_order_model_custom"):
    # Определяем абсолютные пути (предполагаем, что run.py лежит в ml, а model_dir – подпапка)
    base_dir = Path(__file__).parent
    model_path = base_dir / model_dir

    print("Загрузка эмбеддинг-модели...")
    emb_model = SentenceTransformerEmbedding()
    print("Инициализация предсказателя...")
    predictor = Predictor(str(model_path), emb_model)
    print("Загрузка данных...")
    df_input = pd.read_csv(input_csv, sep=';', encoding='utf-8')

    print("Запуск пайплайна...")
    pipeline = PredictionPipeline(predictor)
    result_df = pipeline.run(df_input)

    result_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Готово. Результат сохранён в {output_csv}")
    print(result_df.head())

if __name__ == "__main__":
    # Пример вызова: python -m ml.run_predictions data/test.csv
    if len(sys.argv) < 2:
        print("Использование: python -m ml.run_predictions <path_to_csv> [output_csv]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "predictions.csv"
    main(input_path, output_path)