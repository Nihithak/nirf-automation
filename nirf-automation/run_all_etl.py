# run_all_etl.py
import etl.teaching.faculty_fetch
import etl.research.publications_scraper
import etl.outcomes.placement_data
import etl.outreach.inclusivity_data
import etl.perception.linkedin_mentions

if __name__ == "__main__":
    print("✅ Running all ETL modules...")

    etl.teaching.faculty_fetch.get_faculty_data()
    etl.research.publications_scraper.get_research_data()
    etl.outcomes.placement_data.get_placement_data()
    etl.outreach.inclusivity_data.get_inclusivity_data()
    etl.perception.linkedin_mentions.get_perception_data()

    print("✅ All data processed and saved to data/processed/")
