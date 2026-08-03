import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Кредитный скоринг", layout="wide")

df = pd.read_csv("scored_applications.csv")

st.title("Дашборд по результатам кредитного скоринга")
st.caption("Данные тестовой выборки, оценки вероятности дефолта построены моделью CatBoost")

st.sidebar.header("Фильтры")

regions = st.sidebar.multiselect("Регион", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
employment = st.sidebar.multiselect("Тип занятости", sorted(df["employment_type"].unique()), default=sorted(df["employment_type"].unique()))
age_range = st.sidebar.slider("Возраст", int(df["age"].min()), int(df["age"].max()), (int(df["age"].min()), int(df["age"].max())))
threshold = st.sidebar.slider("Порог отсечения по вероятности дефолта", 0.0, 1.0, 0.5, 0.01)

filtered = df[
    df["region"].isin(regions)
    & df["employment_type"].isin(employment)
    & df["age"].between(*age_range)
]

filtered = filtered.copy()
filtered["risk_flag"] = (filtered["default_proba"] >= threshold).map({True: "Высокий риск", False: "Низкий риск"})

col1, col2, col3, col4 = st.columns(4)
col1.metric("Заявок в выборке", len(filtered))
col2.metric("Средняя вероятность дефолта", f"{filtered['default_proba'].mean():.1%}" if len(filtered) else "—")
col3.metric("Отмечено как высокий риск", int((filtered["risk_flag"] == "Высокий риск").sum()))
col4.metric("Фактических дефолтов в выборке", int(filtered["default_true"].sum()))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Распределение вероятности дефолта")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(filtered[filtered["default_true"] == 0]["default_proba"], bins=25, alpha=0.6, label="Не дефолт", color="#55a868")
    ax.hist(filtered[filtered["default_true"] == 1]["default_proba"], bins=25, alpha=0.6, label="Дефолт", color="#c44e52")
    ax.axvline(threshold, color="black", linestyle="--", label="Порог отсечения")
    ax.set_xlabel("Вероятность дефолта")
    ax.legend()
    st.pyplot(fig)

with right:
    st.subheader("Средний риск по типу занятости")
    by_employment = filtered.groupby("employment_type")["default_proba"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(by_employment.index, by_employment.values, color="#4c72b0")
    ax.set_xlabel("Средняя вероятность дефолта")
    st.pyplot(fig)

st.subheader("Заявки с высоким риском")
high_risk = filtered[filtered["risk_flag"] == "Высокий риск"].sort_values("default_proba", ascending=False)
st.dataframe(
    high_risk[["application_id", "age", "income", "employment_type", "region", "existing_loans", "default_proba"]],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Скачать отфильтрованные заявки (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_applications.csv",
)
