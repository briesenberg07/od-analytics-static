#!/usr/bin/env python3
"""Generate HTML reports from JSON files using Jinja2 templates.

Writes per-file HTML files into docs/ (one per JSON file in data/)
and creates docs/index.html linking to them.
"""

from pathlib import Path
import json
import sys

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except Exception as e:  # pragma: no cover - simple fallback message
    print("Jinja2 is required: pip install jinja2", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
TEMPLATES_DIR = ROOT / "templates"

REPORT_TEMPLATE = "report.html.j2"
INDEX_TEMPLATE = "index.html.j2"


def ensure_templates():
    """Ensure templates dir and files exist; minimal templates are included above in repo.
    This function will not overwrite existing templates."""
    if not TEMPLATES_DIR.exists():
        TEMPLATES_DIR.mkdir(parents=True)

    # If templates are missing, create sensible defaults (only if not present)
    report_path = TEMPLATES_DIR / REPORT_TEMPLATE
    index_path = TEMPLATES_DIR / INDEX_TEMPLATE

    if not report_path.exists():
        report_path.write_text("""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{{ name }}</title>
</head>
<body>
  <h1>{{ name }}</h1>
  {% for top_key in data|dictsort %}
    {% set key = top_key[0] %}
    {% set top_value = top_key[1] %}
    <h2>{{ key }}</h2>
    <p>{{ top_value.get('total','') }} {{ top_value.get('details','') }}</p>
    <ul>
    {% for sub_key in top_value|dictsort %}
      {% set sk = sub_key[0] %}
      {% set sv = sub_key[1] %}
      {% if sk not in ['total','details'] and sk|length == 6 %}
        <li>{{ sk }}: {{ sv.get('total','') }} {{ sv.get('details','') }}</li>
      {% endif %}
    {% endfor %}
    </ul>
  {% endfor %}
</body>
</html>""")

    if not index_path.exists():
        index_path.write_text("""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Oregon Digital analytics data</title>
</head>
<body>
  <h1>Oregon Digital analytics data</h1>
  <ul>
  {% for name, filename in files %}
    <li><a href=\"{{ filename }}\">{{ name }}</a></li>
  {% endfor %}
  </ul>
</body>
</html>""")


def generate():
    ensure_templates()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    report_tmpl = env.get_template(REPORT_TEMPLATE)
    index_tmpl = env.get_template(INDEX_TEMPLATE)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    files = []  # list of (name, filename)

    if not DATA_DIR.exists():
        print(f"No data directory at {DATA_DIR}", file=sys.stderr)
        return 1

    for path in sorted(DATA_DIR.glob("*.json")):
        name = path.stem
        try:
            data = json.loads(path.read_text())
        except Exception as e:
            print(f"Failed to parse {path}: {e}", file=sys.stderr)
            continue

        html = report_tmpl.render(name=name, data=data)
        out_path = DOCS_DIR / f"{name}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"Wrote {out_path}")
        files.append((name, f"{name}.html"))

    # create index
    index_html = index_tmpl.render(files=files)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Wrote {DOCS_DIR / 'index.html'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(generate())
