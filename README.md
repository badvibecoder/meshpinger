# Cluster Diagnostic Tools (meshpinger)

This repository contains a suite of Python-based diagnostic tools designed to validate and troubleshoot high-performance backend cluster networks. 

1. **meshpinger**: Validates Layer 3 connectivity via full-mesh ping testing.
2. **eterrors**: Validates Layer 1/2 health by gathering hardware-level error statistics via `ethtool`.

---

## 1. meshpinger

`meshpinger` performs a **full-mesh ping** between a local node's interfaces and all remote node interfaces specified in a YAML inventory. It identifies specific NIC, cable, or switch-port failures that standard "node-to-node" pings might miss by forcing traffic out of specific source IPs using `ping -I`.

### Features
* **Interface Binding:** Ensures every local NIC in the backend fabric is tested.
* **Scalability:** Designed for high-density environments (e.g., 128 nodes x 8 NICs).
* **Self-Identification:** Automatically matches system hostname against the `nodes.yaml` inventory.
* **Structured Output:** Generates deep-mergeable JSON logs.

---

## 2. eterrors

`eterrors` is a lightweight hardware health monitor. It dynamically discovers all active network interfaces and parses `ethtool -S` output for hardware-level errors, discards "zero-value" noise, and reports only active issues.

### Intent
While `meshpinger` tells you **if** a path is down, `eterrors` helps tell you **why** (e.g., CRC errors, drops, or pause frames indicating a bad cable or transceiver).

### Features
* **Zero-Configuration:** Automatically detects all `enp*` and other physical interfaces; no YAML required.
* **Noise Filtering:** Only records metrics with values > 0 (errors, drops, overruns, etc.).
* **Standardized Schema:** Uses the same JSON hierarchy as `meshpinger` for seamless log aggregation.

---

## Inventory Format (`nodes.yaml`)

Used primarily by `meshpinger` to define the network topology.

```yaml
---
nodes:
  - name: YOURNODE1
    interfaces:
      frontend: [192.168.1.1]
      backend: [10.1.1.1, 10.1.1.2]
  - name: YOURNODE2
    interfaces:
      frontend: [192.168.2.1]
      backend: [10.1.2.1, 10.1.2.2]
```

---

## Usage & Execution

### Prerequisites
* **meshpinger:** Requires `PyYAML` (`pip install pyyaml`).
* **eterrors:** Requires `ethtool` installed on the system (Standard Library only).

### Running Manually
```bash
# Run Layer 3 Mesh Test
python3 meshpinger.py --yaml nodes.yaml --fail-only

# Run Layer 1/2 Error Check
python3 eterrors.py
```

### Advanced Options (meshpinger)
| Flag | Description |
| :--- | :--- |
| `--yaml <file>` | Path to inventory. Defaults to `nodes.yaml`. |
| `--fail-only` | Only record failures in the JSON log. |
| `--threads <int>`| Number of worker threads (Default: 5). |

---

## Results & Logging

Both tools generate timestamped JSON files:
* `hostname-pingtest-YYYYMMDD-HHMM.json`
* `hostname-eterrors-YYYYMMDD-HHMM.json`

### Unified JSON Structure
The output uses a hierarchical key structure (`Node > Test Category > Timestamp`) designed so that hundreds of files can be merged into a single master report for a total cluster health snapshot.

---

## Ansible Integration

These tools are designed for fleet-wide deployment via Ansible. The `/ansible` directory contains roles for both tools that automate:

1. **Deployment:** Pushing scripts and inventories to `/var/tmp/`.
2. **Execution:** Running tests across the entire fleet simultaneously.
3. **Cleanup:** Removing stale logs from previous runs.
4. **Aggregation:** Fetching all JSON results back to the controller's `files/logs/` directory for central analysis.

---

## Author Information
Created for automated cluster backend network validation and hardware health monitoring.