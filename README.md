# Enterprise Dynamic Analytics

> A professional, self-service data intelligence dashboard built with **Streamlit** and **Plotly**.  
> Upload any CSV or Excel file and instantly get KPIs, interactive filters, trend charts, and data-quality insights — no configuration required.

---

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://enterprise-analytics-dashboard-007.streamlit.app/))

---

## Features

| Feature | Description |
|---|---|
| **Auto KPIs** | Detects numeric columns and computes Total, Average, Distinct Count automatically |
| **Smart Slicers** | Generates sidebar filters for every categorical and date column found |
| **Executive Overview** | Auto-renders a trend line and distribution donut based on detected schema |
| **Visual Builder** | Build any chart (Bar, Pie, Line, Area, Scatter) with a no-code point-and-click interface |
| **Data Quality Panel** | Column schema, role detection, missing-value percentages, and a full data preview |
| **CSV Export** | Download the filtered dataset at any time |
| **Any Dataset** | Accepts CSV, XLSX, and XLS files up to 250 MB |

---

## Screenshots

> Upload your dataset and the dashboard auto-generates everything.

| Landing Page | Dashboard View |
|---|---|
| *Hero landing with upload prompt* | *KPIs, charts, and filters rendered automatically* |

---

## Tech Stack

| Library | Version | Purpose |
|---|---|---|
| `streamlit` | >=1.35.0 | Web UI framework |
| `pandas` | >=2.0.0 | Data loading and transformation |
| `plotly` | >=5.20.0 | Interactive charts |
| `openpyxl` | >=3.1.0 | Excel file support |

---

## Getting Started (Local)

### 1. Clone the repository

```bash
git clone https://mohsinshaikh233//enterprise-analytics-dashboard.git
cd enterprise-analytics-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Open your browser at **[(https://enterprise-analytics-dashboard-007.streamlit.app/) and upload a CSV or Excel file to begin.

---

## Deployment (Streamlit Community Cloud)

1. Fork or push this repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** and point it to this repository.
4. Set **Main file path** to `app.py`.
5. Click **Deploy**.

No secrets or environment variables are required.

---

## Supported Dataset Formats

| Format | Extension | Notes |
|---|---|---|
| CSV | `.csv` | UTF-8 and Latin-1 encoding supported |
| Excel | `.xlsx` | All standard Excel workbooks |
| Legacy Excel | `.xls` | Older Excel format |

Maximum file size: **250 MB**

---

## How It Works

```
Upload file
    │
    ▼
Auto-detect column roles
(Measure / Category / Date / Geography / Identifier)
    │
    ▼
Generate sidebar slicers for all categorical + date columns
    │
    ▼
Compute KPIs from the primary measure column
    │
    ▼
Render Executive Overview (trend + distribution)
    │
    ▼
Visual Builder — user selects chart type, dimension, measure, aggregation
    │
    ▼
Data Quality panel + CSV download
```

---

## Project Structure

```
enterprise-analytics-dashboard/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes venv, data files, secrets
└── README.md           # This file
```

> **Note:** The `data/` folder and any uploaded CSV/Excel files are excluded from version control via `.gitignore`. Users upload their own data through the browser.

---

## License

MIT License — free to use, modify, and distribute.

---

## Author

Built with Streamlit and Plotly.  
Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).
