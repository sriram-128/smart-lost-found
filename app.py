"""Smart Lost & Found Portal - deployable Streamlit application."""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DB_PATH = ROOT / "database" / "lost_found.db"
UPLOAD_DIR = ROOT / "assets" / "uploads"
CATEGORIES = ["All", "Electronics", "Documents", "Accessories", "Clothing", "Books", "Keys", "Other"]

st.set_page_config(page_title="Smart Lost & Found Portal", page_icon="🔎", layout="wide")


def inject_css() -> None:
    """Apply the blue, responsive visual theme."""
    st.markdown("""<style>
    .stApp { background: #f6f9ff; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#073b7a,#0e72d2); }
    [data-testid="stSidebar"] * { color: white !important; }
    .hero { padding: 3.2rem 3rem; border-radius: 24px; color: white;
      background: linear-gradient(120deg,#063a7a,#0878dc); margin-bottom: 1.4rem; }
    .hero h1 { font-size: 2.7rem; margin: 0 0 .5rem; }
    .hero p { font-size: 1.1rem; opacity: .95; margin: 0; }
    .section-title { color:#073b7a; font-weight:700; font-size:1.45rem; margin:1.2rem 0 .6rem; }
    .item-card { background:#fff; border:1px solid #dce8f8; border-radius:16px; padding:1.15rem;
      min-height:170px; box-shadow:0 4px 14px rgba(18,74,143,.07); margin-bottom:1rem; }
    .item-card h3 { color:#073b7a; margin:0 0 .4rem; }
    .badge { display:inline-block; border-radius:999px; padding:.18rem .6rem; background:#e4f1ff; color:#075db5; font-weight:600; font-size:.78rem; }
    .small-muted { color:#60718a; font-size:.9rem; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid #dce8f8; border-radius:14px; padding:1rem; }
    .stButton > button { border-radius:9px; border:0; background:#0878dc; color:white; font-weight:600; }
    </style>""", unsafe_allow_html=True)


