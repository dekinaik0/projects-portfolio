import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_predict

df = pd.read_csv("reviews.csv")

result = pd.DataFrame({"id": df["id"]})

for target in ["category", "sentiment"]:
    features = make_union(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)),
        TfidfVectorizer(ngram_range=(1, 2)),
    )
    model = make_pipeline(features, LinearSVC(C=1))
    predictions = cross_val_predict(model, df["text"], df[target], cv=5)
    result[target] = predictions
    print(f"{target}: accuracy {(predictions == df[target]).mean():.3f}")

result.to_csv("predictions.csv", index=False, encoding="utf-8")
print("Предсказания сохранены в predictions.csv")
