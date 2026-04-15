## NIC & RDMA Configuration Reporter

This Bash script provides a unified, high-level view of your network hardware by mapping physical PCI devices to their OS interface names, RDMA devices, and active Quality of Service (QoS) configurations.

## Features

* Hardware-to-OS Mapping: Bridges the gap between physical PCI addresses and Linux interface names (e.g., enp9s0np0).
* RDMA Discovery: Automatically identifies associated RDMA device names (e.g., ionic_0).
* Pause Frame Detection: Reports the current pause configuration (PFC, IEEE, etc.).
* Dynamic QoS Reporting:
* Extracts DSCP-to-Priority mappings.
   * Identifies Traffic Scheduling algorithms (Strict, DWRR) per priority.
* Zero-Noise Filtering: Automatically hides default "Priority 0" configurations to highlight custom tuning.

## Primary Goal

In complex distributed systems, a single physical card is often referred to by four or five different "names" depending on which tool you use. The goal of this script is to bridge these layers, tying the hardware's unique NIC UUID to the PCIe Bus, the Physical MAC, the Linux Ethernet Interface, and the Ionic RDMA device, while simultaneously validating that Quality of Service (QoS) markings are applied correctly across the entire path.

## Prerequisites

The script relies on standard Linux networking tools and specific hardware management utilities:

   1. nicctl: Required for hardware-level queries (commonly used with Pensando/AMD Ionic or Oracle interfaces).
   2. iproute2: For ip link mapping.
   3. rdma-core: For rdma link identification.
   4. Sudo Privileges: Required to execute nicctl and fetch hardware registers.

## Usage

   1. Save the script:
   
   nano nic-report.sh
   
   2. Make it executable:
   
   chmod +x nic-report.sh
   
   3. Run with sudo:
   
   sudo ./nic-report.sh
   
   
## Logic & Constraints

* Dynamic Discovery: No hard-coded MACs or interface names are used. The script crawls your live system state.
* Priority Filter: The script is designed to show active optimizations. Entries set to "Priority 0" (the standard default) are filtered out of the DSCP and Scheduling columns to reduce clutter.
* Formatting: The output uses fixed-width printf columns. If an interface has an exceptionally high number of DSCP mappings, the "DSCP PRIORITY" column may wrap or misalign.
 

## Example Output

```bash
PCI ADDR        | MAC ADDRESS       | PAUSE        | OS IFACE     | RDMA DEV     | DSCP PRIORITY             | SCHEDULING
----------------------------------------------------------------------------------------------------------------------------------------
0000:06:00.0    | 04:90:81:00:00:01 | PFC          | enp9s0np0    | ionic_0      | 24->pri3, 48->pri6        | 3 DWRR, 6 strict
0000:16:00.0    | 04:90:81:00:00:02 | PFC          | enp25s0np0   | ionic_1      | 24->pri3, 48->pri6        | 3 DWRR, 6 strict
0000:66:00.0    | 04:90:81:00:00:03 | PFC          | enp105s0np0  | ionic_2      | 24->pri3, 48->pri6        | 3 DWRR, 6 strict
```

## Troubleshooting

* "Not Found" in OS IFACE: This occurs if the MAC address reported by the hardware doesn't match any interface currently "UP" or visible in ip link.
* Empty RDMA DEV: The interface may not be RDMA-capable, or the RDMA modules (like ib_uverbs) are not loaded.
* All N/A in QoS Columns: Ensure the specific NIC firmware supports nicctl show qos and that non-zero priorities have been configured.
 
