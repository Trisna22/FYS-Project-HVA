import urllib.parse as urlparse
import mysql.connector as mariaDB
import os

import login	# Staat in de /usr/lib/python3.7/ folder.
import logout	# Staat in de /usr/lib/python3.7/ folder.

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
			static = lines.append(line)
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
		html += i

	html = html.replace('{{firstName}}', firstName)
	html = html.replace('{{lastName}}', lastName)
	html = html.replace('{{MAC}}', MAC)
	html = html.replace('{{IP}}', IP)

	file.close()
	status = "200 OK"
	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


def deviceNotLoggedInHTML(environ, start_response):
	status  = '200 OK'
	html = '<html>'
	html += '<head><link rel="stylesheet" type="text/css" href="/static/style.css" >'
	html += '<center style="margin-top: 200px">'
	html += '<form method="post" action="login">'
	html += '<input type="text" name="TICKETNUMBER" placeholder="TicketNumber"/><br>'
	html += '<input type="text" name="SEATNUMBER" placeholder="SeatNumber"/><br>'
	html += '<input type="submit" value="submit"/>'
	html += '</form>'
	html += '</center>'
	html += "<body></html>"

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

def application(environ, start_response):

	status = "200 OK"

	if str(environ['REQUEST_URI']).find('/static/') != -1:
		return sendStaticFile(environ, start_response)

	if environ['REQUEST_METHOD'] == 'GET':

		if login.checkIfDeviceLoggedIn(environ) == True:
			return deviceLoggedInHTML(environ, start_response)
		else:
			return deviceNotLoggedInHTML(environ, start_response)

	# Als we een post request opvangen, we laten de login over aan de login.py script.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'] == '/login':
		return login.doLogin(environ, start_response)

	# Als we een post request opvangen, we laten de logout over aan de logout.py script.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'] == '/logout':
		return logout.doLogout(environ, start_response)

	# Alle overige methodes negeren.
	else:
		status = "405 Method Not Allowed"
		html += "<html><body><h1>Illegal HTTP method!</h1></body></html>"


	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


if __name__ == "__main__":
	application({}, print)

