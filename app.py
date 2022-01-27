from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, send_file
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return redirect("/find")

@app.route("/find", methods=["GET", "POST"])
def find():
    if request.method == "POST":
        level = request.form.get("level")
        tourney = request.form.get("tourneys")
        year = request.form.get("years")
        if level is not None and tourney is not None and year is not None:
            l = "" if level == "Advanced+" else level[0].lower()
            return send_file(f"static/rounds/{tourney}/{l}{year[-2:]}.pdf", attachment_filename=f'round.pdf')
    else:
        t = request.args.get("t")
        if t is None:
            t = "Yale"
        level = request.args.get("level")
        if level is None:
            level = "Advanced"
        tournaments = db.execute("SELECT DISTINCT tournament FROM library ORDER BY tournament DESC")
        levels = db.execute("SELECT DISTINCT level FROM library WHERE tournament LIKE ? ORDER BY level", t)
        years = db.execute("SELECT year FROM library WHERE tournament LIKE ? AND level LIKE ? ORDER BY year DESC", t, level)
        if len(years) == 0:
            years = years = db.execute("SELECT year FROM library WHERE tournament LIKE ? AND level LIKE \"Advanced\" ORDER BY year DESC", t)
        return render_template("find.html", levels = levels, tournaments = tournaments, years = years)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    print(e.code, e.name)
    flash(f"Error {e.code}: {e.name}. Sorry, an error occured.")
    return redirect("/find")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
