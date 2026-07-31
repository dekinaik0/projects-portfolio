import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

conn = sqlite3.connect("shop.db")

blocks = [b.strip() for b in open("queries.sql", encoding="utf-8").read().split("\n\n\n") if b.strip()]


def q(n):
    return pd.read_sql(blocks[n - 1], conn)


categories = q(2)
monthly = q(5)
avg_check = q(6)
retention = q(9)
cancels = q(10)

print("Выручка по категориям:")
print(categories.to_string(index=False))
print()
print("Retention:")
print(retention.to_string(index=False))
print()
print("Всего выручки:", round(monthly["revenue"].sum(), 2))
print("Средний чек за год:", round(avg_check["avg_check"].mean(), 2))

fig, ax = plt.subplots(2, 2, figsize=(14, 9))

ax[0][0].bar(categories["category"], categories["revenue"], color="#4c72b0")
ax[0][0].set_title("Выручка по категориям")
ax[0][0].tick_params(axis="x", rotation=20)

ax[0][1].plot(monthly["month"], monthly["revenue"], marker="o", color="#55a868")
ax[0][1].set_title("Выручка по месяцам")
ax[0][1].tick_params(axis="x", rotation=45)

ax[1][0].plot(avg_check["month"], avg_check["avg_check"], marker="o", color="#c44e52")
ax[1][0].set_title("Средний чек по месяцам")
ax[1][0].tick_params(axis="x", rotation=45)

ax[1][1].bar(cancels["month"], cancels["cancel_rate"], color="#8172b2")
ax[1][1].set_title("Доля отменённых заказов, %")
ax[1][1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("dashboard.png", dpi=120)

print()
print("График сохранён в dashboard.png")

conn.close()
