from pathlib import Path

import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def main() -> None:
    # Load the built-in California housing dataset so the project stays simple.
    print("Loading California housing dataset...")
    dataset = fetch_california_housing()
    X = dataset.data
    y = dataset.target

    print(f"Dataset shape: features={X.shape}, target={y.shape}")

    # A plain linear model keeps training fast and beginner friendly.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training LinearRegression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"Validation R^2 score: {score:.4f}")

    model_path = Path(__file__).with_name("model.pkl")
    joblib.dump(model, model_path)
    print(f"Saved trained model to {model_path}")


if __name__ == "__main__":
    main()

