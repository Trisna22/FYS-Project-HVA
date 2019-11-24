import mysql.connector, sys

# Connect to database.
connection = mysql.connector.connect(host="127.0.0.1", user="root", passwd="IC106_2", db='CaptivePortalDB')
cursor = connection.cursor()

# Retrieve current passenger data from server
# and insert it into the database.
print("[*] Add current flight data.")

insertQuery = "INSERT INTO Passengers"


# Example data.
query = insertQuery + " VALUES ('22', 'Gregory', 'House', '22A');"
cursor.execute(query)

query = insertQuery + " VALUES ('23', 'Richard', 'Hammond', '22B');"
cursor.execute(query)

query = insertQuery + " VALUES ('24', 'Kevin', 'Mitnick', '22C');"
cursor.execute(query)

query = insertQuery + " VALUES ('25', 'Sherlock', 'Holmes', '22D');"
cursor.execute(query)

query = insertQuery + " VALUES ('26', 'Marcus', 'Holloway', '22E');"
cursor.execute(query)

connection.commit()


