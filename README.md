## SaaSquatch Lite - Enhanced Lead Generation Tool

This is a streamlined, AI-augmented lead generation tool that scrapes and enriches company domains with emails and LinkedIn profiles. It assigns a lead score to prioritize prospects based on data completeness.

---

### Features:

* Multi-page scraping (homepage + fallback paths like `/about`, `/contact`)
* Extracts publicly listed emails
* Adds common generic emails (e.g., `info@domain.com`, `sales@domain.com`)
* Detects LinkedIn company/profile links from the website
* Fallbacks to Google-based search when LinkedIn is not explicitly listed
* Calculates a Lead Score from 0–3
* Interactive Streamlit filters
* CSV download for enriched leads

---

### ⚙Installation & Setup:

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/saasquatch-lite
cd saasquatch-lite
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the Streamlit App**

```bash
streamlit run app.py
```

---

### Requirements:

* Python 3.9+
* Libraries:

  * `streamlit`
  * `aiohttp`
  * `bs4`
  * `pandas`
  * `requests`
  * `re`

---

### Dataset:

No external dataset is required. The tool operates directly on user-provided domains and fetches data live from the internet.

### Contact:

Author: Pavankumar Tirumalasetty
Email: tpkumar9121@gmail.com
