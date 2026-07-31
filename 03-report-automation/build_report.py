import pandas as pd
from openpyxl.chart import BarChart, LineChart, Reference

SLA_HOURS = 24

raw = pd.read_csv("raw_tickets.csv")
print(f"Загружено строк: {len(raw)}")

df = raw.drop_duplicates()
print(f"Удалено дублей: {len(raw) - len(df)}")

df = df.copy()
df["department"] = df["department"].str.strip().str.capitalize()
df["status"] = df["status"].str.strip().str.capitalize()
df["operator"] = df["operator"].fillna("").str.strip().replace("", "Не назначен")

def parse_dates(series):
    iso = pd.to_datetime(series, format="%Y-%m-%d %H:%M", errors="coerce")
    ru = pd.to_datetime(series, format="%d.%m.%Y %H:%M", errors="coerce")
    return iso.fillna(ru)


df["created"] = parse_dates(df["created"])
df["closed"] = parse_dates(df["closed"])

df["rating"] = pd.to_numeric(df["rating"].astype(str).str.extract(r"^(\d)$")[0], errors="coerce")

df["hours"] = (df["closed"] - df["created"]).dt.total_seconds() / 3600
df["in_sla"] = df["hours"] <= SLA_HOURS

closed = df[df["hours"].notna()]

summary = pd.DataFrame([
    {"Метрика": "Всего заявок", "Значение": len(df)},
    {"Метрика": "Решено", "Значение": (df["status"] == "Решено").sum()},
    {"Метрика": "В работе", "Значение": (df["status"] == "В работе").sum()},
    {"Метрика": "Отклонено", "Значение": (df["status"] == "Отклонено").sum()},
    {"Метрика": "Среднее время решения, ч", "Значение": round(closed["hours"].mean(), 1)},
    {"Метрика": "Медианное время решения, ч", "Значение": round(closed["hours"].median(), 1)},
    {"Метрика": f"Доля в SLA {SLA_HOURS} ч, %", "Значение": round(100 * closed["in_sla"].mean(), 1)},
    {"Метрика": "Средняя оценка", "Значение": round(df["rating"].mean(), 2)},
    {"Метрика": "Заявок без оценки", "Значение": int(df["rating"].isna().sum())},
])

by_dept = closed.groupby("department").agg(
    Заявок=("ticket_id", "count"),
    Среднее_время_ч=("hours", "mean"),
    Доля_в_SLA=("in_sla", "mean"),
    Средняя_оценка=("rating", "mean"),
).round(2).reset_index()
by_dept["Доля_в_SLA"] = (by_dept["Доля_в_SLA"] * 100).round(1)
by_dept = by_dept.rename(columns={
    "department": "Отдел",
    "Среднее_время_ч": "Среднее время, ч",
    "Доля_в_SLA": "Доля в SLA, %",
    "Средняя_оценка": "Средняя оценка",
})

by_type = df.groupby("type").agg(
    Заявок=("ticket_id", "count"),
    Средняя_оценка=("rating", "mean"),
).round(2).reset_index().rename(columns={"type": "Тип обращения", "Средняя_оценка": "Средняя оценка"})

by_week = df.set_index("created").resample("W")["ticket_id"].count().reset_index()
by_week.columns = ["Неделя", "Заявок"]
by_week["Неделя"] = by_week["Неделя"].dt.strftime("%d.%m")

with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Сводка", index=False)
    by_dept.to_excel(writer, sheet_name="По отделам", index=False)
    by_type.to_excel(writer, sheet_name="По типам", index=False)
    by_week.to_excel(writer, sheet_name="По неделям", index=False)

    book = writer.book

    chart = BarChart()
    chart.title = "Среднее время решения по отделам, ч"
    chart.height = 9
    chart.width = 18
    sheet = writer.sheets["По отделам"]
    data = Reference(sheet, min_col=3, min_row=1, max_row=len(by_dept) + 1)
    cats = Reference(sheet, min_col=1, min_row=2, max_row=len(by_dept) + 1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    sheet.add_chart(chart, "G2")

    line = LineChart()
    line.title = "Заявки по неделям"
    line.height = 9
    line.width = 18
    sheet = writer.sheets["По неделям"]
    data = Reference(sheet, min_col=2, min_row=1, max_row=len(by_week) + 1)
    cats = Reference(sheet, min_col=1, min_row=2, max_row=len(by_week) + 1)
    line.add_data(data, titles_from_data=True)
    line.set_categories(cats)
    sheet.add_chart(line, "E2")

    for name in writer.sheets:
        for column in writer.sheets[name].columns:
            width = max(len(str(cell.value)) for cell in column) + 3
            writer.sheets[name].column_dimensions[column[0].column_letter].width = width

print()
print(summary.to_string(index=False))
print()
print(by_dept.to_string(index=False))
print()
print("Отчёт сохранён в report.xlsx")
