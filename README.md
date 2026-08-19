# 📚 Canvas to PDF Scraper (Targeted Module Engine)

Welcome! This Python tool automatically dives into your Canvas course, finds a specific weekly module, clicks through all the pages inside it, extracts the text, and generates a clean, readable PDF study guide directly onto your Desktop.

This guide will walk you through exactly how to set it up, even if you have never used Python before.

## 🛠️ Step 1: Initial Setup
1. **Install Python:** If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and install it. *(Important: During installation on Windows, check the box that says "Add Python to PATH")*.
2. **Download the Files:** Ensure `canvas_targeted_pdf.py` and `requirements.txt` are saved in the same folder on your computer.
3. **Install Dependencies:** 
   * Open your computer's Terminal (Mac) or Command Prompt/PowerShell (Windows).
   * Navigate to the folder where you saved the files. (Tip: type `cd ` and drag the folder into the terminal window, then press Enter).
   * Run this exact command to install the required background tools:
     `pip install -r requirements.txt`

## 🔑 Step 2: Get Your Canvas Credentials
To allow the script to read your course pages, you need to give it a digital key (API Token) and point it to the right course.

**1. Generate an API Token:**
* Log into your university Canvas account in your web browser.
* Click on **Account** (your profile picture) in the left sidebar, then click **Settings**.
* Scroll down to the "Approved Integrations" section and click the **+ New Access Token** button.
* Give it a purpose (e.g., "PDF Scraper") and click **Generate Token**.
* **Copy the long string of characters.** (Treat this like a password; do not share it).

**2. Find Your Canvas Domain and Course ID:**
* Go to the main homepage of the Canvas course you want to scrape.
* Look at the URL in your browser's address bar. It will look something like this:
  `https://canvas.your_university.edu.au/courses/12345`
* **Domain:** `https://canvas.your_university.edu.au`
* **Course ID:** `12345` (The numbers right after /courses/)

## 📝 Step 3: Configure the Script
Open the `canvas_targeted_pdf.py` file using Notepad (Windows), TextEdit (Mac), or any code editor.

At the very top of the script, fill in your unique details inside the quotation marks:
* `CANVAS_TOKEN = 'PASTE_YOUR_LONG_TOKEN_HERE'`
* `CANVAS_DOMAIN = 'PASTE_YOUR_DOMAIN_HERE'`
* `COURSE_ID = 'PASTE_YOUR_COURSE_ID_HERE'`

## 🎯 Step 4: Protocol of Use (Daily Operation)
Whenever you want to generate a new PDF for a specific week, follow these steps:

1. **Check Canvas:** Look at how your professor named the modules. For example, if the module is named "Block 2" and the page inside it is "Block 2 - Week 8".
2. **Update the Script:** Open `canvas_targeted_pdf.py` and change the Target Navigation section to match the text exactly:
   ```python
   TARGET_BLOCK = "Block 2"
   TARGET_WEEK = "Week 8"
