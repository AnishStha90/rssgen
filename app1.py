#!/usr/bin/env python3
"""
RSS Feed Generator — v11 + Location-Based Approval System + Account-based Location Setup
Removed super_admin role. Reporters cannot scrape.
Migrated from SQLite to PostgreSQL.
"""

import json, os, re, sys, uuid, queue, threading, tempfile, random, string, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from urllib.parse import urljoin, urlparse

# ============================================================
# FIX: Load environment variables from .env file
# ============================================================
from dotenv import load_dotenv

# Load .env from the same directory as this script
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️ .env file not found at: {env_path}, using default location")
    load_dotenv()  # Try default location
# ============================================================

import psycopg2
import psycopg2.extras
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from flask import Flask, Response, abort, jsonify, render_template, request, stream_with_context, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from location_seed import seed_locations, build_location_label, location_scope_from_ids

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)

# ── PostgreSQL connection string from environment ─────────────────────────────
# Set DATABASE_URL like: postgresql://user:password@host:5432/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/rssgen")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify(error="Authentication required"), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# Only two admin roles now: admin (global) and location_admin
ADMIN_ROLES = {"admin", "location_admin"}

def is_admin_role(role: str | None) -> bool:
    return (role or "") in ADMIN_ROLES

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify(error="Authentication required"), 401
            return redirect(url_for("login"))
        if not is_admin_role(session.get("role")):
            return jsonify(error="Admin access required"), 403
        return f(*args, **kwargs)
    return decorated


_sse_clients = {}
_sse_lock = threading.Lock()

# Nepal Timezone (UTC+5:45)
NEPAL_TZ = timezone(timedelta(hours=5, minutes=45), name="Asia/Kathmandu")

def get_nepal_time():
    return datetime.now(NEPAL_TZ)

def to_nepal_time(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=NEPAL_TZ)
    return dt.astimezone(NEPAL_TZ)

def format_nepal_time(dt, format_str="%Y-%m-%d %H:%M:%S"):
    if dt is None:
        return ""
    nepali_dt = to_nepal_time(dt)
    return nepali_dt.strftime(format_str)

def _safe_int(value):
    try:
        if value is None or value == "":
            return None
        return int(value)
    except Exception:
        return None

def format_rfc822_nepal(dt):
    if dt is None:
        return ""
    nepali_dt = to_nepal_time(dt)
    return nepali_dt.strftime("%a, %d %b %Y %H:%M:%S +0545")

MAX_AGE_HOURS     = 24
REFRESH_MINS      = 15
DEFAULT_MAX_ITEMS = 9999

def _broadcast(event, data):
    with _sse_lock:
        dead = []
        for cid, q in _sse_clients.items():
            try:
                q.put_nowait({"event": event, "data": data})
            except queue.Full:
                dead.append(cid)
        for cid in dead:
            del _sse_clients[cid]

# ── PostgreSQL connection ─────────────────────────────────────────────────────

def get_db():
    """Return a new psycopg2 connection with RealDictCursor."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn

def _exec(conn, sql, params=()):
    """Execute a single statement and commit."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.commit()

