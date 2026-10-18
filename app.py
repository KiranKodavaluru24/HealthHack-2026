import streamlit as st
import pandas as pd
from pathlib import Path
import simplify_term  # Imports your backend file

st.set_page_config(page_title="SimplyStats - CAD Health Assistant", page_icon="🫀", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.2rem; }
    .subtitle { font-size: 1rem; color: #64748b; margin-bottom: 1.5rem; }
    .card { background-color: #ffffff; padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; margin-bottom: 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .disclaimer { background-color: #f1f5f9; padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.85rem; color: #475569; margin-bottom: 1.5rem; }
    .badge { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; background-color: #e0f2fe; color: #0369a1; border-radius: 50%; font-size: 0.8rem; font-weight: 700; margin-right: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-title">🫀 SimplyStats</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Check a record • How it works • All records</div>', unsafe_allow_html=True)
st.markdown('<div class="disclaimer">⚠️ Research demo. Not medical advice. Every explanation is designed to help patients understand medical terminology in plain English.</div>', unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    xlsx = next(Path("data").glob("*.xlsx"))
    return pd.read_excel(xlsx, sheet_name=0)

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset not found in 'data/' folder. Run connect_check.py first. Error: {e}")
    st.stop()

# Sidebar: Patient Selector
st.sidebar.header("🔍 Patient Record Selector")
cad_rows = df.index[df["Cath"].astype(str).str.strip() == "CAD"].tolist()
patient_choice = st.sidebar.selectbox("Select Confirmed CAD Patient #", range(1, len(cad_rows) + 1))

selected_row_idx = cad_rows[patient_choice - 1]
p = df.iloc[selected_row_idx]

st.sidebar.markdown(f"**Patient Index:** `{selected_row_idx}`")
st.sidebar.markdown(f"**Age:** {p.get('Age')} | **Sex:** {p.get('Sex')}")
st.sidebar.markdown(f"**Angiography Result:** 🔴 CAD Confirmed")

# Main Content Area: Translated Key Health Variables
st.subheader("Key Health Vitals & Lab Results (Plain English)")
st.markdown("<p style='color: #64748b; font-size: 0.95rem; margin-top: -0.5rem; margin-bottom: 1.5rem;'>Essential measurements and what they mean for heart health.</p>", unsafe_allow_html=True)

# Map dataset columns to user-friendly labels and values
key_metrics = [
    ("Heart Rate (Pulse)", p.get("PR"), "Measures how fast your heart beats. A normal resting heart rate is typically between 60 and 100 beats per minute."),
    ("Blood Pressure", p.get("BP"), simplify_term.CAD_MEANING.get("high blood pressure")),
    ("Body Mass Index (BMI)", f"{p.get('BMI', 0):.1f}" if pd.notnull(p.get('BMI')) else "N/A", simplify_term.CAD_MEANING.get("body mass index")),
    ("Fasting Blood Sugar", f"{p.get('FBS')} mg/dL" if pd.notnull(p.get('FBS')) else "N/A", simplify_term.CAD_MEANING.get("fasting blood sugar")),
    ("LDL Cholesterol (Bad)", f"{p.get('LDL')} mg/dL" if pd.notnull(p.get('LDL')) else "N/A", simplify_term.CAD_MEANING.get("bad cholesterol")),
    ("HDL Cholesterol (Good)", f"{p.get('HDL')} mg/dL" if pd.notnull(p.get('HDL')) else "N/A", simplify_term.CAD_MEANING.get("good cholesterol")),
]

for idx, (label, val, explanation) in enumerate(key_metrics, 1):
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; align-items: center; margin-bottom: 0.4rem;">
            <span class="badge">{idx}</span>
            <span style="font-size: 0.85rem; color: #64748b;">Metric: <b>{label}</b></span>
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-top: 0.2rem;">Value: {val}</div>
        <p style="color: #334155; font-size: 0.95rem; margin-top: 0.4rem; margin-bottom: 0; line-height: 1.5;">{explanation}</p>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area: Clinical Findings Cards
st.markdown("---")
st.subheader("Clinical Findings, Explained")

FINDINGS = {
    "HTN": "hypertension", "DM": "diabetes mellitus", "DLP": "dyslipidemia", "Dyspnea": "dyspnea",
    "Edema": "edema", "Typical Chest Pain": "angina", "CHF": "heart failure",
    "LVH": "left ventricular hypertrophy", "St Depression": "ST depression",
    "St Elevation": "ST elevation", "Tinversion": "T wave inversion", "Q Wave": "Q wave"
}

present = [t for col, t in FINDINGS.items() if col in p and str(p[col]).strip() in ("Y", "1")]
if str(p.get("Region RWMA", 0)) not in ("0", "0.0"): 
    present.append("regional wall motion abnormality")

if present:
    for idx, t in enumerate(present, 1):
        plain, exact = simplify_term.simplify(t)
        cad_note = simplify_term.CAD_MEANING.get(plain, simplify_term.FALLBACK)
        
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; margin-bottom: 0.4rem;">
                <span class="badge" style="background-color: #fee2e2; color: #991b1b;">{idx}</span>
                <span style="font-size: 0.85rem; color: #64748b;">Doctor's word: <b>{t}</b></span>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 0.2rem;">{plain.capitalize()}</div>
            <p style="color: #334155; font-size: 0.95rem; margin-top: 0.4rem; margin-bottom: 0; line-height: 1.5;">{cad_note}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("None of the trackable clinical findings were listed as positive for this patient record.")