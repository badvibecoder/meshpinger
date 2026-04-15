# Ansible Role: meshpinger

An Ansible role to deploy, execute, and retrieve results from the `meshpinger` tool. This role automates the full-mesh network validation of backend cluster interfaces.

## Role Description

This role performs the following operations:
1.  **Environment Prep:** Ensures `python3-pip` and `PyYAML` are installed on target nodes.
2.  **Deployment:** Pushes the `meshpinger.py` script and the `nodes.yaml` inventory to a temporary working directory (`/var/tmp/meshpinger`).
3.  **Cleanup:** Removes any stale `.log` or `.json` results from previous runs to ensure data integrity.
4.  **Execution:** Runs the mesh test. The script identifies the local node's backend IPs and pings all other nodes' backend IPs defined in the YAML.
5.  **Data Collection:** Fetches the resulting structured JSON files from all remote nodes back to the Ansible controller for central analysis.

## Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `meshpinger_dir` | `/var/tmp/meshpinger` | The working directory on the remote nodes. |
| `meshpinger_threads` | `5` | Number of concurrent ping threads per node. |
| `meshpinger_fail_only` | `false` | If `true`, only failures are recorded in the JSON output. |

## File Structure

The role expects the following files to be present in the `files/` directory of the role:
* `meshpinger.py`: The Python script.
* `nodes.yaml`: The master network inventory.

```text
roles/meshpinger/
├── files/
│   ├── meshpinger.py
│   ├── nodes.yaml
│   └── logs/           # Results from remote nodes will be fetched here
├── tasks/
│   └── main.yml
└── README.md
```

## Example Playbook

```yaml
- hosts: backend_nodes
  become: yes
  roles:
    - role: meshpinger
      vars:
        meshpinger_threads: 10
        meshpinger_fail_only: true
```

## Result Aggregation

After the playbook completes, all JSON files are stored on the Ansible controller at:
`{{ role_path }}/files/logs/`

The files follow the naming convention: `{{ inventory_hostname }}-pingtest-YYYYMMDD-HHMM.json`.

### Why JSON?
By fetching JSON files instead of flat text, you can easily run a post-processing script on the controller to merge all results into a single report. Because each JSON file uses the hostname as the top-level key, these files are "deep-merge" ready.

## Air-Gapped Installation (Optional)

If your nodes do not have internet access, you must manually place the `PyYAML` wheel (`.whl`) file in the `files/` directory and update the `pip` task in `tasks/main.yml` to install from the local file:

```yaml
- name: Install PyYAML from local wheel
  ansible.builtin.pip:
    name: "/var/tmp/meshpinger/PyYAML-6.0.1-cp39-cp39-linux_x86_64.whl"
    state: present
```

## Author Information

Created for cluster backend network validation.
