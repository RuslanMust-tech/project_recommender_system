import pandas as pd
from datetime import datetime
from .query_builder import QueryBuilder
from .predictor import Predictor

class PredictionPipeline:
    def __init__(self, predictor: Predictor, query_builder: QueryBuilder = None):
        self.predictor = predictor
        self.query_builder = query_builder or QueryBuilder()

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Принимает DataFrame с колонками: phone, order, time.
        Возвращает DataFrame с предсказаниями.
        """
        df = df.copy()
        # Приводим имена колонок к нижнему регистру и убираем пробелы
        df.columns = [c.strip().lower() for c in df.columns]

        # Парсим время
        df['datetime'] = df['time'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M'))
        df = df.sort_values(['phone', 'datetime'])

        results = []
        for phone, group in df.groupby('phone'):
            group = group.sort_values('datetime')
            orders_items = [row['order'].split(';') for _, row in group.iterrows()]
            total_orders = len(orders_items)
            for i in range(1, total_orders):
                prev_orders = orders_items[:i]          # все заказы до текущего
                current_items = orders_items[i]         # текущий заказ (корзина)
                dt = group.iloc[i]['datetime']

                query = self.query_builder.build(prev_orders, current_items, dt, total_orders)
                predicted = self.predictor.predict(query)

                results.append({
                    'phone': phone,
                    'order_time': group.iloc[i]['time'],
                    'current_order': '; '.join(current_items),
                    'predicted_next': ', '.join(predicted)
                })

        return pd.DataFrame(results)