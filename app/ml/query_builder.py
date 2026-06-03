from datetime import datetime
from typing import List

class QueryBuilder:
    @staticmethod
    def build(prev_orders_items: List[List[str]], current_items: List[str],
              dt: datetime, total_orders: int) -> dict:
        """
        prev_orders_items: список заказов (каждый заказ – список названий блюд) до текущего
        current_items: список блюд текущего заказа (корзина)
        dt: дата/время текущего заказа
        total_orders: общее число заказов пользователя (включая текущий)
        """
        dow_map = {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }
        dow = dow_map[dt.weekday()]

        # предыдущие заказы: объединяем все блюда
        flat_prev = [item for order in prev_orders_items for item in order]
        prev_text = f"previous orders: {', '.join(flat_prev[:10])}" if flat_prev else "previous orders: none"

        context_text = f"order placed on {dow} at {dt.hour}:00"
        user_text = f"user history: {total_orders} total orders"
        calendar_text = f"day: {dow}, hour: {dt.hour}"
        cart_text = f"current cart: {', '.join(current_items[:5])}"

        return {
            'previous_orders': prev_text,
            'current_context': context_text,
            'user_data': user_text,
            'calendar': calendar_text,
            'cart': cart_text
        }