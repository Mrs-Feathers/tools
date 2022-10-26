"""
checkipstatus - see README
"""

import json
from requests import get
from securedata import securedata, mail

ip_current = securedata.getItem("currentIP")

securedata.log("Checking IP")

ip = get('https://api.ipify.org?format=json', timeout=30).text
ip_discovered = json.loads(ip)["ip"]

securedata.log(f"Found {ip_discovered}, currently {ip_current}")

if ip_current == ip_discovered:
    print("No change.")
else:
    msg = f"""Hi Tyler,<br><br>
    Your IP address was changed from {ip_current} to {ip_discovered}.<br><br>
    Please update /etc/wireguard/wg0.conf accordingly.
    """
    
    mail.send("IP Address Updated", msg)
    
    # update securedata
    securedata.setItem("currentIP", ip_discovered)