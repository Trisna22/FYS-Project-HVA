#       Name:                           crew.py (Crew pagina in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  10-12-2019
#       Author:                         Trisna Quebe ic106-2
#       Taken from older version:       wsgi.py by Trisna

# De standaard pagina die de crew krijgt bij een GET request.
def sendCrewPage(environ, start_response):
	prePath = '/var/www/FYS/encrypted/crew/index.html'

	status = "200 OK"

	html = ""
	file = open(prePath, "r")
	for line in file:
		html += line[:-1]
	file.close()

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

# Deze functie behandelt alle POST requests naar /crew.
def handlePOSTrequest(environ, start_response):
		status = "404 Not Found"
		html = "<html><body><h1>URL not found!</h1></body></html>"

		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

