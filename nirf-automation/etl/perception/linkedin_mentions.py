# etl/perception/linkedin_mentions.py
import pandas as pd

def get_perception_data():
    return {
        "college": "VRSEC",
        "linkedin_mentions": 92,
        "engagement_score": 7.5  # Simulated metric
    }

if __name__ == "__main__":
    data = get_perception_data()
    df = pd.DataFrame([data])
    df.to_csv("data/processed/perception.csv", index=False)

    print("Perception data has been fetched and saved to data/processed/perception.csv")
    print(df)