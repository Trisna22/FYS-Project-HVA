#       Name:                           login.py (Login response in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  4-12-2019
#       Author:                         Trisna Quebe ic106-2
#       Taken from older version:       wsgi.py by Trisna

import mysql.connector as mariaDB
import urllib.parse as urlparse
import os
import subprocess

# Kijkt of de gebruiker eigenlijk wel online is.
def checkIfOnline(IP, MAC):
	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	cursor.execute('SELECT EXISTS ( SELECT * FROM LoggedIn WHERE ipAddress = \'' +
		IP + '\' AND macAddress = \'' + MAC + '\');')

	result = cursor.fetchall()
	return result[0][0]

# Gebruiker is niet online, in HTML.
def not_online(environ, start_response):
	status = '200 OK'

	html = '<html><body><h1>Gebruiker niet online!</h1>'
	html += '<a href="/">Klik hier om in te loggen</a></body></html>'

	response_header = [('Content-type', 'text/html')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]

# Verwerk de logout gegevens in de databank en set de iptables.
def updateLoginStatus(IP, MAC):

	connection = mariaDB.connect(host='127.0.0.1', user='root', passwd='IC106_2', db='CaptivePortalDB')
	cursor = connection.cursor()

	# Verwijder de gegevens uit de LoggedIn table van de databank.
	cursor.execute('DELETE FROM LoggedIn WHERE ipAddress = \'' + IP +
		'\' AND macAddress = \'' + MAC + '\';')

	connection.commit()

	# Voeg de PREROUTING tables toe.
	redirect_commands = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', IP,
		'-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.22.1:80']
	subprocess.Popen(redirect_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	redirect_commands2 = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', IP,
		'-p', 'tcp', '--dport', '443', '-j', 'DNAT', '--to-destination', '192.168.22.1:443']
	subprocess.Popen(redirect_commands2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Ontzeg internet voor het IP adres. (POSTROUTING)
	command = ['sudo', 'iptables', '-t', 'nat', '-D', 'POSTROUTING', '--source', IP,
		'-o', 'eth0', '-j', 'MASQUERADE']
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Verkrijg het MAC address van de bijbehorende IP address.
def GetMacFromIP(IP):
	MAC = os.popen("arp -n | grep \"" + IP + "\" | awk \'{print $3}\'").read()
	return MAC[:-1]

# Log gebruiker uit.
def doLogout(environ, start_response):

	# Verkrijg de benodigde MAC en IP adres.
	IP = environ['REMOTE_ADDR']
	MAC = GetMacFromIP(IP)

	# Check of gebruiker online is.
	if checkIfOnline(IP, MAC) == False:
		return not_online(environ, start_response)

	# Update onze gegevens met de databank en iptables.
	updateLoginStatus(IP, MAC)

	# Onze html response.
	html = '<html><body><h1>Succesfully logged out!</h1><br>'
	html += '<a href="/">Click here to go to the login page!</a></body></html>'

	status = '301 Moved Permanently'
	response_header = [('Content-type', 'text/html'), ('Location', '/')]
	start_response(status, response_header)
	return [bytes(html, 'utf-8')]
