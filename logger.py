#       Name:                           logger.py (Crew pagina in python)
#       Project:                        Fasten Your Seatbelts (FYS)
#       Creation date:                  14-12-2019
#       Author:                         Trisna Quebe ic106-2
#       Taken from older version:       wsgi.py by Trisna

import datetime
import os

# Print de actie van client uit in log bestand.
def logAction(IP, MAC, action):
	file = open('/var/www/FYS/encrypted/website_logs.log', 'a')

	line = str(datetime.datetime.now()) + "# " + IP + "::" + MAC + " " + action + '\n'

	file.write(line)
	file.close()

# Opent het logbestand om te laten zien op de website.
def getLogData():

        logs = ""
        file = open('/var/www/FYS/encrypted/website_logs.log', 'r')
        for line in file:
                logs += '<p>' + line + '</p>'
        file.close()

        return logs
