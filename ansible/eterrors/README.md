# Ansible Role: eterrors

An Ansible role to deploy, execute, and retrieve results from the `eterrors.py` tool. This role automates the discovery of network interfaces and the collection of hardware-level error statistics via `ethtool`.

## Role Description

This role performs the following operations:
1.  **Directory Setup:** Creates a dedicated working directory on the remote nodes (`/var/tmp/ethtool_errors`).
2.  **Deployment:** Pushes the `eterrors.py` script to the target nodes. 
3.  **Cleanup:** Automatically finds and removes stale `*eterrors-*.json` results from previous runs to ensure fresh data collection.
4.  **Execution:** Runs the error gatherer. The script dynamically detects all active network interfaces (excluding loopback) and executes `ethtool -S` to parse for specific error counters.
5.  **Filtering:** Only records interfaces and specific metrics that have a value greater than `0`. If an interface is "clean," it is excluded from the JSON to reduce noise.
6.  **Data Collection:** Fetches the resulting structured JSON files from all remote nodes back to the Ansible controller for central analysis.

## Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `eterrors_dir` | `/var/tmp/ethtool_errors` | The working directory on the remote nodes. |
| `eterrors_outdir` | `/var/tmp/ethtool_errors` | The directory where the Python script saves JSON files. |

## File Structure

The role expects the following files to be present in the `files/` directory of the role:
* `eterrors.py`: The Python script.

```text
roles/eterrors/
├── files/
│   ├── eterrors.py
│   └── logs/           # Results from remote nodes will be fetched here
├── tasks/
│   └── main.yml
└── README.md
```

## Example Playbook

```yaml
- hosts: gpu_nodes
  become: yes
  roles:
    - role: eterrors
```

## Result Aggregation

After the playbook completes, all JSON files are stored on the Ansible controller at:
`{{ role_path }}/files/logs/`

The files follow the naming convention: `{{ inventory_hostname }}-eterrors-YYYYMMDD-HHMM.json`.

### JSON Schema Advantage
This role produces JSON output that mirrors the `meshpinger` format. Each file uses the `hostname` as the top-level key, making the results "deep-merge" ready. This allows you to aggregate logs from a 100-node cluster into a single master dictionary for rapid health assessment.

## Requirements

* **Python 3:** The script uses the Python Standard Library and does not require external dependencies like PyYAML.
* **ethtool:** The `ethtool` utility must be installed on the target nodes.
* **Permissions:** The role requires `become: yes` (root/sudo) to execute `ethtool` and access interface statistics.

## Author Information

Created for automated cluster hardware health monitoring and network interface troubleshooting.