import urllib.parse as urlparse
import os

import login	# Staat in de /usr/lib/python3.7/ folder.


# Verstuurt de benodigde bestanden voor de html code.
def sendStaticFile(environ, start_response):
	status = "200 OK"

	prePath = '/var/www/FYS/encrypted/'
	requestFile = prePath + environ['REQUEST_URI']

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
		else:
			response_header = [('Content-type', 'text/html')]

		start_response(status, response_header)
		return [static]


def application(environ, start_response):
	status = "200 OK"
	html = "<html>\n"
	html += '<head>\n'
	html += '<link rel="stylesheet" type="text/css" href="static/style.css" />\n'
	html += '</head>\n'
	html += "<body>\n"

	if str(environ['REQUEST_URI']).find('/static/') != -1:
		return sendStaticFile(environ, start_response)

	if environ['REQUEST_METHOD'] == 'GET':

		html += '<form method="post" action="login">'
		html += '<input type="text" name="TICKETNUMBER"/><br>'
		html += '<input type="text" name="SEATNUMBER"/><br>'
		html += '<input type="submit" value="submit"/>'
		html += '<script src="static/script.js" />'
		html += '</form>'
		html += "<body></html>"

	# Als we een post request opvangen, we laten de login over aan de login.py script.
	elif environ['REQUEST_METHOD'] == 'POST' and environ['REQUEST_URI'] == '/login':

		return login.doLogin(environ, start_response)

	else:
		status = "405 Method Not Allowed"
		html += "<html><body><h1>Illegal HTTP method!</h1></body></html>"


	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


if __name__ == "__main__":
	application({}, print)

