import requests
import json
import time
from datetime import datetime, timedelta, date
from shutil import copyfile

apiKey = 'Insert API Key here'
orgId = #orgID goes here
contact = "Nagios Contacts go here"
vlanId = #vlanID of primary vlan goes here
cfgPath = "/usr/local/nagios/etc/objects/meraki.cfg"

baseUrl = "https://api.meraki.com/api/v1/"
payload={}
headers = {
  'X-Cisco-Meraki-API-Key': apiKey
}

copyfile(cfgPath,"{}.orig".format(cfgPath))
cfg = open(cfgPath, "w")

cfg.write('define hostgroup {{\
        \n\t hostgroup_name     meraki\
        \n\t alias              Meraki Appliances\
        \n}}\
        \n\
        \ndefine service {{\
        \n\t use                     generic-service\
        \n\t hostgroup_name          meraki\
        \n\t service_description     ping\
        \n\t check_command           check_ping!400.0,60%!800.0,80%\
        \n\t check_interval          1\
        \n\t contacts                {0}\
        \n\t check_period            workhours\
        \n\t notifications_enabled   1\
        \n\t notification_period     workhours\
        \n\t notification_options    c\
        \n\t max_check_attempts      5\
	\n\t notification_interval   0\
        \n}}'.format(contact))


def get_name(netId):
    response = requests.request("GET", "{}organizations/{}/networks/{}".format(baseUrl,orgId,netId), headers=headers, data=payload)
    output = response.json()
    return output["name"]
##  This can be used to filter certain networks depending on your organizations layout and what you are trying to monitor. 
##    if output["tags"] == ['SITE'] and "SOLD" not in output["name"]:
##        return output["name"]
##    else:
##        return False

def get_vlan(netId):
    try:
        response = requests.request("GET", "{}networks/{}/appliance/vlans/{}".format(baseUrl,netId,vlanId), headers=headers, data=payload)
        output = response.json()
        return output["applianceIp"]
    except:
        return False


def check_status(lastDate):
    datelimit = datetime.today() - timedelta(days=7)
    try:
        lastup = datetime.strptime(lastDate, '%Y-%m-%dT%H:%M:%SZ')
        if lastup.date() > datelimit.date():
            return True
        else:
            return False
    except:
        return False

response = requests.request("GET", "{}organizations/{}/appliance/uplink/statuses".format(baseUrl,orgId), headers=headers, data=payload)
output = response.json()

for net in output:
    answer = check_status(net["lastReportedAt"]) #checks to see if network has been active in the last 7 days
    if answer == True:
        siteName = get_name(net["networkId"]) #gets siteName or skips site if outside wanted range
        if siteName:
            applianceIp = get_vlan(net["networkId"]) #gets IP
            if applianceIp:
                line1 = ('\n\t define host {\
                    \n\t use                   generic-host')
                line2 = '\n\t host_name             {}'.format(siteName)
                line3 = '\n\t alias                 {}'.format(siteName)
                line4 = '\n\t address               {}'.format(applianceIp)
                line5 = ('\n\t max_check_attempts    5\
                         \n\t hostgroups            meraki\
                         \n\t check_command         check-host-alive\
                         \n\t check_interval        10\
                         \n\t initial_state         o\
                         \n\t check_period          workhours\
                         \n\t contacts              {}\
                         \n\t notification_options  d,u,r\
                         \n\t notifications_enabled 1\
			 \n\t notification_interval 0\
                         \n}}'.format(contact))
                cfg.write('{0} {1} {2} {3} {4}'.format(line1, line2, line3, line4, line5))
    time.sleep(.25)

cfg.close()
