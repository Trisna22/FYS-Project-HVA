#       Name:                           login.py (Login response in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  4-12-2019
#       Author:                         Trisna Quebe ic106-2
#	Taken from older version:	wsgi.py by Trisna

import mysql.connector as mariaDB
import urllib.parse as urlparse

# Verstuurt content van HTML fout login.
def wrong_login(environ, start_response):
	status = '200 OK'

	# Open file with wrong password.
	lines = []
	file = open('/var/www/FYS/encrypted/wrong_login.html', 'r')
	for i in file:
		lines.append(str(i))
	file.close()

	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


# Verstuurt content van HTML goed login.
def correct_login(environ, start_response):
	status = '200 OK'

	html = '<html>'
	html += '<body>Ingelogd!</body>'
	html += '</html>'

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


# Checkt of het apparaat dat op de site komt al is ingelogd.
def checkIfDeviceLoggedIn(IP, MAC):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# SQL Query om te checken.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ipAddress = \'' +
		IP + '\' OR macAddress = \'' + MAC + '\');')

	# Resultaat van SQL Query.
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

	# Kijken of de externe variabelen veilig zijn.
	if checkStringValue(ticketNumber) == False:
		return False
	if checkStringValue(seatNumber) == False:
		return False

	# Nu we weten dat de variabelen veilig zijn,
	# kunnen we kijken of het ticketnummer en stoelnummer kloppen.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT EXISTS ( SELECT * FROM Passengers WHERE ticketNumber = \'' +
		ticketNumber + '\' AND seatNumber = \'' + seatNumber + '\');')

	# Return de output als waar of niet waar.
	result = cursor.fetchall()
	return result[0][0]


# Het inloggen van de gebruiker.
def doLogin(environ, start_response):

	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)

	TICKETNUMBER = params.get('TICKETNUMBER', [''])[0]
	SEATNUMBER = params.get('SEATNUMBER', [''])[0]

	# Login check.
	if checkCredentials(TICKETNUMBER, SEATNUMBER) == False:
		return wrong_login(environ, start_response)
	else:
		return correct_login(environ, start_response)
