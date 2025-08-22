# core/calculator.py

import pandas as pd
import yaml
import os

def load_weights():
    with open("core/weights.yaml") as f:
        return yaml.safe_load(f)

def calculate_individual_scores():
    base_path = "data/processed"

    # Load and calculate TLR Score
    teaching_df = pd.read_csv(os.path.join(base_path, "teaching.csv"))
    tlr_score = (
        (teaching_df["faculty_count"][0] * 0.3) +
        (teaching_df["phd_count"][0] * 0.5) +
        (teaching_df["student_count"][0] * 0.2)
    ) / 100  # Normalize

    # Load and calculate RP Score
    research_df = pd.read_csv(os.path.join(base_path, "research.csv"))
    rp_score = (
        (research_df["publications"][0] * 0.4) +
        (research_df["citations"][0] * 0.4) +
        (research_df["patents"][0] * 0.2)
    ) / 100

    # Load and calculate GO Score
    outcomes_df = pd.read_csv(os.path.join(base_path, "outcomes.csv"))
    go_score = (
        (outcomes_df["median_salary_lpa"][0] * 0.5) +
        (outcomes_df["students_placed"][0] * 0.3) +
        (outcomes_df["higher_studies"][0] * 0.2)
    ) / 10  # Normalized

    # Load and calculate OI Score
    outreach_df = pd.read_csv(os.path.join(base_path, "outreach.csv"))
    oi_score = (
        (outreach_df["female_percentage"][0] * 0.4) +
        (outreach_df["obc_percentage"][0] * 0.3) +
        (outreach_df["sc_percentage"][0] * 0.2) +
        (outreach_df["pwd_students"][0] * 0.1)
    )

    # Load and calculate PR Score
    perception_df = pd.read_csv(os.path.join(base_path, "perception.csv"))
    pr_score = (
        (perception_df["linkedin_mentions"][0] * 0.7) +
        (perception_df["engagement_score"][0] * 0.3)
    )

    return {
        "TLR": tlr_score,
        "RP": rp_score,
        "GO": go_score,
        "OI": oi_score,
        "PR": pr_score
    }

def calculate_total_score(scores, weights):
    total = 0
    for key in scores:
        total += scores[key] * weights[key]
    return total / 100

if __name__ == "__main__":
    weights = load_weights()
    scores = calculate_individual_scores()
    final_score = calculate_total_score(scores, weights)

    print("🎯 Individual Category Scores:")
    for k, v in scores.items():
        print(f"{k}: {v:.2f}")

    print(f"\n✅ Final NIRF Score: {final_score:.2f}")

    # Save to CSV for dashboard
    output = scores.copy()
    output["Total"] = final_score

    # ✅ Save to data/warehouse/nirf_scores.csv
    os.makedirs("data/warehouse", exist_ok=True)
    pd.DataFrame([output]).to_csv("data/warehouse/nirf_scores.csv", index=False)
    print("📁 nirf_scores.csv saved to data/warehouse/")
