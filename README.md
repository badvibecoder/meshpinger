# meshpinger

Need to update.

to do:

- fix pciedegraded to include checks for multiple brands (pensando/mellanox/broadcom)
- add pensando specific nic id to gid to eth id to ionic id to dscp setup checker
    - validate there isnt already a nicctl command for this, you might have wasted time

This started as a backend all to all ping utility to scale reachablability testing across the backend nics of large clusters. 

It has since morphed into an ansible setup to run modules as roles and then gather json logs, aggregate those logs and present a report on the status of the cluster.

```text
├── ansible
│   ├── aggregator # Role grabs all json logs from modules and packages them, then generates an html report
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   ├── aggregator.py # Aggregate json logs from modules via roles/files/logs folder
│   │   │   └── generate_report.py # creates an interactive html file for reporting 
│   │   ├── handlers
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── README.md
│   │   ├── tasks
│   │   │   └── main.yml # Role task controls workflow
│   │   ├── templates
│   │   ├── tests
│   │   │   ├── inventory
│   │   │   └── test.yml
│   │   └── vars
│   │       └── main.yml
│   ├── ansible.cfg
│   ├── eterrors # Scans nodes ethtool error output
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   ├── eterrors.py # Looks for interface errors that may cause performance issues
│   │   │   └── logs
│   │   ├── handlers
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── README.md
│   │   ├── tasks
│   │   │   └── main.yml # Role task controls workflow
│   │   ├── templates
│   │   ├── tests
│   │   │   ├── inventory
│   │   │   └── test.yml
│   │   └── vars
│   │       └── main.yml
│   ├── hosts.ini
│   ├── meshpinger # Checks reachability accross a clusters backend fabric
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   ├── logs
│   │   │   ├── meshpinger.py # This utilizes the yaml file to perform source/dest pings with all possible BE combinations
│   │   │   └── nodes.yaml # yaml configuration file that should minimally contain the node name and BE interface IPs
│   │   ├── handlers
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── README.md
│   │   ├── tasks
│   │   │   └── main.yml # Role task controls workflow
│   │   ├── templates
│   │   ├── tests
│   │   │   ├── inventory
│   │   │   └── test.yml
│   │   └── vars
│   │       └── main.yml
│   ├── pciedegraded # Checks if a nodes backend interface is not running at full speed on the pcie bus
│   │   ├── defaults
│   │   │   └── main.yml
│   │   ├── files
│   │   │   └── pciedegraded.py # Currently looks at backend nics for sub standard pcie lanes, ie x4 instead of x16
│   │   ├── handlers
│   │   │   └── main.yml
│   │   ├── meta
│   │   │   └── main.yml
│   │   ├── README.md
│   │   ├── tasks
│   │   │   └── main.yml # Role task controls workflow
│   │   ├── templates
│   │   ├── tests
│   │   │   ├── inventory
│   │   │   └── test.yml
│   │   └── vars
│   │       └── main.yml
│   └── site.yml

```
