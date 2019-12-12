#       Name:                           login.py (Login response in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  4-12-2019
#       Author:                         Trisna Quebe ic106-2
#	Taken from older version:	wsgi.py by Trisna

import mysql.connector as mariaDB
import urllib.parse as urlparse
import os
import subprocess

# Verstuurt content van HTML fout login.
def wrong_login(environ, start_response):
	status = '200 OK'

	# Open file with wrong login.
	lines = []
	file = open('/var/www/FYS/encrypted/wrong_login.html', 'r')
	for i in file:
		lines.append(i[:-1])
	file.close()

	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Verstuurt content van HTML ticket al ingelogd.
def ticket_already_used(environ, start_response):
	status = '200 OK'

	# Open file with ticket already logged in.
	lines = []
	file = open('/var/www/FYS/encrypted/ticket_already_used.html')
	for i in file:
		lines.append(i[:-1])
	file.close()

	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Update de databank met tickets die al ingelogd zijn.
def updateLoggedInDatabase(IP, MAC, ticketNumber, seatNumber, lastName):

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Nu we weten dat het ticketnummer nog niet ingelogd is,
	# kunnen we de gegevens in de databank inserten.
	insertQuery = "INSERT INTO LoggedIn VALUES (\'" + IP + "\', \'" + MAC + "\', \'"
	insertQuery += ticketNumber + "\', \'" + seatNumber + "\', \'" + lastName + "\');"
	cursor.execute(insertQuery)

	connection.commit()

	# Als we klaar zijn met de database, moeten we de IPtables ook configureren,
	# dat het IP address internet mag gebruiken, en de PREROUTING uitgezet.
	redirect_commands = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', '-s', IP,
		'-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '']
	subprocess.Popen(redirect_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	redirect_commands2 = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', '-s', IP,
		'-p', 'tcp', '--dport', '443', '-j', 'DNAT', '--to-destination', '192.168.22.1:443']
	subprocess.Popen(redirect_commands2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	command = ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '--source', IP, 
		'-o', 'eth0', '-j', 'MASQUERADE']
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Verstuurt content van HTML goed login.
def correct_login(environ, start_response, ticketNumber, seatNumber, IP, MAC):

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Verkrijg de firstName van de databank ovor onze html content.
	cursor.execute('SELECT firstName FROM Passengers WHERE ticketNumber = ' + ticketNumber + ';')
	result = cursor.fetchall()
	firstName = result[0][0].encode('ascii').decode('utf-8')

	# Verkrijg nog de laatste vereiste variabele lastName.
	cursor.execute('SELECT lastName FROM Passengers WHERE ticketNumber = ' + ticketNumber + ';')
	result = cursor.fetchall()
	lastName = result[0][0].encode('ascii').decode('utf-8')

	# Update the LoggedIn databank.
	updateLoggedInDatabase(IP, MAC, ticketNumber, seatNumber, lastName)

	# HTML content.
	status = '200 OK'
	html = ""

	# HTML pagina om te versturen.
	file = open("/var/www/FYS/encrypted/loggedin.html", "r")
	for i in file:
		html += i[:-1]
	file.close()

	html = html.replace('{{firstName}}', firstName)
	html = html.replace('{{lastName}}', lastName)
	html = html.replace('{{MAC}}', MAC)
	html = html.replace('{{IP}}', IP)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Als apparaat al ingelogd is.
def already_loggedin(environ, start_response, ticketNumber, seatNumber, IP, MAC):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Verkrijg de firstName van de databank ovor onze html content.
	cursor.execute('SELECT firstName FROM Passengers WHERE ticketNumber = ' + ticketNumber + ';')
	result = cursor.fetchall()
	firstName = result[0][0].encode('ascii').decode('utf-8')

	# Verkrijg nog de laatste vereiste variabele lastName.
	cursor.execute('SELECT lastName FROM Passengers WHERE ticketNumber = ' + ticketNumber + ';')
	result = cursor.fetchall()
	lastName = result[0][0].encode('ascii').decode('utf-8')

	# HTML pagina om te versturen.
	html = ""
	file = open("/var/www/FYS/encrypted/loggedin.html", "r")
	for i in file:
		html += i[:-1]
	file.close()

	html = html.replace('{{firstName}}', firstName)
	html = html.replace('{{lastName}}', lastName)
	html = html.replace('{{MAC}}', MAC)
	html = html.replace('{{IP}}', IP)

	status = "200 OK"
	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Verkrijg het MAC address van de bijbehorende IP address.
