import sqlite3
from flask import Flask, redirect, render_template, request, send_file
from os.path import exists
import re

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

# Helper function that mimics ".find" but continuously.
# Returns a list of indices, empty if none found
def find_all(text, keyword):
    return [m.start() for m in re.finditer(keyword, text.lower())]

# Helper function to determine whether quoted words are near enough to each other
# Assume arrays is a 2D array of sorted indices
# Returns lowest index upon success and None otherwise
def find_numbers_within_range(arrays, proximity_score):
  if not arrays or not arrays[0]:
      return None  # Handle empty input

  # Number of subarrays and their lengths
  num_subarrays = len(arrays)
  subarray_lengths = [len(subarray) for subarray in arrays]

  # Initialize pointers for each subarray
  pointers = [0] * num_subarrays

  while True:
      # Get the current set of numbers
      current_set = [arrays[i][pointers[i]] for i in range(num_subarrays)]

      # Find the minimum and maximum values in the current set
      min_val, max_val = min(current_set), max(current_set)

      # Check if the condition is met
      if max_val - min_val <= proximity_score:
          return min_val  # Return the smallest number from the set

      # Move the pointer of the subarray with the smallest element in the current set
      min_pointer = current_set.index(min_val)
      pointers[min_pointer] += 1

      # Check if any subarray is exhausted
      if pointers[min_pointer] == subarray_lengths[min_pointer]:
          return None  # No set meeting the conditions

# Helper function to search through a tournament
# Returns next 20 characters
def ctrlf(keywords, path):
    # Handle empty keywords
    if not keywords:
        return False
    # Return false if file doesn't exist
    if exists(path):
        f = open(path, "r")
    else:
        return False
    # Read file
    current_text = f.read()
    f.close()
    current_text_lower = current_text.lower()

    # Separate quoted and unquoted words
    quote_flag_flag = False
    quote_flag = False
    quoted_words = []
    current_quoted_words = []
    unquoted_words = []
    for word in keywords:
        # Check for quote and turn on corresponding flags
        if not quote_flag and word[0] == "\"":
            quote_flag = True
            word = word[1:]
        elif quote_flag and word[-1] == "\"":
            quote_flag_flag = True
            word = word[:-1]
        # Remember by quoted or unquoted
        if quote_flag:
            current_quoted_words.append(word)
        else:
            unquoted_words.append(word)
        # Turn off quote mode if necessary
        if quote_flag_flag:
            quote_flag = False
            quoted_words.append(current_quoted_words)
            current_quoted_words = []
        quote_flag_flag = False
    
    # Account for unclosed quotation
    if quote_flag:
        for word in current_quoted_words:
            unquoted_words.append(word)
    
    # Check unquoted words first
    preview_index = 0
    index_flag = True
    for word in unquoted_words:
        if path.find(word) != -1:
            result = [0]
        else:
            result = find_all(current_text_lower, word)
        if not result:
            return False
        if index_flag:
            preview_index = result[0]
            index_flag = False
    
    # Then, check quoted words
    proximity_score = 100
    for current_words in quoted_words:
        quoted_results = []
        for word in current_words:
            result = find_all(current_text_lower, word)
            if not result:
                return False
            quoted_results.append(result)

        preview_index = find_numbers_within_range(quoted_results, proximity_score)
        if preview_index is None:
            return False

    preview_size = 75 # 75 characters of preview

    # Clean up and return preview
    preview = current_text[preview_index:preview_index+preview_size]
    clean_preview = ""
    for char in preview:
        if char != "\n":
            clean_preview += char
        else:
            clean_preview += " "
    return clean_preview
        

# Returns path to pdf file
def get_path(tournament, level, year):
    return f"./static/rounds/{tournament}/{tournament}_{level}_{year}.txt"

# Returns corresponding color to a level
def get_color(level):
    if level == "novice":
        return "table-success"
    elif level == "intermediate":
        return "table-warning"
    elif level == "advanced":
        return "table-danger"
    elif level == "elite":
        return "table-secondary"
    else:
        return ""

# Helper function for row sorting by level
def sort_level(row):
    if row["level"] == "advanced":
        return 0
    elif row["level"] == "intermediate":
        return 1
    elif row["level"] == "novice":
        return 2
    elif row["level"] == "elite":
        return 3
    else:
        return 4

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
