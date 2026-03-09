import json
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = os.urandom(32)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "football-vault.db")

# Tables in display order and their display-name column (for FK dropdowns)
TABLE_DISPLAY = {
    "Countries":      "name",
    "TeamTypes":      "description",
    "ShirtDesigns":   "description",
    "Stadiums":       "name",
    "Competitions":   "name",
    "Teams":          "name",
    "Matches":        "id",
    "LineupPlayers":  "id",
    "PendingScrapes": "id",
}

# FK target table → which column to show in dropdowns
FK_DISPLAY_COL = {
    "Countries":    "name",
    "Teams":        "name",
    "Stadiums":     "name",
    "Competitions": "name",
    "TeamTypes":    "description",
    "ShirtDesigns": "description",
    "Matches":      "id",
}

# Columns that should use a colour picker
COLOUR_COLUMNS = {"colour1", "colour2", "colour3"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_table_info(table_name):
    """Return list of dicts with column info."""
    db = get_db()
    rows = db.execute(f"PRAGMA table_info([{table_name}])").fetchall()
    return [dict(r) for r in rows]


def get_foreign_keys(table_name):
    """Return dict mapping column_name → (target_table, target_col)."""
    db = get_db()
    rows = db.execute(f"PRAGMA foreign_key_list([{table_name}])").fetchall()
    return {r["from"]: (r["table"], r["to"]) for r in rows}


def get_fk_options(target_table):
    """Return list of (id, display_label) for a FK target table."""
    db = get_db()
    display_col = FK_DISPLAY_COL.get(target_table, "id")
    rows = db.execute(
        f"SELECT id, [{display_col}] as label FROM [{target_table}] ORDER BY [{display_col}]"
    ).fetchall()
    return [(r["id"], r["label"]) for r in rows]


def match_display_label(row):
    """Build a readable label for a Matches row."""
    db = get_db()
    home = away = "?"
    if row["home_team_id"]:
        r = db.execute("SELECT name FROM Teams WHERE id=?", (row["home_team_id"],)).fetchone()
        if r:
            home = r["name"]
    if row["away_team_id"]:
        r = db.execute("SELECT name FROM Teams WHERE id=?", (row["away_team_id"],)).fetchone()
        if r:
            away = r["name"]
    date = row["match_date"] or "?"
    return f"{home} vs {away} ({date})"


# ── Routes ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    db = get_db()
    table_counts = {}
    for t in TABLE_DISPLAY:
        count = db.execute(f"SELECT COUNT(*) as c FROM [{t}]").fetchone()["c"]
        table_counts[t] = count
    return render_template("index.html", table_counts=table_counts)


@app.route("/table/<table_name>")
def table_list(table_name):
    if table_name not in TABLE_DISPLAY:
        flash("Unknown table.", "danger")
        return redirect(url_for("index"))

    db = get_db()
    columns = get_table_info(table_name)
    fks = get_foreign_keys(table_name)

    page = request.args.get("page", 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    search = request.args.get("q", "").strip()
    if search:
        col_names = [c["name"] for c in columns]
        where_clauses = " OR ".join(f"CAST([{c}] AS TEXT) LIKE ?" for c in col_names)
        search_param = f"%{search}%"
        params = [search_param] * len(col_names)
        total = db.execute(
            f"SELECT COUNT(*) as c FROM [{table_name}] WHERE {where_clauses}", params
        ).fetchone()["c"]
        rows = db.execute(
            f"SELECT * FROM [{table_name}] WHERE {where_clauses} ORDER BY id LIMIT ? OFFSET ?",
            params + [per_page, offset],
        ).fetchall()
    else:
        total = db.execute(f"SELECT COUNT(*) as c FROM [{table_name}]").fetchone()["c"]
        rows = db.execute(
            f"SELECT * FROM [{table_name}] ORDER BY id LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()

    # Resolve FK display values
    fk_display = {}
    for col, (target_table, target_col) in fks.items():
        display_col = FK_DISPLAY_COL.get(target_table, "id")
        fk_display[col] = {}
        for row in rows:
            val = row[col]
            if val is not None:
                if target_table == "Matches":
                    match_row = db.execute(
                        "SELECT * FROM Matches WHERE id=?", (val,)
                    ).fetchone()
                    if match_row:
                        fk_display[col][val] = match_display_label(match_row)
                else:
                    r = db.execute(
                        f"SELECT [{display_col}] as label FROM [{target_table}] WHERE [{target_col}]=?",
                        (val,),
                    ).fetchone()
                    if r:
                        fk_display[col][val] = r["label"]

    total_pages = max(1, (total + per_page - 1) // per_page)

    # Build FK options for inline-edit dropdowns
    fk_options = {}
    for col, (target_table, _) in fks.items():
        if target_table == "Matches":
            match_rows = db.execute("SELECT * FROM Matches ORDER BY match_date DESC").fetchall()
            fk_options[col] = [[r["id"], match_display_label(r)] for r in match_rows]
        else:
            fk_options[col] = [list(pair) for pair in get_fk_options(target_table)]

    return render_template(
        "table.html",
        table_name=table_name,
        columns=columns,
        rows=rows,
        fks=fks,
        fk_display=fk_display,
        fk_options_json=json.dumps(fk_options),
        page=page,
        total_pages=total_pages,
        total=total,
        search=search,
    )


@app.route("/table/<table_name>/add", methods=["GET", "POST"])
def add_record(table_name):
    if table_name not in TABLE_DISPLAY:
        flash("Unknown table.", "danger")
        return redirect(url_for("index"))

    db = get_db()
    columns = get_table_info(table_name)
    fks = get_foreign_keys(table_name)

    # Build FK options for dropdowns
    fk_options = {}
    for col, (target_table, _) in fks.items():
        if target_table == "Matches":
            match_rows = db.execute("SELECT * FROM Matches ORDER BY match_date DESC").fetchall()
            fk_options[col] = [(r["id"], match_display_label(r)) for r in match_rows]
        else:
            fk_options[col] = get_fk_options(target_table)

    if request.method == "POST":
        editable = [c for c in columns if c["name"] != "id"]
        col_names = []
        values = []
        for c in editable:
            val = request.form.get(c["name"], "").strip()
            if val == "":
                val = None
            col_names.append(c["name"])
            values.append(val)

        placeholders = ", ".join("?" for _ in col_names)
        col_sql = ", ".join(f"[{c}]" for c in col_names)
        try:
            db.execute(
                f"INSERT INTO [{table_name}] ({col_sql}) VALUES ({placeholders})",
                values,
            )
            db.commit()
            flash("Record added successfully.", "success")
            return redirect(url_for("table_list", table_name=table_name))
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", "danger")

    return render_template(
        "form.html",
        table_name=table_name,
        columns=columns,
        fks=fks,
        fk_options=fk_options,
        record=None,
        colour_columns=COLOUR_COLUMNS,
    )


@app.route("/table/<table_name>/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(table_name, record_id):
    if table_name not in TABLE_DISPLAY:
        flash("Unknown table.", "danger")
        return redirect(url_for("index"))

    db = get_db()
    columns = get_table_info(table_name)
    fks = get_foreign_keys(table_name)

    record = db.execute(
        f"SELECT * FROM [{table_name}] WHERE id=?", (record_id,)
    ).fetchone()
    if not record:
        flash("Record not found.", "danger")
        return redirect(url_for("table_list", table_name=table_name))

    fk_options = {}
    for col, (target_table, _) in fks.items():
        if target_table == "Matches":
            match_rows = db.execute("SELECT * FROM Matches ORDER BY match_date DESC").fetchall()
            fk_options[col] = [(r["id"], match_display_label(r)) for r in match_rows]
        else:
            fk_options[col] = get_fk_options(target_table)

    if request.method == "POST":
        editable = [c for c in columns if c["name"] != "id"]
        set_clauses = []
        values = []
        for c in editable:
            val = request.form.get(c["name"], "").strip()
            if val == "":
                val = None
            set_clauses.append(f"[{c['name']}] = ?")
            values.append(val)
        values.append(record_id)

        try:
            db.execute(
                f"UPDATE [{table_name}] SET {', '.join(set_clauses)} WHERE id = ?",
                values,
            )
            db.commit()
            flash("Record updated successfully.", "success")
            return redirect(url_for("table_list", table_name=table_name))
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", "danger")

    return render_template(
        "form.html",
        table_name=table_name,
        columns=columns,
        fks=fks,
        fk_options=fk_options,
        record=record,
        colour_columns=COLOUR_COLUMNS,
    )


@app.route("/table/<table_name>/delete/<int:record_id>", methods=["GET", "POST"])
def delete_record(table_name, record_id):
    if table_name not in TABLE_DISPLAY:
        flash("Unknown table.", "danger")
        return redirect(url_for("index"))

    db = get_db()
    record = db.execute(
        f"SELECT * FROM [{table_name}] WHERE id=?", (record_id,)
    ).fetchone()
    if not record:
        flash("Record not found.", "danger")
        return redirect(url_for("table_list", table_name=table_name))

    columns = get_table_info(table_name)

    if request.method == "POST":
        try:
            db.execute(f"DELETE FROM [{table_name}] WHERE id = ?", (record_id,))
            db.commit()
            flash("Record deleted.", "success")
            return redirect(url_for("table_list", table_name=table_name))
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", "danger")

    return render_template(
        "delete.html",
        table_name=table_name,
        record=record,
        columns=columns,
    )


@app.route("/api/table/<table_name>/update", methods=["POST"])
def api_inline_update(table_name):
    if table_name not in TABLE_DISPLAY:
        return {"error": "Unknown table"}, 400

    data = request.get_json()
    record_id = data.get("id")
    column = data.get("column")
    value = data.get("value")

    if record_id is None or not column:
        return {"error": "Missing id or column"}, 400

    columns = get_table_info(table_name)
    col_names = {c["name"] for c in columns}
    if column not in col_names or column == "id":
        return {"error": "Invalid column"}, 400

    if isinstance(value, str) and value.strip() == "":
        value = None

    db = get_db()
    try:
        db.execute(
            f"UPDATE [{table_name}] SET [{column}] = ? WHERE id = ?",
            (value, record_id),
        )
        db.commit()

        # Return resolved FK display if applicable
        fks = get_foreign_keys(table_name)
        display = None
        if column in fks and value is not None:
            target_table, target_col = fks[column]
            display_col = FK_DISPLAY_COL.get(target_table, "id")
            if target_table == "Matches":
                match_row = db.execute("SELECT * FROM Matches WHERE id=?", (value,)).fetchone()
                if match_row:
                    display = match_display_label(match_row)
            else:
                r = db.execute(
                    f"SELECT [{display_col}] as label FROM [{target_table}] WHERE [{target_col}]=?",
                    (value,),
                ).fetchone()
                if r:
                    display = r["label"]

        return {"ok": True, "display": display}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 400


@app.route("/api/table/<table_name>/bulk-update", methods=["POST"])
def api_bulk_update(table_name):
    if table_name not in TABLE_DISPLAY:
        return {"error": "Unknown table"}, 400

    data = request.get_json()
    ids = data.get("ids", [])
    column = data.get("column")
    value = data.get("value")

    if not ids or not column:
        return {"error": "Missing ids or column"}, 400

    columns = get_table_info(table_name)
    col_names = {c["name"] for c in columns}
    if column not in col_names or column == "id":
        return {"error": "Invalid column"}, 400

    if isinstance(value, str) and value.strip() == "":
        value = None

    # Validate all ids are integers
    try:
        ids = [int(i) for i in ids]
    except (ValueError, TypeError):
        return {"error": "Invalid ids"}, 400

    db = get_db()
    try:
        placeholders = ",".join("?" for _ in ids)
        db.execute(
            f"UPDATE [{table_name}] SET [{column}] = ? WHERE id IN ({placeholders})",
            [value] + ids,
        )
        db.commit()
        return {"ok": True, "count": len(ids)}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True, port=5555)
