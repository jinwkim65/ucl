from cs50 import SQL
db = SQL("sqlite:///data.db")

while True:
    level = input("Level: ")
    tournament = input("Tournament: ")
    min_year = int(input("Min year: "))
    max_year = int(input("Max year: "))
    if level == "all":
        for i in range(min_year, max_year+1):
            db.execute("INSERT INTO library (level, tournament, year) VALUES (?, ?, ?)", 'Novice', tournament, i)
            db.execute("INSERT INTO library (level, tournament, year) VALUES (?, ?, ?)", 'Intermediate', tournament, i)
            db.execute("INSERT INTO library (level, tournament, year) VALUES (?, ?, ?)", 'Advanced', tournament, i)
            print(f"Inserted {level}-{tournament}-{i} into UCL")
    else:
        for i in range(min_year, max_year+1):
            db.execute("INSERT INTO library (level, tournament, year) VALUES (?, ?, ?)", level, tournament, i)
            print(f"Inserted {level}-{tournament}-{i} into UCL")