import sys
import os
sys.path.append('nirf-automation')

from dashboard.app import basic_scrape_site, map_scraped_to_record

# Test with a direct file path instead of localhost
print("Testing Demo College Website Directly...")
print("=" * 50)

# Read the HTML file directly
with open('demo-college-website/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f"HTML content length: {len(html_content)} characters")
print(f"First 500 characters: {html_content[:500]}")

# Test the scraper with the HTML content
import requests
from bs4 import BeautifulSoup

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')
text = soup.get_text()

print(f"\nExtracted text length: {len(text)} characters")
print(f"Text contains '250': {'250' in text}")
print(f"Text contains '5000': {'5000' in text}")
print(f"Text contains '750': {'750' in text}")

# Test the basic_scrape_site function with the HTML content
def test_scrape_with_content(html_content):
    from bs4 import BeautifulSoup
    import re
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    data = {}
    
    # Faculty patterns
    faculty = None
    faculty_patterns = [
        r'([0-9,]+)\s*faculty', r'([0-9,]+)\s*professors?', r'([0-9,]+)\s*teaching\s*staff',
        r'([0-9,]+)\s*academic\s*staff', r'([0-9,]+)\s*teachers?', r'([0-9,]+)\s*staff\s*members?',
        r'faculty\s*strength[:\s]*([0-9,]+)', r'teaching\s*staff[:\s]*([0-9,]+)',
        r'([0-9,]+)\s*qualified\s*faculty', r'([0-9,]+)\s*permanent\s*faculty',
        r'([0-9,]+)\s*faculty\s*members', r'([0-9,]+)\s*faculty\s*members\s*including',
        r'([0-9,]+)\s*qualified\s*faculty\s*members\s*including'
    ]
    
    for pattern in faculty_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            faculty = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if faculty:
        data['faculty_count'] = faculty
        print(f"Found faculty: {faculty}")
    
    # Student patterns
    students = None
    student_patterns = [
        r'([0-9,]+)\s*students?', r'([0-9,]+)\s*enrolled', r'([0-9,]+)\s*undergraduate',
        r'student\s*count[:\s]*([0-9,]+)', r'enrollment[:\s]*([0-9,]+)',
        r'([0-9,]+)\s*students\s*enrolled'
    ]
    
    for pattern in student_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            students = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if students:
        data['student_count'] = students
        print(f"Found students: {students}")
    
    # Publication patterns
    pubs = None
    pub_patterns = [
        r'([0-9,]+)\s*publications?', r'([0-9,]+)\s*research\s*papers?',
        r'([0-9,]+)\s*journal\s*articles?', r'([0-9,]+)\s*papers?\s*published',
        r'publications[:\s]*([0-9,]+)', r'research\s*output[:\s]*([0-9,]+)',
        r'([0-9,]+)\s*research\s*publications', r'([0-9,]+)\s*research\s*publications\s*in\s*peer-reviewed'
    ]
    
    for pattern in pub_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pubs = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if pubs:
        data['publications'] = pubs
        print(f"Found publications: {pubs}")
    
    # Citation patterns
    cites = None
    cite_patterns = [
        r'([0-9,]+)\s*citations?', r'([0-9,]+)\s*cited', r'citation\s*count[:\s]*([0-9,]+)'
    ]
    
    for pattern in cite_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cites = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if cites:
        data['citations'] = cites
        print(f"Found citations: {cites}")
    
    # Job offers patterns
    jobs = None
    job_patterns = [
        r'([0-9,]+)\s*job\s*offers?', r'([0-9,]+)\s*placement\s*offers?',
        r'([0-9,]+)\s*offers?\s*received', r'job\s*offers[:\s]*([0-9,]+)'
    ]
    
    for pattern in job_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            jobs = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if jobs:
        data['job_offers'] = jobs
        print(f"Found job offers: {jobs}")
    
    # Additional patterns for missing data
    # Patents
    patents = None
    patent_patterns = [
        r'([0-9,]+)\s*patents?\s*granted', r'([0-9,]+)\s*patents?\s*filed\s*and\s*([0-9,]+)\s*patents?\s*granted'
    ]
    
    for pattern in patent_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'and' in pattern:
                patents = int(re.sub(r"[^0-9]", "", match.group(2)))  # Get granted patents
            else:
                patents = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if patents:
        data['patents'] = patents
        print(f"Found patents: {patents}")
    
    # Applications
    apps = None
    app_patterns = [
        r'([0-9,]+)\s*applications?\s*received', r'([0-9,]+)\s*applications?'
    ]
    
    for pattern in app_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            apps = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if apps:
        data['applications'] = apps
        print(f"Found applications: {apps}")
    
    # Sanctioned seats/intake
    seats = None
    seat_patterns = [
        r'([0-9,]+)\s*seats?', r'sanctioned\s*intake[:\s]*([0-9,]+)'
    ]
    
    for pattern in seat_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            seats = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if seats:
        data['sanctioned_seats'] = seats
        print(f"Found sanctioned seats: {seats}")
    
    # Library and lab expenditure
    lib_phys = None
    lib_phys_patterns = [
        r'library\s*expenditure\s*\(physical\)[:\s]*₹([0-9,]+)', r'₹([0-9,]+)\s*lakhs?\s*physical'
    ]
    
    for pattern in lib_phys_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            lib_phys = int(re.sub(r"[^0-9]", "", match.group(1)))
            break
    
    if lib_phys:
        data['library_physical'] = lib_phys
        print(f"Found library physical: {lib_phys}")
    
    # Diversity statistics
    women_students = None
    women_patterns = [
        r'women\s*students[:\s]*([0-9]+)%', r'([0-9]+)%\s*women\s*students'
    ]
    
    for pattern in women_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            women_students = int(match.group(1))
            break
    
    if women_students:
        data['women_students_percent'] = women_students
        print(f"Found women students: {women_students}%")
    
    return data

# Test the scraping
result = test_scrape_with_content(html_content)
print(f"\nScraped data: {result}")

# Test the mapping
record = map_scraped_to_record("KBN College", "http://localhost:8000", result)
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

print("\n" + "=" * 50)
print("Direct demo website test completed!")
