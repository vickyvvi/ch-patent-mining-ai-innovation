# Patent-Based Innovation Efficiency – Code Repository

This repository contains the code used in my seminar paper on the impact of Artificial Intelligence on corporate innovation efficiency (Swiss listed firms, 2014–2023).  
Only code and lightweight processed files are included; large proprietary datasets are excluded.

---

## Folder Structure

### **data_crawling/**
Scripts for collecting patent data.
- `scrape_patents_ipi.cjs` – Swissreg (IPI) patent crawler.
- `patent_scraping_google.py` – Google Patents crawler.

### **datasets/**
Cleaned datasets and Stata analysis code.
- `selected_data_final.xlsx`
- `merged_patent_data_IPI.parquet`
- `merged_patent_data_google.xlsx`
- `AI_Frequency_Analysis.xlsx`
- `Data_1129.dta` – Stata panel dataset.
- `Analysis_Commands.do` – main regression script (FE models, robustness checks).

### **key_metrics/**
Text-mining and indicator construction.
- `AI_extract.py` – AI keyword frequency extraction.
- `EWM_Calculation.do` – Entropy Weight Method (innovation efficiency score).

---

## Environment
- Python 3.9+
- Stata 17+
- Key Python libs: `pandas`, `numpy`, `pyarrow`, `tqdm`, `requests`, `beautifulsoup4`

---

## Notes
Large raw text files (annual reports, full patent archives) are not included.  
This repo contains only the code and necessary processed outputs for reproducibility.
