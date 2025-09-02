import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from app.utils_text import normalize

here = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(here, ".."))

def load_data():
    path = os.path.join(root, "data", "samples.csv")
    df = pd.read_csv(path)
    return df

def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=normalize, ngram_range=(1,2), min_df=1)),
        ("clf", LogisticRegression(max_iter=200))
    ])

def main():
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"])
    pipe = build_pipeline()
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))
    os.makedirs(os.path.join(root, "app", "model"), exist_ok=True)
    joblib.dump(pipe, os.path.join(root, "app", "model", "pipeline.joblib"))
    print("Model saved to app/model/pipeline.joblib")

if __name__ == "__main__":
    main()
