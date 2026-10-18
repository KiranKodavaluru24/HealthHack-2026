"""Rule-based medical-term simplifier + 'what it means for heart disease' notes. Just lookup tables.
Usage:  python simplify_terms.py tachycardia        (explain one term)
        python simplify_terms.py patient 1          (explain the medical findings in one patient's record)
NOTE: every sentence in CAD_MEANING is hand-written and must be reviewed by a clinician before any real-world use."""
import sys
from pathlib import Path

# 1) Exact terms we know well (checked first)
KNOWN = {
    "tachycardia": "fast heart rate", "bradycardia": "slow heart rate",
    "hypertension": "high blood pressure", "hypotension": "low blood pressure",
    "dyspnea": "shortness of breath", "edema": "swelling", "angina": "chest pain from the heart",
    "ischemia": "not enough blood flow", "arrhythmia": "irregular heartbeat",
    "dyslipidemia": "high fat levels in the blood", "hyperlipidemia": "high fat levels in the blood",
    "diabetes mellitus": "diabetes", "myocardial infarction": "heart attack",
    "cardiomyopathy": "disease of the heart muscle", "myocarditis": "inflammation of the heart muscle",
    "pericarditis": "inflammation of the sac around the heart",
    "heart failure": "heart not pumping well", "left ventricular hypertrophy": "thickened main pumping chamber of the heart",
    "regional wall motion abnormality": "part of the heart wall not moving normally",
    "st depression": "ST depression on the heart tracing", "st elevation": "ST elevation on the heart tracing",
    "t wave inversion": "flipped T wave on the heart tracing", "q wave": "Q wave on the heart tracing",
}

# 2) Word parts, used as a backup for terms not in KNOWN
PREFIX = {"hyper": "high", "hypo": "low", "brady": "slow", "tachy": "fast"}
ROOT = {"card": "heart", "neur": "nerve", "gastr": "stomach", "derm": "skin", "dermat": "skin", "myo": "muscle", "hepat": "liver",
        "nephr": "kidney", "pulmon": "lung", "angi": "blood vessel", "arter": "artery", "arthr": "joint", "oste": "bone"}
SUFFIX = {"itis": "inflammation of the {}", "ectomy": "surgical removal of the {}", "pathy": "disease of the {}",
          "algia": "pain in the {}", "megaly": "enlarged {}", "osis": "abnormal condition of the {}",
          "plasty": "surgical repair of the {}"}

def split_term(term):
    """Return (prefix, [roots], suffix), or None if the word can't be fully explained."""
    t = term.lower().strip()
    prefix = next((p for p in sorted(PREFIX, key=len, reverse=True) if t.startswith(p)), None)
    if prefix: t = t[len(prefix):]
    suffix = next((s for s in sorted(SUFFIX, key=len, reverse=True) if t.endswith(s)), None)
    if suffix: t = t[:-len(suffix)]
    roots, i = [], 0
    while i < len(t):                                   # read roots left to right, skipping joining vowels
        r = next((r for r in sorted(ROOT, key=len, reverse=True) if t.startswith(r, i)), None)
        if r: roots.append(r); i += len(r)
        elif t[i] in "aeiou": i += 1
        else: return None
    return (prefix, roots, suffix) if (prefix or roots or suffix) and roots else None

def simplify(term):
    """Return (plain wording, is_exact) or (None, False) if unknown."""
    key = term.lower().strip()
    if key in KNOWN: return KNOWN[key], True
    parts = split_term(key)
    if not parts: return None, False
    prefix, roots, suffix = parts
    what = " and ".join(ROOT[r] for r in roots)
    if suffix: text = SUFFIX[suffix].format(what)
    else: text = what
    if prefix: text = f"{PREFIX[prefix]} {text}" if not suffix else f"{text} (the '{prefix}' part means {PREFIX[prefix]})"
    return text, False

