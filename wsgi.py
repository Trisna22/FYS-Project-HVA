#	Author:		Trisna Quebe
#	Name:		wsgi.py (Webserver response in python)
#	Project:	Fasten Your Seatbelts (FYS)

import sys
import datetime
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape


# For debugging.
debug = False

# Kijkt of de gebruikersnaam of wachtwoord bestaat in de database file.
def checkLogin(c1, c2):
	f = open("/home/tris/database.txt", "r")
	for i in f:
		if i.find(c1 + "   ") != -1:
			if i.find(c2 + "   ") != -1:
				return True
	f.close()
	return False

# Maakt een nieuw account aan in the database file.
def createAccount(c1, c2, c3):

	# Kijkt of de gebruikers naam al bestaat.
	if checkUserNameMail(c1, c3) == True:
		return "Gebruikersnaam of emailadres bestaat al!"

	# Vanwege permission problemen heb ik het in de home folder gedaan.
	f = open("/home/tris/database.txt", "a")
	f.write(c1 + "   " + c2 + "   " + c3 + "\n")
	f.close()

	return "TRUE"

# Kijkt of de gebruikersnaam of email al bestaat.
def checkUserNameMail(user, mail):
	f = open("/home/tris/database.txt", "r")
	for i in f:
		if i.find(user + "   ") != -1 or i.find("   " + mail) != -1:
			return True

	f.close
	return False

# Main function van script.
def application(environ, start_response):

	if debug == True:
		status = "200 OK"
		array = []
		fs = open("/var/www/FYS/index.html", "r")
		for i in fs:
			array.append(i)

		html = '\n'.join(array)
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# GET REQUEST.
	if environ['REQUEST_METHOD'] == 'GET' and environ['REQUEST_URI'] == '/wsgi':
		status = "200 OK"
		array = []
		fs = open("/var/www/FYS/index.html", "r")
		for i in fs:
			array.append(i)

		html = '\n'.join(array)
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Response to the login.
	elif environ['REQUEST_METHOD'] == 'GET' and '/wsgi?login;' in environ['REQUEST_URI']:
		status = "200 OK"

		str = environ['REQUEST_URI']

		lines = []
		# Split the string in information values.
		c1 = str[str.find("user=")+5:str.find("&")]
		c2 = str[str.find("&")+6:]

		# Check if username and password exists in database.
		if checkLogin(c1, c2) == True:
			lines.append("TRUE")
		else:
			lines.append("Fout gebruikersnaam of wachtwoord ingevoerd!")

		html = '\n'.join(lines)
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# Response to creating account.
	elif environ['REQUEST_METHOD'] == 'GET' and '/wsgi?signup;' in environ['REQUEST_URI']:
		status = "200 OK"

		str = environ['REQUEST_URI']
		lines = []

		# Split the string in information values.
		c1 = str[str.find("user=")+5:str.find("&pass")]
		c2 = str[str.find("&pass=")+6:str.find("&email")]
		c3 = str[str.find("&email=")+7:]

		# Creates account.
		lines.append(createAccount(c1, c2, c3))

		html = '\n'.join(lines)
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	else:
		status = "200 OK"
		lines = [
			'<html>',
			'       <body>',
			'               <title>Test-wsgi page for fys</title>',
			'		<p>Other request</p>',
			'		<peviron: {ev:s}</p>',
			'       </body>',
			'</html>' ]
		html = '\n'.join(lines).format(ev=str(environ))
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]


if __name__ == "__main__":
	application({}, print)
