# This scripts redirects all IP addresses in the range of our network.
# Author:		Trisna Quebe ic106-2
import subprocess

command = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', 'IP',
	'-p', 'tcp', '--dport', '80', '-j', 'DNAT', '--to-destination', '192.168.22.1:80' ]

command2 = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-s', 'IP',
	'-p', 'tcp', '--dport', '443', '-j', 'DNAT', '--to-destination', '192.168.22.1:443' ]

print("[*] Redirecting IP addresses to Captive Portal.")
for i in range(2, 255):
	command[7] = '192.168.22.' + str(i)
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	command2[7] = '192.168.22.' + str(i)
	subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


