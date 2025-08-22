# etl/outcomes/placement_data.py
import pandas as pd

def get_placement_data():
    return {
        "college": "VRSEC",
        "median_salary_lpa": 4.2,
        "students_placed": 380,
        "higher_studies": 45
    }

if __name__ == "__main__":
    data = get_placement_data()
    df = pd.DataFrame([data])
    df.to_csv("data/processed/outcomes.csv", index=False)
    print("Placement data has been fetched and saved to data/processed/outcomes.csv")
    print(df)