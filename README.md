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

## Setup and run

### Requirements

- Python 3.10 or newer.
- A SerpApi account and API key to search for jobs. The website can load without a key, but job searches require one.
- The project files on your computer (download or clone this repository).

Open a terminal in the project folder, then change to the backend directory:

```text
cd backend
```

### Windows (PowerShell)

Run these commands from the `backend` directory. Create a virtual environment and install the required packages:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

In the `.env` file, set `SERPAPI_API_KEY` to your SerpApi API key, then save and close the file. Keep the key in this backend file; do not put it in frontend files or share it publicly.

Start the website from the same `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### macOS or Linux

Run these commands from the `backend` directory:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
nano .env
```

Set `SERPAPI_API_KEY` in `.env` to your SerpApi API key and save the file. Then start the website:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Open the website

Keep the terminal open while using the website and visit <http://127.0.0.1:8000>. The health check is at <http://127.0.0.1:8000/health>. To stop the server, press **Ctrl+C** in the terminal.

For later runs, open a terminal in the project folder, run `cd backend`, and repeat only the Uvicorn command for your operating system. The virtual environment and dependencies do not need to be recreated.

If the search reports an unsupported location, use a location accepted by SerpApi's location database. For example, the default Hillsboro location is `Hillsboro,Oregon,United States`.

## Profile and search behavior

- The provided profile is prefilled from the Careerify brief. Replace it for other clients.
- The form has an **Add field** button and a slider for 1–50 job results.
- Profile values are saved in the current browser's `localStorage` on this device. They are not sent to SerpApi. This storage is not encrypted; use a trusted local browser profile and clear its site data when appropriate.
- The backend sends target-role query text and job-search location/localization parameters to SerpApi. It keeps the key server-side in `.env`.
- Expected salary is not a Google Jobs API filter. Salary, work authorization, posting status, experience fit, and commute requirements must be verified manually on the employer's page.
- Search-result descriptions may be snippets. The page does not submit applications or claim that a result is still active.
- The backend filters excluded employer names from returned results. It can fetch up to 50 results across multiple SerpApi pages; each page may use a search credit.

The original browser-extension package is separate; this directory contains the local website version.