def GetMacFromIP(IP):
	MAC = os.popen("arp -n | grep \"" + IP + "\" | awk \'{print $3}\'").read()
	return MAC[:-1]

# Checkt of het apparaat dat op de site komt al is ingelogd.
def checkIfDeviceLoggedIn(environ):

	# Verkrijg de benodigde MAC en IP adres.
	IP = environ['REMOTE_ADDR']
	MAC = GetMacFromIP(IP)

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# SQL Query om te checken.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ipAddress = \'' +
		IP + '\' OR macAddress = \'' + MAC + '\');')

	# Resultaat van SQL Query.
	result = cursor.fetchall()
	return result[0][0]

# Checkt of het ticketnummer al ingelogd is.
def checkIfTicketLoggedIn(ticketNumber, seatNumber):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# SQL Query om te checken.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ticketNumber = \'' +
		ticketNumber + '\' OR seatNumber = \'' + seatNumber + '\');')
	result = cursor.fetchall()
	return result[0][0]


# Controleert of een string geen code of string escaping bevat.
def checkStringValue(string):
	# Set up a list with forbidden characters.
	forbiddenChars = ['#', '\'', '\\', '"', '~', '/', '>', '@', '\n', '\t', '-', '=',
		'<', '{', '}', ';', ':', '(', ')', '?', '*', '$', '!', '|', '*']

	# Vergelijk elke character van de string met de verboden lijst.
	for characterFromString in string:
		for charFromForbiddenList in forbiddenChars:
			if characterFromString == charFromForbiddenList:
				return False

	# Kijkt of de ASCII waarden tussen de 0-9, a-z en A-Z liggen.
	for characterFromString in string:
		if ord(characterFromString) < 48 or ord(characterFromString) > 122:
			return False

	# Lijst met verboden strings om te checken in de variabelen.
	# Gebasseerd op onderzoek Trisna.
	'''
	forbiddenStrings = ['SELECT', 'select', 'drop', '<SCRIPT>','<script>', '/>',
		'DROP', '<?', '?>']
	for stringInString in string:
		for forbiddenStr in forbiddenStrings:
			if stringInString == forbiddenStr:
				return False
	'''

	# Als de string veilig is return waar.
	return True


# Checkt of de ticketnummer met de stoelnummer correct zijn.
def checkCredentials(ticketNumber, seatNumber):

	# Nu we weten dat de variabelen veilig zijn,
	# kunnen we kijken of het ticketnummer en stoelnummer kloppen.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT EXISTS ( SELECT * FROM Passengers WHERE ticketNumber = \'' +
		ticketNumber + '\' AND seatNumber = \'' + seatNumber + '\');')

	# Return de output als waar of niet waar.
	result = cursor.fetchall()
	return result[0][0]


# Het inloggen van de gebruiker. (POST request)
def doLogin(environ, start_response):

	# Verkrijg de benodigde MAC en IP adres.
	IP = environ['REMOTE_ADDR']
	MAC = GetMacFromIP(IP)

	# Parse de POST variabelen van onze form.
	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)
	ticketNumber = params.get('TICKETNUMBER', [''])[0]
	seatNumber = params.get('SEATNUMBER', [''])[0]

	# Kijken of de externe variabelen veilig zijn.
	if checkStringValue(ticketNumber) == False:
		return wrong_login(environ, start_response)
	if checkStringValue(seatNumber) == False:
		return wrong_login(environ, start_response)

	# Als het apparaat de POST request nog een keer stuurt, maar al ingelogd is.
	if checkIfDeviceLoggedIn(environ) == True:
		return already_loggedin(environ, start_response, ticketNumber, seatNumber, IP, MAC)

	# Checken of de ticket en stoelnummer al gebruikt zijn om in te loggen.
	if checkIfTicketLoggedIn(ticketNumber, seatNumber) == True:
		return ticket_already_used(environ, start_response)

	# Login check.
	if checkCredentials(ticketNumber, seatNumber) == False:
		return wrong_login(environ, start_response)
	else:
		return correct_login(environ, start_response, ticketNumber, seatNumber, IP, MAC)

