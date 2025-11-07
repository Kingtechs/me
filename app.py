from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash
from pathlib import Path
from datetime import datetime
import markdown2
import json, time

app = Flask(__name__)
app.secret_key = "change-me"  # needed for flash() messages

# --- Frozen-Flask config for GitHub Pages ---
app.config.update(
    FREEZER_DESTINATION='docs',
    FREEZER_REMOVE_EXTRA_FILES=True,
    FREEZER_RELATIVE_URLS=True
)

# ---- Paths ----
PROJECTS_PATH = Path("data/projects.json")
POSTS_DIR = Path("posts")
COMMENTS_PATH = Path("data/comments.json")
COMMENTS_PATH.parent.mkdir(exist_ok=True)

# ---- Helpers ----
def load_projects():
    if PROJECTS_PATH.exists():
        with open(PROJECTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_posts():
    posts = []
    POSTS_DIR.mkdir(exist_ok=True)
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        slug = md_file.stem
        text = md_file.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        # title from first H1 if present, else from filename
        title = ""
        if lines:
            first = lines[0].strip()
            if first.startswith("#"):
                title = first.lstrip("# ").strip()
        if not title:
            title = slug.replace("-", " ").title()
        html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
        # simple excerpt: first non-empty non-heading line
        excerpt = ""
        for line in lines:
            if line.strip() and not line.startswith("#"):
                excerpt = line.strip()
                break
        posts.append({"slug": slug, "title": title, "excerpt": excerpt, "html": html})
    posts.sort(key=lambda p: p["slug"], reverse=True)
    return posts

def load_comments():
    if COMMENTS_PATH.exists():
        try:
            return json.loads(COMMENTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_comments(items):
    COMMENTS_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")

# ---- Routes ----
@app.route("/")
def home():
    projects = load_projects()[:3]
    posts = load_posts()[:3]
    return render_template("index.html", projects=projects, posts=posts)

@app.route("/projects")
def projects():
    return render_template("projects.html", projects=load_projects())

@app.route("/blog")
def blog():
    return render_template("blog.html", posts=load_posts())

@app.route("/blog/<slug>")
def post(slug):
    md_path = POSTS_DIR / f"{slug}.md"
    if not md_path.exists():
        abort(404)
    text = md_path.read_text(encoding="utf-8")
    lines = text.strip().splitlines()
    title = ""
    if lines:
        first = lines[0].strip()
        if first.startswith("#"):
            title = first.lstrip("# ").strip()
    if not title:
        title = slug
    html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
    return render_template("post.html", title=title, html=html)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ---- Comments (simple discussion page) ----
@app.route("/comments", methods=["GET", "POST"])
def comments():
    comments = load_comments()

    if request.method == "POST":
        # honeypot: hidden field must be empty
        if request.form.get("website"):
            flash("Submission blocked.")
            return redirect(url_for("comments"))

        name = (request.form.get("name") or "").strip()[:60]
        message = (request.form.get("message") or "").strip()[:1000]

        if not name or not message:
            flash("Please provide your name and a message.")
            return redirect(url_for("comments"))

        # simple rate-limit via cookie
        now = time.time()
        last = float(request.cookies.get("last_comment_ts", "0"))
        if now - last < 20:
            flash("You’re commenting too fast. Please wait a few seconds.")
            resp = redirect(url_for("comments"))
            return resp

        item = {
            "name": name,
            "message": message,
            "ts": int(now),
            "when": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        comments.insert(0, item)
        save_comments(comments)

        resp = redirect(url_for("comments"))
        resp.set_cookie("last_comment_ts", str(int(now)), max_age=3600)
        flash("Thanks for your comment!")
        return resp

    return render_template("comments.html", comments=comments[:200])

@app.route("/api/projects")
def api_projects():
    return jsonify(load_projects())

@app.route("/api/comments")
def api_comments():
    return jsonify(load_comments()[:200])

# ---- Errors ----
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# ---- Dev server ----
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


