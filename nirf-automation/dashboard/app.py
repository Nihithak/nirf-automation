from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import sys

# Resolve project base directory regardless of current working directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


# Storage for raw inputs used to compute percentile-based metrics
INPUTS_STORE = os.path.join(BASE_DIR, "data", "warehouse", "inputs.json")
SCORES_CSV = os.path.join(BASE_DIR, "data", "warehouse", "nirf_scores.csv")
RESULTS_CSV = os.path.join(BASE_DIR, "data", "warehouse", "results_summary.csv")
HISTORY_JSON = os.path.join(BASE_DIR, "data", "warehouse", "history.json")


def ensure_dirs():
    os.makedirs(os.path.dirname(SCORES_CSV), exist_ok=True)


def load_inputs() -> List[Dict[str, Any]]:
    if os.path.exists(INPUTS_STORE):
        try:
            with open(INPUTS_STORE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_inputs(records: List[Dict[str, Any]]):
    ensure_dirs()
    with open(INPUTS_STORE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def append_history(entry: Dict[str, Any]):
    ensure_dirs()
    history: List[Dict[str, Any]] = []
    if os.path.exists(HISTORY_JSON):
        try:
            with open(HISTORY_JSON, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(entry)
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def percentile(values: List[float], target: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    # Percentile rank: percentage of values <= target
    count_le = sum(1 for v in sorted_vals if v <= target)
    return (count_le / len(sorted_vals)) * 100.0


def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        return float(val)
    except Exception:
        return default


def compute_scores(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Precompute vectors needed for percentiles
    # Publication composite P and citations composite CC
    P_list: List[float] = []
    CC_over_F_list: List[float] = []
    PF_over_F_list: List[float] = []
    PG_over_F_list: List[float] = []
    EP_over_F_list: List[float] = []
    EXLI_per_student_list: List[float] = []
    EXLB_per_student_list: List[float] = []
    PE_index_list: List[float] = []
    CES_N_list: List[float] = []
    RD_other_states_list: List[float] = []
    RD_other_countries_list: List[float] = []
    PR_SR_ratio_list: List[float] = []

    computed_internals: List[Dict[str, float]] = []

    for r in records:
        F1 = safe_float(r.get("F1"))
        F2 = safe_float(r.get("F2"))
        F_total = F1 + 0.3 * F2
        seats_N = safe_float(r.get("seats_N"))

        PW = safe_float(r.get("PW"))
        PS = safe_float(r.get("PS"))
        PG = safe_float(r.get("PG"))
        PI = safe_float(r.get("PI"))
        P = 0.3 * PW + 0.5 * PS + 0.1 * PG + 0.1 * PI

        CCW = safe_float(r.get("CCW"))
        CCS = safe_float(r.get("CCS"))
        CCG = safe_float(r.get("CCG"))
        CCI = safe_float(r.get("CCI"))
        CC = 0.3 * CCW + 0.5 * CCS + 0.1 * CCG + 0.1 * CCI

        PF = safe_float(r.get("PF_filed"))
        PG_granted = safe_float(r.get("PG_granted"))
        EP = safe_float(r.get("EP_revenue"))

        EXLIP = safe_float(r.get("EXLIP"))
        EXLIE = safe_float(r.get("EXLIE"))
        EXLB = safe_float(r.get("EXLB"))

        EXLI_per_student = 0.0
        EXLB_per_student = 0.0
        if seats_N > 0:
            EXLI_per_student = (EXLIP / seats_N) + (2.0 * EXLIE / seats_N)
            EXLB_per_student = EXLB  # EXLB is already per student if provided; else it will be percentile against totals

        pe_index = safe_float(r.get("PE_index"))
        CES_N = safe_float(r.get("CES_N"))
        RD_other_states = safe_float(r.get("RD_other_states"))
        RD_other_countries = safe_float(r.get("RD_other_countries"))

        A_apps = safe_float(r.get("applications_A"))
        S_intake = safe_float(r.get("sanctioned_S"))
        SR_ratio = (A_apps / S_intake) if S_intake > 0 else 0.0

        P_list.append(P / (F_total if F_total > 0 else 1.0))
        CC_over_F_list.append((CC / (P if P > 0 else 1.0)))
        PF_over_F_list.append(PF / (F_total if F_total > 0 else 1.0))
        PG_over_F_list.append(PG_granted / (F_total if F_total > 0 else 1.0))
        EP_over_F_list.append(EP / (F_total if F_total > 0 else 1.0))
        EXLI_per_student_list.append(EXLI_per_student)
        EXLB_per_student_list.append(EXLB_per_student)
        PE_index_list.append(pe_index)
        CES_N_list.append(CES_N)
        RD_other_states_list.append(RD_other_states)
        RD_other_countries_list.append(RD_other_countries)
        PR_SR_ratio_list.append(SR_ratio)

        computed_internals.append({
            "F_total": F_total,
            "P": P,
            "CC": CC,
            "EXLI_per_student": EXLI_per_student,
            "EXLB_per_student": EXLB_per_student,
            "SR_ratio": SR_ratio
        })

    # Compute global anchors
    R_star = max(PR_SR_ratio_list) if PR_SR_ratio_list else 1.0

    results: List[Dict[str, Any]] = []
    for idx, r in enumerate(records):
        internals = computed_internals[idx]
        F_total = internals["F_total"]
        seats_N = safe_float(r.get("seats_N"))
        inst_type = (r.get("institution_type") or "college").lower()

        # 1. TLR
        # (a) FSR
        F_over_N = (F_total / seats_N) if seats_N > 0 else 0.0
        if inst_type == "university":
            FSR = 20.0 * (15.0 * F_over_N)
        else:
            FSR = 30.0 * (20.0 * F_over_N)
        if F_over_N < (1.0 / 50.0):
            FSR = 0.0

        # (b) FQE = FQ + FE
        phd_percent = safe_float(r.get("phd_percent"))  # percentage of faculty with PhD
        FQ = 15.0 * (phd_percent / 95.0) if phd_percent <= 95.0 else 15.0
        avg_exp = safe_float(r.get("avg_experience_years"))
        Ei = 0.0
        if avg_exp <= 45.0:
            Ei = max(avg_exp - 30.0, 0.0)
        else:
            Ei = 15.0
        E = Ei  # using average directly per definition
        FE = 15.0 * (E / 15.0) if E <= 15.0 else 15.0
        FQE = FQ + FE

        # (c) Library & Lab
        EXLI_ps = internals["EXLI_per_student"]
        EXLB_ps = internals["EXLB_per_student"]
        p_EXLI = percentile(EXLI_per_student_list, EXLI_ps)
        p_EXLB = percentile(EXLB_per_student_list, EXLB_ps)
        if inst_type == "university":
            LI = 20.0 * p_EXLI / 100.0
            LB = 20.0 * p_EXLB / 100.0
        else:
            LI = 15.0 * p_EXLI / 100.0
            LB = 15.0 * p_EXLB / 100.0
        LL = LI + LB

        # (d) SEC
        pA = safe_float(r.get("SEC_pA_percentile")) / 100.0
        pB = safe_float(r.get("SEC_pB_percentile")) / 100.0
        winners = safe_float(r.get("SEC_winners_count"))
        pC_val = 1.0 if winners >= 3 else (safe_float(r.get("SEC_pC_percentile")) / 100.0)
        SEC = 10.0 * (pA / 2.0 + pB / 4.0 + pC_val / 4.0)

        TLR = FSR + FQE + LL + SEC

        # 2. RPII
        # (a) Publications
        P_over_F = internals["P"] / (F_total if F_total > 0 else 1.0)
        p_pub = percentile(P_list, P_over_F)
        PU = 45.0 * (p_pub / 100.0)

        # (b) Citations
        CC = internals["CC"]
        P_val = internals["P"]
        # Percentile of publication intensity P/F across all institutions
        p_P = percentile(P_list, P_over_F)
        base_citation_index = (CC / (P_val if P_val > 0 else 1.0)) * (p_P / 100.0)
        p_citation = percentile(CC_over_F_list, base_citation_index)
        CI = 45.0 * (p_citation / 100.0)

        # (c) IPR
        PF_val = safe_float(r.get("PF_filed"))
        PG_granted_val = safe_float(r.get("PG_granted"))
        EP_val = safe_float(r.get("EP_revenue"))
        PF_comp = 2.0 * (percentile(PF_over_F_list, PF_val / (F_total if F_total > 0 else 1.0)) / 100.0)
        PG_comp = 4.0 * (percentile(PG_over_F_list, PG_granted_val / (F_total if F_total > 0 else 1.0)) / 100.0)
        I_P = 1.0 if PG_granted_val >= 1 and safe_float(r.get("PL_licensed_count")) >= 1 else 0.0
        PL_comp = 2.0 * I_P + 2.0 * (percentile(EP_over_F_list, EP_val / (F_total if F_total > 0 else 1.0)) / 100.0)
        IPR = PF_comp + PG_comp + PL_comp

        RPII = PU + CI + IPR

        # 3. GO
        UE_percent = safe_float(r.get("UE_graduating_percent"))
        UE = 50.0 * (UE_percent / 80.0)
        pe_index = safe_float(r.get("PE_index"))
        p_pe = percentile(PE_index_list, pe_index)
        PE = 50.0 * (p_pe / 100.0)
        GO = UE + PE

        # 4. OI
        CES_base = safe_float(r.get("CES_N"))
        CES_score = 25.0 * (percentile(CES_N_list, CES_base) / 100.0)
        RD_states = 18.0 * (percentile(RD_other_states_list, safe_float(r.get("RD_other_states"))) / 100.0)
        RD_countries = 7.0 * (percentile(RD_other_countries_list, safe_float(r.get("RD_other_countries"))) / 100.0)
        RD_score = RD_states + RD_countries
        N1 = safe_float(r.get("WS_women_students_percent"))
        N2 = safe_float(r.get("WS_women_faculty_percent"))
        N3 = safe_float(r.get("WS_women_leadership_percent"))
        WS = 8.0 * (N1 / 50.0) + 8.0 * (N2 / 20.0) + 4.0 * (N3 / 2.0)
        ESCS_N = safe_float(r.get("ESCS_disadvantaged_percent"))
        ESCS = 20.0 * (ESCS_N / 50.0)
        DAP = (
            (2.0 if r.get("DAP_ramps") else 0.0) +
            (2.0 if r.get("DAP_lifts") else 0.0) +
            (2.0 if r.get("DAP_walking_aids") else 0.0) +
            (1.5 if r.get("DAP_toilets") else 0.0) +
            (1.0 if r.get("DAP_braille_labs") else 0.0) +
            (1.5 if r.get("DAP_av_aids") else 0.0)
        )
        OI = CES_score + RD_score + WS + ESCS + DAP

        # 5. PR
        PR_survey = safe_float(r.get("PR_survey"))  # out of 50
        SR_ratio = internals["SR_ratio"]
        SR = 50.0 * ((SR_ratio / R_star) if R_star > 0 else 0.0)
        PR = PR_survey + SR

        # Total using weights.yaml
        try:
            weights = {
                "TLR": 30.0,
                "RP": 30.0,
                "GO": 20.0,
                "OI": 10.0,
                "PR": 10.0,
            }
            weights_path = os.path.join(BASE_DIR, "core", "weights.yaml")
            if os.path.exists(weights_path):
                import yaml  # type: ignore
                with open(weights_path, "r", encoding="utf-8") as f:
                    weights = yaml.safe_load(f)
        except Exception:
            weights = {"TLR": 30.0, "RP": 30.0, "GO": 20.0, "OI": 10.0, "PR": 10.0}

        total_score = (
            (TLR * weights["TLR"]) +
            (RPII * weights.get("RP", weights.get("RPII", 30.0))) +
            (GO * weights["GO"]) +
            (OI * weights["OI"]) +
            (PR * weights["PR"]) 
        ) / 100.0

        results.append({
            "college_name": r.get("college_name"),
            "institution_type": inst_type,
            "image_url": r.get("image_url", ""),
            "website_url": r.get("website_url", ""),
            "scraping_status": r.get("scraping_status", "manual_input"),
            "TLR": round(TLR, 2),
            "RP": round(RPII, 2),
            "GO": round(GO, 2),
            "OI": round(OI, 2),
            "PR": round(PR, 2),
            "Total": round(total_score, 2),
        })

    return results

app = Flask(__name__)

@app.route("/")
def index():
    """Main dashboard page showing NIRF scores for all colleges"""
    # Load the detailed scores
    scores_file = SCORES_CSV
    results_file = RESULTS_CSV
    
    try:
        if os.path.exists(scores_file):
            df_scores = pd.read_csv(scores_file)
            colleges_data = df_scores.to_dict('records')
        else:
            colleges_data = []
            
        if os.path.exists(results_file):
            df_results = pd.read_csv(results_file)
            # Sort by total score
            df_results = df_results.sort_values('Total Score', ascending=False)
            results_data = df_results.to_dict('records')
        else:
            results_data = []
            
    except Exception as e:
        colleges_data = []
        results_data = []
        error_message = f"Error loading data: {str(e)}"
    
    return render_template("dashboard.html", 
                         colleges=colleges_data, 
                         results=results_data,
                         title="NIRF Dashboard",
                         year=datetime.now().year)

@app.route("/college/<college_name>")
def college_detail(college_name):
    """Detailed view for a specific college"""
    scores_file = SCORES_CSV
    
    try:
        if os.path.exists(scores_file):
            df_scores = pd.read_csv(scores_file)
            # For suggestions we need cohort percentiles and rank
            df_scores_sorted = df_scores.sort_values('Total', ascending=False).reset_index(drop=True)
            college_data = df_scores_sorted[df_scores_sorted['college_name'] == college_name]
            
            if not college_data.empty:
                college = college_data.iloc[0].to_dict()
                # Rank of the college (1-based)
                try:
                    rank_position = (
                        df_scores_sorted.index[df_scores_sorted['college_name'] == college_name][0] + 1
                    )
                except Exception:
                    rank_position = None

                # AI-like suggestions: find weakest parameters vs cohort percentiles
                def pctl(series, val):
                    try:
                        return (series.le(val).sum() / max(len(series), 1)) * 100.0
                    except Exception:
                        return 0.0
                suggestions = []
                if not rank_position or rank_position > 3:
                    for key, label in [("TLR", "Teaching & Learning Resources"),
                                       ("RP", "Research & Professional Practice"),
                                       ("GO", "Graduation Outcomes"),
                                       ("OI", "Outreach & Inclusivity"),
                                       ("PR", "Perception")]:
                        pct = pctl(df_scores_sorted[key], college[key]) if key in df_scores_sorted else 0
                        # Only suggest for weaker areas (below 60th percentile)
                        if pct < 60.0:
                            suggestions.append({
                                "key": key,
                                "label": label,
                                "score": float(college[key]),
                                "percentile": round(pct, 1)
                            })
                    # Sort by ascending percentile (weakest first) and limit to top 3 areas
                    suggestions.sort(key=lambda x: x["percentile"]) 
                    suggestions = suggestions[:3]
                    # Simple actionable advice text per area
                    advice_map = {
                        "TLR": "Improve FSR by increasing qualified full-time faculty (F1) relative to sanctioned seats and invest in library/lab expenditure.",
                        "RP": "Increase peer-reviewed publications and citations; strengthen patent filings and technology transfer.",
                        "GO": "Raise graduation-on-time %, placement outcomes, and median salaries via industry partnerships and career services.",
                        "OI": "Enhance regional/women participation, disadvantaged student inclusion, and accessibility infrastructure.",
                        "PR": "Boost applications per seat via outreach/branding and improve peer perception through collaborations."
                    }
                    for s in suggestions:
                        s["advice"] = advice_map.get(s["key"], "Focus on strengthening this parameter.")

                return render_template("college_detail.html", college=college, suggestions=suggestions, title=f"{college_name} - Details")
            else:
                return "College not found", 404
        else:
            return "No data available", 404
            
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/compare")
def compare_colleges():
    """Compare multiple colleges side by side"""
    scores_file = SCORES_CSV
    
    try:
        if os.path.exists(scores_file):
            df_scores = pd.read_csv(scores_file)
            colleges_data = df_scores.to_dict('records')
        else:
            colleges_data = []
            
    except Exception as e:
        colleges_data = []
        error_message = f"Error loading data: {str(e)}"
    
    return render_template("compare.html", 
                         colleges=colleges_data, 
                         title="Compare Colleges")


@app.route("/input", methods=["GET", "POST"])
def input_metrics():
    if request.method == "GET":
        # Optional prefill by college name for editing
        college_name = request.args.get("college")
        record = None
        if college_name:
            for r in load_inputs():
                if r.get("college_name") == college_name:
                    record = r
                    break
        return render_template("input.html", title="Add College Metrics", year=datetime.now().year, record=record)

    # POST: collect form data
    form = request.form
    record: Dict[str, Any] = {
        "college_name": form.get("college_name", "").strip(),
        "website_url": form.get("website_url", "").strip(),
        "image_url": form.get("image_url", "").strip(),
        "institution_type": form.get("institution_type", "college"),
        "scraping_status": "manual_input",
        # Faculty and seats
        "F1": form.get("F1", "0"),
        "F2": form.get("F2", "0"),
        "seats_N": form.get("seats_N", "0"),
        "phd_percent": form.get("phd_percent", "0"),
        "avg_experience_years": form.get("avg_experience_years", "0"),
        # Library & Lab
        "EXLIP": form.get("EXLIP", "0"),
        "EXLIE": form.get("EXLIE", "0"),
        "EXLB": form.get("EXLB", "0"),
        # SEC inputs
        "SEC_pA_percentile": form.get("SEC_pA_percentile", "0"),
        "SEC_pB_percentile": form.get("SEC_pB_percentile", "0"),
        "SEC_pC_percentile": form.get("SEC_pC_percentile", "0"),
        "SEC_winners_count": form.get("SEC_winners_count", "0"),
        # Publications & Citations
        "PW": form.get("PW", "0"),
        "PS": form.get("PS", "0"),
        "PG": form.get("PG", "0"),
        "PI": form.get("PI", "0"),
        "CCW": form.get("CCW", "0"),
        "CCS": form.get("CCS", "0"),
        "CCG": form.get("CCG", "0"),
        "CCI": form.get("CCI", "0"),
        # Patents
        "PF_filed": form.get("PF_filed", "0"),
        "PG_granted": form.get("PG_granted", "0"),
        "PL_licensed_count": form.get("PL_licensed_count", "0"),
        "EP_revenue": form.get("EP_revenue", "0"),
        # GO
        "UE_graduating_percent": form.get("UE_graduating_percent", "0"),
        "PE_index": form.get("PE_index", "0"),
        # OI
        "CES_N": form.get("CES_N", "0"),
        "RD_other_states": form.get("RD_other_states", "0"),
        "RD_other_countries": form.get("RD_other_countries", "0"),
        "WS_women_students_percent": form.get("WS_women_students_percent", "0"),
        "WS_women_faculty_percent": form.get("WS_women_faculty_percent", "0"),
        "WS_women_leadership_percent": form.get("WS_women_leadership_percent", "0"),
        "ESCS_disadvantaged_percent": form.get("ESCS_disadvantaged_percent", "0"),
        "DAP_ramps": bool(form.get("DAP_ramps")),
        "DAP_lifts": bool(form.get("DAP_lifts")),
        "DAP_walking_aids": bool(form.get("DAP_walking_aids")),
        "DAP_toilets": bool(form.get("DAP_toilets")),
        "DAP_braille_labs": bool(form.get("DAP_braille_labs")),
        "DAP_av_aids": bool(form.get("DAP_av_aids")),
        # PR
        "PR_survey": form.get("PR_survey", "0"),
        "applications_A": form.get("applications_A", "0"),
        "sanctioned_S": form.get("sanctioned_S", "0"),
    }

    inputs = load_inputs()
    # Update existing record if present (edit flow)
    updated = False
    for i, r in enumerate(inputs):
        if r.get("college_name") == record.get("college_name"):
            inputs[i] = record
            updated = True
            break
    if not updated:
        inputs.append(record)
    save_inputs(inputs)

    # Recompute scores for all inputs
    scores = compute_scores(inputs)
    ensure_dirs()
    # Save detailed scores
    df_scores = pd.DataFrame(scores)
    df_scores.to_csv(SCORES_CSV, index=False)

    # Save summary sorted by total score desc
    df_results = pd.DataFrame([
        {
            "Rank": i + 1,
            "College": s["college_name"],
            "TLR": s["TLR"],
            "RP": s["RP"],
            "GO": s["GO"],
            "OI": s["OI"],
            "PR": s["PR"],
            "Total Score": s["Total"],
            "Status": "manual_input",
        }
        for i, s in enumerate(sorted(scores, key=lambda x: x["Total"], reverse=True))
    ])
    df_results.to_csv(RESULTS_CSV, index=False)
    # Append history for this college
    try:
        saved_score = next((s for s in scores if s.get("college_name") == record.get("college_name")), None)
        if saved_score:
            append_history({
                "timestamp": datetime.now().isoformat(),
                "college_name": record.get("college_name"),
                "record": record,
                "scores": saved_score,
            })
    except Exception:
        pass

    return redirect(url_for("index"))

@app.route("/run-analysis")
def run_analysis():
    """Redirect to input form to add metrics and recompute rankings"""
    return redirect(url_for("input_metrics"))


# --- Automation: scrape by college name and (optional) official URL ---
try:
    from main import NIRFCalculator
except Exception:
    NIRFCalculator = None  # type: ignore


def resolve_official_site(college_name: str, provided_url: str | None) -> str | None:
    if provided_url:
        return provided_url.strip()
    # Heuristic guesses for official sites
    name = college_name.lower().replace(" ", "").replace("university", "").replace("college", "")
    candidates = [
        f"https://www.{name}.ac.in",
        f"https://{name}.ac.in",
        f"https://www.{name}.edu.in",
        f"https://{name}.edu.in",
    ]
    import requests
    for url in candidates:
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code < 400:
                return resp.url
        except Exception:
            continue
    return None


def map_scraped_to_record(college_name: str, website_url: str, scraped: Dict[str, Any]) -> Dict[str, Any]:
    faculty_count = scraped.get("faculty_count")
    phd_count = scraped.get("phd_count")
    student_count = scraped.get("student_count")
    publications = scraped.get("publications")
    citations = scraped.get("citations")
    patents = scraped.get("patents")
    phd_percent = 0.0
    if faculty_count and phd_count and faculty_count > 0:
        try:
            phd_percent = (float(phd_count) / float(faculty_count)) * 100.0
        except Exception:
            phd_percent = 0.0

    record: Dict[str, Any] = {
        "college_name": college_name,
        "website_url": website_url,
        "image_url": scraped.get("image_url", ""),
        "institution_type": "college",
        "scraping_status": "success" if scraped else "manual_input",
        # Faculty & seats (approximations; user can edit)
        "F1": faculty_count or 0,
        "F2": 0,
        "seats_N": student_count or 0,
        "phd_percent": round(phd_percent, 2),
        "avg_experience_years": 0,
        # Library & Lab (unknown)
        "EXLIP": 0, "EXLIE": 0, "EXLB": 0,
        # SEC
        "SEC_pA_percentile": 0, "SEC_pB_percentile": 0, "SEC_pC_percentile": 0, "SEC_winners_count": 0,
        # Publications & Citations (map what we can)
        "PW": 0, "PS": publications or 0, "PG": 0, "PI": 0,
        "CCW": 0, "CCS": citations or 0, "CCG": 0, "CCI": 0,
        # Patents
        "PF_filed": 0, "PG_granted": patents or 0, "PL_licensed_count": 0, "EP_revenue": 0,
        # GO
        "UE_graduating_percent": 0, "PE_index": 0,
        # OI
        "CES_N": 0,
        "RD_other_states": 0, "RD_other_countries": 0,
        "WS_women_students_percent": 0, "WS_women_faculty_percent": 0, "WS_women_leadership_percent": 0,
        "ESCS_disadvantaged_percent": 0,
        "DAP_ramps": False, "DAP_lifts": False, "DAP_walking_aids": False, "DAP_toilets": False,
        "DAP_braille_labs": False, "DAP_av_aids": False,
        # PR
        "PR_survey": 0, "applications_A": 0, "sanctioned_S": 0,
    }
    return record


@app.route("/auto", methods=["GET", "POST"])
def auto_scrape():
    if request.method == "GET":
        return render_template("auto.html", title="Auto Add College", year=datetime.now().year)

    college_name = (request.form.get("college_name") or "").strip()
    website_url = (request.form.get("website_url") or "").strip()
    if not college_name:
        return render_template("auto.html", title="Auto Add College", year=datetime.now().year, error="College name is required")

    site = resolve_official_site(college_name, website_url or None)
    if NIRFCalculator is None:
        return render_template("auto.html", title="Auto Add College", year=datetime.now().year, error="Scraper not available.")
    if not site:
        # Create a minimal record and redirect to edit
        minimal = map_scraped_to_record(college_name, website_url or "", scraped={})
        inputs = load_inputs()
        # Upsert
        replaced = False
        for i, r in enumerate(inputs):
            if r.get("college_name") == college_name:
                inputs[i] = minimal
                replaced = True
                break
        if not replaced:
            inputs.append(minimal)
        save_inputs(inputs)
        return redirect(url_for("input_metrics", college=college_name))

    try:
        calc = NIRFCalculator()
        scraped = calc.advanced_scraping(site, college_name)
    except Exception:
        scraped = {}

    record = map_scraped_to_record(college_name, site, scraped or {})

    inputs = load_inputs()
    # Upsert
    replaced = False
    for i, r in enumerate(inputs):
        if r.get("college_name") == college_name:
            inputs[i] = record
            replaced = True
            break
    if not replaced:
        inputs.append(record)
    save_inputs(inputs)

    return redirect(url_for("input_metrics", college=college_name))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
