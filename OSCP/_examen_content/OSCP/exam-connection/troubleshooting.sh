#!/bin/bash
## OffSec's troubleshooting script
## Last updated: 2025-03-25


## Bash colours
YELLOW="\033[01;33m"
BLUE="\033[01;34m"
BOLD="\033[01;01m"
RED="\033[01;31m"
GREEN="\033[01;32m"
RESET="\033[00m"


## Banner/Notice
echo -e "\n${BLUE}[+]${RESET} Should you experience any connectivity issues, please ${BOLD}send the log file './troubleshoot.log'${RESET} along with the ${BOLD}output from the OpenVPN window${RESET}, with ${BOLD}your OSID${RESET} to '${BOLD}help@offensive-security.com${RESET}'."
sleep 3s


## Checking user
echo -e "\n\n${YELLOW}[i]${RESET} Checking User"
echo -e "[i] Checking User" > troubleshoot.log
if [[ "${EUID}" -ne 0 ]]; then
  echo -e "${RED}[-]${RESET} This script must be run as ${RED}root${RESET}"
  echo -e "[-] This script must be run as root" >> troubleshoot.log
  sleep 2s
  exit 1
fi
id | tee -a troubleshoot.log
sleep 3s


## Date
echo -e "\n\n${YELLOW}[i]${RESET} Date"
echo -e "\n\n[i] Date" >> troubleshoot.log
date | tee -a troubleshoot.log
sleep 3s


## VM check
echo -e "\n\n${YELLOW}[i]${RESET} Virtual Machine Check"
echo -e "\n\n[i] Virtual Machine Check" >> troubleshoot.log
if (dmidecode | grep -iq vmware); then
  echo -e "VMware Detected" | tee -a troubleshoot.log
elif (dmidecode | grep -iq virtualbox); then
  echo -e "${YELLOW}[i] VirtualBox Detected${RESET}!   It is highly recommended that all students use the VMware student VM." | tee -a troubleshoot.log
  echo -e "VirtualBox Detected!   It is highly recommended that all students use the VMware student VM." >> troubleshoot.log
  echo -e "    See: https://help.offensive-security.com/hc/en-us/articles/360049796792-Kali-Linux-Virtual-Machine"
  sleep 2s
else
  echo -e "${RED}[-] VM not detected${RESET}!   It is highly recommended that all students use the VMware student VM."
  echo -e "VM not detected!   It is highly recommended that all students use the VMware student VM." >> troubleshoot.log
  echo -e "    See: https://help.offensive-security.com/hc/en-us/articles/360049796792-Kali-Linux-Virtual-Machine"
  sleep 2s
fi
sleep 3s


## Network interfaces
TUN0_COUNT=$(ifconfig | grep -c "tun0")

if [[ $TUN0_COUNT -eq 0 ]]; then
    echo -e "\n${RED}[!] VPN is NOT connected! Please make sure to connect to the VPN.${RESET}"
    echo -e "\n[!] VPN is NOT connected! Please make sure to connect to the VPN." >> troubleshoot.log
elif [[ $TUN0_COUNT -gt 1 ]]; then
    echo -e "\n\n${RED}[!] Multiple VPN connections detected ($TUN0_COUNT tun0 interfaces). Please ensure you only have one active VPN connection.${RESET}"
    echo -e "\n\n[!] Multiple VPN connections detected ($TUN0_COUNT tun0 interfaces). Please ensure you only have one active VPN connection." >> troubleshoot.log
else
    echo -e "\n\n${GREEN}[✓] VPN is connected (tun0 detected).${RESET}"
    echo -e "\n\n[✓] VPN is connected (tun0 detected)." >> troubleshoot.log
fi

echo -e "\n${YELLOW}[i]${RESET} Network Interfaces"
echo -e "\n\n[i] Network Interfaces" >> troubleshoot.log
ifconfig -a | tee -a troubleshoot.log
sleep 3s


## Network routes
echo -e "\n\n${YELLOW}[i]${RESET} Network Routes"
echo -e "\n\n[i] Network Routes" >> troubleshoot.log
route -n | tee -a troubleshoot.log
sleep 3s


