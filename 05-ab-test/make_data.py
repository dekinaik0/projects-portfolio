import numpy as np
import pandas as pd

np.random.seed(7)

n_control = 5200
n_test = 5150

control = np.random.binomial(1, 0.084, n_control)
test = np.random.binomial(1, 0.101, n_test)

df = pd.DataFrame({
    "user_id": range(1, n_control + n_test + 1),
    "group": ["control"] * n_control + ["test"] * n_test,
    "converted": np.concatenate([control, test]),
})
df = df.sample(frac=1, random_state=1).reset_index(drop=True)
df.to_csv("ab_test_data.csv", index=False, encoding="utf-8")

print(f"Строк: {len(df)}")
print(df.groupby("group")["converted"].agg(["count", "mean"]).round(4))