def connection() -> sqlite3.Connection:
    """Open a database connection with dictionary-style rows."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_database() -> None:
    """Create schema and a small useful demo dataset on first run."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type TEXT NOT NULL CHECK(item_type IN ('Lost','Found')),
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            item_date TEXT NOT NULL,
            location TEXT NOT NULL,
            image_path TEXT,
            contact_number TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','Claimed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            claimant_id INTEGER NOT NULL,
            note TEXT,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES items(id),
            FOREIGN KEY(claimant_id) REFERENCES users(id)
        );
        """)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.executemany("INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)", [
                ("admin", hash_password("admin123"), "Portal Administrator", "admin"),
                ("student", hash_password("student123"), "Demo Student", "user"),
            ])
            conn.executemany("""INSERT INTO items(user_id,item_type,item_name,category,description,item_date,location,contact_number)
                VALUES(?,?,?,?,?,?,?,?)""", [
                (2, "Lost", "Blue Water Bottle", "Accessories", "Steel bottle with a blue silicone cover.", "2026-07-20", "College Library", "9876543210"),
                (2, "Found", "Wireless Earbuds Case", "Electronics", "Black charging case found near the computer lab.", "2026-07-22", "Computer Lab", "9876543210"),
                (2, "Lost", "Data Structures Notebook", "Books", "Black notebook with notes for Unit 3.", "2026-07-24", "Block A, Room 204", "9876543210"),
            ])


def query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with connection() as conn:
        return conn.execute(sql, params).fetchall()


def execute(sql: str, params: tuple = ()) -> None:
    with connection() as conn:
        conn.execute(sql, params)
        conn.commit()


def current_user() -> sqlite3.Row | None:
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    rows = query("SELECT * FROM users WHERE id=?", (user_id,))
    return rows[0] if rows else None


def stats() -> tuple[int, int, int, int]:
    with connection() as conn:
        return tuple(conn.execute("""SELECT
            SUM(item_type='Lost'), SUM(item_type='Found'), SUM(status='Open'), SUM(status='Claimed') FROM items""").fetchone())


def save_image(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    suffix = Path(uploaded_file.name).suffix.lower()
    filename = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOAD_DIR / filename
    with target.open("wb") as destination:
        shutil.copyfileobj(uploaded_file, destination)
    return str(target.relative_to(ROOT)).replace("\\", "/")


def login_page() -> None:
    st.title("Login")
    st.caption("Use the demo credentials: admin / admin123 or student / student123")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        rows = query("SELECT * FROM users WHERE username=? AND password_hash=?", (username.strip(), hash_password(password)))
        if rows:
            st.session_state.user_id = rows[0]["id"]
            st.success(f"Welcome, {rows[0]['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def home_page() -> None:
    lost, found, open_items, claimed = stats()
    st.markdown("""<div class="hero"><h1>SMART LOST &amp; FOUND PORTAL</h1>
    <p>A simple and secure way for students to report, discover, and recover belongings on campus.</p></div>""", unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("Lost Reports", lost or 0); b.metric("Found Reports", found or 0)
    c.metric("Open Items", open_items or 0); d.metric("Claimed Items", claimed or 0)
    st.markdown('<p class="section-title">About the project</p>', unsafe_allow_html=True)
    st.write("Smart Lost & Found Portal replaces notice-board searching with one organized digital space. Students can submit reports, search for matching items, and submit transparent claims. Administrators can moderate reports and approve genuine claims.")
    st.markdown('<p class="section-title">How it helps</p>', unsafe_allow_html=True)
    x, y, z = st.columns(3)
    x.info("📣 **Report quickly**\n\nAdd clear details, date, location, contact number, and an optional photo.")
    y.info("🔎 **Search easily**\n\nFilter reports by category and review complete item information.")
    z.info("✅ **Recover safely**\n\nClaims are reviewed by an administrator before an item is marked claimed.")


def dashboard_page() -> None:
    user = current_user()
    if not user: login_page(); return
    st.title("Dashboard")
    lost, found, open_items, claimed = stats()
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Total Lost", "Total Found", "Open", "Claimed"], [lost, found, open_items, claimed]):
        col.metric(label, value or 0)
    st.subheader("Recent Reports")
    reports = query("""SELECT i.*, u.full_name FROM items i JOIN users u ON i.user_id=u.id
                     ORDER BY i.created_at DESC LIMIT 8""")
    if reports:
        st.dataframe(pd.DataFrame([dict(r) for r in reports])[["item_name","item_type","category","location","status","item_date","full_name"]], use_container_width=True, hide_index=True)
    else: st.info("No reports have been submitted yet.")


def report_page() -> None:
    user = current_user()
    if not user: login_page(); return
    st.title("Report Lost / Found Item")
    st.caption("Provide accurate details so the item can be identified quickly.")
    with st.form("report_item", clear_on_submit=True):
        item_type = st.radio("Report type", ["Lost", "Found"], horizontal=True)
        item_name = st.text_input("Item Name", max_chars=80)
        category = st.selectbox("Category", CATEGORIES[1:])
        description = st.text_area("Description", max_chars=500, help="Mention color, brand, unique marks, or contents.")
        left, right = st.columns(2)
        item_date = left.date_input("Date", value=date.today(), max_value=date.today())
        location = right.text_input("Location", max_chars=100)
        upload = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png"])
        contact = st.text_input("Contact Number", max_chars=20)
        submitted = st.form_submit_button("Submit Report")
    if submitted:
        if not all([item_name.strip(), description.strip(), location.strip(), contact.strip()]):
            st.error("Please complete all required fields.")
        else:
            image_path = save_image(upload)
            execute("""INSERT INTO items(user_id,item_type,item_name,category,description,item_date,location,image_path,contact_number)
                VALUES(?,?,?,?,?,?,?,?,?)""", (user["id"], item_type, item_name.strip(), category, description.strip(), str(item_date), location.strip(), image_path, contact.strip()))
            st.success("Your report has been submitted successfully.")


def browse_page() -> None:
    user = current_user()
    st.title("Browse Items")
    left, right, status_col = st.columns([2, 1, 1])
    search = left.text_input("Search by item, description, or location")
    category = right.selectbox("Category", CATEGORIES)
    status = status_col.selectbox("Availability", ["Open", "All", "Claimed"])
    sql = "SELECT i.*, u.full_name FROM items i JOIN users u ON i.user_id=u.id WHERE 1=1"
    params: list[str] = []
    if search:
        sql += " AND (i.item_name LIKE ? OR i.description LIKE ? OR i.location LIKE ?)"; term = f"%{search}%"; params += [term, term, term]
    if category != "All": sql += " AND i.category=?"; params.append(category)
    if status != "All": sql += " AND i.status=?"; params.append(status)
    items = query(sql + " ORDER BY i.created_at DESC", tuple(params))
    if not items: st.info("No items match the current filters."); return
    for item in items:
        with st.container():
            c1, c2 = st.columns([1, 3])
            if item["image_path"] and (ROOT / item["image_path"]).exists(): c1.image(str(ROOT / item["image_path"]), use_container_width=True)
            else: c1.markdown("## 📦")
            c2.markdown(f"""<div class="item-card"><span class="badge">{item['item_type']} • {item['category']}</span>
                <h3>{item['item_name']}</h3><p>{item['description']}</p>
                <p class="small-muted">📍 {item['location']} &nbsp; | &nbsp; 📅 {item['item_date']} &nbsp; | &nbsp; Status: {item['status']}</p></div>""", unsafe_allow_html=True)
            with st.expander(f"View details — {item['item_name']}"):
                st.write(f"**Reported by:** {item['full_name']}")
                st.write(f"**Contact:** {item['contact_number']}")
                if user and item["status"] == "Open" and item["user_id"] != user["id"]:
                    with st.form(f"claim_{item['id']}"):
                        note = st.text_input("Why do you believe this item is yours?", key=f"note_{item['id']}")
                        if st.form_submit_button("Mark Item as Claimed"):
                            exists = query("SELECT id FROM claims WHERE item_id=? AND claimant_id=? AND status='Pending'", (item["id"], user["id"]))
                            if exists: st.warning("You already have a pending claim for this item.")
                            else:
                                execute("INSERT INTO claims(item_id,claimant_id,note) VALUES(?,?,?)", (item["id"], user["id"], note.strip()))
                                st.success("Claim submitted for administrator approval.")
                elif not user: st.info("Log in to submit a claim.")


def admin_page() -> None:
    user = current_user()
    if not user: login_page(); return
    if user["role"] != "admin": st.error("Administrator access is required."); return
    st.title("Admin Panel")
    lost, found, open_items, claimed = stats()
    a, b, c, d = st.columns(4)
    a.metric("Lost", lost or 0); b.metric("Found", found or 0); c.metric("Open", open_items or 0); d.metric("Claimed", claimed or 0)
    st.subheader("All Reports")
    reports = query("SELECT id,item_name,item_type,category,location,status,item_date FROM items ORDER BY created_at DESC")
    for report in reports:
        r1, r2 = st.columns([5, 1])
        r1.write(f"**#{report['id']} — {report['item_name']}** · {report['item_type']} · {report['category']} · {report['status']}")
        if r2.button("Delete", key=f"delete_{report['id']}"):
            execute("DELETE FROM claims WHERE item_id=?", (report["id"],)); execute("DELETE FROM items WHERE id=?", (report["id"],)); st.rerun()
    st.subheader("Pending Claims")
    claims = query("""SELECT c.*, i.item_name, u.full_name FROM claims c JOIN items i ON c.item_id=i.id
                    JOIN users u ON c.claimant_id=u.id WHERE c.status='Pending' ORDER BY c.created_at DESC""")
    if not claims: st.info("There are no pending claims.")
    for claim in claims:
        st.write(f"**{claim['full_name']}** claims **{claim['item_name']}**. Reason: {claim['note'] or 'Not provided'}")
        approve, reject = st.columns(2)
        if approve.button("Approve Claim", key=f"approve_{claim['id']}"):
            execute("UPDATE claims SET status='Approved' WHERE id=?", (claim["id"],)); execute("UPDATE items SET status='Claimed' WHERE id=?", (claim["item_id"],)); st.rerun()
        if reject.button("Reject Claim", key=f"reject_{claim['id']}"):
            execute("UPDATE claims SET status='Rejected' WHERE id=?", (claim["id"],)); st.rerun()


def main() -> None:
    init_database(); inject_css()
    user = current_user()
    with st.sidebar:
        st.markdown("## 🔎 Smart L&F")
        st.caption("Campus recovery made simple")
        page = st.radio("Navigation", ["Home", "Login", "Dashboard", "Report Lost Item", "Browse Items", "Admin Panel"])
        st.divider()
        if user:
            st.write(f"Signed in as **{user['full_name']}**")
            if st.button("Logout", use_container_width=True):
                st.session_state.clear(); st.rerun()
        else: st.caption("Please log in to submit reports or claims.")
    pages = {"Home": home_page, "Login": login_page, "Dashboard": dashboard_page, "Report Lost Item": report_page, "Browse Items": browse_page, "Admin Panel": admin_page}
    pages[page]()


if __name__ == "__main__": main()

import streamlit as st

st.sidebar.markdown("## 🔗 Project Links")
st.sidebar.markdown("[🌐 Live Demo](https://smart-lost-found-stpxdl4hxtbmzpxkunox5l.streamlit.app/)")
st.sidebar.markdown("[💻 GitHub Repository](https://github.com/sriram-128/smart-lost-found)")