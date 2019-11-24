import mysql.connector, sys

connection = mysql.connector.connect(host="127.0.0.1", user="root", passwd="IC106_2")
cursor = connection.cursor()

# Flush all previous databases and data.
print("[*] Drop all previous data from database.")
query = "DROP SCHEMA CaptivePortalDB";
cursor.execute(query)

# First create a database called 'CaptivePortalDB'.
print("[*] Create CaptivePortalDB database.")
query = "CREATE SCHEMA CaptivePortalDB;"
cursor.execute(query)

query = "use CaptivePortalDB;"
cursor.execute(query)

# Create a table Passenger with the columns that are required to login.
print("[*] Create table for passenger data.")
query = "CREATE TABLE Passengers (ticketNumber VARCHAR(20) NOT NULL, firstName VARCHAR(20) NOT NULL, lastName VARCHAR(20) NOT NULL, "
query += "seatNumber VARCHAR(15) NOT NULL, CONSTRAINT pkTicketNumber PRIMARY KEY(ticketNumber));"
cursor.execute(query)

# Create a table LoggedIn with the columns that are required for checking.
# if certain devices already are logged in.
print("[*] Create table for logged in devices.")
query = "CREATE TABLE LoggedIn (ipAddress VARCHAR(15) NOT NULL, macAddress VARCHAR(20) NOT NULL, "
query += "ticketNumber VARCHAR(20) NOT NULL, seatNumber VARCHAR(15) NOT NULL,  firstName VARCHAR(20) NOT NULL,"
query += "CONSTRAINT pkTicketNumber PRIMARY KEY(ticketNumber));"
cursor.execute(query)
