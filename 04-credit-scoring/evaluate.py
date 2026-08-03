import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from catboost import CatBoostClassifier, Pool

df = pd.read_csv("credit_applications.csv")
pred = pd.read_csv("predictions.csv")

cat_features = ["region", "employment_type"]
features = [c for c in df.columns if c != "default"]

model = CatBoostClassifier()
model.load_model("model.cbm")

importance = pd.Series(
    model.get_feature_importance(Pool(df[features], df["default"], cat_features=cat_features)),
    index=features,
).sort_values()

fpr, tpr, _ = roc_curve(pred["default_true"], pred["default_proba"])
auc = roc_auc_score(pred["default_true"], pred["default_proba"])

cm = confusion_matrix(pred["default_true"], (pred["default_proba"] >= 0.5).astype(int))

fig, ax = plt.subplots(2, 2, figsize=(13, 10))

ax[0][0].barh(importance.index, importance.values, color="#4c72b0")
ax[0][0].set_title("Важность признаков")

ax[0][1].plot(fpr, tpr, color="#c44e52", label=f"CatBoost (AUC = {auc:.3f})")
ax[0][1].plot([0, 1], [0, 1], "--", color="grey", label="Случайное угадывание")
ax[0][1].set_xlabel("False Positive Rate")
ax[0][1].set_ylabel("True Positive Rate")
ax[0][1].set_title("ROC-кривая")
ax[0][1].legend()

ax[1][0].hist(pred[pred["default_true"] == 0]["default_proba"], bins=30, alpha=0.6, label="Не дефолт", color="#55a868")
ax[1][0].hist(pred[pred["default_true"] == 1]["default_proba"], bins=30, alpha=0.6, label="Дефолт", color="#c44e52")
ax[1][0].set_title("Распределение предсказанной вероятности")
ax[1][0].set_xlabel("Вероятность дефолта")
ax[1][0].legend()

im = ax[1][1].imshow(cm, cmap="Blues")
ax[1][1].set_xticks([0, 1], ["Не дефолт", "Дефолт"])
ax[1][1].set_yticks([0, 1], ["Не дефолт", "Дефолт"])
ax[1][1].set_xlabel("предсказано")
ax[1][1].set_ylabel("факт")
ax[1][1].set_title("Матрица ошибок (порог 0.5)")
for i in range(2):
    for j in range(2):
        ax[1][1].text(j, i, cm[i][j], ha="center", va="center")

plt.tight_layout()
plt.savefig("quality.png", dpi=120)
print("Графики сохранены в quality.png")
