# meshpinger

`meshpinger` is a Python-based diagnostic tool designed to validate Layer 3 connectivity across high-performance back-end cluster networks. It performs a **full-mesh ping** between the local node's interfaces and all remote node interfaces specified in a YAML inventory.

The goal is to ensure every possible network path in the backend fabric is functional, identifying specific NIC, cable, or switch-port failures that standard "node-to-node" pings might miss.

## Intent

  * **YAML-Driven:** Precisely defines nodes and their specific `backend` interfaces.
  * **Interface Binding:** Uses `ping -I` to force traffic out of specific source IPs, ensuring every local NIC is tested.
  * **Full Mesh:** Every permutation of source/destination is tested (excluding intra-node pings).
  * **Scalability:** Designed for high-density environments.
      * *Example:* 128 nodes with 8 NICs each = 8,128 individual path tests per node.
      * Total mesh coverage: **Source (8 NICs) x Remote Nodes (127) x Remote NICs (8)**.

## Features

  * **Self-Identification:** The script automatically identifies its own source IPs by matching the system's short hostname against the `name` field in the YAML.
  * **Structured Output:** Generates deep-mergeable JSON logs for easy aggregation and analysis.
  * **Multi-threaded:** Concurrent execution to speed up large-scale mesh tests (defaults to 5 threads).
  * **Air-Gap Friendly:** Minimal dependencies (requires `PyYAML`).

-----

## Inventory Format (`nodes.yaml`)

The inventory separates `frontend` and `backend` interfaces. The script currently targets **backend** IPs for mesh testing.

```yaml
---
nodes:
  - name: YOURNODE1
    interfaces:
      frontend:
        - 192.168.1.1
      backend:
        - 10.1.1.1
        - 10.1.1.2
        - 10.1.1.3
        - 10.1.1.4
  - name: YOURNODE2
    interfaces:
      frontend:
        - 192.168.2.1
      backend:
        - 10.1.2.1
        - 10.1.2.2
        - 10.1.2.3
        - 10.1.2.4
```

-----

## Usage

### Prerequisites

Install the YAML parser (required for the script to read the inventory):

```bash
pip install pyyaml
```

### Execution

```bash
python3 meshpinger.py
```

### Advanced Options

| Flag | Description |
| :--- | :--- |
| `--yaml <file>` | Path to your inventory. Defaults to `nodes.yaml`. |
| `--fail-only` | Suppress `[PASS]` entries in the JSON log; only record failures. |
| `--threads <int>` | Set number of worker threads (Default: 5). *Note: Pings are CPU switched; keep this low.* |

**Example:**

```bash
python3 meshpinger.py --yaml site_inventory.yaml --fail-only --threads 8
```

-----

## Results & Logging

The script generates a JSON file named: `hostname-pingtest-YYYYMMDD-HHMM.json`.

### JSON Structure

The output uses a hierarchical key structure (`Node > Test Type > Timestamp`) designed for easy aggregation of hundreds of files into a single master report.

```json
{
  "YOURNODE1": {
    "tests": {
      "backendpingtest": {
        "20260403-1430": {
          "successes": [
            { "src": "10.1.1.1", "dst": "10.1.2.1" }
          ],
          "failures": [
            { 
              "src": "10.1.1.2", "dst": "10.1.2.2", 
              "error": "Timeout / 100% packet loss" 
            }
          ]
        }
      }
    }
  }
}
```

-----

## Ansible Integration

This tool is designed to be deployed via Ansible. An example role is provided in the `/ansible` directory which handles:

1.  Pushing the `meshpinger.py` script and `nodes.yaml`.
2.  Installing dependencies (or `.whl` files for air-gapped nodes).
3.  Executing the mesh test across the entire fleet simultaneously.
4.  Fetching all JSON results back to the controller for central reporting.

[View Ansible Example](https://www.google.com/search?q=./ansible)