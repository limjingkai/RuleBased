# app.py
import json
from typing import List, Dict, Any, Tuple
import operator
import streamlit as st

# ----------------------------
# 1) Minimal rule engine
# ----------------------------
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
}

# ----------------------------
# Load rules from JSON file
# ----------------------------
RULES_FILE = "ac_rules.json"  # Save your JSON content into this file

try:
    with open(RULES_FILE, "r") as f:
        DEFAULT_RULES: List[Dict[str, Any]] = json.load(f)
except Exception as e:
    st.error(f"Failed to load rules from {RULES_FILE}. Using empty rules. Details: {e}")
    DEFAULT_RULES = []

def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    """Evaluate a single condition: [field, op, value]."""
    if len(cond) != 3:
        return False
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    try:
        return OPS[op](facts[field], value)
    except Exception:
        return False

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """All conditions must be true (AND)."""
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Returns (best_action, fired_rules)
    - best_action: chosen by highest priority among fired rules (ties keep the first encountered)
    - fired_rules: list of rule dicts that matched
    """
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return ({"ac_mode": "OFF", "fan_speed": "LOW", "setpoint": None, "reason": "No rule matched"}, [])

    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    best = fired_sorted[0].get("action", {"ac_mode": "OFF", "fan_speed": "LOW", "setpoint": None, "reason": "No action"})
    return best, fired_sorted

# ----------------------------
# 2) Streamlit UI
# ----------------------------
st.set_page_config(page_title="Rule-Based AC Controller", page_icon="", layout="wide")
st.title("Rule-Based Smart Home AC Controller")
st.caption("Enter home conditions, edit rules (optional), and evaluate the AC settings.")

with st.sidebar:
    st.header("Home Facts")
    temperature = st.number_input("Temperature (°C)", min_value=10, max_value=40, step=1, value=22)
    humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, step=1, value=46)
    occupancy = st.selectbox("Occupancy", options=["OCCUPIED", "EMPTY"], index=0)
    time_of_day = st.selectbox("Time of day", options=["MORNING", "AFTERNOON", "EVENING", "NIGHT"], index=3)
    windows_open = st.checkbox("Windows open?", value=False)

    st.divider()
    st.header("Rules (JSON)")
    st.caption("You can keep the defaults or paste your own JSON array of rules.")
    default_json = json.dumps(DEFAULT_RULES, indent=2)
    rules_text = st.text_area("Edit rules here", value=default_json, height=400)

    run = st.button("Evaluate", type="primary")

facts = {
    "temperature": float(temperature),
    "humidity": float(humidity),
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open,
}

st.subheader("Home Facts")
st.json(facts)

# Parse rules (fall back to defaults if invalid)
try:
    rules = json.loads(rules_text)
    assert isinstance(rules, list), "Rules must be a JSON array"
except Exception as e:
    st.error(f"Invalid rules JSON. Using defaults. Details: {e}")
    rules = DEFAULT_RULES

st.subheader("Active Rules")
with st.expander("Show rules", expanded=False):
    st.code(json.dumps(rules, indent=2), language="json")

st.divider()

if run:
    action, fired = run_rules(facts, rules)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("AC Decision")
        mode = action.get("ac_mode", "OFF")
        fan = action.get("fan_speed", "LOW")
        setpoint = action.get("setpoint", "-")
        reason = action.get("reason", "-")
        st.info(f"AC Mode: {mode}\nFan Speed: {fan}\nSetpoint: {setpoint}\nReason: {reason}")

    with col2:
        st.subheader("Matched Rules (by priority)")
        if not fired:
            st.info("No rules matched.")
        else:
            for i, r in enumerate(fired, start=1):
                st.write(f"**{i}. {r.get('name','(unnamed)')}** | priority={r.get('priority',0)}")
                st.caption(f"Action: {r.get('action',{})}")
                with st.expander("Conditions"):
                    for cond in r.get("conditions", []):
                        st.code(str(cond))

else:
    st.info("Set input values and click **Evaluate**.")
