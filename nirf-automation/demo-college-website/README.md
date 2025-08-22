# Demo College Website

This is a demo college website created to showcase the NIRF automation scraping functionality. The website contains all the required NIRF data embedded in the content to demonstrate how the scraper extracts information.

## 🎯 Purpose

This demo website serves as a test case to show that the web scraping functionality works perfectly when the college website contains the required data in a parseable format.

## 📊 Embedded NIRF Data

The website contains the following NIRF parameters embedded in the content:

### Faculty & Students
- **Faculty Count**: 250
- **PhD Faculty**: 175 (70%)
- **Student Count**: 5000
- **Average Experience**: 12 years

### Research & Publications
- **Publications**: 750
- **Citations**: 3750
- **Patents Filed**: 25
- **Patents Granted**: 15
- **Research Revenue**: ₹25 lakhs

### Placement & Career
- **Job Offers**: 500+
- **Placement Rate**: 85%
- **Average Salary**: 8.5 LPA
- **Applications**: 7500
- **Sanctioned Seats**: 5000

### Infrastructure
- **Library Expenditure (Physical)**: ₹15 lakhs
- **Library Expenditure (Electronic)**: ₹8 lakhs
- **Laboratory Expenditure**: ₹12 lakhs

### Diversity & Inclusion
- **Women Students**: 45%
- **Women Faculty**: 35%
- **Women Leadership**: 40%
- **Other States Students**: 30%
- **International Students**: 5%
- **Disadvantaged Students**: 25%

### Sports & Extra-curricular
- **Sports Activities**: 85th percentile
- **Student Competitions**: 90th percentile
- **Cultural Activities**: 80th percentile
- **Winners**: 5

### Accessibility
- **Ramps**: Available
- **Lifts**: Available
- **Walking Aids**: Available
- **Accessible Toilets**: Available
- **Braille Labs**: Available
- **AV Aids**: Available

## 🚀 How to Use

1. **Start a local server** in this directory:
   ```bash
   python -m http.server 8000
   ```

2. **Access the website** at: `http://localhost:8000`

3. **Test the scraper** by using the URL in your NIRF automation dashboard:
   - Go to Auto Add College
   - Enter "Demo College" as name
   - Enter "http://localhost:8000" as website URL
   - Click "Scrape and Prefill"

## ✅ Expected Results

When the scraper processes this demo website, it should extract and pre-fill the form with:
- Faculty: 250
- Students: 5000
- PhD %: 70%
- Publications: 750
- Citations: 3750
- Patents: 15
- Job Offers: 500
- Applications: 7500
- And many more fields...

## 🎨 Design Features

- Professional college website design
- Responsive layout
- Realistic content and statistics
- All NIRF data naturally embedded in the text
- Proper HTML structure for easy parsing

This demo website proves that the scraping functionality works perfectly when the source website contains the required data in a readable format.

