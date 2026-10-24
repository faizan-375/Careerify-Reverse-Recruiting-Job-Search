# Careerify local job-search website

This version runs as a website on your laptop. FastAPI serves both the browser interface and the job-search API at `http://127.0.0.1:8000`; no Chrome extension is required.

## Structure

```text
careerify-job-search-webapp/
├── frontend/
│   ├── index.html       # Client profile form and results page
│   ├── styles.css       # Responsive website styling
│   └── app.js           # Browser storage, add-field UI, search and results
└── backend/
    ├── app/
    │   ├── main.py      # Serves website and proxies search requests to SerpApi
    │   ├── config.py    # Loads backend environment settings
    │   └── schemas.py   # Search request and job result models
    ├── .env.example     # Key template; copy this to .env
    ├── requirements.txt
    └── .gitignore
```

## Run on Windows in VS Code

Open the integrated terminal in VS Code and change to the `backend` folder. Set up the Python environment and install packages (if not already done):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and set `SERPAPI_API_KEY` to a newly generated key. Do not paste the key into the website files or share it in screenshots. Then start the local website:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep the terminal open and visit <http://127.0.0.1:8000>. The health endpoint is <http://127.0.0.1:8000/health>.

If PowerShell blocks virtual-environment activation, no activation command is needed; invoke Python from `.venv\Scripts\python.exe` as above.

## Profile and search behavior

- The provided profile is prefilled from the Careerify brief. Replace it for other clients.
- The form has an **Add field** button and a slider for 1–50 job results.
- Profile values are saved in the current browser's `localStorage` on this device. They are not sent to SerpApi. This storage is not encrypted; use a trusted local browser profile and clear its site data when appropriate.
- The backend sends target-role query text and job-search location/localization parameters to SerpApi. It keeps the key server-side in `.env`.
- Expected salary is not a Google Jobs API filter. Salary, work authorization, posting status, experience fit, and commute requirements must be verified manually on the employer's page.
- Search-result descriptions may be snippets. The page does not submit applications or claim that a result is still active.
- The backend filters excluded employer names from returned results. It can fetch up to 50 results across multiple SerpApi pages; each page may use a search credit.

The original browser-extension package is separate; this directory contains the local website version.
