# Sets up OS database and txt files

import os
import sqlite3

def get_db_connection():
    sql = sqlite3.connect("data.db")
    sql.row_factory = sqlite3.Row
    return sql

def add_to_sql(filename, sql):
    state = 0
    tournament = ""
    level = ""
    year = ""
    for char in filename:
        if char == "_":
            state += 1
            continue

        if state == 0:
            tournament += char
        elif state == 1:
            level += char
        else:
            year += char
    year = int(year)
    
    if (sql.execute("SELECT * FROM library WHERE tournament = ? AND year = ? AND level = ?", (tournament, year, level)).fetchall()):
        return 0
    elif level not in ["novice", "intermediate", "advanced", "elite"]:
        return 0
    sql.execute("INSERT INTO library (tournament, year, level) VALUES (?, ?, ?)", (tournament, year, level))
    sql.commit()
    return 1

# Connect to SQL
sql = get_db_connection()

# Clear any old tables
sql.execute("DROP TABLE IF EXISTS library")
sql.execute("CREATE TABLE library (tournament TEXT NOT NULL, year INT NOT NULL, level TEXT NOT NULL)")

# Go to rounds directory
cwd = os.chdir("./static/rounds")
ls = os.listdir()
# For every tournament:
for folder in ls:
    if folder == ".ds_store":
        continue
    # Go into the tournament folder
    os.chdir(f"{folder.lower()}")
    subfolders = os.listdir()
    for f in subfolders:
        # Add to SQL
        filename = f[:-4]
        fending = f[-4:]
        if fending == ".pdf":
            if (add_to_sql(filename, sql) == 0):
                print(f"Error with adding {filename}")
            # Create txt file
            os.system(f"pdftotext {f}")
    
    # Return to previous directory after finishing
    os.chdir("..")

print("Finished")