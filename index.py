#       Name:                           index.py (HTTP response in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  4-12-2019
#       Author:                         Trisna Quebe ic106-2
#       Taken from older version:       wsgi.py by Trisna

import urllib.parse as urlparse
import mysql.connector as mariaDB
import os

# De onderstaande modules staan in de map /usr/lib/python3.7/
import login	# Module om gebruikers in te loggen.
import logout	# Module om gebruikers uit te loggen.
import crew	# Module om crew login panel te verwerken.
import kickDevice # Module om apparaten uit het netwerk te schoppen.

# Verstuurt de benodigde bestanden voor de html code.
def sendStaticFile(environ, start_response):
	status = "200 OK"


	prePath = '/var/www/FYS/encrypted/'
	requestFile = prePath + environ['REQUEST_URI']

	# Beveiliging voor string escaping.
	if requestFile.find("..") != -1:
		status = "404 Not Found"
		html = "<html><body><h1>URL not found!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Kijken of het bestand bestaat op de schijf.
	if os.path.isfile(requestFile) == False:
		status = "404 Not Found"
		html = "<html><body><h1>URL not found!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Bestanden die als ascii text verstuurd kan worden.
	if requestFile.find('.css') != -1 or requestFile.find('.js') != -1:
		file = open(requestFile, 'r')
		lines = []
		for line in file:
			static = lines.append(line[:-1])
		file.close()

		html = '\n'.join(lines)

		response_header = []
		if requestFile.find('.css') != -1:
			response_header = [('Content-type', 'text/css')]
		else:
			response_header = [('Content-type', 'text/javascript')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Negeer de base files.
	elif requestFile.find('.html') != -1 or requestFile.find('.php') != -1:
		status = "404 Not Found"
		html = "<html><body><h1>URL not found!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]


	# Bestanden die als foto format verstuurd moet worden.
	else:
		# Open file from DocumentRoot than give it to the client.
		file = open(requestFile, 'rb')
		static = file.read()
		file.close()

		response_header = []
		if requestFile.find('.jpg') != -1:
			response_header = [('Content-type', 'image/jpg')]
		elif requestFile.find('.png') != -1:
			response_header = [('Content-type', 'image/png')]
		elif requestFile.find('.gif') != -1:
			response_header = [('Content-type', 'image/gif')]
		else:
			response_header = [('Content-type', 'text/html')]

		start_response(status, response_header)
		return [static]

# Als apparaat al ingelogd html code.
def deviceLoggedInHTML(environ, start_response):

	# Verkrijg IP en MAC
	IP = environ['REMOTE_ADDR']
	MAC = login.GetMacFromIP(IP)

	# Verkrijg gebruikersnaam en wachtwoord.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# DB: lastName
	cursor.execute('SELECT lastName FROM LoggedIn WHERE macAddress = \'' + MAC +
		'\' AND ipAddress = \'' + IP + '\';')
	result = cursor.fetchall()
	lastName = result[0][0].encode('ascii').decode('utf-8')

	# DB: ticketNumber
	cursor.execute('SELECT ticketNumber FROM LoggedIn WHERE macAddress = \'' + MAC +
		'\' AND ipAddress = \'' + IP + '\';')
	result = cursor.fetchall()
	ticketNumber = result[0][0].encode('ascii').decode('utf-8')

	# DB: firstName
	cursor.execute('SELECT firstName FROM Passengers WHERE lastName = \'' + lastName +
		'\' AND ticketNumber = \'' + ticketNumber + '\';')
	result = cursor.fetchall()
	firstName = result[0][0].encode('ascii').decode('utf-8')

	html = ""
	file = open('/var/www/FYS/encrypted/loggedin.html', 'r')
	for i in file:
		html += i[:-1]

	html = html.replace('{{firstName}}', firstName)
	html = html.replace('{{lastName}}', lastName)
	html = html.replace('{{MAC}}', MAC)
	html = html.replace('{{IP}}', IP)

	file.close()
	status = "200 OK"
	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# De standaard pagina die de client gaat als hij naar de Captive Portal gaat.
def deviceNotLoggedInHTML(environ, start_response):
	status  = '200 OK'

	# Pad naar standaard html file.
	htmlPath = '/var/www/FYS/encrypted/login.html'

	# Opent bestand voor de html code en leest het uit.
	file = open(htmlPath, 'r')
	lines = []
	for line in file:
		static = lines.append(line[:-1])
	file.close()

	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# De main functie van het hele programma.
def application(environ, start_response):

	status = "200 OK"

	# Als de browsers vragen om fotos of css/javascript files.
	if str(environ['REQUEST_URI']).find('/static/') != -1:
		return sendStaticFile(environ, start_response)

	# Elke GET request wordt opgevangen en verwerkt.
	if environ['REQUEST_METHOD'] == 'GET':

		if environ['REQUEST_URI'].find('/crew/static/') != -1:
			return crew.sendStaticFiles(environ, start_response)

		# Verstuurt de crew HTML code.
		if environ['REQUEST_URI'] == '/crew':
			return crew.sendCrewPage(environ, start_response)

		# Als het apparaat ingelogd is, doorverwijzen naar loggedIn HTML.
		if login.checkIfDeviceLoggedIn(environ) == True:
			return deviceLoggedInHTML(environ, start_response)
		# Als het apparaat nog niet ingelogd is, doorverwijzen naar nog niet ingelogd HTML.
		else:
			return deviceNotLoggedInHTML(environ, start_response)

	# Als we een post request opvangen, we laten de login over aan de login.py script.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'] == '/login':
		return login.doLogin(environ, start_response)

	# Als we een post request opvangen, we laten de logout over aan de logout.py script.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'] == '/logout':
		return logout.doLogout(environ, start_response)

	# Alle POST requests dat wordt gebruikt om mensen te kicken.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'].find('/crew/kick/') != -1:
		return kickDevice.kick(environ, start_response)

	# Alle overige POST requests met /crew in de query.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'].find('/crew') != -1:
		return crew.handlePOSTrequest(environ, start_response)

	# Alle overige HTTP methodes negeren.
	else:
		status = "405 Method Not Allowed"
		html = "<html><body><h1>Illegal HTTP method!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]


# Het allereerste ding waar de python interpreter naar kijkt.
if __name__ == "__main__":
	application({}, print)

