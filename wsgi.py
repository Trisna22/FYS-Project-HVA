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
	forbiddenChars = ['#', '\'', '\\', '"', '~', '/', '>', '@', '\n', '\t', '-', '=',
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

# Retrieves the MAC address from the IP in the ARP table.
def GetMACFromIP(IP):
	MAC = os.popen("arp -n | grep \"" + IP + "\" | awk \'{print $3}\'").read()
	return MAC[:-1]

# Adds current connected device to database.
def UpdateLoggedInDatabase(TICKETNUMBER, SEATNUMBER, IP, MAC, LASTNAME):

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()


	# First check if the device is already logged in.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ipAddress = \'' + 
		IP + '\' OR macAddress = \'' + MAC + '\');')
	result = cursor.fetchall()
	if result[0][0] == True:
		return 1

	# Than check if the ticketnumber is already logged in.
	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ticketNumber = \'' +
		TICKETNUMBER + '\' OR lastName = \'' + LASTNAME + '\');')
	result = cursor.fetchall()
	if result[0][0] == True:
		return 2

	insertQuery = "INSERT INTO LoggedIn VALUES (\'" + IP + "\', \'" + MAC + "\', \'" + TICKETNUMBER
	insertQuery += "\', \'" + SEATNUMBER + "\', \'" + LASTNAME + "\'); "
	cursor.execute(insertQuery)

	connection.commit()
	return 0

# Prints out the page for wrong username/password.
def incorrect_password(environ, start_response):
	status = "307 Temporary Redirect"
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
	MAC = GetMACFromIP(IP)

	statusCode = UpdateLoggedInDatabase(TICKETNUMBER, SEATNUMBER, IP, MAC, LASTNAME)

	# Check if the device is already logged in.
	if statusCode == 1:
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

	# Check if the ticketnumber is already logged in.
	elif statusCode == 2:

		status = "307 Temporary Redirect"
		lines = [
			'<html>',
			'	<body>',
			'		<title>Ticket already logged in!</title>',
			'		<h1>Ticket is already logged in!</title>',
			'	</body>',
			'</html>' ]

		html = '\n'.join(lines)
		response_header = [('Content-type', 'text/html'), ('Location', '/ticket_already_loggedin.html')]
		start_response(status, response_header)
		return [bytes(html, 'utf-8')]

	# If the device and ticketnumber isn't yet logged in.
	elif statusCode == 0:

		# Delete the redirection to captive portal.
		redirect_commands = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', '-s', IP,
			'-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.22.1:80' ]
		subprocess.Popen(redirect_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		redirect_commands2 = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', '-s', IP,
			'-p', 'tcp', '--dport', '443', '-j', 'DNAT', '--to-destination', '192.168.22.1:443' ]
		subprocess.Popen(redirect_commands2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		# Using subprocess module to create a system command with iptables.
		# MOET NOG VERANDEREN NAAR MAC!
		command = ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '--source', IP, '-o', 'eth0', '-j', 'MASQUERADE']
		p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		error_msg = p.communicate()

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

	# If the status code is something else than we expected.
	else:
		status = "200 OK"
		lines = [
			'<html>',
			'<body>',
			'	<h1>Unknown status code occured: {cd:s}',
			'</body>',
			'</html>' ]
		html = '\n'.join(lines).format(cd=str(statusCode))

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

