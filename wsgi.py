#	Name: 				wsgi.py (Webserver response in python)
#	Project: 			Fasten Your Seatbelts (FYS)
#	Creation date: 			9-10-2019
#	Author: 			Trisna Quebe ic106-2

import urllib.parse as urlparse
import os
import subprocess
import mysql.connector as mariaDB

debug = False

# If debug is set, run this code for the website.
def run_debug_code(environ, start_response):
	status = "200 OK"
	lines = [
		'<html>',
		'       <body>',
		'               <title>Test-wsgi page for fys</title>',
		'		TicketNumber: {us:s}<br>',
		'		SeatNumber: {pw:s}<br>',
		'		Environ vars: {en:s}<br>',
		'       </body>',
		'</html>' ]


	s = environ['wsgi.input'].read().decode()
	params = urlparse.parse_qs(s)

	username = params.get('TICKETNUMBER', [''])[0]
	password = params.get('SEATNUMBER', [''])[0]


	html = '\n'.join(lines).format(ev=str(environ), us=str(username),
		pw=str(password), en=str(environ))

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

# Checks ticketnumber and seatnumber for login.
def checkCredentials(TICKETNUMBER, SEATNUMBER):

	# Check if the strings doesn't contain any escaping code.
	if checkStringValue(TICKETNUMBER) == False:
		return False
	if checkStringValue(SEATNUMBER) == False:
		return False

	# Now we know that the variables are safe,
	# we can check if it is correct.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT EXISTS ( SELECT * FROM Passengers WHERE ticketNumber = \'' +
		 TICKETNUMBER + '\' AND seatNumber = \'' + SEATNUMBER + '\');')

	result = cursor.fetchall()
	return result[0][0]

# Adds current connected device to database.
def UpdateLoggedInDatabase(TICKETNUMBER, SEATNUMBER, IP, MAC, LASTNAME):

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# First check if the device is already logged in.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ipAddress = \'' + 
		IP + '\' OR macAddress = \'' + MAC + '\');')
	result = cursor.fetchall()
	if result[0][0] == True:
		return False

	insertQuery = "INSERT INTO LoggedIn VALUES (\'" + IP + "\', \'" + MAC + "\', \'" + TICKETNUMBER
	insertQuery += "\', \'" + SEATNUMBER + "\', \'" + LASTNAME + "\'); "
	cursor.execute(insertQuery)

	connection.commit()
	return True

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

# Function that allows device connect to internet.
def AllowDeviceToInternet(TICKETNUMBER, SEATNUMBER, IP, start_response):

	# Connect to database.
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Retrieve firstname from database.
	cursor.execute('SELECT firstName FROM Passengers WHERE ticketNumber = ' + TICKETNUMBER + ';')
	result = cursor.fetchall()
	FIRSTNAME = result[0][0].encode('ascii').decode('utf-8')

	# Retrieve lastname from database.
	cursor.execute('SELECT lastName FROM Passengers WHERE ticketNumber = ' + TICKETNUMBER + ';')
	result = cursor.fetchall()
	LASTNAME = result[0][0].encode('ascii').decode('utf-8')

	# Retrieve MAC address from device.
	MAC = "AA:BB:CC:DD:AA:BB"

	# Check if we already are logged in
	if UpdateLoggedInDatabase(TICKETNUMBER, SEATNUMBER, IP, MAC, LASTNAME) == False:

		status = "200 OK"
		lines = [
			'<html>',
			'       <body>',
			'               <title>Already logged in!</title>',
			'               <br><br>',
			'		<h3> This device is already logged in!!</h3>',
			'               <p>Client IP address: {ip:s}</p>',
			'               <p>Client MAC address: {mc:s}</p>',
			'       </body>',
			'</html>' ]

		html = '\n'.join(lines).format(ip=IP, mc=MAC)
		response_header = [('Content-type', 'text/html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	else:
		# Using subprocess module to create a system command with iptables.
		command = ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-m', 'mac', '--mac-source', MAC, '-o', 'eth0', '-j', 'MASQUERADE']
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		error_msg = p.communicate()

		# Our response.
		status = "200 OK"

		lines = [
			'<html>',
			'       <body>',
			'               <title>Succesfully logged in!</title>',
			'		<br><br>',
			'		<h3>Dear {fr:s} {ln:s},</br></br> you can use the internet now!<h3>',
			'		<p>Client IP address: {ip:s}</p>',
			'		<p>Client MAC address: {mc:s}</p>',
			'		<p>Error msg: {er:s}</p>',
			'       </body>',
			'</html>' ]
		html = '\n'.join(lines).format(fr=FIRSTNAME, ln=LASTNAME, ip=IP, mc=MAC, er=str(error_msg))

		response_header = [('Content-type', 'text/html')]
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
	TICKETNUMBER = params.get('TICKETNUMBER', [''])[0]
	SEATNUMBER = params.get('SEATNUMBER', [''])[0]

	# IP address we want to allow to our network.
	IP = environ['REMOTE_ADDR']

	# Check if credentials is correct.
	if checkCredentials(TICKETNUMBER, SEATNUMBER) == False:
		return incorrect_password(environ, start_response)

	# Allow device to internet.
	return AllowDeviceToInternet(TICKETNUMBER, SEATNUMBER, IP, start_response)

if __name__ == "__main__":
	application({}, print)

