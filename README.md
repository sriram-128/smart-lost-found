# Smart Lost & Found Portal

A college-level web application that digitizes campus lost-and-found reporting. Students can report a lost or found item, upload an optional image, browse and filter items, and submit a claim. An administrator can remove fake reports and approve or reject claims.

## Features

- Login and logout with role-based administrator access
- Home page with welcome banner, project information, and live statistics
- Dashboard with lost/found/open/claimed totals and recent reports
- Lost or found report form with image upload
- Item search, category filters, detailed item views, and claims
- Admin moderation, claim approval/rejection, report deletion, and statistics
- SQLite database initialized automatically with safe demo accounts and data
- Responsive blue Streamlit interface with custom CSS

## Folder structure

```text
Smart-Lost-Found/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/config.toml
├── assets/uploads/
├── database/                 # lost_found.db is created automatically on first run
└── pages/README.md
```

## Installation and local run

1. Install Python 3.10 or newer.
2. Open a terminal in the `Smart-Lost-Found` folder.
3. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

4. Install packages and start the project:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. SQLite creates `database/lost_found.db` and the image folder automatically—no database server or configuration is required.

## Demo login accounts

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `admin123` |
| Student | `student` | `student123` |

For a real deployment, change the demo credentials before sharing the app.

## Deploy to Streamlit Community Cloud

1. Create a new GitHub repository and upload the contents of the `Smart-Lost-Found` folder.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and choose **Create app**.
3. Select the repository and branch.
4. Set the main file path to `app.py`.
5. Click **Deploy**. Streamlit reads `requirements.txt` automatically.

### SQLite note

The application needs no external database setup: it creates the SQLite file at startup. On Streamlit Community Cloud, files are stored on temporary disk and may reset after restarts or redeployments. This is suitable for a college demonstration. For permanent production data, replace SQLite with a managed database such as Supabase, PostgreSQL, or MySQL.

## Presentation material

The repository includes a 10-slide presentation, sample screenshots, a simple 8–10 minute presentation script, 20 viva questions, and 20 technical questions in the `presentation-materials` folder.
