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
echo "                                       \"\"I\"\""
echo "			 _________________________________________"
echo "			|                                         |"
echo "			| Author:          Trisna Quebe ic106-2   |"
echo "			| Creation date:   12-10-2019             |"
echo "			| Name:            AccessPoint_install.sh |"
echo "			|                                         |"
echo "			|_________________________________________|"


echo
echo
echo "[*] Flushing all previous iptable settings."
iptables --flush
iptables -t nat --flush

echo "[*] Allow tcp connections to ports 22, 80, 443."
iptables -A INPUT -p tcp --dport 22 --destination 192.168.22.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 --destination 192.168.22.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 --destination 192.168.22.1 -j ACCEPT

echo "[*] Debug IP priveledges."
iptables -I INPUT -p tcp --source 192.168.137.1 -j ACCEPT

echo "[*] Drop all connections to anyone."
iptables -A INPUT -p tcp --jump DROP

echo
echo "Wifi access point succesfully installed and ready for use."
