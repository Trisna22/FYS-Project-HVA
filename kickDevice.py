
#       Name:                           kickDevice.py (Table voor HTML in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  13-12-2019
#       Author:                         Trisna Quebe ic106-2

import mysql.connector as mariaDB
import os
import subprocess
import urllib.parse as urlparse

# Verkrijg het aantal rijen in tabel.
def GetCountOfLoggedInDevices():
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT COUNT(ticketNumber) FROM LoggedIn;')

	result = cursor.fetchall()
	return int(result[0][0])

# Verkrijg voornaam met de ticketnummer.
def GetFirstNameFromPassengers(TICKETNUMBER):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute("SELECT firstName FROM Passengers WHERE ticketNumber = '" + TICKETNUMBER + "';")

	result = cursor.fetchall()
	return str(result[0][0])

# Verkrijg achternaam met de ticketnummer.
def GetLastNameFromPassengers(TICKETNUMBER):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute("SELECT lastName FROM Passengers WHERE ticketNumber = '" + TICKETNUMBER + "';")

	result = cursor.fetchall()
	return str(result[0][0])

# Maak een tabel met gegevens van de databank.
def createHTMLTable():

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT * FROM LoggedIn')
	result = cursor.fetchall()

	table = ''

	# Loopen door elke apparaat.
	for i in range(0, GetCountOfLoggedInDevices()):

		IP = result[i][0]
		MAC = result[i][1]
		TICKETNUMBER = result[i][2]
		SEATNUMBER = result[i][3]
		FirstName = GetFirstNameFromPassengers(str(TICKETNUMBER))
		LastName = GetLastNameFromPassengers(str(TICKETNUMBER))

		row = '<tr>\n'  # Begin rij
		row += '<td>' + FirstName + '</td>\n'   # Voornaam
		row += '<td>' + LastName + '</td>\n'    # Achternaam
		row += '<td>' + SEATNUMBER + '</td>\n'  # Stoelnummer
		row += '<td>' + str(TICKETNUMBER) + '</td>\n'        # Ticketnummer
		row += '<td>' + IP + '</td>\n'           # IP van apparaat
		row += '<td>' + MAC + '</td>\n'          # MAC van apparaat
		row += '<td><button name="Dev' + str(i)+ '">Delete</button></td>\n' # button
		row += '</tr>\n'        # Einde rij
		table += row

	return table

# Verkrijg het MAC address van de bijbehorende IP address.
def GetMacFromIP(IP):
	MAC = os.popen("arp -n | grep \"" + IP + "\" | awk \'{print $3}\'").read()
	return MAC[:-1]

# Kick device off network.
def kick(environ, start_response):

	IP = environ['REQUEST_URI']
	MAC = GetMacFromIP(IP)

	# Delete device from network.
	

	# Update iptables settings.


	# Redirect to /crew again.
	status = "307 Temporary Redirect"
	html = '<html><body><a href="/crew">Klik hier om doorverwezen te worden</a></body></html>'
	response_header = [('Content-type', 'text/html'), ('Location', '/crew/fuck')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]
