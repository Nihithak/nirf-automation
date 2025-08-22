import sys
import os
sys.path.append('nirf-automation')

from dashboard.app import basic_scrape_site, map_scraped_to_record

# Test the demo website
print("Testing Demo College Website...")
print("=" * 50)

# Test the scraper
result = basic_scrape_site('http://localhost:8000')
print(f"Scraped data: {result}")

# Test the mapping
record = map_scraped_to_record("Demo College", "http://localhost:8000", result)
print(f"\nMapped record preview:")
print(f"F1 (Regular): {record.get('F1', 0)}")
print(f"seats_N: {record.get('seats_N', 0)}")
print(f"phd_percent: {record.get('phd_percent', 0)}%")
print(f"PS (Publications): {record.get('PS', 0)}")
print(f"CCS (Citations): {record.get('CCS', 0)}")
print(f"PG_granted (Patents): {record.get('PG_granted', 0)}")
print(f"UE_graduating_percent: {record.get('UE_graduating_percent', 0)}%")
print(f"applications_A: {record.get('applications_A', 0)}")
print(f"sanctioned_S: {record.get('sanctioned_S', 0)}")
print(f"EXLIP: {record.get('EXLIP', 0)}")
print(f"EXLIE: {record.get('EXLIE', 0)}")
print(f"EXLB: {record.get('EXLB', 0)}")
print(f"SEC_pA_percentile: {record.get('SEC_pA_percentile', 0)}")
print(f"SEC_pB_percentile: {record.get('SEC_pB_percentile', 0)}")
print(f"SEC_pC_percentile: {record.get('SEC_pC_percentile', 0)}")
print(f"WS_women_students_percent: {record.get('WS_women_students_percent', 0)}%")
print(f"WS_women_faculty_percent: {record.get('WS_women_faculty_percent', 0)}%")
print(f"RD_other_states: {record.get('RD_other_states', 0)}%")
print(f"ESCS_disadvantaged_percent: {record.get('ESCS_disadvantaged_percent', 0)}%")
print(f"image_url: {record.get('image_url', '')}")

print("\n" + "=" * 50)
print("Demo website test completed!")

