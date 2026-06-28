from flask import Flask, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Load model and dataset
model = pickle.load(open("model.pkl", "rb"))
df = pd.read_csv("final_data.csv")

# -------------------- PREDICTION ROUTE --------------------
@app.route("/predict/<state>", methods=["GET"])
def predict_by_state(state):
    try:
        # Normalize input
        state = state.strip().lower()

        # Filter dataset
        state_data = df[df["state"].str.lower() == state]

        if state_data.empty:
            return jsonify({"error": "State not found"})

        # Aggregate values
        avg_crime = int(state_data["total_crime"].mean())
        ipc = avg_crime
        women = int(state_data["women_ratio"].mean() * avg_crime)
        children = int(state_data["children_ratio"].mean() * avg_crime)

        # Latest row safely
        latest = state_data.sort_values("year").iloc[-1]

        # Prepare features
        features = pd.DataFrame([{
            "total_crime": latest["total_crime"],
            "crime_per_police": latest["crime_per_police"],
            "arrest_rate": latest["arrest_rate"],
            "crime_growth": latest["crime_growth"],
            "women_ratio": latest["women_ratio"],
            "children_ratio": latest["children_ratio"],
            "year": latest["year"]
        }])

        # Prediction
        prediction = model.predict(features)[0]

        # Reason mapping
        reason_map = {
            "High": "High crime risk due to consistently high crime levels and moderate enforcement.",
            "Medium": "Moderate crime risk with fluctuating trends and average enforcement.",
            "Low": "Low crime risk due to controlled crime levels and effective enforcement."
        }

        # Recommendation mapping
        recommendation_map = {
            "High": [
                "Increase police deployment",
                "Install CCTV and smart surveillance",
                "Strengthen law enforcement"
            ],
            "Medium": [
                "Improve response time",
                "Monitor sensitive areas",
                "Increase awareness programs"
            ],
            "Low": [
                "Maintain current strategies",
                "Monitor trends",
                "Encourage community participation"
            ]
        }

        return jsonify({
            "state": state.upper(),
            "average_crime": avg_crime,
            "risk_level": prediction,
            "reason": reason_map.get(prediction, ""),
            "crime_breakdown": {
                "IPC Crimes": ipc,
                "Women-related Crimes": women,
                "Children-related Crimes": children
            },
            "recommendations": recommendation_map.get(prediction, [])
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------- STATES ROUTE (FOR DROPDOWN) --------------------
@app.route("/states", methods=["GET"])
def get_states():
    states = sorted(df["state"].unique())
    return jsonify(states)


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    app.run(debug=True)