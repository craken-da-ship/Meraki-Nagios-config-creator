# Meraki-Nagios-config-creator
Base script to create an automatic network creation in Nagios for all networks in a Meraki Organiztion that have been active within last week.

This script pulls the data from meraki via API for each network. It can check to only grab certain networks, EG we tag ours that we want in meraki and then filter by tag on the pull. It then creates a nagios config file with all the relevant informtation. You can set up a task to run it everyday or every week to update the config file. It will copy the current to a .old incase a rollback needs to occur. 
