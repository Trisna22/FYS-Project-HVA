#       Name:                           crew.py (Crew pagina in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  10-12-2019
#       Author:                         Trisna Quebe ic106-2
#       Taken from older version:       wsgi.py by Trisna

import mysql.connector as mariaDB
import urllib.parse as urlparse
import os
import subprocess
import hashlib

# De standaard pagina die de crew krijgt bij een GET request.
def sendCrewPage(environ, start_response, triedAlready = False):
	prePath = '/var/www/FYS/encrypted/crew/index.html'

	status = "200 OK"

	html = ""
	file = open(prePath, "r")
	for line in file:
		html += line[:-1]
	file.close()

	# Kijken if gebruiker al eerder heeft ingelogd.
	if triedAlready == True:
		html = html.replace("hidden", "")

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# De functie die de bestanden in de static map verstuurt.
def sendStaticFiles(environ, start_response):

	prePath = '/var/www/FYS/encrypted/crew/static/'
	requestFile = prePath + environ['REQUEST_URI']

	# Beveiliging voor string escaping.
	if requestFile.find("..") != -1:
		status = "400 Not Found"
		html = "<html><body><h1>URL not found!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Kijken of het bestand bestaat op de schijf.
	if os.path.isfile(requestFile) == False:
		status = "400 Not Found"
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

	# Als de string veilig is return waar.
	return True

# Checkt of de gebruikersnaam en wachtwoord klopt.
def checkLogin(username, password):

	# Connectie maken met databank en inlog checken.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Hash het wachtwoord om te vergelijken. We gebruiken MD5.
	# De MD5 hash is gesalted, zodat het moeilijker te kraken is.
	saltedPassword = "*///CaptP_" + password + "_CaptP*///"

	hashObject = hashlib.md5(saltedPassword.encode())
	hashCompare = hashObject.hexdigest()

	# SQL query om te checken.
	cursor.execute('SELECT EXISTS ( SELECT * FROM CrewLogin WHERE username = \'' + username +
		'\' AND password = \'' + hashCompare + '\');')

	result = cursor.fetchall()
	return result[0][0]

# Deze functie behandelt alle POST requests naar /crew.
def handlePOSTrequest(environ, start_response):

	# Verkrijg externe variabelen en kijk of ze veilig zijn.
	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)
	userName = params.get('CREW_USERNAME', [''])[0]
	passWord = params.get('CREW_PASSWORD', [''])[0]

	# Input validatie van de variabelen.
	if checkStringValue(userName) == False:
		return sendCrewPage(environ, start_response, True)
	if checkStringValue(passWord) == False:
		return sendCrewPage(environ, start_response, True)

	# Inlog checken.
	if checkLogin(userName, passWord) == False:
		return sendCrewPage(environ, start_response, True)

	# Kijken of inloggen werkt.
	html = "<html><body>"
	html += "USERNAME: " + userName + "<br>"
	html += "PASSWORD: " + passWord + "<br>"
	html += "Succesvol ingelogd!</body></html>"
	status = "200 OK"

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