# 3) What each plain-English finding can mean for coronary artery disease (CAD)
CAD_MEANING = {
    "fast heart rate": "A fast heart rate makes the heart work harder and use more oxygen. If the heart's arteries are narrowed, it may not get enough blood to keep up.",
    "slow heart rate": "A slow heart rate can mean less blood is pumped around the body. It has many causes, and a doctor would check whether the heart's blood supply is one of them.",
    "high blood pressure": "High blood pressure strains the arteries and is one of the main things that speeds up fatty build-up in the arteries that feed the heart.",
    "low blood pressure": "Low blood pressure can mean less blood is reaching the body. With heart disease, it can be a sign the heart is not pumping well.",
    "shortness of breath": "Getting out of breath easily can be a sign the heart is not getting enough blood, especially during activity.",
    "swelling": "Swelling in the legs or ankles can happen when the heart is not pumping as well as it should.",
    "chest pain from the heart": "This is a classic warning sign that the heart is not getting enough blood, often because its arteries are narrowed.",
    "diabetes": "Diabetes raises the risk of narrowed heart arteries, because high blood sugar slowly damages blood vessels.",
    "high fat levels in the blood": "Too much fat in the blood can build up inside the heart's arteries and narrow them.",
    "heart not pumping well": "When narrowed arteries starve the heart of blood over time, the heart can become weaker and pump less well.",
    "thickened main pumping chamber of the heart": "The heart muscle can thicken when it works against high pressure for a long time. It often goes together with heart disease.",
    "part of the heart wall not moving normally": "A part of the heart that moves weakly can be a sign it is not getting enough blood.",
    "ST depression on the heart tracing": "This tracing pattern can mean part of the heart is not getting enough blood, though it has other causes too.",
    "ST elevation on the heart tracing": "A new ST elevation can be a sign of a heart attack and needs urgent medical care.",
    "flipped T wave on the heart tracing": "This tracing pattern can mean part of the heart is short of blood, but it also has other causes.",
    "heart attack": "A heart attack happens when a heart artery is suddenly blocked. It is the most serious result of narrowed heart arteries.",
    "disease of the heart muscle": "The heart muscle itself is diseased. It has many causes, including a long-term shortage of blood from narrowed arteries.",
    "irregular heartbeat": "An irregular heartbeat can happen when part of the heart is short of blood. It also has many other causes.",
    "not enough blood flow": "This is what happens in the heart when its arteries are narrowed. It is the central problem in coronary artery disease.",
    "Q wave on the heart tracing": "A Q wave can be a sign of an old heart attack or scarring of the heart muscle.",
}
FALLBACK = "We don't have a plain-English note for this finding. Ask a doctor how it relates to heart disease."

def explain(term):
    plain, exact = simplify(term)
    if plain is None:
        return f"'{term}': we don't recognise this term. Ask a doctor what it means."
    if exact and term.lower().strip() in plain.lower(): head = f"{plain[0].upper()}{plain[1:]}."
    elif exact: head = f"{term} means {plain}."
    else: head = f"{term} roughly means {plain} (best guess from the word parts)."
    return f"{head} {CAD_MEANING.get(plain, FALLBACK)}"

# 4) Link dataset columns to medical terms, so we can explain a patient's record
FINDINGS = {"HTN": "hypertension", "DM": "diabetes mellitus", "DLP": "dyslipidemia", "Dyspnea": "dyspnea",
            "Edema": "edema", "Typical Chest Pain": "angina", "CHF": "heart failure",
            "LVH": "left ventricular hypertrophy", "St Depression": "ST depression",
            "St Elevation": "ST elevation", "Tinversion": "T wave inversion", "Q Wave": "Q wave"}

def explain_patient(row):
    import pandas as pd
    df = pd.read_excel(next(Path("data").glob("*.xlsx")), sheet_name=0)
    p = df.iloc[row]
    present = [t for col, t in FINDINGS.items() if col in p and str(p[col]).strip() in ("Y", "1")]
    if str(p.get("Region RWMA", 0)) not in ("0", "0.0"): present.append("regional wall motion abnormality")
    print(f"Medical findings listed in patient {row}'s record, in plain English:\n")
    for t in present: print(f"- {explain(t)}\n")
    if not present: print("None of the findings we can explain were listed.")
    print("This is general information, not a diagnosis. A doctor can tell you what these mean for you.")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "patient": explain_patient(int(sys.argv[2]))
    else: print(explain(" ".join(sys.argv[1:]) or "tachycardia"))