# etl/teaching/faculty_fetch.py
import pandas as pd
import os

def get_faculty_data():
    data = {
        "college": "VRSEC",
        "faculty_count": 180,
        "phd_count": 140,
        "student_count": 3200
    }
    # Ensure the directory exists
    os.makedirs("data/processed", exist_ok=True)
    pd.DataFrame([data]).to_csv("data/processed/teaching.csv", index=False)
    return data

if __name__ == "__main__":
    get_faculty_data()
