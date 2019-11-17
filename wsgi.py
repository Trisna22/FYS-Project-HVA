#	Name: 				wsgi.py (Webserver response in python)
#	Project: 			Fasten Your Seatbelts (FYS)
#	Creation date: 			9-10-2019
#	Author: 			Trisna Quebe ic106

import urllib.parse as urlparse
import os
import subprocess

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

# Checks if the external variable contains code execution
# by string escaping or weird characters.
def checkStringValue(string):

	# Set up a list with forbidden characters.
	forbiddenChars = ['#', '\'', '\\', '"', '~', '/', '>', '@',
			'<', '{', '}', ';', ':', '(', ')', '?', '*', '$', '!', '|']

	# Compare every character of string with the list.
	for characterFromString in string:
		for charFromForbiddenList in forbiddenChars:
			if characterFromString == charFromForbiddenList:
				return False

	# Check if the values of the string is between 0-z (48 - 122)
	# on the ASCII table, so no weird characters can be used.
	for characterFromString in string:
		if ord(characterFromString) < 48 or ord(characterFromString) > 122:
			return False

	return True

# Checks username and password for login.
# (dummy)
def checkCredentials(username, password):

	# Check if the strings doesn't contain any escaping code.
	if checkStringValue(username) == False:
		return False
	if checkStringValue(password) == False:
		return False

	# Now we know that the variables are safe,
	# we can check if it is corerct.
	if username == "admin" and password == "pass":
		return True
	else:
		return False

# Prints out the page for wrong username/password.
def incorrect_password(environ, start_response):
	status = "307 Temporary Redirect"

	"""
	lines = [
		'<html>',
		'       <body>',
		'               <title>Wrong credentials</title>',
		'		<h3>Wrong username/password!</h3>',
		'		<h4>Dummy login page</h4>',
		'       </body>',
		'</html>' ]
	"""

	html = '\n'

	response_header = [('Content-type', 'text/html'), ('Location', '/wrong_password.html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# If the user sent a wrong HTTP request.
def wrong_request(environ, start_response):
	status = "307 Temporary Redirect"
	lines = [
		'<html>',
		'	<body>',
		'		<title>Bad request</title>',
		'		<h3>Invalid request sent!</h3>',
		'	</body>',
		'</html>' ]
	html = '\n'.join(lines)

	response_header = [('Content-type', 'text/html'), ('Location', '/index.html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Main function of program.
def application(environ, start_response):

	# Check if we want the debug code to run.
	if debug == True:
		return run_debug_code(environ, start_response)

	if environ['REQUEST_METHOD'] != 'POST':
		return wrong_request(environ, start_response)

	# Retrieve login credentials.
	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)
	username = params.get('TICKETNUMBER', [''])[0]
	password = params.get('SEATNUMBER', [''])[0]


	# Check if credentials is correct.
	if checkCredentials(username, password) == False:
		return incorrect_password(environ, start_response)


	# IP address we want to allow to our network.
	IP = environ['REMOTE_ADDR']

	# Using subprocess module to create a system command with iptables.
	command = ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '--source', IP, '-o', 'eth0', '-j', 'MASQUERADE']
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	error_msg = p.communicate()

	# Our response.
	status = "200 OK"

	lines = [
		'<html>',
		'       <body>',
		'               <title>Succesfully logged in!</title>',
		'		<center>',
		'		Username: {us:s}<br>',
		'		Password: {pw:s}<br>',
		'		<br><br>',
		'		<h3>You can use the wifi network now!<h3>',
		'		<p>Client IP address: {ip:s}</p>',
		'		<p>Error msg: {er:s}</p>',
		'		</center>',
		'       </body>',
		'</html>' ]
	html = '\n'.join(lines).format(us=str(username),
		pw=str(password), ip=str(environ['REMOTE_ADDR']), er=str(error_msg))


	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]


if __name__ == "__main__":
	application({}, print)

