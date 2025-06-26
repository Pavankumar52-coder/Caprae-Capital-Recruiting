# SaaSquatch Lite – LeadGen Enricher

# Tool Creation

## Introduction to the leadgen tool:
A Streamlit-based leadgen tool to enrich company domains with publicly available emails and LinkedIn profiles. Supports multi-page scraping and smart LinkedIn fallback via Google Search.

## Setup Instructions:
1. Clone the repo  Caprae Capital, Recruiting
2. `pip install -r requirements.txt`  
3. `streamlit run app.py`

## Usage:
- Enter domains (one per line, any TLD) or copy paste them
- Click “Enrich” button
- View enriched table:
  - Emails (found or generic)
  - LinkedIn links
  - Status & Score
- Download the results as CSV file easily

## Features:
- Async scraping from multiple key pages
- DNS resolution check
- Fallback LinkedIn lookup via Google Search
- Lead scoring: email + LinkedIn + success status
- Filtering and CSV export
