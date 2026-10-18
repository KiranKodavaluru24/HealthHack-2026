from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, recall_score, confusion_matrix

# 1. Load the data (unzipped by connect_check.py into ./data)
xlsx = next(Path("data").glob("*.xlsx"))
df = pd.read_excel(xlsx, sheet_name=0)
print(f"Loaded {df.shape[0]} patients from {xlsx.name}")

# 2. Target: 1 = CAD, 0 = Normal
y = (df["Cath"].astype(str).str.strip() == "CAD").astype(int)

# 3. Features: drop the angiography results that define the answer (would be cheating)
X = df.drop(columns=["LAD", "LCX", "RCA", "Cath"])
text_cols = [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]
num_cols = [c for c in X.columns if c not in text_cols]

def make_model():
    prep = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), text_cols),
    ])
    return Pipeline([("prep", prep),
                     ("clf", LogisticRegression(max_iter=5000, C=0.3, class_weight="balanced"))])

# 4. Honest accuracy: 5-fold cross-validation
cv = StratifiedKFold(5, shuffle=True, random_state=42)
acc = cross_val_score(make_model(), X, y, cv=cv, scoring="accuracy")
auc = cross_val_score(make_model(), X, y, cv=cv, scoring="roc_auc")
print(f"\n5-fold cross-validation: accuracy {acc.mean():.1%}, AUC {auc.mean():.2f}")

# 5. Hold out 25% of patients the model never sees
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=7)
model = make_model().fit(X_tr, y_tr)
prob = model.predict_proba(X_te)[:, 1]
pred = (prob >= 0.5).astype(int)
print(f"\nHeld-out test ({len(y_te)} patients):")
print(f"  accuracy    {accuracy_score(y_te, pred):.1%}")
print(f"  AUC         {roc_auc_score(y_te, prob):.2f}")
print(f"  sensitivity {recall_score(y_te, pred):.1%}  (CAD patients caught)")
print(f"  specificity {recall_score(y_te, pred, pos_label=0):.1%}  (normal patients cleared)")
print("  confusion matrix [[TN FP] [FN TP]]:\n", confusion_matrix(y_te, pred))

# 6. Example predictions on 8 unseen patients
demo = pd.DataFrame({"Age": X_te["Age"].values, "Sex": X_te["Sex"].values,
                     "prob_CAD": prob.round(2),
                     "predicted": ["CAD" if p else "Normal" for p in pred],
                     "actual": ["CAD" if a else "Normal" for a in y_te]}).head(8)
print("\nExample unseen patients:\n", demo.to_string(index=False))

# 7. Save a final model trained on all patients
final = make_model().fit(X, y)
joblib.dump({"model": final, "columns": list(X.columns)}, "cad_model.joblib")
print("\nSaved cad_model.joblib")