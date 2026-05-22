import requests

response = requests.post(
    'http://localhost:8001/api/v1/dishes/',
    json={
        "category": "Роллы",
        "name": "Ролл Форилье",
        "pieces": 8,
        "weight_g": 178,
        "composition": [
            "тортилья",
            "куриное филе жареное",
            "сыр сливочный",
            "помидоры",
            "пекинская капуста",
            "соус гриль"
        ],
        "proteins_g": 11,
        "fats_g": 13,
        "carbs_g": 18,
        "calories_kcal": 233,
        "price_rub": 349
    }
)
print(response)
