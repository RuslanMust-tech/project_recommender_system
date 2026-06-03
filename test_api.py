import requests
import json

# json_file = open("app/menu.json", 'r', encoding='utf-8')
# data = json.load(json_file)
# for i in data['items']:
#     response = requests.post(
#         'http://localhost:8001/api/v1/dishes/',
#         json=i
#     )
#     print(response)

# response = requests.get('http://localhost:8001/api/v1/dishes/search/by_name?category=Ролл')
# response = requests.post('http://localhost:8001/api/v1/orders/',
#     json={
#     "order_id": "123",
#     "user_id": "1",
#     "food_id": "1"
#     })

# response = requests.post('http://localhost:8001/api/v1/users/',
#     json={
#     "phone_number": "123",
#     })
# print(response.text)

response = requests.get('http://localhost:8001/api/v1/user/123')
print(response)


# def transform_nutrition_data(item):
#     if 'nutrition_per_100g' in item:
#         nutrition = item.pop('nutrition_per_100g')  # удаляем и получаем значение
#         # Добавляем все поля из nutrition на верхний уровень
#         item.update(nutrition)
#     return item
 
# inf = open("app/menu.json")
# data = json.load(inf)

# data['items'] = [transform_nutrition_data(item) for item in data['items']]

# inf.close()
# # Обратно в JSON
# outf = open("app/menu2.json", "w")
# new_json_str = json.dump(data, outf, ensure_ascii=False, indent=2)
# outf.close()