# meshpinger

This is a python script designed to validate layer 3 connectivity across the back-end of clusters. This tool performs a full mesh ping between the node and all other nodes/ips specified in a csv. The goal is to ping test every direction to ensure all backend nics can reach all other nodes backend nics.

## Intent

- CSV controls both source interface/ips and targets whether its 2 nics or 20
- Remote targets are reachable (PASS) or are not reachable (FAIL)
- Every permutation of source/destination is tested except intra node
- 128 nodes (8 nics) = 8128 individial ping tests per node
        - Source node 8 interfaces x 127 nodes x 8 interfaces

## Features

- The script will self ID its own source IPs via hostname in the CSV
        - Hostnames and IPs must be accurate
- Uses `ping -I` to bind source ips
- Adjustable thread count (defaults to 5, I do not suggest changing)
- Logs are `hostname-pingtest-YYYY-MM-DD-H-M.log`

### CSV Format

Hostname,Backend IP

```txt
YOURNODE1,10.0.1.1
YOURNODE1,10.0.1.2
YOURNODE1,10.0.1.3
YOURNODE1,10.0.1.4
YOURNODE1,10.0.1.5
YOURNODE1,10.0.1.6
YOURNODE1,10.0.1.7
YOURNODE1,10.0.1.8
YOURNODE2,10.0.1.1
YOURNODE2,10.0.2.2
YOURNODE2,10.0.2.3
YOURNODE2,10.0.2.4
YOURNODE2,10.0.2.5
YOURNODE2,10.0.2.6
YOURNODE2,10.0.2.7
YOURNODE2,10.0.2.8
YOURNODE3,10.0.3.1
YOURNODE3,10.0.3.2
YOURNODE3,10.0.3.3
YOURNODE3,10.0.3.4
YOURNODE3,10.0.3.5
YOURNODE3,10.0.3.6
YOURNODE3,10.0.3.7
YOURNODE3,10.0.3.8
```

### Usage

```bash
python meshpinger.py
#or
python3 meshpinger.py
#or
sudo python3 meshpinger.py
```

### Advanced Options

- `--csv <file>` Path to your csv, default/assumed csv name `nodes.csv`
- `--fail-only` Supress `[PASS]` entries, only log failures
- `--threads <int>` Set a number of thread workers
        - Keep in mind, pings are cpu switched and cpu processed

Usage: `python3 meshpinger.py --csv mylistofnodes.csv --fail-only --threads 3`

### Log Output

```
14:30:05 - YOURNODE1 | [PASS] 10.0.1.1 -> 10.0.2.1
14:30:06 - YOURNODE1 | [FAIL] 10.0.1.1 -> 10.0.3.4
```

### Ansible

I have an example of using this in an ansible role to deploy and scale out to many servers.

<a href="ansible\">Here</a>
