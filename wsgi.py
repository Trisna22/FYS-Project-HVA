#	Name:		wsgi.py (Webserver response in python)
#	Project:	Fasten Your Seatbelts (FYS)
#	Creation date:	9-10-2019

import sys
import datetime
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

import urllib.parse as urlparse

debug = False

# If debug is set, run this code for the website.
def run_debug_code(environ, start_response):
	status = "200 OK"
	lines = [
		'<html>',
		'       <body>',
		'               <title>Test-wsgi page for fys</title>',
		'		Username: {us:s}<br>',
		'		Password: {pw:s}<br>',
		'       </body>',
		'</html>' ]


	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)

	username = params.get('USERNAME', [''])[0]
	password = params.get('PASSWORD', [''])[0]


	html = '\n'.join(lines).format(ev=str(environ), us=str(username),
		pw=str(password))

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


# Checks username and password for login.
# (dummy)
def checkCredentials(username, password):
	if username == "admin" and password == "pass":
		return True
	else:
		return False

# Prints out the page for wrong username/password.
def incorrect_password(environ, start_response):
	status = "200 OK"
	lines = [
		'<html>',
		'       <body>',
		'               <title>Test-wsgi page for fys</title>',
		'		<h3>Wrong username/password!</h3>',
		'		<h4>Dummy login page</h4>',
		'       </body>',
		'</html>' ]

	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


def application(environ, start_response):

	# Check if we want the debug code to run.
	if debug == True:
		return run_debug_code(environ, start_response)


	# Retrieve login credentials.
	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)
	username = params.get('USERNAME', [''])[0]
	password = params.get('PASSWORD', [''])[0]


	# Check if credentials is correct.
	if checkCredentials(username, password) == False:
		return incorrect_password(environ, start_response)


	#
	#
	#	TEST CODE beneden.
	#
	#
	status = "200 OK"
	lines = [
		'<html>',
		'       <body>',
		'               <title>Test-wsgi page for fys</title>',
		'		Username: {us:s}<br>',
		'		Password: {pw:s}<br>',
		'       </body>',
		'</html>' ]



	html = '\n'.join(lines).format(us=str(username),
		pw=str(password))

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


if __name__ == "__main__":
	application({}, print)

