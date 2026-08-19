import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from fpdf import FPDF

# =====================================================================
# --- 1. YOUR CREDENTIALS & CONFIGURATION (FILL THIS OUT ONCE) ---
# =====================================================================
# Generate this in Canvas -> Account -> Settings -> New Access Token
CANVAS_TOKEN = 'PASTE_YOUR_CANVAS_API_TOKEN_HERE'

# e.g., 'https://canvas.institution.edu' (No trailing slash)
CANVAS_DOMAIN = 'PASTE_YOUR_CANVAS_DOMAIN_HERE'

# The number in your URL: canvas.edu/courses/12345 -> 12345
COURSE_ID = 'PASTE_YOUR_COURSE_ID_HERE'
# =====================================================================


# =====================================================================
# --- 2. TARGET NAVIGATION (CHANGE THESE EVERY TIME YOU RUN IT) ---
# =====================================================================
# Type EXACTLY what the module and week are called in Canvas. Case sensitive.
TARGET_BLOCK = "Block [x]"
TARGET_WEEK = "Week [x]"
# =====================================================================

headers_canvas = {
    'Authorization': f'Bearer {CANVAS_TOKEN}'
}

visited_urls = set()

class CanvasPDF(FPDF):
    """Custom PDF template with headers and footers."""
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"{TARGET_BLOCK} - {TARGET_WEEK} Scrape", 0, 1, "R")

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_topic(self, title, url, body_text):
        self.add_page()
        
        # 1. Clean Title (H1)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 0, 0)
        safe_title = title.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 10, safe_title)
        self.ln(2)

        # 2. Clickable Original URL
        self.set_font("Helvetica", "U", 10)
        self.set_text_color(0, 102, 204)
        safe_url = url if url else ''
        self.cell(0, 5, "Original Canvas Link", ln=1, link=safe_url)
        self.ln(5)

        # 3. Clean Body Text
        self.set_font("Helvetica", "", 11)
        self.set_text_color(0, 0, 0)
        safe_body = body_text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, safe_body)
        self.ln(10)

# Initialize the PDF document
pdf = CanvasPDF()
pdf.set_auto_page_break(auto=True, margin=15)

def extract_clean_text(raw_html):
    """Removes messy HTML tags and condenses huge blank spaces."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator="\n").strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def push_to_pdf(title, raw_html, link):
    """Extracts text and pushes it to the PDF document."""
    body_text = extract_clean_text(raw_html)
    if body_text:
        print(f"    -> Formatting and adding to PDF: {title}")
        pdf.add_topic(title, link, body_text)

def fetch_child_link(href, link_title):
    """Drills down into the links found inside a Week page."""
    if href in visited_urls:
        return
    visited_urls.add(href)
    
    if "/pages/" in href:
        page_suffix = href.split('/pages/')[-1].split('?')[0]
        page_suffix = urllib.parse.unquote(page_suffix) 
        
        child_res = requests.get(f"{CANVAS_DOMAIN}/api/v1/courses/{COURSE_ID}/pages/{page_suffix}", headers=headers_canvas)
        if child_res.status_code == 200:
            child_data = child_res.json()
            actual_title = child_data.get('title', link_title)
            push_to_pdf(actual_title, child_data.get('body', ''), href)

def main():
    if "PASTE_YOUR_" in CANVAS_TOKEN or "PASTE_YOUR_" in COURSE_ID:
        print("\nERROR: You must fill in your Canvas Token, Domain, and Course ID at the top of the script before running!")
        return

    print(f"Initiating PDF Generation for {TARGET_BLOCK}, {TARGET_WEEK}...")
    
    modules_url = f"{CANVAS_DOMAIN}/api/v1/courses/{COURSE_ID}/modules"
    modules_res = requests.get(modules_url, headers=headers_canvas)
    
    if modules_res.status_code != 200:
        print("Failed to access Canvas course. Please check your Token and Course ID.")
        return
        
    modules = modules_res.json()
    item_found = False
    
    for module in modules:
        module_name = module.get('name', '')
        
        # FILTER 1: Does the module match the Block?
        if TARGET_BLOCK not in module_name:
            continue
            
        print(f"\nTarget Module Found: {module_name}")
        module_id = module['id']
        
        items_url = f"{CANVAS_DOMAIN}/api/v1/courses/{COURSE_ID}/modules/{module_id}/items"
        items_res = requests.get(items_url, headers=headers_canvas)
        items = items_res.json()
        
        for item in items:
            item_title = item.get('title', 'Untitled')
            item_type = item.get('type')
            
            # FILTER 2: Does the page inside the module match the Week?
            if TARGET_WEEK not in item_title:
                continue
                
            item_found = True
            if item_type == 'Page':
                print(f"  -> Entering: {item_title}")
                page_url_suffix = item.get('page_url')
                page_res = requests.get(f"{CANVAS_DOMAIN}/api/v1/courses/{COURSE_ID}/pages/{page_url_suffix}", headers=headers_canvas)
                page_data = page_res.json()
                raw_html = page_data.get('body', '')
                
                # 1. Add the main Week Page itself to the PDF
                push_to_pdf(item_title, raw_html, item.get('html_url'))
                
                # 2. Extract and drill down into all links found inside the Week Page
                soup = BeautifulSoup(raw_html, "html.parser")
                links = soup.find_all('a')
                
                for a_tag in links:
                    href = a_tag.get('href', '')
                    link_text = a_tag.get_text(strip=True) or "Extracted Link"
                    
                    if f"/courses/{COURSE_ID}" in href:
                        fetch_child_link(href, link_text)

    if not item_found:
        print(f"\nError: Could not find any pages containing '{TARGET_WEEK}' inside '{TARGET_BLOCK}'.")
        print("Check Canvas to make sure you typed the names exactly as they appear.")
        return

    # Define where to save it (Desktop) and name the file dynamically
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    safe_block_name = TARGET_BLOCK.replace(" ", "")
    safe_week_name = TARGET_WEEK.replace(" ", "")
    pdf_path = os.path.join(desktop_path, f"Canvas_{safe_block_name}_{safe_week_name}.pdf")
    
    print(f"\nGenerating PDF document at: {pdf_path}...")
    try:
        pdf.output(pdf_path)
        print("--- PDF SUCCESS: Your document is ready on your Desktop! ---")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    main()