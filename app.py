import sqlite3
from flask import Flask, redirect, render_template, request, send_file
from helper import *

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure SQLite
# .schema : CREATE TABLE library (tournament TEXT NOT NULL, year INT NOT NULL, level TEXT NOT NULL);
def get_db_connection():
    sql = sqlite3.connect("data.db")
    sql.row_factory = sqlite3.Row
    return sql

# Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        db = get_db_connection()
        # Get arguments from GET request
        tournament = request.args.get("tournament")
        level = request.args.get("level")
        year = request.args.get("year")
        tournaments = db.execute("SELECT DISTINCT tournament FROM library ORDER BY tournament").fetchall()

        # Scenario 1: Loading the page without any prior searches
        if tournament is None:
            tournament = tournaments[0][0]
        # Scenario 2: Level is selected
        if not level is None and year is None:
            levels = db.execute("SELECT DISTINCT level FROM library WHERE tournament LIKE ? ORDER BY level", (tournament, )).fetchall()
            years = db.execute("SELECT year FROM library WHERE tournament LIKE ? AND level LIKE ? ORDER BY year DESC", (tournament, level)).fetchall()
        # Scenario 3: Year is selected
        elif level is None and not year is None:
            years = db.execute("SELECT year FROM library WHERE tournament LIKE ? ORDER BY year DESC", (tournament, )).fetchall()
            levels = db.execute("SELECT DISTINCT level FROM library WHERE tournament LIKE ? AND year LIKE ? ORDER BY level", (tournament, year)).fetchall()
        # Scenario 4: Tournament is selected
        elif level is None and year is None:
            levels = db.execute("SELECT DISTINCT level FROM library WHERE tournament LIKE ? ORDER BY level", (tournament, )).fetchall()
            years = db.execute("SELECT DISTINCT year FROM library WHERE tournament LIKE ? ORDER BY year DESC", (tournament,)).fetchall()
        else:
            print("This should never arrive here.")

        return render_template("index.html", tournaments=tournaments, levels=levels, years=years)
    else:
        tournament = request.form.get("tournament")
        level = request.form.get("level")
        year = request.form.get("year")
        if level is not None and tournament is not None and year is not None:
            return send_file(f"./static/rounds/{tournament.lower()}/{tournament}_{level}_{year}.pdf")
        else:
            return redirect("/")

# Search Page
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        original_text = request.form.get("search")
        text = original_text.lower().split()
        db = get_db_connection()
        all = db.execute("SELECT * FROM library").fetchall()

        # Check every file for matches
        result_rows = []
        
        for row in all:
            # If the search within this file is successful, remember it
            preview = ctrlf(text, get_path(row["tournament"], row["level"], row["year"]))
            if (preview):
                row_copy = {
                    "tournament":row["tournament"],
                    "level":row["level"],
                    "year":row["year"],
                    "preview":preview,
                    "color":get_color(row["level"])
                }
                result_rows.append(row_copy)

            # Temporarily sort results by name then level. We can add sorting features later (I'm tired).
            result_rows.sort(key=lambda x: (x["tournament"], x["level"]))

        return render_template("search.html", rows=result_rows, query=original_text)
