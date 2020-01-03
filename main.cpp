/*
	Author:		Trisna Quebe
	Group:		ic106-2
	School:		Hogeschool van Amsterdam (HvA)
	Project Name:	Fasten Your Seatbelts (FYS)
	Name:		hostsEditor
*/

#include <iostream>
#include <string>
#include <fstream>

#include <arpa/inet.h> // inet_pton() function.
#include <stdlib.h> // system() function.
#include <netdb.h> // gethostbyname() function.

using namespace std;

/*   Checkt of de string een IP adres is.   */
bool isIP(string IP)
{
	struct sockaddr_in sa;
	int result = inet_pton(AF_INET, IP.c_str(), &(sa.sin_addr));
	return result != 0;
}

/*   Checkt of de string wel een hostname is.   */
bool isHostName(string hostName)
{
	struct hostent* hostEntry = gethostbyname(hostName.c_str());
	if (hostEntry == NULL)
	{
		return false;
	}

	string IP = string(inet_ntoa(*((struct in_addr*)hostEntry->h_addr_list[0])));
	return isIP(IP);
}

/*   Voeg een host string toe aan de hosts file.   */
bool addHostToHostsFile(string host)
{
	// Open de hosts file.
	ofstream hostsFile("/etc/dnsmasq.conf", ios::app);
	if (!hostsFile.is_open())
	{
		printf("Failed to open the hosts file!\n\n");
		return false;
	}

	hostsFile << "address=/" + host + "/127.0.0.1" << endl;
	hostsFile.close();
	return true;
}

/*   Verwijder een host uit de hosts file.   */
bool deleteHostFromHostsFile(string host)
{
	// Open de hosts file.
	ofstream hostsFile("/etc/hosts");
	if (!hostsFile.is_open())
	{
		printf("Failed to open the hosts file!\n\n");
		return false;
	}
	return false;
}

int main(int argc, char* argv[])
{
	if (argc != 3)
	{
		printf("No argument/option given!\n\n");
		return -1;
	}

	// Checken of de 2e argument een bekend is.
	string secondArg = argv[1];
	if (!(secondArg == "-a" || secondArg == "-d"))
	{
		printf("Unknown argument/option!\n\n");
		return -1;
	}

	// Checken of de 3e argument wel een geldig hostname/ IP adres is.
	if (isIP(argv[2]) == false && isHostName(argv[2]) == false)
	{
		printf("The given string is not a real hostname/IP address!\n\n");
		return -1;
	}

	// Een host toevoegen aan de hosts file.
	if (secondArg == "-a")
	{
		if (addHostToHostsFile(argv[2]) == false)
		{
			printf("Failed to add host to hosts file!\n\n");
			return -1;
		}
	}

	// Een host verwijderen uit de hosts file.
	else if (secondArg == "-d")
	{
		if (deleteHostFromHostsFile(argv[2]) == false)
		{
			printf("Failed to delete host from hosts file!\n\n");
			return -1;
		}
	}

	// Als het toevoegen goed gaat, moeten we de dns server restarten.
	system("service dnsmasq restart");
	printf("Action succeeded!\n\n");
	return 0;
}
