import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train():
    df = pd.read_csv("poker_data.csv")

    X = df.drop(columns=["action", "won_hand"])
    y = df["action"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, predictions):.2%}")
    print(classification_report(y_test, predictions))

    joblib.dump(model, "poker_model.pkl")
    print("Model saved to poker_model.pkl")

if __name__ == "__main__":
    train()