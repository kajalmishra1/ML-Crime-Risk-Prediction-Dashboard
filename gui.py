import streamlit as st
import requests

st.set_page_config(page_title="Crime Prediction", layout="centered")

st.title("Crime Risk Prediction Dashboard")

# Fetch states
try:
    response = requests.get("http://127.0.0.1:5000/states")
    states = response.json()
except:
    st.error("Flask server is not running")
    st.stop()

# Dropdown
selected_state = st.selectbox("Select State", states)

# Button
if st.button("Predict"):
    url = f"http://127.0.0.1:5000/predict/{selected_state}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            st.success(f"Risk Level: {data['risk_level']}")

            st.subheader("Average Crime")
            st.write(data["average_crime"])

            st.subheader("Reason")
            st.write(data["reason"])

            st.subheader("Crime Breakdown")

            st.bar_chart(data["crime_breakdown"])

            for crime, value in data["crime_breakdown"].items():
                st.write(f"• {crime}: {value}")

            st.subheader("Recommendations")
            for rec in data["recommendations"]:
                st.write("•", rec)

    except:
        st.error("Error connecting to Flask server")