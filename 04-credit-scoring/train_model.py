import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from catboost import CatBoostClassifier, Pool

df = pd.read_csv("credit_applications.csv")

target = "default"
cat_features = ["region", "employment_type"]
features = [c for c in df.columns if c != target]

X_train, X_test, y_train, y_test = train_test_split(
    df[features], df[target], test_size=0.25, random_state=42, stratify=df[target]
)

train_pool = Pool(X_train, y_train, cat_features=cat_features)
test_pool = Pool(X_test, y_test, cat_features=cat_features)

model = CatBoostClassifier(
    iterations=300,
    depth=4,
    learning_rate=0.05,
    loss_function="Logloss",
    eval_metric="AUC",
    class_weights=[1, (y_train == 0).sum() / (y_train == 1).sum()],
    random_seed=42,
    verbose=False,
)
model.fit(train_pool, eval_set=test_pool)

proba = model.predict_proba(test_pool)[:, 1]
pred = (proba >= 0.5).astype(int)

baseline = LogisticRegression(max_iter=1000)
X_train_num = X_train.drop(columns=cat_features)
X_test_num = X_test.drop(columns=cat_features)
baseline.fit(X_train_num, y_train)
baseline_proba = baseline.predict_proba(X_test_num)[:, 1]

print("=== CatBoost ===")
print(f"ROC-AUC:   {roc_auc_score(y_test, proba):.3f}")
print(f"Precision: {precision_score(y_test, pred):.3f}")
print(f"Recall:    {recall_score(y_test, pred):.3f}")
print(f"F1:        {f1_score(y_test, pred):.3f}")

print()
print("=== Логистическая регрессия (baseline) ===")
print(f"ROC-AUC:   {roc_auc_score(y_test, baseline_proba):.3f}")

print()
print("=== Важность признаков (CatBoost) ===")
importance = pd.Series(model.get_feature_importance(train_pool), index=features)
print(importance.sort_values(ascending=False).round(1).to_string())

test_result = X_test.copy()
test_result["default_true"] = y_test.values
test_result["default_proba"] = proba.round(3)
test_result.to_csv("predictions.csv", index=False, encoding="utf-8")

model.save_model("model.cbm")
print()
print("Предсказания сохранены в predictions.csv, модель — в model.cbm")
