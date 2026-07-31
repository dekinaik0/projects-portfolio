import sqlite3
import random
from datetime import date, timedelta

random.seed(42)

conn = sqlite3.connect("shop.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT,
    signup_date TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
);
""")

cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
first_names = ["Иван", "Мария", "Пётр", "Анна", "Сергей", "Ольга", "Дмитрий", "Елена"]
last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов"]

start = date(2024, 1, 1)

customers = []
for i in range(1, 501):
    name = random.choice(first_names) + " " + random.choice(last_names)
    city = random.choice(cities)
    signup = start + timedelta(days=random.randint(0, 300))
    customers.append((i, name, city, signup.isoformat()))

cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)

categories = {
    "Электроника": ["Наушники", "Клавиатура", "Мышь", "Монитор", "Веб-камера"],
    "Одежда": ["Футболка", "Джинсы", "Куртка", "Кроссовки"],
    "Книги": ["Роман", "Учебник", "Комикс"],
    "Дом": ["Лампа", "Кружка", "Плед", "Коврик"],
}

products = []
pid = 1
for category, names in categories.items():
    for n in names:
        price = round(random.uniform(300, 25000), 2)
        products.append((pid, n, category, price))
        pid += 1

cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

orders = []
items = []
order_id = 1
item_id = 1

for customer_id, name, city, signup in customers:
    signup_date = date.fromisoformat(signup)
    n_orders = random.choices([0, 1, 2, 3, 4, 5], weights=[15, 35, 25, 12, 8, 5])[0]
    max_offset = (date(2024, 12, 31) - signup_date).days
    if max_offset < 1:
        continue
    for _ in range(n_orders):
        order_date = signup_date + timedelta(days=random.randint(1, max_offset))
        status = random.choices(["delivered", "cancelled"], weights=[88, 12])[0]
        orders.append((order_id, customer_id, order_date.isoformat(), status))
        for _ in range(random.randint(1, 4)):
            product_id = random.randint(1, len(products))
            quantity = random.choices([1, 2, 3], weights=[70, 22, 8])[0]
            items.append((item_id, order_id, product_id, quantity))
            item_id += 1
        order_id += 1

cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", items)

conn.commit()

print("Клиентов:", len(customers))
print("Товаров:", len(products))
print("Заказов:", len(orders))
print("Позиций в заказах:", len(items))

conn.close()