def _fetchone(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()

def _fetchall(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# ── DB init ───────────────────────────────────────────────────────────────────

def init_db():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id           TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                source_url   TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                item_count   INTEGER DEFAULT 0,
                last_fetched TEXT,
                status       TEXT DEFAULT 'ok',
                last_error   TEXT,
                paused       INTEGER DEFAULT 0,
                custom_name  TEXT,
                max_items    INTEGER DEFAULT 9999,
                pub_date_iso TEXT
            );
            CREATE TABLE IF NOT EXISTS items (
                id           TEXT PRIMARY KEY,
                feed_id      TEXT NOT NULL,
                title        TEXT,
                link         TEXT UNIQUE,
                description  TEXT,
                body_html    TEXT,
                author       TEXT,
                publisher    TEXT,
                pub_date     TEXT,
                pub_date_iso TEXT,
                mod_date     TEXT,
                image        TEXT,
                categories   TEXT,
                guid         TEXT UNIQUE,
                fetched_at   TEXT,
                FOREIGN KEY(feed_id) REFERENCES feeds(id)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS users (
                id            TEXT PRIMARY KEY,
                username      TEXT UNIQUE NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                phone         TEXT,
                password_hash TEXT NOT NULL,
                role          TEXT DEFAULT 'reporter',
                created_at    TEXT NOT NULL,
                login_method  TEXT DEFAULT 'username'
            );
            CREATE TABLE IF NOT EXISTS manual_items (
                id                   TEXT PRIMARY KEY,
                title                TEXT NOT NULL,
                body_html            TEXT,
                description          TEXT,
                category             TEXT,
                tags                 TEXT,
                source_name          TEXT,
                source_url           TEXT,
                creator              TEXT,
                image                TEXT,
                pub_date             TEXT,
                pub_date_iso         TEXT,
                location             TEXT,
                country_id           INTEGER,
                province_id          INTEGER,
                district_id          INTEGER,
                local_level_id       INTEGER,
                ward_id              INTEGER,
                area_id              INTEGER,
                approval_scope_level TEXT,
                approval_scope_id    INTEGER,
                approval_count       INTEGER DEFAULT 0,
                required_approvals   INTEGER DEFAULT 2,
                link                 TEXT,
                guid                 TEXT UNIQUE,
                created_at           TEXT NOT NULL,
                submitted_by         TEXT,
                submitted_at         TEXT,
                approval_status      TEXT DEFAULT 'pending',
                approved_by          TEXT,
                approved_at          TEXT,
                approval_notes       TEXT,
                reporter_phone       TEXT,
                reporter_email       TEXT,
                submitted_by_user_id TEXT
            );
            CREATE TABLE IF NOT EXISTS news_approvals (
                id         TEXT PRIMARY KEY,
                news_id    TEXT NOT NULL,
                admin_id   TEXT NOT NULL,
                action     TEXT NOT NULL,
                comment    TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(news_id, admin_id)
            );
            CREATE TABLE IF NOT EXISTS admin_locations (
                id             SERIAL PRIMARY KEY,
                user_id        TEXT NOT NULL,
                country_id     INTEGER,
                province_id    INTEGER,
                district_id    INTEGER,
                local_level_id INTEGER,
                ward_id        INTEGER,
                area_id        INTEGER,
                created_at     TEXT NOT NULL
            );
            """)

            # Add columns if missing (idempotent migrations)
            migrations = [
                ("feeds",        "pub_date_iso",        "TEXT"),
                ("feeds",        "paused",              "INTEGER DEFAULT 0"),
                ("feeds",        "custom_name",         "TEXT"),
                ("feeds",        "max_items",           "INTEGER DEFAULT 9999"),
                ("manual_items", "submitted_by",        "TEXT"),
                ("manual_items", "submitted_at",        "TEXT"),
                ("manual_items", "approval_status",     "TEXT DEFAULT 'pending'"),
                ("manual_items", "approved_by",         "TEXT"),
                ("manual_items", "approved_at",         "TEXT"),
                ("manual_items", "approval_notes",      "TEXT"),
                ("manual_items", "reporter_phone",      "TEXT"),
                ("manual_items", "reporter_email",      "TEXT"),
                ("manual_items", "submitted_by_user_id","TEXT"),
                ("manual_items", "country_id",          "INTEGER"),
                ("manual_items", "province_id",         "INTEGER"),
                ("manual_items", "district_id",         "INTEGER"),
                ("manual_items", "local_level_id",      "INTEGER"),
                ("manual_items", "ward_id",             "INTEGER"),
                ("manual_items", "area_id",             "INTEGER"),
                ("manual_items", "approval_scope_level","TEXT"),
                ("manual_items", "approval_scope_id",   "INTEGER"),
                ("manual_items", "approval_count",      "INTEGER DEFAULT 0"),
                ("manual_items", "required_approvals",  "INTEGER DEFAULT 2"),
                ("users",        "login_method",        "TEXT DEFAULT 'username'"),
            ]
            for table, col, coldef in migrations:
                try:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {coldef}")
                except Exception:
                    conn.rollback()

            # Fix up submitted_by_user_id from reporter_email
            try:
                cur.execute("""
                    UPDATE manual_items
                    SET submitted_by_user_id = (
                        SELECT id FROM users WHERE users.email = manual_items.reporter_email
                    )
                    WHERE (submitted_by_user_id IS NULL OR submitted_by_user_id = '')
                      AND reporter_email IS NOT NULL AND reporter_email != ''
                      AND EXISTS (SELECT 1 FROM users WHERE users.email = manual_items.reporter_email)
                """)
            except Exception:
                conn.rollback()

        conn.commit()
        seed_locations(conn)
        conn.commit()
    finally:
        conn.close()

init_db()

def _ensure_default_admin():
    conn = get_db()
    try:
        existing = _fetchone(conn, "SELECT id FROM users LIMIT 1")
        if not existing:
            now = get_nepal_time().isoformat()
            _exec(conn,
                "INSERT INTO users (id,username,email,phone,password_hash,role,created_at,login_method) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (str(uuid.uuid4()), "nabin", "nabin@rssgen.local", "", generate_password_hash("password"), "admin", now, "admin_created")
            )
    finally:
        conn.close()

_ensure_default_admin()

def _load_settings():
    global MAX_AGE_HOURS, REFRESH_MINS, DEFAULT_MAX_ITEMS
    conn = get_db()
    try:
        rows = _fetchall(conn, "SELECT key, value FROM settings")
    finally:
        conn.close()
    d = {r["key"]: r["value"] for r in rows}
    if "REFRESH_MINS"  in d: REFRESH_MINS  = int(d["REFRESH_MINS"])
    if "MAX_AGE_HOURS" in d: MAX_AGE_HOURS = int(d["MAX_AGE_HOURS"])
    if "MAX_ITEMS"     in d: DEFAULT_MAX_ITEMS = int(d["MAX_ITEMS"])

def _get_drive_config():
    conn = get_db()
    try:
        rows = _fetchall(conn, "SELECT key, value FROM settings WHERE key IN (%s,%s)",
                         ("GOOGLE_DRIVE_FOLDER_ID", "GOOGLE_SERVICE_ACCOUNT_JSON"))
    finally:
        conn.close()
    d = {r["key"]: r["value"] for r in rows}
    folder_id  = d.get("GOOGLE_DRIVE_FOLDER_ID","").strip() or os.environ.get("GOOGLE_DRIVE_FOLDER_ID","").strip()
    sa_json    = d.get("GOOGLE_SERVICE_ACCOUNT_JSON","").strip() or ""
    if not sa_json:
        sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT","").strip()
        if sa_path and os.path.isfile(sa_path):
            try:
                with open(sa_path) as f:
                    sa_json = f.read().strip()
            except Exception:
                pass
    return folder_id, sa_json

def drive_configured():
    folder_id, sa_json = _get_drive_config()
    return bool(folder_id and sa_json)

def _title_to_filename(title, ext):
    slug = re.sub(r'[^\w\s-]', '', (title or 'image'), flags=re.UNICODE)
    slug = re.sub(r'[\s_]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug).strip('-').lower()
    slug = slug[:60] or 'image'
    return f"{slug}.{ext}"

_load_settings()

# ── LOCATION HELPER ────────────────────────────────────────────
def user_has_location(user_id):
    conn = get_db()
    try:
        row = _fetchone(conn, "SELECT 1 FROM admin_locations WHERE user_id=%s LIMIT 1", (user_id,))
    finally:
        conn.close()
    return row is not None

def get_user_location(user_id):
    conn = get_db()
    try:
        row = _fetchone(conn, """
            SELECT country_id, province_id, district_id, local_level_id, ward_id, area_id
            FROM admin_locations WHERE user_id=%s
        """, (user_id,))
        if not row:
            return None
        return build_location_label(conn, row['country_id'], row['province_id'], row['district_id'],
                                    row['local_level_id'], row['ward_id'], row['area_id'],
                                    fallback="Assigned location")
    finally:
        conn.close()

def get_user_location_object(user_id):
    conn = get_db()
    try:
        return _fetchone(conn, """
            SELECT country_id, province_id, district_id, local_level_id, ward_id, area_id
            FROM admin_locations WHERE user_id=%s
        """, (user_id,))
    finally:
        conn.close()

_otp_store = {}
_otp_lock  = threading.Lock()

def _get_smtp_config():
    conn = get_db()
    try:
        rows = _fetchall(conn, "SELECT key,value FROM settings WHERE key IN (%s,%s,%s,%s,%s)",
                         ("SMTP_HOST","SMTP_PORT","SMTP_USER","SMTP_PASS","SMTP_FROM"))
    finally:
        conn.close()
    return {r["key"]: r["value"] for r in rows}

def _send_otp_email(to_email, otp):
    cfg = _get_smtp_config()
    host = cfg.get("SMTP_HOST","").strip()
    port = int(cfg.get("SMTP_PORT","587") or 587)
    user = cfg.get("SMTP_USER","").strip()
    pwd  = cfg.get("SMTP_PASS","").strip()
    frm  = cfg.get("SMTP_FROM","").strip() or user
    if not (host and user and pwd):
        return False, "SMTP not configured"
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "RSS/gen — Your OTP verification code"
        msg["From"]    = frm
        msg["To"]      = to_email
        html = f"""<div style="font-family:sans-serif;max-width:420px;margin:auto">
          <h2 style="color:#4ade80">RSS/gen Verification</h2>
          <p>Your one-time password is:</p>
          <div style="font-size:2rem;font-weight:bold;letter-spacing:.3em;color:#1a1d27;
               background:#4ade80;padding:1rem 2rem;border-radius:8px;display:inline-block">{otp}</div>
          <p style="color:#64748b;font-size:.85rem">This code expires in 10 minutes. Do not share it.</p>
        </div>"""
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(host, port, timeout=10) as srv:
            srv.starttls()
            srv.login(user, pwd)
            srv.sendmail(frm, [to_email], msg.as_string())
        return True, "sent"
    except Exception as e:
        return False, str(e)

def _generate_otp(identifier, reg_data):
    otp = "".join(random.choices(string.digits, k=6))
    expires = datetime.now(timezone.utc).timestamp() + 600
    with _otp_lock:
        _otp_store[identifier] = {"otp": otp, "expires_at": expires, "data": reg_data}
    return otp

def _verify_otp(identifier, otp_input):
    with _otp_lock:
        entry = _otp_store.get(identifier)
        if not entry:
            return False, None, "OTP not found or expired"
        if datetime.now(timezone.utc).timestamp() > entry["expires_at"]:
            del _otp_store[identifier]
            return False, None, "OTP expired"
        if entry["otp"] != otp_input.strip():
            return False, None, "Incorrect OTP"
        data = entry["data"]
        del _otp_store[identifier]
    return True, data, "ok"

def _validate_password_strength(pw):
    if len(pw) < 12:
        return "Password must be at least 12 characters."
    if not re.search(r'[A-Z]', pw):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', pw):
        return "Password must contain at least one number."
    if not re.search(r'[^A-Za-z0-9]', pw):
        return "Password must contain at least one special character."
    return None

def _validate_email(email):
    return bool(re.fullmatch(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', email))

def _validate_phone(phone):
    return bool(re.fullmatch(r'\+[1-9]\d{6,14}', phone.replace(" ", "").replace("-", "")))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ne-NP,ne;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

HEADERS_ALT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch_url(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code in (403, 429, 503):
            raise requests.HTTPError(f"{r.status_code} {r.reason}", response=r)
        r.raise_for_status()
    except requests.HTTPError:
        r = requests.get(url, headers=HEADERS_ALT, timeout=timeout, allow_redirects=True)
        r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r

def _text(tag): return tag.get_text(strip=True) if tag else ""

def _meta(soup, *names):
    for name in names:
        t = (soup.find("meta", attrs={"name": name})
             or soup.find("meta", attrs={"property": name})
             or soup.find("meta", attrs={"itemprop": name}))
        if t and t.get("content", "").strip():
            return t["content"].strip()
    return ""

def _ld_json(soup):
    blocks = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(tag.string or "{}")
            blocks.extend(d if isinstance(d, list) else [d])
        except Exception:
            pass
    return blocks

def _find_ld(blocks, *types):
    for b in blocks:
        bt = b.get("@type", "")
        if isinstance(bt, list): bt = " ".join(bt)
        if any(t.lower() in bt.lower() for t in types):
            return b
    return {}

_URL_DATE_RE = re.compile(r"/(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})[/\-?]")
_BS_YEAR_MIN, _BS_YEAR_MAX = 2070, 2090

def _date_from_url(url):
    m = _URL_DATE_RE.search(url)
    if m:
        year = int(m.group(1))
        if _BS_YEAR_MIN <= year <= _BS_YEAR_MAX:
            return None
        try:
            return datetime(year, int(m.group(2)), int(m.group(3)), tzinfo=NEPAL_TZ)
        except ValueError:
            pass
    return None

def _parse_dt(raw):
    if not raw: return None
    try:
        dt = dateparser.parse(str(raw))
        if dt:
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=NEPAL_TZ)
            else:
                dt = dt.astimezone(NEPAL_TZ)
        return dt
    except Exception:
        return None

def _rfc822(raw):
    if not raw: return ""
    dt = _parse_dt(raw)
    if dt:
        nepali_dt = to_nepal_time(dt)
        return format_rfc822_nepal(nepali_dt)
    return ""

def _is_within_24h(url, pub_raw=None):
    cutoff = get_nepal_time() - timedelta(hours=MAX_AGE_HOURS)
    if pub_raw:
        dt = _parse_dt(pub_raw)
        if dt:
            return dt >= cutoff
    dt = _date_from_url(url)
    if dt:
        day_end = dt.replace(hour=23, minute=59, second=59)
        if day_end < cutoff:
            return False
        return None
    return None

# ── UNIVERSAL ARTICLE EXTRACTOR ───────────────────────────────

def _get_author(ld, soup):
    a = ld.get("author", "")
    if isinstance(a, dict):  return a.get("name", "")
    if isinstance(a, list):  return ", ".join(x.get("name","") if isinstance(x,dict) else str(x) for x in a)
    if a: return str(a)
    for sel in [
        {"itemprop": "author"},
        {"rel": "author"},
        {"class": re.compile(r"author|byline|writer|reporter|journalist", re.I)},
    ]:
        tag = soup.find(attrs=sel)
        if tag:
            t = _text(tag)
            if t and 2 < len(t) < 80:
                return t
    return _meta(soup, "author", "DC.creator", "article:author") or ""

_GENERIC_CAT_WORDS = {
    "news", "online news", "latest news", "breaking news", "nepal news",
    "nepali news", "article", "articles", "online", "today", "update",
    "updates", "home", "video", "videos", "photo", "photos", "general",
}

def _category_from_url(url, site_name=""):
    try:
        path = urlparse(url).path.strip("/")
        if not path: return ""
        first = path.split("/")[0]
        if not first or first.isdigit(): return ""
        if not re.match(r"^[A-Za-z][A-Za-z0-9_-]{1,30}$", first): return ""
        label = first.replace("-", " ").replace("_", " ").strip()
        if label.lower() in _GENERIC_CAT_WORDS: return ""
        if site_name and label.lower() == site_name.lower(): return ""
        return label
    except Exception:
        return ""

def _get_categories(ld, soup, url="", site_name=""):
    out = []
    url_cat = _category_from_url(url, site_name)
    if url_cat: out.append(url_cat)
    cats = ld.get("articleSection", [])
    if isinstance(cats, str): cats = [cats]
    out += [c.strip() for c in cats if c and c.strip()]
    kw = ld.get("keywords", "")
    if isinstance(kw, str): kw = [k.strip() for k in kw.split(",") if k.strip()]
    meta_kw = _meta(soup, "keywords", "news_keywords")
    if meta_kw: kw += [k.strip() for k in meta_kw.split(",") if k.strip()]
    for k in kw:
        if not k or len(k) > 25: continue
        if k.lower() in _GENERIC_CAT_WORDS: continue
        if site_name and k.lower() == site_name.lower(): continue
        out.append(k)
    seen, deduped = set(), []
    for c in out:
        key = c.lower()
        if key in seen: continue
        seen.add(key)
        deduped.append(c)
    return deduped[:8]

def _clean_title(raw, site_name=""):
    t = raw.strip()
    for sep in [" - ", " | ", " – ", " — ", " :: ", " • "]:
        if site_name:
            if t.endswith(sep + site_name):
                t = t[:-(len(sep)+len(site_name))].strip(); break
            if t.startswith(site_name + sep):
                t = t[len(site_name)+len(sep):].strip(); break
    return t or raw

def _get_image_from_body(body_tag, base_url):
    if not body_tag: return ""
    for attr in ("data-src", "data-lazy-src", "data-original", "data-lazy", "data-image", "src"):
        tag = body_tag.find("img", attrs={attr: True})
        if tag:
            src = tag.get(attr, "")
            if src and not src.startswith("data:") and len(src) > 10:
                return urljoin(base_url, src) if not src.startswith("http") else src
    return ""

def _get_best_image(ld, soup, body_tag, url):
    image = ""
    img_ld = ld.get("image", "")
    if isinstance(img_ld, dict):   image = img_ld.get("url", "")
    elif isinstance(img_ld, list) and img_ld:
        first = img_ld[0]; image = first.get("url","") if isinstance(first,dict) else str(first)
    elif isinstance(img_ld, str):  image = img_ld
    if not image: image = _meta(soup, "og:image", "twitter:image")
    if not image: image = _get_image_from_body(body_tag, url)
    if not image:
        fig = soup.find("figure")
        if fig:
            img_tag = fig.find("img")
            if img_tag:
                image = (img_tag.get("data-src") or img_tag.get("data-lazy-src") or img_tag.get("src",""))
    if image and not image.startswith("http"): image = urljoin(url, image)
    if image and re.search(r"[?&](w|h|width|height)=1\b", image): image = ""
    return image

def _get_pub_raw(ld, soup, url):
    pub = ld.get("datePublished", "")
    if pub: return pub
    for name in ("article:published_time", "datePublished", "DC.date",
                 "pubdate", "date", "publish_date", "publication_date",
                 "article:published", "og:article:published_time"):
        v = _meta(soup, name)
        if v: return v
    for time_tag in soup.find_all("time", attrs={"datetime": True}):
        v = time_tag.get("datetime", "").strip()
        if v and len(v) >= 10: return v
    for time_tag in soup.find_all("time"):
        v = _text(time_tag)
        if v and re.search(r"\d{4}", v): return v
    tag = soup.find(attrs={"itemprop": re.compile(r"datePublished|dateCreated", re.I)})
    if tag:
        v = tag.get("content","") or tag.get("datetime","") or _text(tag)
        if v: return v
    m = _URL_DATE_RE.search(url)
    if m:
        return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    return ""

def _get_body(soup):
    body_tag = soup.find("article")
    if not body_tag:
        patterns = re.compile(
            r"(article|story|news|post|entry|content|detail|khabar|samachar"
            r"|news[\-_]?body|article[\-_]?body|post[\-_]?body|story[\-_]?body"
            r"|full[\-_]?story|article[\-_]?text|story[\-_]?text|single[\-_]?post"
            r"|entry[\-_]?content|td[\-_]?post[\-_]?content"
            r"|description|article-description)"
            r"[\-_]?(body|text|content|wrap|detail|inner|area|section|page)?",
            re.I
        )
        body_tag = (
            soup.find(class_=patterns) or
            soup.find(id=patterns)
        )
    if not body_tag:
        body_tag = soup.find(attrs={"itemprop": re.compile(r"articleBody", re.I)})
    if not body_tag:
        body_tag = soup.find("main")
    if not body_tag:
        candidates = []
        for div in soup.find_all("div"):
            ps = div.find_all("p", recursive=False)
            if len(ps) >= 2:
                text_len = len(div.get_text(" ", strip=True))
                candidates.append((text_len, div))
        if candidates:
            body_tag = max(candidates, key=lambda x: x[0])[1]
    if body_tag:
        for noise in body_tag.find_all(
            ["script","style","nav","aside","iframe","noscript","form","footer"],
        ):
            noise.decompose()
        for noise in body_tag.find_all(
            class_=re.compile(r"ad|sponsor|promo|social|share|comment|related|sidebar|widget|banner|tag[\-_]?cloud", re.I)
        ):
            noise.decompose()
        body_html = str(body_tag)
        body_text = body_tag.get_text(" ", strip=True)
        return body_tag, body_html, body_text
    return None, "", ""

def is_real_article(soup):
    ld_blocks = _ld_json(soup)
    has_article_ld = bool(_find_ld(ld_blocks, "NewsArticle", "Article", "BlogPosting",
                                    "ReportageNewsArticle", "LiveBlogPosting"))
    og_type = (soup.find("meta", attrs={"property": "og:type"}) or {}).get("content", "").lower()
    is_article_og = "article" in og_type
    _, _, body_text = _get_body(soup)
    body_length = len(body_text)
    h1_tag = soup.find("h1")
    h1_text = _text(h1_tag) if h1_tag else ""
    article_links = 0
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if ("/story/" in href or "/news/" in href or "/article/" in href or
            re.search(r"/\d{4}/\d{1,2}/", href) or
            re.search(r"/[^/]+-\d+\.html?$", href)):
            article_links += 1
            if article_links >= 3:
                break
    if article_links >= 5:
        return False
    if has_article_ld and body_length > 200:
        return True
    if is_article_og and body_length > 200:
        return True
    p_tags = soup.find_all("p")
    meaningful_ps = [p for p in p_tags if len(_text(p)) > 50]
    if len(meaningful_ps) >= 3 and body_length > 400:
        return True
    generic_h1 = ["news", "home", "blog", "articles", "latest", "trending",
                  "popular", "featured", "category", "archive"]
    if h1_text and h1_text.lower() not in generic_h1 and len(h1_text) > 10 and body_length > 300:
        return True
    list_classes = ["list-group", "list-item", "media-list", "article-list",
                    "post-list", "news-list", "row", "grid"]
    for cls in list_classes:
        if soup.find(class_=re.compile(cls, re.I)):
            if article_links >= 2:
                return False
    if body_length > 500 and len(meaningful_ps) >= 2:
        return True
    return body_length > 400

def extract_article(url, soup):
    ld_blocks = _ld_json(soup)
    ld = _find_ld(ld_blocks, "NewsArticle", "Article", "BlogPosting",
                  "WebPage", "ReportageNewsArticle", "LiveBlogPosting")
    site_name = _meta(soup, "og:site_name") or urlparse(url).netloc
    title = ld.get("headline", "")
    if not title or len(title) < 5:
        title = _meta(soup, "og:title", "twitter:title", "")
    if not title or len(title) < 5:
        h1 = soup.find("h1")
        if h1: title = _text(h1)
    if not title or len(title) < 5:
        title = _clean_title(_text(soup.find("title") or ""), site_name)
    generic_titles = ["home", "news", "nagarik news", "latest news", "breaking news",
                      "trending", "popular", "featured", "videos", "photos"]
    if title.lower() in generic_titles or len(title) < 5:
        title = "(No title)"
    title = _clean_title(title, site_name)
    body_tag, body_html, body_text = _get_body(soup)
    if body_tag and len(body_text) < 100:
        return None
    author = _get_author(ld, soup)
    pub_raw = _get_pub_raw(ld, soup, url)
    image = _get_best_image(ld, soup, body_tag, url)
    description = (ld.get("description")
                   or _meta(soup, "og:description", "twitter:description", "description")
                   or "").strip()
    if len(description) > 300: description = description[:297] + "…"
    if not description and body_text:
        words = body_text.split()
        description = " ".join(words[:40]) + ("…" if len(words) > 40 else "")
    pub_ld = ld.get("publisher", {})
    publisher = (pub_ld.get("name","") if isinstance(pub_ld, dict) else "")
    if not publisher:
        publisher = _meta(soup, "og:site_name", "DC.publisher") or urlparse(url).netloc
    mod_raw = (ld.get("dateModified") or _meta(soup, "article:modified_time", "DC.modified"))
    canonical = ld.get("url","")
    cl = soup.find("link", rel="canonical")
    if cl and cl.get("href"): canonical = cl["href"]
    if not canonical: canonical = url
    pub_dt = _parse_dt(pub_raw)
    if pub_dt:
        nepali_pub_dt = to_nepal_time(pub_dt)
        pub_date_rfc = format_rfc822_nepal(nepali_pub_dt)
        pub_date_iso = nepali_pub_dt.isoformat()
    else:
        pub_date_rfc = ""
        pub_date_iso = ""
    mod_dt = _parse_dt(mod_raw)
    mod_date_rfc = format_rfc822_nepal(mod_dt) if mod_dt else ""
    categories = _get_categories(ld, soup, url=url, site_name=site_name)
    return dict(title=title, link=canonical, guid=canonical,
                description=description or "",
                body_html=body_html, author=author or "",
                pub_date=pub_date_rfc, pub_date_iso=pub_date_iso,
                mod_date=mod_date_rfc, publisher=publisher,
                image=image, categories=categories)

def _base_domain(netloc):
    parts = netloc.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else netloc

def get_article_links(base_url, soup, stats=None):
    if stats is not None:
        stats.setdefault("candidates", 0)
        stats.setdefault("skipped_old", 0)
        stats.setdefault("used_fallback", False)
    seen, results = set(), []
    base_domain = _base_domain(urlparse(base_url).netloc)
    base_norm = base_url.rstrip("/")
    ART_PATTERNS = [
        r"/\d{4}/\d{2}/",
        r"/\d{4}/\d{1,2}/\d{1,2}/",
        r"/(?:story|article|news|post|detail|content|read|khabar|samachar|news-detail|fullnews|full-news)/\w",
        r"/[a-z0-9][a-z0-9-]{12,}/?$",
        r"-\d{4,}",
        r"/\d{5,}(?:[/?]|$)",
        r"/[^/]+-\d{3,}",
        r"/np/\w",
        r"\.html$",
        r"\.php\?id=\d+",
    ]
    _ART_RE = re.compile("|".join(ART_PATTERNS), re.I)
    SKIP_PATTERNS = [
        r"/(?:wp-content|wp-json|tag|category|author|search|page/\d+|feed|login|register|cart|checkout|cdn-cgi)/",
        r"/\?s=",
        r"/page/\d+/?$",
        r"/comments",
        r"/print/",
    ]
    _SKIP_RE = re.compile("|".join(SKIP_PATTERNS), re.I)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")): continue
        href = urljoin(base_url, href)
        p = urlparse(href)
        if _base_domain(p.netloc) != base_domain: continue
        if _SKIP_RE.search(p.path): continue
        if href in seen: continue
        full_path = p.path + ("?" + p.query if p.query else "")
        is_article_link = bool(_ART_RE.search(full_path))
        link_text = _text(a)
        is_long_text = len(link_text) > 20
        if not is_article_link and not is_long_text: continue
        seen.add(href)
        if stats is not None: stats["candidates"] += 1
        pub_hint = ""
        parent = a.parent
        for _ in range(4):
            if parent is None: break
            time_el = parent.find("time", attrs={"datetime": True})
            if time_el:
                pub_hint = time_el.get("datetime","")
                break
            for attr in ("data-date", "data-time", "data-published"):
                v = parent.get(attr,"")
                if v: pub_hint = v; break
            if pub_hint: break
            parent = parent.parent
        freshness = _is_within_24h(href, pub_hint)
        if freshness is False:
            if stats is not None: stats["skipped_old"] += 1
            continue
        results.append((href, pub_hint))
    if not results:
        if stats is not None: stats["used_fallback"] = True
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")): continue
            href = urljoin(base_url, href)
            p = urlparse(href)
            if _base_domain(p.netloc) != base_domain: continue
            if _SKIP_RE.search(p.path): continue
            if href in seen: continue
            if href.rstrip("/") in (base_norm, ""): continue
            if len(p.path.strip("/")) < 3: continue
            text = _text(a)
            if len(text) < 5: continue
            seen.add(href)
            if stats is not None: stats["candidates"] += 1
            pub_hint = ""
            parent = a.parent
            for _ in range(4):
                if parent is None: break
                time_el = parent.find("time", attrs={"datetime": True})
                if time_el:
                    pub_hint = time_el.get("datetime", "")
                    break
                for attr in ("data-date", "data-time", "data-published"):
                    v = parent.get(attr, "")
                    if v: pub_hint = v; break
                if pub_hint: break
                parent = parent.parent
            freshness = _is_within_24h(href, pub_hint)
            if freshness is False:
                if stats is not None: stats["skipped_old"] += 1
                continue
            results.append((href, pub_hint))
    return results

def purge_old_items(feed_id=None):
    cutoff = (get_nepal_time() - timedelta(hours=MAX_AGE_HOURS)).isoformat()
    earlier_expr = """
        CASE
          WHEN NULLIF(pub_date_iso,'') IS NULL THEN fetched_at
          WHEN NULLIF(fetched_at,'')   IS NULL THEN pub_date_iso
          WHEN pub_date_iso < fetched_at        THEN pub_date_iso
          ELSE fetched_at
        END
    """
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if feed_id:
                cur.execute(
                    f"DELETE FROM items WHERE feed_id=%s AND ({earlier_expr}) < %s",
                    (feed_id, cutoff)
                )
                cur.execute("UPDATE feeds SET item_count=(SELECT COUNT(*) FROM items WHERE feed_id=%s) WHERE id=%s",
                            (feed_id, feed_id))
            else:
                cur.execute(f"DELETE FROM items WHERE ({earlier_expr}) < %s", (cutoff,))
                cur.execute("UPDATE feeds SET item_count=(SELECT COUNT(*) FROM items WHERE feed_id=id)")
        conn.commit()
    finally:
        conn.close()

def insert_articles(feed_id, articles):
    added = 0
    now_nepal = get_nepal_time()
    cutoff    = now_nepal - timedelta(hours=MAX_AGE_HOURS)
    conn = get_db()
    try:
        with conn.cursor() as cur:
            for art in articles:
                pub_dt = _parse_dt(art.get("pub_date_iso") or art.get("pub_date",""))
                if pub_dt:
                    if pub_dt < cutoff:
                        continue
                else:
                    has_body  = bool((art.get("body_html") or "").strip())
                    has_desc  = bool((art.get("description") or "").strip())
                    has_title = bool((art.get("title") or "").strip())
                    if not has_body and not has_desc and not has_title:
                        continue
                    pub_dt = now_nepal
                    art["pub_date"]     = format_datetime(pub_dt)
                    art["pub_date_iso"] = pub_dt.isoformat()
                if not art.get("pub_date"):
                    art["pub_date"]     = format_datetime(pub_dt)
                    art["pub_date_iso"] = pub_dt.isoformat()
                existing = _fetchone(conn, "SELECT 1 FROM items WHERE guid=%s OR link=%s",
                                     (art["guid"], art["link"]))
                if existing: continue
                cur.execute(
                    """INSERT INTO items
                       (id, feed_id, title, link, description, body_html, author, publisher,
                        pub_date, pub_date_iso, mod_date, image, categories, guid, fetched_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT DO NOTHING""",
                    (str(uuid.uuid4()), feed_id, art["title"], art["link"],
                     art["description"], art["body_html"], art["author"], art["publisher"],
                     art["pub_date"], art.get("pub_date_iso",""), art["mod_date"], art["image"],
                     json.dumps(art["categories"]), art["guid"], now_nepal.isoformat())
                )
                added += 1
            if added:
                cur.execute(
                    "UPDATE feeds SET item_count=(SELECT COUNT(*) FROM items WHERE feed_id=%s), last_fetched=%s WHERE id=%s",
                    (feed_id, now_nepal.isoformat(), feed_id)
                )
        conn.commit()
    finally:
        conn.close()
    return added

def _fetch_and_extract_article(link):
    try:
        r2 = fetch_url(link, timeout=10)
        s2 = BeautifulSoup(r2.text, "lxml")
        if is_listing(s2) and not is_real_article(s2):
            return None
        art = extract_article(link, s2)
        if not art or not art.get("title") or art.get("title") == "(No title)":
            return None
        if art.get("body_html") and len(art.get("body_html", "")) < 200:
            return None
        pub_dt = _parse_dt(art.get("pub_date_iso") or art.get("pub_date",""))
        if pub_dt:
            cutoff = get_nepal_time() - timedelta(hours=MAX_AGE_HOURS)
            if pub_dt < cutoff:
                return None
        return art
    except Exception:
        return None

MAX_LINKS_PER_PAGE = 60
SCRAPE_WORKERS     = 10

def is_listing(soup):
    links = soup.find_all("a", href=True)
    article_links = sum(1 for a in links if re.search(r"/\d{4}/\d{2}/|/(?:story|article|news|post)/", a["href"]))
    if article_links >= 3:
        return True
    content_links = [a for a in links if len(_text(a)) > 20 and
                     not a.get("href","").startswith(("#","mailto:","tel:"))]
    return len(content_links) >= 5

def process_url(url, feed_name, max_items, progress_cb=None):
    try:
        if progress_cb: progress_cb("fetching", f"Fetching {url}…")
        resp = fetch_url(url)
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        if is_listing(soup):
            link_pairs = get_article_links(url, soup)
            cap = MAX_LINKS_PER_PAGE
            if max_items and max_items < MAX_LINKS_PER_PAGE:
                cap = min(MAX_LINKS_PER_PAGE, max_items * 2)
            link_pairs = link_pairs[:cap]
            total = len(link_pairs)
            done = 0
            if progress_cb: progress_cb("scraping", f"Article 0/{total}")
            with ThreadPoolExecutor(max_workers=SCRAPE_WORKERS) as ex:
                futures = {ex.submit(_fetch_and_extract_article, link): link
                           for link, _pub_hint in link_pairs}
                for fut in as_completed(futures):
                    done += 1
                    if progress_cb: progress_cb("scraping", f"Article {done}/{total}")
                    try:
                        art = fut.result()
                    except Exception:
                        art = None
                    if art:
                        articles.append(art)
        else:
            if progress_cb: progress_cb("scraping", "Extracting article…")
            art = extract_article(url, soup)
            if art:
                articles.append(art)
        if not articles:
            return None, None, 0, "No articles within last 24h could be extracted"
        if not feed_name:
            feed_name = _meta(soup, "og:site_name") or urlparse(url).netloc
        conn = get_db()
        try:
            existing = _fetchone(conn, "SELECT id FROM feeds WHERE source_url=%s", (url,))
        finally:
            conn.close()
        if existing:
            feed_id = existing["id"]
            conn = get_db()
            try:
                _exec(conn, "UPDATE feeds SET name=%s, status='ok', last_error=NULL WHERE id=%s",
                      (feed_name, feed_id))
            finally:
                conn.close()
        else:
            feed_id = str(uuid.uuid4())[:8]
            now_iso = get_nepal_time().isoformat()
            conn = get_db()
            try:
                _exec(conn,
                    "INSERT INTO feeds (id, name, source_url, created_at, item_count, last_fetched, status, last_error, paused, custom_name, max_items) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (feed_id, feed_name, url, now_iso, 0, now_iso, "ok", None, 0, None, max_items)
                )
            finally:
                conn.close()
        if progress_cb: progress_cb("saving", "Saving articles…")
        added = insert_articles(feed_id, articles)
        purge_old_items(feed_id)
        return feed_id, feed_name, added, None
    except Exception as e:
        return None, feed_name or url, 0, str(e)

def refresh_all_feeds():
    _broadcast("refresh_start", {"ts": get_nepal_time().isoformat()})
    conn = get_db()
    try:
        feeds = _fetchall(conn, "SELECT * FROM feeds WHERE paused=0 OR paused IS NULL")
    finally:
        conn.close()
    for feed in feeds:
        try:
            max_items = feed["max_items"] or DEFAULT_MAX_ITEMS
            feed_id, _, added, err = process_url(feed["source_url"], feed["name"], max_items)
            if err:
                conn = get_db()
                try:
                    _exec(conn, "UPDATE feeds SET status='error', last_error=%s WHERE id=%s", (err, feed["id"]))
                finally:
                    conn.close()
                _broadcast("feed_refreshed", {"id": feed["id"], "status": "error", "error": err})
            else:
                conn = get_db()
                try:
                    row = _fetchone(conn, "SELECT item_count, last_fetched FROM feeds WHERE id=%s", (feed["id"],))
                finally:
                    conn.close()
                _broadcast("feed_refreshed", {"id": feed["id"], "added": added,
                           "item_count": row["item_count"], "last_fetched": row["last_fetched"], "status": "ok"})
        except Exception as e:
            _broadcast("feed_refreshed", {"id": feed["id"], "status": "error", "error": str(e)})
    purge_old_items()
    job = scheduler.get_job("auto_refresh")
    next_run = job.next_run_time.astimezone(NEPAL_TZ).isoformat() if job and job.next_run_time else None
    _broadcast("refresh_done", {"ts": get_nepal_time().isoformat(), "next": next_run})

scheduler = BackgroundScheduler(timezone=NEPAL_TZ)
scheduler.add_job(refresh_all_feeds, "interval", minutes=REFRESH_MINS, id="auto_refresh")
scheduler.start()

def cdata(s):
    s = (s or "").replace("]]>", "]]]]><![CDATA[>")
    return f"<![CDATA[{s}]]>"

def build_rss_xml(feed_row, items, base_url, feed_url_override=None):
    now = format_datetime(get_nepal_time())
    feed_url = feed_url_override or f"{base_url}/feed/{feed_row['id']}.xml"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"',
             '  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"',
             '  xmlns:media="http://search.yahoo.com/mrss/">', '<channel>',
             f'  <title>{cdata(feed_row["name"])}</title>',
             f'  <link>{feed_row["source_url"]}</link>',
             f'  <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>',
             f'  <description>{cdata("News feed from " + feed_row["source_url"])}</description>',
             f'  <lastBuildDate>{now}</lastBuildDate>', '  <language>ne</language>',
             f'  <ttl>{REFRESH_MINS}</ttl>',
             f'  <generator>RSS/gen v11</generator>']
    for item in items:
        cats = json.loads(item["categories"] or "[]")
        lines += ['', '  <item>',
                  f'    <title>{cdata(item["title"])}</title>',
                  f'    <link>{item["link"]}</link>']
        if item["pub_date"]:     lines.append(f'    <pubDate>{item["pub_date"]}</pubDate>')
        if item["mod_date"]:     lines.append(f'    <dc:date>{item["mod_date"]}</dc:date>')
        if item["author"]:       lines.append(f'    <dc:creator>{cdata(item["author"])}</dc:creator>')
        if item["publisher"]:    lines.append(f'    <dc:publisher>{cdata(item["publisher"])}</dc:publisher>')
        for cat in cats:         lines.append(f'    <category>{cdata(cat)}</category>')
        lines.append(f'    <guid isPermaLink="true">{item["guid"]}</guid>')
        if item["description"]:  lines.append(f'    <description>{cdata(item["description"])}</description>')
        if item["body_html"]:    lines.append(f'    <content:encoded>{cdata(item["body_html"])}</content:encoded>')
        if item["image"]:
            lines.append(f'    <media:content url="{item["image"]}" medium="image"/>')
            lines.append(f'    <media:thumbnail url="{item["image"]}"/>')
        lines.append('  </item>')
    lines += ['', '</channel>', '</rss>']
    return "\n".join(lines)

def build_master_rss_xml(base_url):
    now = format_datetime(get_nepal_time())
    master_url = f"{base_url}/feed/master.xml"
    conn = get_db()
    try:
        items = _fetchall(conn, """
            SELECT i.*, f.name as feed_name, f.source_url as feed_source
            FROM items i JOIN feeds f ON i.feed_id = f.id
            ORDER BY COALESCE(NULLIF(i.pub_date_iso,''), i.fetched_at) DESC
        """)
        manual_items = _fetchall(conn, """
            SELECT * FROM manual_items
            WHERE title != '__draft__' AND (approval_status='approved' OR approval_status IS NULL)
            ORDER BY COALESCE(NULLIF(pub_date_iso,''), created_at) DESC
        """)
    finally:
        conn.close()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"',
             '  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"',
             '  xmlns:media="http://search.yahoo.com/mrss/">', '<channel>',
             '  <title><![CDATA[RSS/gen — All Feeds (Master)]]></title>',
             f'  <link>{base_url}</link>',
             f'  <atom:link href="{master_url}" rel="self" type="application/rss+xml"/>',
             '  <description><![CDATA[Combined live news from all tracked sources + manual items — last 24h only]]></description>',
             f'  <lastBuildDate>{now}</lastBuildDate>',
             '  <language>ne</language>',
             f'  <ttl>{REFRESH_MINS}</ttl>',
             f'  <generator>RSS/gen v11</generator>']
    combined = []
    for item in items:
        d = dict(item)
        d['_type'] = 'scraped'
        combined.append((d.get('pub_date_iso') or d.get('fetched_at') or '', d))
    for item in manual_items:
        d = dict(item)
        d['_type'] = 'manual'
        combined.append((d.get('pub_date_iso') or d.get('created_at') or '', d))
    combined.sort(key=lambda x: x[0], reverse=True)
    for _, item in combined:
        if item['_type'] == 'scraped':
            cats = json.loads(item.get("categories") or "[]")
            lines += ['', '  <item>',
                      f'    <title>{cdata(item["title"])}</title>',
                      f'    <link>{item["link"]}</link>']
            if item["pub_date"]:   lines.append(f'    <pubDate>{item["pub_date"]}</pubDate>')
            if item["mod_date"]:   lines.append(f'    <dc:date>{item["mod_date"]}</dc:date>')
            if item["author"]:     lines.append(f'    <dc:creator>{cdata(item["author"])}</dc:creator>')
            if item["publisher"]:  lines.append(f'    <dc:publisher>{cdata(item["publisher"])}</dc:publisher>')
            if item.get("feed_name"): lines.append(f'    <source url="{item["feed_source"]}">{cdata(item["feed_name"])}</source>')
            for cat in cats:       lines.append(f'    <category>{cdata(cat)}</category>')
            lines.append(f'    <guid isPermaLink="true">{item["guid"]}</guid>')
            if item["description"]: lines.append(f'    <description>{cdata(item["description"])}</description>')
            if item["body_html"]:   lines.append(f'    <content:encoded>{cdata(item["body_html"])}</content:encoded>')
            if item["image"]:
                lines.append(f'    <media:content url="{item["image"]}" medium="image"/>')
                lines.append(f'    <media:thumbnail url="{item["image"]}"/>')
            lines.append('  </item>')
        else:
            tags = json.loads(item.get("tags") or "[]")
            img  = item.get("image") or ""
            if img and img.startswith("/"): img = base_url + img
            link = item.get("link") or base_url
            lines += ['', '  <item>',
                      f'    <title>{cdata(item["title"])}</title>',
                      f'    <link>{link}</link>']
            if item.get("pub_date"):    lines.append(f'    <pubDate>{item["pub_date"]}</pubDate>')
            if item.get("creator"):     lines.append(f'    <dc:creator>{cdata(item["creator"])}</dc:creator>')
            if item.get("source_name"): lines.append(f'    <dc:publisher>{cdata(item["source_name"])}</dc:publisher>')
            if item.get("category"):    lines.append(f'    <category>{cdata(item["category"])}</category>')
            for tag in tags:            lines.append(f'    <category>{cdata(tag)}</category>')
            if item.get("location"):    lines.append(f'    <dc:coverage>{cdata(item["location"])}</dc:coverage>')
            lines.append(f'    <source url="{base_url}/feed/manual.xml">{cdata("Manual News")}</source>')
            lines.append(f'    <guid isPermaLink="false">{item["guid"]}</guid>')
            if item.get("description"): lines.append(f'    <description>{cdata(item["description"])}</description>')
            if item.get("body_html"):   lines.append(f'    <content:encoded>{cdata(item["body_html"])}</content:encoded>')
            if img:
                lines.append(f'    <media:content url="{img}" medium="image"/>')
                lines.append(f'    <media:thumbnail url="{img}"/>')
            lines.append('  </item>')
    lines += ['', '</channel>', '</rss>']
    return "\n".join(lines)

# ── LOCATION RBAC HELPERS ─────────────────────────────────────

def get_user_location_scopes(user_id):
    conn = get_db()
    try:
        rows = _fetchall(conn, """
            SELECT country_id, province_id, district_id, local_level_id, ward_id, area_id
            FROM admin_locations WHERE user_id=%s
        """, (user_id,))
    finally:
        conn.close()
    scopes = []
    for r in rows:
        for level, id_val in [('area', r['area_id']),
                              ('ward', r['ward_id']),
                              ('local_level', r['local_level_id']),
                              ('district', r['district_id']),
                              ('province', r['province_id']),
                              ('country', r['country_id'])]:
            if id_val:
                scopes.append((level, id_val))
                break
    return scopes

def is_user_eligible_for_news(user_id, news_item):
    conn = get_db()
    try:
        user = _fetchone(conn, "SELECT role FROM users WHERE id=%s", (user_id,))
    finally:
        conn.close()
    if not user:
        return False
    if user['role'] == 'admin':
        return True
    if user['role'] == 'location_admin':
        user_scopes = get_user_location_scopes(user_id)
        if not user_scopes:
            return False
        news_level = news_item['approval_scope_level']
        news_id    = news_item['approval_scope_id']
        if not news_level or not news_id:
            return False
        hierarchy = ['area', 'ward', 'local_level', 'district', 'province', 'country']
        for user_level, user_val in user_scopes:
            if user_level in hierarchy and news_level in hierarchy:
                if hierarchy.index(user_level) <= hierarchy.index(news_level):
                    if user_level == 'country' and news_item['country_id'] == user_val:
                        return True
                    elif user_level == 'province' and news_item['province_id'] == user_val:
                        return True
                    elif user_level == 'district' and news_item['district_id'] == user_val:
                        return True
                    elif user_level == 'local_level' and news_item['local_level_id'] == user_val:
                        return True
                    elif user_level == 'ward' and news_item['ward_id'] == user_val:
                        return True
                    elif user_level == 'area' and news_item['area_id'] == user_val:
                        return True
    return False

# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/api/imgproxy")
def img_proxy():
    url = request.args.get("url","").strip()
    if not url or not url.startswith("http"): abort(400)
    try:
        referer = "{0}://{1}".format(urlparse(url).scheme, urlparse(url).netloc)
        r = requests.get(url, headers={**HEADERS, "Referer": referer}, timeout=10, stream=True)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type","image/jpeg")
        if not ctype.startswith("image/"): abort(400)
        return Response(r.content, mimetype=ctype, headers={"Cache-Control": "public, max-age=3600"})
    except Exception:
        abort(404)

# ── AUTH ROUTES ────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        identifier = (request.form.get("username") or "").strip()
        password   = (request.form.get("password") or "").strip()
        conn = get_db()
        try:
            user = _fetchone(conn,
                "SELECT * FROM users WHERE username=%s OR email=%s",
                (identifier, identifier))
        finally:
            conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["role"]     = user["role"]
            if not user_has_location(user["id"]):
                return redirect(url_for("account_panel"))
            return redirect(url_for("index"))
        error = "Invalid username/email or password."
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    error = None
    step  = request.form.get("step", "form")
    if request.method == "POST" and step == "form":
        username   = (request.form.get("username") or "").strip()
        email      = (request.form.get("email") or "").strip()
        phone      = (request.form.get("phone") or "").strip()
        password   = (request.form.get("password") or "").strip()
        otp_via    = (request.form.get("otp_via") or "email").strip()
        if not all([username, email, password]):
            error = "Username, email, and password are required."
        elif not _validate_email(email):
            error = "Please enter a valid email address (e.g. you@example.com)."
        elif phone and not _validate_phone(phone):
            error = "Phone must be in international format, e.g. +977 9812345678."
        elif otp_via == "phone" and not phone:
            error = "Please enter a phone number to receive OTP via phone."
        else:
            pw_err = _validate_password_strength(password)
            if pw_err:
                error = pw_err
            else:
                conn = get_db()
                try:
                    existing = _fetchone(conn,
                        "SELECT id FROM users WHERE username=%s OR email=%s",
                        (username, email))
                finally:
                    conn.close()
                if existing:
                    error = "Username or email is already taken."
                else:
                    reg_data = {"username": username, "email": email,
                                "phone": phone, "password": password}
                    identifier = email if otp_via == "email" else phone
                    otp = _generate_otp(identifier, reg_data)
                    fallback_otp = None
                    if otp_via == "email":
                        ok, msg = _send_otp_email(email, otp)
                        if not ok:
                            fallback_otp = otp
                            error = f"Email could not be sent ({msg}). Your OTP is shown below — ask admin to configure SMTP for automatic delivery."
                            print(f"[OTP] {email}: {otp}")
                    else:
                        fallback_otp = otp
                        error = "SMS delivery is not yet configured. Your OTP is shown below."
                        print(f"[OTP-SMS] {phone}: {otp}")
                    return render_template("register.html", error=error,
                                           step="otp", identifier=identifier,
                                           otp_via=otp_via, fallback_otp=fallback_otp)
    elif request.method == "POST" and step == "otp":
        identifier = (request.form.get("identifier") or "").strip()
        otp_input  = (request.form.get("otp") or "").strip()
        ok, reg_data, msg = _verify_otp(identifier, otp_input)
        if not ok:
            return render_template("register.html", error=msg,
                                   step="otp", identifier=identifier,
                                   otp_via=request.form.get("otp_via","email"))
        now = get_nepal_time().isoformat()
        conn = get_db()
        try:
            _exec(conn,
                "INSERT INTO users (id,username,email,phone,password_hash,role,created_at,login_method) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (str(uuid.uuid4()), reg_data["username"], reg_data["email"],
                 reg_data.get("phone",""), generate_password_hash(reg_data["password"]),
                 "reporter", now, "gmail_registration")
            )
        finally:
            conn.close()
        return redirect(url_for("login", registered=1))
    return render_template("register.html", error=error, step="form")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if "user_id" in session:
        return redirect(url_for("index"))
    error = None
    success = None
    step = request.form.get("step", "request")
    if request.method == "POST" and step == "request":
        identifier = (request.form.get("identifier") or "").strip()
        if not identifier:
            error = "Please enter your username or email address."
        else:
            conn = get_db()
            try:
                user = _fetchone(conn,
                    "SELECT * FROM users WHERE username=%s OR email=%s",
                    (identifier, identifier))
            finally:
                conn.close()
            if not user:
                return render_template("forgot_password.html", step="otp",
                    info="If that account exists, an OTP has been sent to the registered email.",
                    identifier=identifier)
            email = user["email"]
            otp = _generate_otp(f"reset:{email}", {"user_id": user["id"], "email": email})
            ok, msg = _send_otp_email(email, otp)
            fallback_otp = None
            send_error = None
            if not ok:
                fallback_otp = otp
                send_error = msg
                print(f"[FORGOT-OTP] {email}: {otp}")
            parts = email.split("@")
            masked = parts[0][:2] + "***@" + parts[1] if len(parts) == 2 else email
            return render_template("forgot_password.html", step="otp",
                identifier=email, fallback_otp=fallback_otp,
                masked_email=masked,
                info=f"Email could not be sent ({send_error}). Your OTP is shown below — copy it manually." if send_error else None)
    elif request.method == "POST" and step == "otp":
        identifier = (request.form.get("identifier") or "").strip()
        otp_input  = (request.form.get("otp") or "").strip()
        ok, data, msg = _verify_otp(f"reset:{identifier}", otp_input)
        if not ok:
            return render_template("forgot_password.html", step="otp",
                identifier=identifier, error=msg)
        reset_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        expires = datetime.now(timezone.utc).timestamp() + 600
        with _otp_lock:
            _otp_store[f"token:{reset_token}"] = {"otp": reset_token, "expires_at": expires, "data": data}
        return render_template("forgot_password.html", step="reset", reset_token=reset_token)
    elif request.method == "POST" and step == "reset":
        reset_token = (request.form.get("reset_token") or "").strip()
        new_pw      = (request.form.get("password") or "").strip()
        confirm_pw  = (request.form.get("confirm_password") or "").strip()
        if new_pw != confirm_pw:
            return render_template("forgot_password.html", step="reset",
                reset_token=reset_token, error="Passwords do not match.")
        pw_err = _validate_password_strength(new_pw)
        if pw_err:
            return render_template("forgot_password.html", step="reset",
                reset_token=reset_token, error=pw_err)
        ok, data, msg = _verify_otp(f"token:{reset_token}", reset_token)
        if not ok:
            return render_template("forgot_password.html", step="request",
                error="Session expired. Please start over.")
        conn = get_db()
        try:
            _exec(conn, "UPDATE users SET password_hash=%s WHERE id=%s",
                (generate_password_hash(new_pw), data["user_id"]))
        finally:
            conn.close()
        return redirect(url_for("login", reset=1))
    return render_template("forgot_password.html", step="request", error=error, success=success)

@app.route("/admin")
@admin_required
def admin_panel():
    return render_template("admin.html")

@app.route("/account")
@login_required
def account_panel():
    user_location = get_user_location(session["user_id"])
    return render_template("account.html", user_location=user_location)

@app.route("/api/account/profile", methods=["GET"])
@login_required
def api_account_get():
    conn = get_db()
    try:
        user = _fetchone(conn,
            "SELECT id,username,email,phone,role,created_at,login_method FROM users WHERE id=%s",
            (session["user_id"],))
    finally:
        conn.close()
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(dict(user))

@app.route("/api/account/profile", methods=["PATCH"])
@login_required
def api_account_update():
    data = request.get_json() or {}
    updates, params = [], []
    if "username" in data:
        username = (data["username"] or "").strip()
        if not username or len(username) < 3:
            return jsonify(error="Username must be at least 3 characters"), 400
        updates.append("username=%s"); params.append(username)
    if "phone" in data:
        phone = (data["phone"] or "").strip()
        if phone and not _validate_phone(phone):
            return jsonify(error="Phone must be in international format e.g. +977 9812345678"), 400
        updates.append("phone=%s"); params.append(phone or None)
    if "new_password" in data and data["new_password"]:
        current_pw = (data.get("current_password") or "").strip()
        conn = get_db()
        try:
            user = _fetchone(conn, "SELECT password_hash FROM users WHERE id=%s", (session["user_id"],))
        finally:
            conn.close()
        if not user or not check_password_hash(user["password_hash"], current_pw):
            return jsonify(error="Current password is incorrect"), 400
        pw_err = _validate_password_strength(data["new_password"])
        if pw_err:
            return jsonify(error=pw_err), 400
        updates.append("password_hash=%s"); params.append(generate_password_hash(data["new_password"]))
    if not updates:
        return jsonify(error="Nothing to update"), 400
    params.append(session["user_id"])
    conn = get_db()
    try:
        _exec(conn, f"UPDATE users SET {', '.join(updates)} WHERE id=%s", params)
        user = _fetchone(conn, "SELECT username FROM users WHERE id=%s", (session["user_id"],))
    finally:
        conn.close()
    if user:
        session["username"] = user["username"]
    return jsonify(ok=True)

@app.route("/api/account/location", methods=["POST"])
@login_required
def api_account_location():
    data = request.get_json() or {}
    user_id = session["user_id"]
    country_id = _safe_int(data.get("country_id"))
    province_id = _safe_int(data.get("province_id"))
    district_id = _safe_int(data.get("district_id"))
    local_level_id = _safe_int(data.get("local_level_id"))
    ward_id = _safe_int(data.get("ward_id"))
    area_id = _safe_int(data.get("area_id"))
    if all(v is None for v in [country_id, province_id, district_id, local_level_id, ward_id, area_id]):
        return jsonify(error="Please select at least one location field"), 400
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM admin_locations WHERE user_id=%s", (user_id,))
            now = get_nepal_time().isoformat()
            cur.execute("""
                INSERT INTO admin_locations (user_id, country_id, province_id, district_id, local_level_id, ward_id, area_id, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, country_id, province_id, district_id, local_level_id, ward_id, area_id, now))
        conn.commit()
    finally:
        conn.close()
    return jsonify(ok=True, message="Location updated successfully")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/auth/me")
def api_auth_me():
    if "user_id" not in session:
        return jsonify(error="Not logged in"), 401
    return jsonify(user_id=session["user_id"], username=session["username"], role=session["role"])

@app.route("/api/auth/users", methods=["GET"])
@admin_required
def api_list_users():
    conn = get_db()
    try:
        users = _fetchall(conn,
            "SELECT id,username,email,phone,role,created_at,login_method FROM users ORDER BY created_at DESC")
    finally:
        conn.close()
    return jsonify([dict(u) for u in users])

@app.route("/api/auth/users", methods=["POST"])
@admin_required
def api_create_user():
    if session.get("role") != "admin":
        return jsonify(error="Only admin can create users"), 403
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email") or "").strip()
    phone    = (data.get("phone") or "").strip()
    password = (data.get("password") or "").strip()
    role     = data.get("role", "reporter")
    if role not in ("admin", "location_admin", "reporter"):
        role = "reporter"
    if not all([username, email, password]):
        return jsonify(error="username, email and password are required"), 400
    if not _validate_email(email):
        return jsonify(error="Please enter a valid email address"), 400
    if phone and not _validate_phone(phone):
        return jsonify(error="Phone must be in international format e.g. +977 9812345678"), 400
    pw_err = _validate_password_strength(password)
    if pw_err:
        return jsonify(error=pw_err), 400
    conn = get_db()
    try:
        existing = _fetchone(conn,
            "SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        if existing:
            return jsonify(error="Username or email is already taken"), 409
        now = get_nepal_time().isoformat()
        new_id = str(uuid.uuid4())
        _exec(conn,
            "INSERT INTO users (id,username,email,phone,password_hash,role,created_at,login_method) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (new_id, username, email, phone, generate_password_hash(password), role, now, "admin_created")
        )
    finally:
        conn.close()
    return jsonify(ok=True, id=new_id), 201

@app.route("/api/auth/users/<user_id>", methods=["PATCH"])
@admin_required
def api_update_user(user_id):
    data = request.get_json() or {}
    updates, params = [], []
    if "role" in data and data["role"] in ("admin", "location_admin", "reporter"):
        updates.append("role=%s"); params.append(data["role"])
    if "password" in data and len(data["password"]) >= 6:
        updates.append("password_hash=%s"); params.append(generate_password_hash(data["password"]))
    if not updates:
        return jsonify(error="Nothing to update"), 400
    params.append(user_id)
    conn = get_db()
    try:
        _exec(conn, f"UPDATE users SET {', '.join(updates)} WHERE id=%s", params)
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/auth/users/<user_id>", methods=["DELETE"])
@admin_required
def api_delete_user(user_id):
    if session.get("role") != "admin":
        return jsonify(error="Only admin can delete users"), 403
    if user_id == session.get("user_id"):
        return jsonify(error="Cannot delete your own account"), 400
    conn = get_db()
    try:
        _exec(conn, "DELETE FROM users WHERE id=%s", (user_id,))
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/locations/countries")
@login_required
def api_locations_countries():
    conn = get_db()
    try:
        rows = _fetchall(conn, "SELECT id, name, code FROM countries ORDER BY name")
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/locations/provinces")
@login_required
def api_locations_provinces():
    country_id = _safe_int(request.args.get("country_id"))
    conn = get_db()
    try:
        if country_id:
            rows = _fetchall(conn, "SELECT id, country_id, name, code, nepali_name FROM provinces WHERE country_id=%s ORDER BY id", (country_id,))
        else:
            rows = _fetchall(conn, "SELECT id, country_id, name, code, nepali_name FROM provinces ORDER BY id")
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/locations/districts")
@login_required
def api_locations_districts():
    province_id = _safe_int(request.args.get("province_id"))
    conn = get_db()
    try:
        if province_id:
            rows = _fetchall(conn, "SELECT id, province_id, name, nepali_name FROM districts WHERE province_id=%s ORDER BY id", (province_id,))
        else:
            rows = _fetchall(conn, "SELECT id, province_id, name, nepali_name FROM districts ORDER BY id")
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/locations/local-levels")
@login_required
def api_locations_local_levels():
    district_id = _safe_int(request.args.get("district_id"))
    conn = get_db()
    try:
        if district_id:
            rows = _fetchall(conn, "SELECT id, district_id, name, nepali_name, level_type, type_name, ward_count FROM local_levels WHERE district_id=%s ORDER BY id", (district_id,))
        else:
            rows = _fetchall(conn, "SELECT id, district_id, name, nepali_name, level_type, type_name, ward_count FROM local_levels ORDER BY id")
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/locations/wards")
@login_required
def api_locations_wards():
    local_level_id = _safe_int(request.args.get("local_level_id"))
    conn = get_db()
    try:
        if local_level_id:
            rows = _fetchall(conn, "SELECT id, local_level_id, ward_number FROM wards WHERE local_level_id=%s ORDER BY ward_number", (local_level_id,))
        else:
            rows = _fetchall(conn, "SELECT id, local_level_id, ward_number FROM wards ORDER BY ward_number")
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin-locations", methods=["GET","POST"])
@login_required
def api_admin_locations():
    conn = get_db()
    try:
        if request.method == "GET":
            user_id_filter = request.args.get("user_id", "").strip()
            if user_id_filter:
                rows = _fetchall(conn, "SELECT * FROM admin_locations WHERE user_id=%s ORDER BY created_at DESC", (user_id_filter,))
            elif is_admin_role(session.get("role")):
                rows = _fetchall(conn, "SELECT * FROM admin_locations ORDER BY created_at DESC")
            else:
                rows = _fetchall(conn, "SELECT * FROM admin_locations WHERE user_id=%s ORDER BY created_at DESC", (session["user_id"],))
            return jsonify([dict(r) for r in rows])
        if not is_admin_role(session.get("role")):
            return jsonify(error="Admin access required"), 403
        data = request.get_json() or {}
        user_id = (data.get("user_id") or "").strip()
        if not user_id:
            return jsonify(error="user_id is required"), 400
        country_id = _safe_int(data.get("country_id"))
        province_id = _safe_int(data.get("province_id"))
        district_id = _safe_int(data.get("district_id"))
        local_level_id = _safe_int(data.get("local_level_id"))
        ward_id = _safe_int(data.get("ward_id"))
        area_id = _safe_int(data.get("area_id"))
        now = get_nepal_time().isoformat()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO admin_locations (user_id,country_id,province_id,district_id,local_level_id,ward_id,area_id,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
            """, (user_id, country_id, province_id, district_id, local_level_id, ward_id, area_id, now))
        conn.commit()
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/admin-locations/<int:loc_id>", methods=["DELETE"])
@admin_required
def api_admin_locations_delete(loc_id):
    conn = get_db()
    try:
        _exec(conn, "DELETE FROM admin_locations WHERE id=%s", (loc_id,))
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/")
@login_required
def index():
    has_loc = user_has_location(session["user_id"])
    user_location_obj = get_user_location_object(session["user_id"])
    user_location_label = get_user_location(session["user_id"]) or "No location assigned"
    conn = get_db()
    try:
        feeds = _fetchall(conn, "SELECT * FROM feeds ORDER BY created_at DESC")
    finally:
        conn.close()
    job = scheduler.get_job("auto_refresh")
    next_run = job.next_run_time.astimezone(NEPAL_TZ).isoformat() if job and job.next_run_time else None
    return render_template("index.html", feeds=feeds, next_run=next_run,
                           refresh_mins=REFRESH_MINS, max_age_hours=MAX_AGE_HOURS,
                           default_max_items=DEFAULT_MAX_ITEMS,
                           nepal_time=format_nepal_time(get_nepal_time()),
                           current_user={"username": session.get("username"), "role": session.get("role")},
                           has_location=has_loc,
                           user_location=user_location_obj,
                           user_location_label=user_location_label)

@app.route("/api/settings", methods=["GET"])
@login_required
def api_settings_get():
    folder_id, sa_json = _get_drive_config()
    smtp = _get_smtp_config()
    return jsonify(REFRESH_MINS=REFRESH_MINS, MAX_AGE_HOURS=MAX_AGE_HOURS, MAX_ITEMS=DEFAULT_MAX_ITEMS,
                   drive_configured=bool(folder_id and sa_json),
                   drive_folder_id=folder_id,
                   drive_sa_set=bool(sa_json),
                   server_time=get_nepal_time().isoformat(),
                   smtp_host=smtp.get("SMTP_HOST",""),
                   smtp_port=smtp.get("SMTP_PORT","587"),
                   smtp_user=smtp.get("SMTP_USER",""),
                   smtp_from=smtp.get("SMTP_FROM",""),
                   smtp_configured=bool(smtp.get("SMTP_HOST") and smtp.get("SMTP_USER") and smtp.get("SMTP_PASS")))

@app.route("/api/settings", methods=["POST"])
@admin_required
def api_settings_post():
    global REFRESH_MINS, MAX_AGE_HOURS, DEFAULT_MAX_ITEMS
    data = request.get_json() or {}
    updated = {}
    if "REFRESH_MINS" in data:
        val = max(1, min(1440, int(data["REFRESH_MINS"])))
        REFRESH_MINS = val; updated["REFRESH_MINS"] = val
        scheduler.reschedule_job("auto_refresh", trigger="interval", minutes=val)
    if "MAX_AGE_HOURS" in data:
        val = max(1, min(720, int(data["MAX_AGE_HOURS"])))
        MAX_AGE_HOURS = val; updated["MAX_AGE_HOURS"] = val
    if "MAX_ITEMS" in data:
        val = max(1, int(data["MAX_ITEMS"]))
        DEFAULT_MAX_ITEMS = val; updated["MAX_ITEMS"] = val
    for key in ("GOOGLE_DRIVE_FOLDER_ID",):
        if key in data and isinstance(data[key], str):
            updated[key] = data[key].strip()
    if "GOOGLE_SERVICE_ACCOUNT_JSON" in data and isinstance(data["GOOGLE_SERVICE_ACCOUNT_JSON"], str):
        sa_json = data["GOOGLE_SERVICE_ACCOUNT_JSON"].strip()
        if sa_json:
            try:
                json.loads(sa_json)
                updated["GOOGLE_SERVICE_ACCOUNT_JSON"] = sa_json
            except json.JSONDecodeError as e:
                return jsonify(error=f"Invalid service account JSON: {e}"), 400
        else:
            updated["GOOGLE_SERVICE_ACCOUNT_JSON"] = ""
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"):
        if key in data and isinstance(data[key], str):
            updated[key] = data[key].strip()
    conn = get_db()
    try:
        with conn.cursor() as cur:
            for k, v in updated.items():
                cur.execute(
                    "INSERT INTO settings (key,value) VALUES (%s,%s) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value",
                    (k, str(v))
                )
        conn.commit()
    finally:
        conn.close()
    next_run = scheduler.get_job("auto_refresh").next_run_time
    next_run_iso = next_run.astimezone(NEPAL_TZ).isoformat() if next_run else None
    return jsonify(ok=True, updated={k: v for k, v in updated.items() if "JSON" not in k and "PASS" not in k},
                   drive_configured=drive_configured(),
                   next_run=next_run_iso)

@app.route("/api/settings/smtp-test", methods=["POST"])
@admin_required
def api_smtp_test():
    data = request.get_json() or {}
    to = data.get("to","").strip() or session.get("username","")
    cfg = _get_smtp_config()
    host = cfg.get("SMTP_HOST","").strip()
    if not host:
        return jsonify(ok=False, error="SMTP not configured yet.")
    ok, msg = _send_otp_email(to, "123456")
    return jsonify(ok=ok, message=msg if ok else f"Failed: {msg}")

@app.route("/api/feed/<feed_id>", methods=["PATCH"])
@admin_required
def api_feed_patch(feed_id):
    data = request.get_json() or {}
    updates, params = [], []
    if "name" in data:
        updates.append("custom_name=%s"); params.append(data["name"].strip())
        updates.append("name=%s");        params.append(data["name"].strip())
    if "paused" in data:
        updates.append("paused=%s"); params.append(1 if data["paused"] else 0)
    if "max_items" in data:
        updates.append("max_items=%s"); params.append(max(1, int(data["max_items"])))
    if not updates:
        return jsonify(error="Nothing to update"), 400
    params.append(feed_id)
    conn = get_db()
    try:
        _exec(conn, f"UPDATE feeds SET {', '.join(updates)} WHERE id=%s", params)
        feed = _fetchone(conn, "SELECT * FROM feeds WHERE id=%s", (feed_id,))
    finally:
        conn.close()
    return jsonify(dict(feed) if feed else {})

@app.route("/api/fetch", methods=["POST"])
@admin_required
def api_fetch():
    data = request.get_json() or {}
    urls_raw = data.get("urls", data.get("url",""))
    feed_name = data.get("name","").strip()
    max_items = int(data.get("max_items", DEFAULT_MAX_ITEMS))
    if isinstance(urls_raw, list):
        urls = [u.strip() for u in urls_raw if u.strip()]
    else:
        urls = [u.strip() for u in re.split(r"[\n,]+", urls_raw) if u.strip()]
    if not urls:
        return jsonify(error="At least one URL is required"), 400
    results = []
    for url in urls:
        feed_id, name, added, err = process_url(url, feed_name, max_items)
        if err:
            results.append({"url": url, "error": err, "ok": False})
        else:
            results.append({"url": url, "ok": True, "feed_id": feed_id,
                            "feed_name": name, "added": added,
                            "feed_url": f"/feed/{feed_id}.xml",
                            "preview_url": f"/feed/{feed_id}"})
    return jsonify(results=results)

@app.route("/api/refresh/<feed_id>", methods=["POST"])
@admin_required
def api_refresh(feed_id):
    conn = get_db()
    try:
        feed = _fetchone(conn, "SELECT * FROM feeds WHERE id=%s", (feed_id,))
    finally:
        conn.close()
    if not feed: return jsonify(error="Feed not found"), 404
    max_items = feed["max_items"] or DEFAULT_MAX_ITEMS
    _, _, added, err = process_url(feed["source_url"], feed["name"], max_items)
    if err:
        conn = get_db()
        try:
            _exec(conn, "UPDATE feeds SET status='error', last_error=%s WHERE id=%s", (err, feed_id))
        finally:
            conn.close()
        return jsonify(error=err), 400
    conn = get_db()
    try:
        total   = _fetchone(conn, "SELECT COUNT(*) AS c FROM items WHERE feed_id=%s", (feed_id,))["c"]
        updated = _fetchone(conn, "SELECT * FROM feeds WHERE id=%s", (feed_id,))
    finally:
        conn.close()
    return jsonify(added=added, total=total, last_fetched=updated["last_fetched"], status="ok")

@app.route("/api/delete/<feed_id>", methods=["DELETE"])
@admin_required
def api_delete(feed_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items WHERE feed_id=%s", (feed_id,))
            cur.execute("DELETE FROM feeds WHERE id=%s", (feed_id,))
        conn.commit()
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/items/<feed_id>")
@login_required
def api_items(feed_id):
    conn = get_db()
    try:
        items = _fetchall(conn,
            "SELECT * FROM items WHERE feed_id=%s ORDER BY COALESCE(NULLIF(pub_date_iso,''), fetched_at) DESC",
            (feed_id,))
    finally:
        conn.close()
    return jsonify([dict(i) for i in items])

@app.route("/api/feeds")
@login_required
def api_feeds():
    conn = get_db()
    try:
        feeds = _fetchall(conn, "SELECT * FROM feeds ORDER BY created_at DESC")
    finally:
        conn.close()
    return jsonify([dict(f) for f in feeds])

@app.route("/api/master-feed-url")
@login_required
def api_master_url():
    return jsonify(url=f"{request.host_url.rstrip('/')}/feed/master.xml")

@app.route("/api/scheduler/status")
@login_required
def scheduler_status():
    job = scheduler.get_job("auto_refresh")
    next_run = job.next_run_time.astimezone(NEPAL_TZ).isoformat() if job and job.next_run_time else None
    return jsonify(running=scheduler.running,
                   next_run=next_run,
                   interval_minutes=REFRESH_MINS,
                   server_time=get_nepal_time().isoformat())

@app.route("/api/events")
def sse_events():
    cid = str(uuid.uuid4())
    q = queue.Queue(maxsize=50)
    with _sse_lock:
        _sse_clients[cid] = q
    def generate():
        try:
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield f"event: {msg['event']}\ndata: {json.dumps(msg['data'])}\n\n"
                except queue.Empty:
                    yield ": ping\n\n"
        finally:
            with _sse_lock:
                _sse_clients.pop(cid, None)
    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/feed/master.xml")
def serve_master_rss():
    xml = build_master_rss_xml(request.host_url.rstrip("/"))
    return Response(xml, mimetype="application/rss+xml; charset=utf-8",
                    headers={"Cache-Control": f"public, max-age={REFRESH_MINS * 60}"})

@app.route("/feed/<feed_id>.xml")
def serve_rss(feed_id):
    conn = get_db()
    try:
        feed = _fetchone(conn, "SELECT * FROM feeds WHERE id=%s", (feed_id,))
        if not feed: abort(404)
        items = _fetchall(conn,
            "SELECT * FROM items WHERE feed_id=%s ORDER BY COALESCE(NULLIF(pub_date_iso,''), fetched_at) DESC",
            (feed_id,))
    finally:
        conn.close()
    xml = build_rss_xml(feed, items, request.host_url.rstrip("/"))
    return Response(xml, mimetype="application/rss+xml; charset=utf-8",
                    headers={"Cache-Control": f"public, max-age={REFRESH_MINS * 60}"})

@app.route("/feed/<feed_id>")
def preview_feed(feed_id):
    conn = get_db()
    try:
        feed = _fetchone(conn, "SELECT * FROM feeds WHERE id=%s", (feed_id,))
        if not feed: abort(404)
        items = _fetchall(conn,
            "SELECT * FROM items WHERE feed_id=%s ORDER BY COALESCE(NULLIF(pub_date_iso,''), fetched_at) DESC",
            (feed_id,))
    finally:
        conn.close()
    return render_template("feed_preview.html", feed=feed, items=items)

# ── MANUAL ITEMS ──────────────────────────────────────────────

@app.route("/api/manual-items", methods=["GET"])
@login_required
def api_list_manual_items():
    status = request.args.get("status", "approved")
    user_id = session.get("user_id")
    user_role = session.get("role")

    conn = get_db()
    try:
        where = ["title != '__draft__'"]
        params = []

        if user_role == "reporter":
            where.append("submitted_by_user_id=%s")
            params.append(user_id)
        elif user_role in ("location_admin", "admin"):
            loc_rows = _fetchall(conn,
                "SELECT country_id, province_id, district_id, local_level_id, ward_id, area_id "
                "FROM admin_locations WHERE user_id=%s", (user_id,))
            if loc_rows:
                scope_sql = []
                scope_params = []
                for r in loc_rows:
                    lvl, sid = location_scope_from_ids(
                        r["country_id"], r["province_id"], r["district_id"],
                        r["local_level_id"], r["ward_id"], r["area_id"]
                    )
                    if lvl and sid:
                        scope_sql.append("(approval_scope_level=%s AND approval_scope_id=%s)")
                        scope_params.extend([lvl, sid])
                if scope_sql:
                    where.append("(" + " OR ".join(scope_sql) + ")")
                    params.extend(scope_params)
            else:
                if user_role != "admin":
                    return jsonify([])

        if status == "all":
            pass
        elif status == "pending":
            where.append("(approval_status IN ('pending','under_review') OR approval_status IS NULL)")
        else:
            where.append("(approval_status=%s OR approval_status IS NULL)")
            params.append(status)

        query = "SELECT * FROM manual_items WHERE " + " AND ".join(where) + \
                " ORDER BY COALESCE(NULLIF(pub_date_iso,''), created_at) DESC"
        items = _fetchall(conn, query, params)
    finally:
        conn.close()
    return jsonify([dict(i) for i in items])

@app.route("/api/manual-items", methods=["POST"])
@login_required
def api_create_manual_item():
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400

    user_role = session.get("role")
    user_id = session.get("user_id")

    if user_role == "reporter":
        submitted_by = (data.get("submitted_by") or "").strip()
        reporter_phone = (data.get("reporter_phone") or "").strip()
        reporter_email = (data.get("reporter_email") or "").strip()
        if not submitted_by:
            return jsonify(error="Reporter Name is required"), 400
        if not reporter_phone:
            return jsonify(error="Phone number is required"), 400
        if not reporter_email:
            return jsonify(error="Email is required"), 400
        user_loc = get_user_location_object(user_id)
        if not user_loc:
            return jsonify(error="You must have a location assigned before submitting news"), 400
        country_id = user_loc['country_id']
        province_id = user_loc['province_id']
        district_id = user_loc['district_id']
        local_level_id = user_loc['local_level_id']
        ward_id = user_loc['ward_id']
        area_id = user_loc['area_id']
    else:
        submitted_by = (data.get("submitted_by") or session.get("username") or "").strip() or session.get("username", "unknown")
        reporter_phone = (data.get("reporter_phone") or "").strip()
        reporter_email = (data.get("reporter_email") or "").strip()
        country_id = _safe_int(data.get("country_id"))
        province_id = _safe_int(data.get("province_id"))
        district_id = _safe_int(data.get("district_id"))
        local_level_id = _safe_int(data.get("local_level_id"))
        ward_id = _safe_int(data.get("ward_id"))
        area_id = _safe_int(data.get("area_id"))

    now_nepal = get_nepal_time()
    item_id = str(uuid.uuid4())
    guid    = data.get("guid") or f"manual:{item_id}"

    raw_date = (data.get("pub_date_iso") or data.get("pub_date") or "").strip()
    pub_dt   = _parse_dt(raw_date) if raw_date else now_nepal
    if not pub_dt: pub_dt = now_nepal
    pub_date_iso = pub_dt.isoformat()
    pub_date_rfc = format_datetime(pub_dt)

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in re.split(r"[,;]+", tags) if t.strip()]

    category = (data.get("category") or "").strip()
    if "," in category or ";" in category:
        category = re.split(r"[,;]+", category)[0].strip()
    if category:
        tags = [t for t in tags if t.lower() != category.lower()]

    scope_level, scope_id = location_scope_from_ids(country_id, province_id, district_id, local_level_id, ward_id, area_id)

    conn = get_db()
    try:
        location_label = build_location_label(conn, country_id, province_id, district_id, local_level_id, ward_id, area_id, fallback=(data.get("location") or "").strip())
        _exec(conn, """
            INSERT INTO manual_items
               (id, title, body_html, description, category, tags, source_name, source_url,
                creator, image, pub_date, pub_date_iso, location, country_id, province_id,
                district_id, local_level_id, ward_id, area_id, approval_scope_level,
                approval_scope_id, approval_count, required_approvals, link, guid, created_at,
                submitted_by, submitted_at, approval_status, reporter_phone, reporter_email,
                submitted_by_user_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item_id, title,
             data.get("body_html") or data.get("body") or "",
             data.get("description",""), category, json.dumps(tags),
             data.get("source_name") or data.get("source",""), data.get("source_url",""),
             data.get("creator") or data.get("author",""), data.get("image",""),
             pub_date_rfc, pub_date_iso, location_label, country_id, province_id, district_id,
             local_level_id, ward_id, area_id, scope_level, scope_id, 0, 2,
             data.get("link",""), guid, now_nepal.isoformat(),
             submitted_by, now_nepal.isoformat(), "pending",
             reporter_phone, reporter_email, user_id)
        )
    finally:
        conn.close()
    return jsonify(ok=True, id=item_id), 201

@app.route("/api/manual-items/<item_id>", methods=["PUT"])
@login_required
def api_update_manual_item(item_id):
    data = request.get_json() or {}
    conn = get_db()
    try:
        existing = _fetchone(conn, "SELECT * FROM manual_items WHERE id=%s", (item_id,))
    finally:
        conn.close()
    if not existing:
        return jsonify(error="Not found"), 404

    title = (data.get("title") or existing["title"]).strip()
    if not title: return jsonify(error="title is required"), 400

    user_role = session.get("role")
    user_id = session.get("user_id")

    if user_role == "reporter":
        submitted_by = (data.get("submitted_by") or "").strip()
        reporter_phone = (data.get("reporter_phone") or "").strip()
        reporter_email = (data.get("reporter_email") or "").strip()
        if not submitted_by: return jsonify(error="Reporter Name is required"), 400
        if not reporter_phone: return jsonify(error="Phone number is required"), 400
        if not reporter_email: return jsonify(error="Email is required"), 400
        user_loc = get_user_location_object(user_id)
        if not user_loc:
            return jsonify(error="You must have a location assigned before updating news"), 400
        country_id = user_loc['country_id']
        province_id = user_loc['province_id']
        district_id = user_loc['district_id']
        local_level_id = user_loc['local_level_id']
        ward_id = user_loc['ward_id']
        area_id = user_loc['area_id']
    else:
        submitted_by = (data.get("submitted_by") or existing["submitted_by"] or "").strip()
        reporter_phone = (data.get("reporter_phone") or existing["reporter_phone"] or "").strip()
        reporter_email = (data.get("reporter_email") or existing["reporter_email"] or "").strip()
        country_id = _safe_int(data.get("country_id", existing["country_id"]))
        province_id = _safe_int(data.get("province_id", existing["province_id"]))
        district_id = _safe_int(data.get("district_id", existing["district_id"]))
        local_level_id = _safe_int(data.get("local_level_id", existing["local_level_id"]))
        ward_id = _safe_int(data.get("ward_id", existing["ward_id"]))
        area_id = _safe_int(data.get("area_id", existing["area_id"]))

    raw_date = (data.get("pub_date_iso") or data.get("pub_date") or existing["pub_date_iso"] or "").strip()
    now_nepal = get_nepal_time()
    pub_dt   = _parse_dt(raw_date) if raw_date else now_nepal
    if not pub_dt: pub_dt = now_nepal
    pub_date_iso = pub_dt.isoformat()
    pub_date_rfc = format_datetime(pub_dt)

    tags = data.get("tags", json.loads(existing["tags"] or "[]"))
    if isinstance(tags, str):
        tags = [t.strip() for t in re.split(r"[,;]+", tags) if t.strip()]

    category = (data.get("category", existing["category"] or "")).strip()
    if "," in category or ";" in category:
        category = re.split(r"[,;]+", category)[0].strip()
    if category:
        tags = [t for t in tags if t.lower() != category.lower()]

    scope_level, scope_id = location_scope_from_ids(country_id, province_id, district_id, local_level_id, ward_id, area_id)

    conn = get_db()
    try:
        location_label = build_location_label(conn, country_id, province_id, district_id, local_level_id, ward_id, area_id,
                                               fallback=(data.get("location", existing["location"] or "") if existing else ""))
        owner_user_id = existing["submitted_by_user_id"] if existing.get("submitted_by_user_id") else user_id
        _exec(conn, """
            UPDATE manual_items SET
               title=%s, body_html=%s, description=%s, category=%s, tags=%s, source_name=%s,
               source_url=%s, creator=%s, image=%s, pub_date=%s, pub_date_iso=%s, location=%s,
               country_id=%s, province_id=%s, district_id=%s, local_level_id=%s, ward_id=%s, area_id=%s,
               approval_scope_level=%s, approval_scope_id=%s,
               submitted_by=%s, reporter_phone=%s, reporter_email=%s, submitted_by_user_id=%s
               WHERE id=%s""",
            (title,
             data.get("body_html") or data.get("body") or existing["body_html"] or "",
             data.get("description", existing["description"] or ""),
             category, json.dumps(tags),
             data.get("source_name") or data.get("source") or existing["source_name"] or "",
             data.get("source_url", existing["source_url"] or ""),
             data.get("creator") or data.get("author") or existing["creator"] or "",
             data.get("image", existing["image"] or ""),
             pub_date_rfc, pub_date_iso, location_label,
             country_id, province_id, district_id, local_level_id, ward_id, area_id,
             scope_level, scope_id,
             submitted_by, reporter_phone, reporter_email, owner_user_id, item_id)
        )
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/manual-items/<item_id>", methods=["DELETE"])
@login_required
def api_delete_manual_item(item_id):
    conn = get_db()
    try:
        _exec(conn, "DELETE FROM manual_items WHERE id=%s", (item_id,))
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/manual-items/<item_id>/approve", methods=["POST"])
@admin_required
def api_approve_manual_item(item_id):
    data = request.get_json() or {}
    action = (data.get("action") or "approve").strip().lower()
    approval_notes = (data.get("approval_notes") or "").strip()
    approver_username = session.get("username") or (data.get("approved_by") or "").strip()

    if action not in ("approve", "reject"):
        return jsonify(error="Invalid action"), 400

    conn = get_db()
    try:
        existing = _fetchone(conn, "SELECT * FROM manual_items WHERE id=%s", (item_id,))
        if not existing:
            return jsonify(error="Not found"), 404

        if not is_user_eligible_for_news(session["user_id"], existing):
            return jsonify(error="You are not authorized to approve news at this location"), 403

        dup = _fetchone(conn, "SELECT id FROM news_approvals WHERE news_id=%s AND admin_id=%s",
                        (item_id, session["user_id"]))
        if dup:
            return jsonify(error="You have already acted on this news item"), 409

        now_nepal = get_nepal_time().isoformat()
        _exec(conn,
            "INSERT INTO news_approvals (id, news_id, admin_id, action, comment, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
            (str(uuid.uuid4()), item_id, session["user_id"], action, approval_notes, now_nepal)
        )

        if action == "reject":
            _exec(conn,
                "UPDATE manual_items SET approval_status='rejected', approved_by=%s, approved_at=%s, approval_notes=%s WHERE id=%s",
                (approver_username, now_nepal, approval_notes, item_id)
            )
            return jsonify(ok=True, status="rejected")

        row = _fetchone(conn,
            "SELECT COUNT(*) AS c FROM news_approvals WHERE news_id=%s AND action='approve'",
            (item_id,))
        approve_count = row["c"]
        required = int(existing["required_approvals"] or 2)
        new_status = "approved" if approve_count >= required else "under_review"
        _exec(conn,
            "UPDATE manual_items SET approval_status=%s, approved_by=%s, approved_at=%s, approval_count=%s WHERE id=%s",
            (new_status, approver_username, now_nepal, approve_count, item_id)
        )
        return jsonify(ok=True, status=new_status, approval_count=approve_count, required_approvals=required)
    finally:
        conn.close()

@app.route("/api/manual-items/<item_id>/approvals")
@login_required
def api_item_approvals(item_id):
    conn = get_db()
    try:
        rows = _fetchall(conn, """
            SELECT na.*, u.username as admin_username
            FROM news_approvals na
            JOIN users u ON na.admin_id = u.id
            WHERE na.news_id=%s
            ORDER BY na.created_at
        """, (item_id,))
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/items/<item_id>", methods=["DELETE"])
@login_required
def api_delete_scraped_item(item_id):
    conn = get_db()
    try:
        item = _fetchone(conn, "SELECT feed_id FROM items WHERE id=%s", (item_id,))
        if not item:
            return jsonify(error="Not found"), 404
        feed_id = item["feed_id"]
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items WHERE id=%s", (item_id,))
            cur.execute("UPDATE feeds SET item_count=(SELECT COUNT(*) FROM items WHERE feed_id=%s) WHERE id=%s",
                        (feed_id, feed_id))
        conn.commit()
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/items/<item_id>", methods=["PUT"])
@login_required
def api_update_scraped_item(item_id):
    data = request.get_json() or {}
    conn = get_db()
    try:
        existing = _fetchone(conn, "SELECT * FROM items WHERE id=%s", (item_id,))
    finally:
        conn.close()
    if not existing:
        return jsonify(error="Not found"), 404

    title = (data.get("title") or existing["title"] or "").strip()
    if not title:
        return jsonify(error="title is required"), 400

    description = data.get("description", existing["description"] or "")
    body_html   = data.get("body_html", existing["body_html"] or "")
    author      = data.get("author", existing["author"] or "")
    image       = data.get("image", existing["image"] or "")
    categories  = data.get("categories", None)
    if categories is not None:
        if isinstance(categories, str):
            categories = [c.strip() for c in re.split(r"[,;]+", categories) if c.strip()]
        categories = json.dumps(categories)
    else:
        categories = existing["categories"] or "[]"

    raw_date = (data.get("pub_date_iso") or existing["pub_date_iso"] or "").strip()
    now_nepal = get_nepal_time()
    pub_dt = _parse_dt(raw_date) if raw_date else now_nepal
    if not pub_dt: pub_dt = now_nepal
    pub_date_iso = pub_dt.isoformat()
    pub_date_rfc = format_datetime(pub_dt)

    conn = get_db()
    try:
        _exec(conn,
            "UPDATE items SET title=%s, description=%s, body_html=%s, author=%s, image=%s, categories=%s, pub_date=%s, pub_date_iso=%s WHERE id=%s",
            (title, description, body_html, author, image, categories, pub_date_rfc, pub_date_iso, item_id)
        )
    finally:
        conn.close()
    return jsonify(ok=True)

@app.route("/api/manual-items/upload-image-new", methods=["POST"])
@login_required
def api_upload_image_new():
    f = request.files.get("image")
    if not f:
        return jsonify(error="No image file provided"), 400
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    mime = f.mimetype or "image/jpeg"
    if mime not in allowed:
        return jsonify(error="Unsupported image type"), 400

    item_id  = str(uuid.uuid4())
    now_nepal = get_nepal_time()
    guid     = f"manual:{item_id}"
    ext      = mime.split("/")[1]
    title    = (request.form.get("title") or "").strip()
    fname    = _title_to_filename(title, ext) if title else f"{item_id}.{ext}"

    conn = get_db()
    try:
        _exec(conn, """
            INSERT INTO manual_items
               (id, title, body_html, description, category, tags, source_name, source_url,
                creator, image, pub_date, pub_date_iso, location, link, guid, created_at,
                submitted_by_user_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (item_id, "__draft__", "", "", "", "[]", "", "", "", "",
             format_datetime(now_nepal), now_nepal.isoformat(), "", "", guid, now_nepal.isoformat(),
             session.get("user_id"))
        )
    finally:
        conn.close()

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name

    drive_url = None
    final_url = None
    try:
        drive_url = _upload_to_gdrive(tmp_path, fname, mime)
        if drive_url:
            final_url = drive_url
        else:
            upload_dir = os.path.join(app.static_folder or "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            local_path = os.path.join(upload_dir, fname)
            import shutil
            shutil.copy2(tmp_path, local_path)
            final_url = f"/static/uploads/{fname}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    conn = get_db()
    try:
        _exec(conn, "UPDATE manual_items SET image=%s WHERE id=%s", (final_url, item_id))
    finally:
        conn.close()
    return jsonify(ok=True, item_id=item_id, url=final_url, via_drive=bool(drive_url))

def _upload_to_gdrive(file_path, filename, mime):
    folder_id, sa_json = _get_drive_config()
    if not folder_id or not sa_json:
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        sa_info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(
            sa_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        file_meta = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype=mime, resumable=False)
        uploaded = service.files().create(
            body=file_meta, media_body=media, fields="id"
        ).execute()
        file_id = uploaded.get("id", "")
        if not file_id:
            return None
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as exc:
        app.logger.warning(f"Google Drive upload failed: {exc}")
        return None

@app.route("/api/drive/status")
@login_required
def api_drive_status():
    return jsonify(configured=drive_configured())

@app.route("/api/manual-items/<item_id>/upload-image", methods=["POST"])
@login_required
def api_upload_manual_image(item_id):
    f = request.files.get("image")
    if not f:
        return jsonify(error="No image file provided"), 400
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    mime = f.mimetype or "image/jpeg"
    if mime not in allowed:
        return jsonify(error="Unsupported image type"), 400

    ext   = mime.split("/")[1]
    title = (request.form.get("title") or "").strip()
    if not title:
        conn = get_db()
        try:
            row = _fetchone(conn, "SELECT title FROM manual_items WHERE id=%s", (item_id,))
            if row: title = (row["title"] or "").strip()
        finally:
            conn.close()
    fname = _title_to_filename(title, ext) if title else f"{item_id}.{ext}"

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name

    drive_url = None
    final_url = None
    try:
        drive_url = _upload_to_gdrive(tmp_path, fname, mime)
        if drive_url:
            final_url = drive_url
        else:
            upload_dir = os.path.join(app.static_folder or "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            local_path = os.path.join(upload_dir, fname)
            import shutil
            shutil.copy2(tmp_path, local_path)
            final_url = f"/static/uploads/{fname}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    conn = get_db()
    try:
        _exec(conn, "UPDATE manual_items SET image=%s WHERE id=%s", (final_url, item_id))
    finally:
        conn.close()
    return jsonify(ok=True, url=final_url, via_drive=bool(drive_url))

@app.route("/feed/manual.xml")
def serve_manual_rss():
    conn = get_db()
    try:
        items = _fetchall(conn,
            "SELECT * FROM manual_items WHERE title != '__draft__' AND (approval_status='approved' OR approval_status IS NULL) ORDER BY COALESCE(NULLIF(pub_date_iso,''), created_at) DESC")
    finally:
        conn.close()
    base = request.host_url.rstrip("/")
    now  = format_datetime(get_nepal_time())
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"',
        '  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"',
        '  xmlns:media="http://search.yahoo.com/mrss/">', '<channel>',
        f'  <title>{cdata("Manually Added News")}</title>',
        f'  <link>{base}</link>',
        f'  <atom:link href="{base}/feed/manual.xml" rel="self" type="application/rss+xml"/>',
        f'  <description>{cdata("News items manually added by editors")}</description>',
        f'  <lastBuildDate>{now}</lastBuildDate>',
        '  <language>ne</language>',
        f'  <generator>RSS/gen v11</generator>',
    ]
    for item in items:
        tags = json.loads(item["tags"] or "[]")
        img  = item["image"] or ""
        if img and img.startswith("/"): img = base + img
        lines += ['', '  <item>',
                  f'    <title>{cdata(item["title"])}</title>']
        if item["link"]:  lines.append(f'    <link>{item["link"]}</link>')
        else:             lines.append(f'    <link>{base}</link>')
        if item["pub_date"]:      lines.append(f'    <pubDate>{item["pub_date"]}</pubDate>')
        if item["creator"]:       lines.append(f'    <dc:creator>{cdata(item["creator"])}</dc:creator>')
        if item["source_name"]:   lines.append(f'    <dc:publisher>{cdata(item["source_name"])}</dc:publisher>')
        if item["category"]:      lines.append(f'    <category>{cdata(item["category"])}</category>')
        for tag in tags:          lines.append(f'    <category>{cdata(tag)}</category>')
        if item["location"]:      lines.append(f'    <dc:coverage>{cdata(item["location"])}</dc:coverage>')
        lines.append(f'    <guid isPermaLink="false">{item["guid"]}</guid>')
        if item["description"]:   lines.append(f'    <description>{cdata(item["description"])}</description>')
        if item["body_html"]:     lines.append(f'    <content:encoded>{cdata(item["body_html"])}</content:encoded>')
        if img:
            lines.append(f'    <media:content url="{img}" medium="image"/>')
            lines.append(f'    <media:thumbnail url="{img}"/>')
        lines.append('  </item>')
    lines += ['', '</channel>', '</rss>']
    return Response("\n".join(lines), mimetype="application/rss+xml; charset=utf-8",
                    headers={"Cache-Control": "no-cache"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)