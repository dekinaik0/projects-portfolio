import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

truth = pd.read_csv("reviews.csv")
pred = pd.read_csv("predictions.csv")

df = truth.merge(pred, on="id", suffixes=("_true", "_pred"))


def report(column):
    true_col = column + "_true"
    pred_col = column + "_pred"
    accuracy = (df[true_col] == df[pred_col]).mean()

    rows = []
    for label in sorted(df[true_col].unique()):
        tp = ((df[true_col] == label) & (df[pred_col] == label)).sum()
        fp = ((df[true_col] != label) & (df[pred_col] == label)).sum()
        fn = ((df[true_col] == label) & (df[pred_col] != label)).sum()
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        rows.append({
            "label": label,
            "support": tp + fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        })

    return accuracy, pd.DataFrame(rows)


def confusion(column, ax):
    true_col = column + "_true"
    pred_col = column + "_pred"
    labels = sorted(set(df[true_col]) | set(df[pred_col]))
    matrix = pd.DataFrame(0, index=labels, columns=labels)
    for t, p in zip(df[true_col], df[pred_col]):
        matrix.loc[t, p] += 1

    ax.imshow(matrix.values, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("предсказано")
    ax.set_ylabel("эталон")
    ax.set_title(column)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, matrix.values[i][j], ha="center", va="center")


fig, ax = plt.subplots(1, 2, figsize=(13, 5))

for column, axis in [("category", ax[0]), ("sentiment", ax[1])]:
    accuracy, table = report(column)
    print(f"=== {column} ===")
    print(f"accuracy: {accuracy:.3f}")
    print(table.to_string(index=False))
    print()
    confusion(column, axis)

errors = df[(df["category_true"] != df["category_pred"]) | (df["sentiment_true"] != df["sentiment_pred"])]
print(f"Ошибок: {len(errors)} из {len(df)}")
if len(errors):
    print(errors[["text", "category_true", "category_pred", "sentiment_true", "sentiment_pred"]].to_string(index=False))

errors.to_csv("errors.csv", index=False, encoding="utf-8")

plt.tight_layout()
plt.savefig("quality.png", dpi=120)
print("\nМатрицы ошибок сохранены в quality.png")