## DNS information
RESOLV_CONF="/etc/resolv.conf"
BACKUP_FILE="/etc/resolv.conf.backup-$(date +%F_%T)"

	# Backup current DNS settings
	echo -e "\n${YELLOW}[i]${RESET} Creating a backup of your current DNS settings..."
	echo -e "\n[i] Creating a backup of your current DNS settings..." >> troubleshoot.log
	sleep 2s
	sudo cp "$RESOLV_CONF" "$BACKUP_FILE"

	if [ $? -eq 0 ]; then
	    echo -e "\n${GREEN}[✓]${RESET} Backup saved as $BACKUP_FILE"
	    echo -e "\n[✓] Backup saved as $BACKUP_FILE" >> troubleshoot.log
	else
	    echo -e "\n${RED}[!] Failed to create a backup. Exiting...${RESET}"
	    echo -e "\n[!] Failed to create a backup. Exiting...${RESET}" >> troubleshoot.log
	    exit 1
	fi
	sleep 2s

	# Check if the file has immutable attribute
	if lsattr "$RESOLV_CONF" | grep -q 'i'; then
	    echo -e "\n${YELLOW}[i]${RESET} Removing immutable attribute from $RESOLV_CONF..."
	    echo -e "\n[i] Removing immutable attribute from $RESOLV_CONF..." >> troubleshoot.log
	    sleep 2s
	    sudo chattr -i "$RESOLV_CONF"
	fi

	# Read existing DNS entries
	DNS_ENTRIES=($(grep -oP 'nameserver \K.*' "$RESOLV_CONF"))

	# Count the number of DNS entries
	DNS_COUNT=${#DNS_ENTRIES[@]}

	if [ "$DNS_COUNT" -eq 0 ]; then
	    echo -e "\n${YELLOW}[i]${RESET} No existing DNS found. Adding Google DNS as primary and secondary..."
	    echo -e "\n[i] No existing DNS found. Adding Google DNS as primary and secondary..." >> troubleshoot.log
	    sleep 2s
	    echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" | sudo tee "$RESOLV_CONF" > /dev/null
	    echo -e "\n${GREEN}[✓]${RESET} Google DNS added successfully!"
	    echo -e "\n[✓] Google DNS added successfully!" >> troubleshoot.log
	elif [ "$DNS_COUNT" -eq 1 ]; then
	    if [[ "${DNS_ENTRIES[0]}" != "8.8.8.8" ]]; then
		echo -e "\n${YELLOW}[i]${RESET} One existing DNS found. Appending 8.8.8.8 as secondary..."
		echo -e "\n[i] One existing DNS found. Appending 8.8.8.8 as secondary..." >> troubleshoot.log
		sleep 2s
		echo -e "nameserver 8.8.8.8" | sudo tee -a "$RESOLV_CONF" > /dev/null
	    else
		echo -e "\n${YELLOW}[i]${RESET} Primary Google DNS (8.8.8.8) detected. Appending 8.8.4.4 as secondary..."
		echo -e "\n[i] Primary Google DNS (8.8.8.8) detected. Appending 8.8.4.4 as secondary..." >> troubleshoot.log
		sleep 2s
		echo -e "nameserver 8.8.4.4" | sudo tee -a "$RESOLV_CONF" > /dev/null
	    fi
	    echo -e "\n${GREEN}[✓]${RESET} Google DNS added successfully!"
	    echo -e "\n[✓] Google DNS added successfully!" >> troubleshoot.log
	else
	    echo -e "\n${GREEN}[✓]${RESET} Existing DNS settings are already configured. No changes made."
	    echo -e "\n[✓] Existing DNS settings are already configured. No changes made." >> troubleshoot.log
	fi
	sleep 2s

	# Re-add immutable attribute
	sudo chattr +i "$RESOLV_CONF"

	echo -e "\n${YELLOW}[i]${RESET} If you wish to remove Google DNS later, first run 'sudo chattr -i /etc/resolv.conf' before editing."
	echo -e "\n[i] If you wish to remove Google DNS later, first run 'sudo chattr -i /etc/resolv.conf' before editing." >> troubleshoot.log
	sleep 2s
	echo -e "\n${YELLOW}[i]${RESET} DNS Information:"
	echo -e "\n[i] DNS Information:" >> troubleshoot.log
	sleep 2s
	cat /etc/resolv.conf | tee -a troubleshoot.log
	sleep 3s


## Ping test
echo -e "\n\n${YELLOW}[i]${RESET} Ping Test (External: www.Google.com)"
echo -e "\n\n[i] Ping Test (External: www.Google.com)" >> troubleshoot.log
ping -c 30 8.8.8.8 | tee -a troubleshoot.log
if [[ $? != '0' ]]; then
  echo -e "${RED}[-]${RESET} Ping test failed (8.8.8.8).\n${RED}[-]${RESET} Please make sure you have Internet access."
  sleep 2s
fi
echo -e "" | tee -a troubleshoot.log
ping -c 30 www.google.com | tee -a troubleshoot.log
if [[ $? != '0' ]]; then
  echo -e "${RED}[-]${RESET} Ping test failed (www.google.com)...\n${RED}[-]${RESET} Please make sure you have Internet access."
  sleep 2s
fi
sleep 3s


## External IP
echo -e "\n\n${YELLOW}[i]${RESET} External IP"
echo -e "\n\n[i] External IP" >> troubleshoot.log

EXTERNAL_IP=$(curl -sS -m 20 http://ipinfo.io/ip)
if [[ -z "$EXTERNAL_IP" ]]; then
    echo -e "\n${RED}[!] Failed to retrieve external IP. Check your connection.${RESET}"
    echo -e "\n[!] Failed to retrieve external IP. Check your connection." >> troubleshoot.log
else
    echo -e "$EXTERNAL_IP" | tee -a troubleshoot.log
    sleep 3s

    # Get Location Info
    echo -e "\n${YELLOW}[i]${RESET} External IP Country"
    echo -e "\n[i] External IP Country" >> troubleshoot.log

    LOCATION_INFO=$(curl -sS -m 20 http://ipinfo.io/$EXTERNAL_IP/json | grep -E "country" | sed -E 's/.*: "(.*)".*/\1/')
    
    if [[ -z "$LOCATION_INFO" ]]; then
        echo -e "\n${RED}[!] Failed to retrieve location info.${RESET}"
        echo -e "\n[!] Failed to retrieve location info." >> troubleshoot.log
    else
        echo -e "$LOCATION_INFO" | tee -a troubleshoot.log
    fi
fi
sleep 3s


## UDP port test
echo -e "\n\n${YELLOW}[i]${RESET} UDP Port Test"
echo -e "\n\n[i] UDP Port Test" >> troubleshoot.log
files=$(find . -name '*.ovpn' -maxdepth 1 2>/dev/null | wc -l)
if [[ "${files}" == "1" ]]; then
  IP=$(grep -e '^remote ' *.ovpn | awk '{print $2}')
  nc -vzu ${IP} 1194 2>&1 | tee -a troubleshoot.log
elif [[ "${files}" == "0" ]]; then
  echo -e "${RED}[-]${RESET} Missing connection pack"
  echo -e "\n\n[-] Missing connection pack" >> troubleshoot.log
  ls -lah | tee -a troubleshoot.log
  pwd | tee -a troubleshoot.log
  sleep 2s
else
  echo -e "${RED}[-]${RESET} Multiple connection packs, please remove the old one(s)"
  echo -e "\n\n[-] Multiple connection packs, please remove the old one(s)" >> troubleshoot.log
  pwd | tee -a troubleshoot.log
  find . -name '*.ovpn' -maxdepth 1 -ls 2>/dev/null | tee -a troubleshoot.log
  echo -e "" | tee -a troubleshoot.log
  ls -lah | tee -a troubleshoot.log
  sleep 2s
fi
sleep 3s


## Checking kernel version
echo -e "\n\n${YELLOW}[i]${RESET} Checking Kernel Version"
echo -e "\n\n[i] Checking Kernel Version" >> troubleshoot.log
uname -a | tee -a troubleshoot.log
if [[ "$(uname -a)" == *"pae"* ]]; then
  echo -e "${RED}[-]${RESET} PAE kernel detected.    Please use the VMware student VM."
  echo -e '    See: https://help.offensive-security.com/hc/en-us/articles/360049796792-Kali-Linux-Virtual-Machine'
  sleep 2s
fi
sleep 3s


## Checking OS
echo -e "\n\n${YELLOW}[i]${RESET} Checking OS"
echo -e "\n\n[i] Checking OS" >> troubleshoot.log
cat /etc/issue | tee -a troubleshoot.log
cat /etc/*-release | tee -a troubleshoot.log
sleep 3s


## Notice
echo -e "\n\n${BLUE}[+]${RESET} Test complete."
echo -e "${BLUE}[+]${RESET} Should you experience any connectivity issues, please ${BOLD}send the log file './troubleshoot.log'${RESET} along with the ${BOLD}output from the OpenVPN window${RESET}, with ${BOLD}your OSID${RESET} to '${BOLD}help@offensive-security.com${RESET}'."
sleep 3s
