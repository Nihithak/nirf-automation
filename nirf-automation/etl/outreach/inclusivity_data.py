# etl/outreach/inclusivity_data.py
import pandas as pd

def get_inclusivity_data():
    return {
        "college": "VRSEC",
        "male_percentage": 60,
        "female_percentage": 40,
        "gen_percentage": 50,
        "obc_percentage": 30,
        "sc_percentage": 15,
        "st_percentage": 5,
        "pwd_students": 12
    }

if __name__ == "__main__":
    data = get_inclusivity_data()
    df = pd.DataFrame([data])
    df.to_csv("data/processed/outreach.csv", index=False)
    print("Inclusivity data has been fetched and saved to data/processed/outreach.csv")
    print(df)