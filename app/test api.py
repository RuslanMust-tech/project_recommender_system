import requests

# response = requests.post(
#     'http://localhost:8001/api/v1/dishes/',
#     json={
#         "category": "Роллы",
#         "name": "Ролл ФуФ",
#         "pieces": 8,
#         "weight_g": 178,
#         "composition": [
#             "тортилья",
#             "куриное филе жареное",
#             "сыр сливочный",
#             "помидоры",
#             "пекинская капуста",
#             "соус гриль"
#         ],
#         "proteins_g": 11,
#         "fats_g": 13,
#         "carbs_g": 18,
#         "calories_kcal": 233,
#         "price_rub": 349
#     }
# )

# response = requests.get('http://localhost:8001/api/v1/dishes/search/by_name?category=Ролл')
# response = requests.post('http://localhost:8001/api/v1/orders/',
#     json={
#     "order_id": "123",
#     "user_id": "1",
#     "food_id": "1"
#     })

response = requests.post('http://localhost:8001/api/v1/users/',
    json={
    "phone_number": "123",
    })
print(response.text)

 