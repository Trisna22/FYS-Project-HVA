import mysql.connector as mariaDB

print("[*] Creating crew login database")

connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
cursor = connection.cursor()

cursor.execute('CREATE TABLE CrewLogin (username VARCHAR(15) NOT NULL,' \
	'password VARCHAR(40) NOT NULL);')

cursor.execute("INSERT INTO CrewLogin VALUES ('gregory', '6716cdf5c470fa94f88bf5313f86a83c');")


cursor.execute('CREATE TABLE CrewSessions (ipAddress VARCHAR(15) NOT NULL, ' \
	'macAddress VARCHAR(20) NOT NULL, username VARCHAR(15) NOT NULL,' \
	'sessionExpire DATETIME NOT NULL);')

connection.commit()
