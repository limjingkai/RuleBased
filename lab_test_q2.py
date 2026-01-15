import streamlit as st

st.title("Smart Home Air Conditioner Controller")

temperature = 22
humidity = 46
occupancy = "OCCUPIED"
time_of_day = "NIGHT"
windows_open = False

def apply_rules():
    if windows_open:
        return "OFF", "LOW", "-", "Windows are open"
    if temperature <= 22:
        return "OFF", "LOW", "-", "Already cold"
    if occupancy == "EMPTY" and temperature >= 24:
        return "ECO", "LOW", "27°C", "Home empty; save energy"
    if occupancy == "OCCUPIED" and time_of_day == "NIGHT" and temperature >= 26:
        return "SLEEP", "LOW", "26°C", "Night comfort"
    if occupancy == "OCCUPIED" and temperature >= 30 and humidity >= 70:
        return "COOL", "HIGH", "23°C", "Hot and humid"
    if occupancy == "OCCUPIED" and temperature >= 28:
        return "COOL", "MEDIUM", "24°C", "Temperature high"
    if occupancy == "OCCUPIED" and 26 <= temperature < 28:
        return "COOL", "LOW", "25°C", "Slightly warm"
    return "OFF", "LOW", "-", "No rule matched"

mode, fan, setpoint, reason = apply_rules()

st.write("AC Mode:", mode)
st.write("Fan Speed:", fan)
st.write("Setpoint:", setpoint)
st.write("Reason:", reason)
