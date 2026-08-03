import numpy as np
import pandas as pd

np.random.seed(42)
n = 4000

age = np.random.randint(20, 65, n)
income = np.random.lognormal(mean=10.8, sigma=0.45, size=n).round(-2)
experience = np.clip(age - 20 - np.random.randint(0, 8, n), 0, None)
credit_history_years = np.random.randint(0, 15, n)
existing_loans = np.random.poisson(0.8, n)
loan_amount = np.random.lognormal(mean=11.5, sigma=0.6, size=n).round(-3)
region = np.random.choice(["Москва", "Санкт-Петербург", "Регион"], n, p=[0.25, 0.15, 0.6])
employment = np.random.choice(["Наёмный труд", "ИП", "Самозанятый", "Без работы"], n, p=[0.65, 0.12, 0.13, 0.10])

debt_to_income = loan_amount / (income * 12 + 1)

risk_score = (
    -0.00002 * income
    + 0.35 * existing_loans
    + 2.2 * debt_to_income
    - 0.05 * credit_history_years
    - 0.02 * experience
    + (employment == "Без работы") * 1.4
    + (employment == "Самозанятый") * 0.3
    + np.random.normal(0, 0.6, n)
)

prob_default = 1 / (1 + np.exp(-(risk_score - 1.2)))
default = (np.random.rand(n) < prob_default).astype(int)

df = pd.DataFrame({
    "age": age,
    "income": income.astype(int),
    "experience_years": experience,
    "credit_history_years": credit_history_years,
    "existing_loans": existing_loans,
    "loan_amount": loan_amount.astype(int),
    "region": region,
    "employment_type": employment,
    "default": default,
})

df.to_csv("credit_applications.csv", index=False, encoding="utf-8")
print(f"Строк: {len(df)}, доля дефолтов: {df['default'].mean():.1%}")
