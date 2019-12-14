
#       Name:                           kickDevice.py (Table voor HTML in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  13-12-2019
#       Author:                         Trisna Quebe ic106-2

import mysql.connector as mariaDB
import os
import subprocess
import urllib.parse as urlparse

import logger

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
		row += '<td><form method="post" action="/crew/kick/'

		row += str(i) + '"><button>Delete</button></form></td>\n' # button
		row += '</tr>\n'        # Einde rij
		table += row

	return table

# Verkrijg het MAC address van de bijbehorende IP address.
def GetMacFromIP(IP):
	MAC = os.popen("arp -n | grep \"" + IP + "\" | awk \'{print $3}\'").read()
	return MAC[:-1]

# Checkt of het IP en MAC toestemming heeft om apparaten te verwijderen uit het netwerk.
def isMACandIPAllowed(IP, MAC):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT EXISTS (SELECT * FROM CrewSessions WHERE ipAddress = \'' + IP +
		'\' AND macAddress = \'' + MAC + '\');')
	result = cursor.fetchall()
	return result[0][0]

# Checkt of de string een int bevat en returnt deze.
def checkStringInt(string):

	for char in string:
		if ord(char) < 48 or ord(char) > 57:
			return -1

	return int(char)

# Verkrijg de MAC adres van de index uit de lijst.
def GetMACFromCount(count):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT * FROM LoggedIn')
	result = cursor.fetchall()

	# Count = rijnummer
	# 1 = MAC addressen.
	return result[count][1]

# Verkrijg de IP adres van de index uit de lijst.
def GetIPFromCount(count):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT * FROM LoggedIn')
	result = cursor.fetchall()

	# Count = rijnummer
	# 0 = IP addressen.
	return result[count][0]


# Kick device off network.
def kick(environ, start_response):

	IP = environ['REMOTE_ADDR']
	MAC = GetMacFromIP(IP)

	# Checken of de IP en MAC rechten hebben.
	if isMACandIPAllowed(IP, MAC) == False:

		logger.logAction(IP, MAC, "tried to kick a device without permission")
		# Doorverwijzen naar / pagina.
		status = "307 Temporary Redirect"
		html = '<html><body>Jij hebt geen toestemming!<br><a href="/crew">Klik hier om doorverwezen te worden</a></body></html>'
		response_header = [('Content-type', 'text/html'), ('Location', '/')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Verkrijg de MAC en IP adres die we willen verwijderen.
	# Deze staat in de URL. (een deel)
	devPath = environ['REQUEST_URI']
	number = devPath[11:]
	index = checkStringInt(number)

	# Als we geen nummer hebben gekregen.
	if index == -1:
		# Doorverwijzen naar / pagina.
		status = "307 Temporary Redirect"
		html = '<html><body>Sorry geen kicken voor jou!<br><a href="/crew">Klik hier om doorverwezen te worden</a></body></html>'
		response_header = [('Content-type', 'text/html'), ('Location', '/')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Als de nummer groter is dan er eigenlijk is in de databank.
	if index >= GetCountOfLoggedInDevices():
		# Doorverwijzen naar / pagina.
		status = "307 Temporary Redirect"
		html = '<html><body>Index out of range!<br><a href="/crew">Klik hier om doorverwezen te worden</a></body></html>'
		response_header = [('Content-type', 'text/html'), ('Location', '/')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	MACToDelete = GetMACFromCount(index)
	IPToDelete = GetIPFromCount(index)

	# Verwijder gegevens uit databank.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute("DELETE FROM LoggedIn WHERE macAddress = '" + MACToDelete + "';")
	connection.commit()

	# Zet iptables settings terug.
	redirect_commands = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', IPToDelete,
		'-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.22.1:80']
	subprocess.Popen(redirect_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	redirect_commands2 = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', IPToDelete,
		'-p', 'tcp', '--dport', '443', '-j', 'DNAT', '--to-destination', '192.168.22.1:443']
	subprocess.Popen(redirect_commands2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Ontzeg internet voor het IP adres. (POSTROUTING)
	command = ['sudo', 'iptables', '-t', 'nat', '-D', 'POSTROUTING', '--source', IPToDelete,
		'-o', 'eth0', '-j', 'MASQUERADE']
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Doorverwijzen naar /crew.
	status = "307 Temporary Redirect"
	html = '<html><body><a href="/crew">Klik hier om doorverwezen te worden</a></body></html>'
	response_header = [('Content-type', 'text/html'), ('Location', '/crew')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]
