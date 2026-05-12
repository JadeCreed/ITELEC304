# FocusFlow Analytics System

FocusFlow is a Django-based screen time analytics app designed to help users understand their digital habits, identify productive vs distracting app usage, and improve focus through simple dashboards and reports.

## Features

- Track app usage by category and date
- Log screen time manually or import from CSV
- Dashboard with daily totals, most used app, productivity score, and focus/distraction split
- Analytics page with weekly trends, category distribution, and productivity score history
- Reports page with weekly summary and smart insights
- Activity log management with search, filter, sort, and delete

## Data Model

The app stores screen time records using the `ScreenTimeLog` model with:

- `app_name`
- `category` (`Study`, `Work`, `Social`, `Gaming`, `Entertainment`)
- `duration_minutes`
- `date`
- `notes`

## Productivity Logic

Productivity is calculated by weighting categories:

- `Study`: positive
- `Work`: positive
- `Social`: negative
- `Gaming`: negative
- `Entertainment`: neutral

The score is normalized to a 0–100 range, where a higher value means the user is spending more time on productive categories.

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install Django
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Run the app:

```powershell
python manage.py runserver
```

5. Open the site in your browser:

```
http://127.0.0.1:8000/
```

## Usage

- Use the Dashboard to view today’s total screen time, productivity score, and focus/distraction metrics.
- Add new logs via the `Add Screen Time Log` form.
- Upload CSV files from the `Import` page to populate data quickly.
- Use the Analytics page to inspect weekly trends, category breakdown, and productivity history.
- Use the Reports page for weekly summaries and automated insights.

## GitHub / Deployment Notes

- The repository uses SQLite by default (`db.sqlite3`).
- `db.sqlite3` and the local `venv/` folder are excluded by `.gitignore`.
- For production, switch to a production-ready database and configure allowed hosts in `focusflow/settings.py`.

## Project Structure

- `analytics/` – application logic, models, views, templates, and services
- `focusflow/` – project settings, URLs, and WSGI/ASGI entry points
- `manage.py` – Django management script
- `.gitignore` – excludes local environment files and database
- `README.md` – project overview and setup instructions

## Notes

- If you add more dependencies, save them to `requirements.txt` using:

```powershell
pip freeze > requirements.txt
```

- The app is ready for GitHub once the local environment and database are excluded.
