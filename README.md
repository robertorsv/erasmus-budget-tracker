# Erasmus Budget Tracker 💶

A mobile-first, zero-cost budget tracker tailored for Erasmus students. 
Strictly enforces a fixed monthly budget with real-time "burnt rate" calculation and category limits.

## Setup Instructions

### 1. Functionality
- **Track Expenses**: Log daily spendings in multiple currencies (EUR, CZK, PLN, etc.)
- **Budget Alerts**: Visual warnings when category limits are approached.
- **Zero Cost**: Built on Streamlit Community Cloud + Google Sheets.

### 2. Installation
1.  **Clone/Open** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Credentials**:
    -   You need a `credentials.json` file from Google Cloud.
    -   **[Read the Setup Guide Here](file:///C:/Users/Roberto/.gemini/antigravity/brain/ae1ef3ec-e3e4-46cb-b8fb-665a4f384536/google_sheets_setup.md)** to generate it.
    -   Place `credentials.json` inside the `.streamlit/` folder.

### 3. Running the App
```bash
streamlit run app.py
```

## Project Structure
- `app.py`: Main application interface.
- `budget_logic.py`: Core financial logic and currency conversion.
- `data_manager.py`: Google Sheets API handler.
