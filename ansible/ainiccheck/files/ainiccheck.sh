#!/bin/bash

# Header - Adjusting widths for dynamic content
printf "%-15s | %-17s | %-12s | %-12s | %-12s | %-25s | %-20s\n" \
    "PCI ADDR" "MAC ADDRESS" "PAUSE" "OS IFACE" "RDMA DEV" "DSCP PRIORITY" "SCHEDULING"
printf "%s\n" "----------------------------------------------------------------------------------------------------------------------------------------"

sudo nicctl show port | awk '
function print_row() {
    if (nic_pci != "" && mac != "") {
        print nic_pci "|" mac "|" ptype "|" nic_uuid
    }
    nic_pci=""; mac=""; ptype="N/A"; nic_uuid=""
}

/NIC[ \t]*:/ {
    print_row()
    if (match($0, /NIC[ \t]*:[ \t]*([^ \t(]+)[ \t]*\(([^)]+)\)/, m)) {
        nic_uuid = m[1]
        nic_pci = m[2]
    }
}

/Pause type[ \t]*:/ {
    split($0, a, ":")
    ptype = a[2]
    gsub(/[ \t]+/, "", ptype)
}

/MAC address[ \t]*:/ {
    mac = substr($0, index($0, ":") + 1)
    gsub(/[ \t]+/, "", mac)
    mac = tolower(mac)
}

END { print_row() }
' | while IFS="|" read -r p_nic p_mac p_type p_uuid; do

    os_iface=$(ip -o link | grep -iw "$p_mac" | awk -F': ' '{print $2}' | cut -d'@' -f1 | head -n 1)

    if [ -n "$os_iface" ]; then
        rdma_dev=$(rdma link show | grep -w "netdev $os_iface" | awk '{print $2}' | cut -d'/' -f1)

        # Fetch QoS Data
        qos_data=$(sudo nicctl show qos -c "$p_uuid" 2>/dev/null)

        # DYNAMIC EXTRACTION:
        # 1. Grab any DSCP mapping that is NOT priority 0
        # This looks for the line format: "DSCP : 46 ==> priority : 6"
        dscp_col=$(echo "$qos_data" | awk -F'[:>]' '
            /DSCP[ \t]*:[ \t]*[0-9]/ && !/priority[ \t]*:[ \t]*0/ {
                # $2 is the DSCP value, $4 is the priority
                val=$2; pri=$4;
                gsub(/[ \t]+/, "", val); gsub(/[ \t]+/, "", pri);
                printf "%s->pri%s ", val, pri
            }' | sed 's/ $//; s/ /, /g')

        # 2. Grab any Scheduling rows that are NOT priority 0
        # This looks for the table rows where column 1 is a number > 0
        sched_col=$(echo "$qos_data" | awk '
            $1 ~ /^[0-9]+$/ && $1 != "0" {
                printf "%s %s ", $1, $2
            }' | sed 's/ $//; s/ /, /g')

        printf "%-15s | %-17s | %-12s | %-12s | %-12s | %-25s | %-20s\n" \
            "$p_nic" "$p_mac" "$p_type" "$os_iface" "${rdma_dev:-None}" "${dscp_col:-None}" "${sched_col:-None}"
    else
        printf "%-15s | %-17s | %-12s | %-12s | %-12s | %-25s | %-20s\n" \
            "$p_nic" "$p_mac" "$p_type" "Not Found" "N/A" "N/A" "N/A"
    fi
done
