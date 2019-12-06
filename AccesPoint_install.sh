# Author:		Trisna Quebe ic106-2
# Creation date:	12-10-2019
# Name:			AccessPoint_install.sh

reset
echo
echo
echo "Installing wifi access point for FYS project..."
echo
echo "                               .,amm###############mma,. "
echo "                        .a###################################m,"
echo "                   .m#############################################m,"
echo "               .m#####################################################ma"
echo "            a#########################RRRMMMMMRRR#########################m"
echo "         a##################RMET*-                   -""YMR##################m"
echo "      .################RB7-                                 .\"7R################,"
echo "     z##############RE\"                   .....                   !7K##############m"
echo "   (############MT            .am#####################mg,            \"M############"
echo "    K########RC           a#################################m           ?K########M"
echo "     4####M'         a#########################################m         'K####M\""
echo "        I\"         a###############################################m         I\""
echo "                ##################RMBTT\"*\"\"\"!\"T7YMR#################M"
echo "              ###############MT-                     \"7K##############M"
echo "               4##########RT-                              ?M##########M"
echo "                 4######E            .am#######mg,            ?######M\""
echo "                   7RM\"         .m###################ma         ?RRE"
echo "                            .###########################g"
echo "                           z###############################m"
echo "                           ###############RRR###############"
echo "                            7#######RE\".        [YR#######M-"
echo "                              7###E-                7###E"
echo "                                      .a#######m,"
echo "                                    ##############m"
echo "                                  .#################p"
echo "                                  ###################"
echo "                                 [###################E"
echo "                                 j###################E"
echo "                                  K#################M"
echo "                                   ?###############E"
echo "                                    ?R#########MT"
echo "                                         \"\"I\"\""
echo "			 _________________________________________"
echo "			|                                         |"
echo "			| Author:          Trisna Quebe ic106-2   |"
echo "			| Creation date:   12-10-2019             |"
echo "			| Name:            AccessPoint_install.sh |"
echo "			|                                         |"
echo "			|_________________________________________|"


echo
echo

echo "[*] Refreshing ssl private certificate files."
#openssl req -new -x509 -days 365 -keyout /etc/apache2/ssl/key/FYS.key -out /etc/apache2/ssl/crt/FYS.crt -nodes -subj  '/O=Wifi in plane/OU=Official Corendon Login page/CN=corendon.com'

echo "[*] Flushing all previous iptables settings."
iptables --flush
iptables -t nat --flush

echo "[*] Allow tcp connections to ports 22, 80, 443."
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --source 127.0.0.1 --destination 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --destination 10.42.0.170 -j ACCEPT

echo "[*] Redirecting devices to login page."
python redirect_script.py

# Delete if not debugging on windows......
echo "[*] Debug IP priveledges for windows."
iptables -I INPUT -p tcp --source 192.168.137.1 -j ACCEPT
# .............................

echo "[*] Drop all connections to anyone."
iptables -A INPUT -p tcp --jump DROP

echo "[*] Executing python script that will create the databases."
python sql_create.py

echo "[*] Executing python script that will insert passenger data."
python sql_insert.py

echo
echo "Wifi access point succesfully installed and ready for use."

