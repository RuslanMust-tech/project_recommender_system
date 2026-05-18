# # здесь будет находиться код для работы с базой данных, включая функции для получения сессии и инициализации базы данных
# import sqlite3

# def create_db():
#     # создание подключения к бабе данных
#     connection = sqlite3.connect('my_database.db')

#     # курсор какой-то хз ваще, но можно им sql запросы писать ХУУУУУЙ
#     cursor = connection.cursor()

#     # таблица для каталога еды
#     cursor.execute('''
#         CREATE TABLE Food_catalog (
#         id INTEGER PRIMARY KEY,
#         category TEXT NOT NULL,
#         name TEXT NOT NULL,
#         pieces INTEGER,
#         weight INTEGER,
#         composition TEXT,
#         proteins REAL,
#         fats REAL,
#         carbs REAL,
#         calories INTEGER,
#         price INTEGER
#     )
#     ''')
#     # таблица для юзера, пользователя, клиента
#     cursor.execute('''
#         CREATE TABLE User (
#         id INTEGER PRIMARY KEY,
#         phone_number INTEGER NOT NULL
#     ''')
#     # таблица для заказа
#     cursor.execute('''
#         CREATE TABLE Order (
#         id INTEGER PRIMARY KEY,
#         order_id INTEGER NOT NULL,
#         user_id INTEGER REFERENCES User(id),
#         food_id INTEGER REFERENCES Food_catalog(id)
#     ''')


