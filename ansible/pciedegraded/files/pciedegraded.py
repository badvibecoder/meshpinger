import json
import socket
import subprocess
import argparse
import sys
import os
from datetime import datetime

def get_args():
    parser = argparse.ArgumentParser(description="Node PCIe Link Status Checker")
    parser.add_argument("--outdir", default="/var/tmp/pciedegraded", help="Directory to save JSON output")
    return parser.parse_args()

def check_pcie_degraded():
    hostname = socket.gethostname().split('.')[0]
    results = []
    
    # This command looks for the AMD Pensando device and checks if 'downgraded' appears in its LnkSta
    # We use a shell=True approach here to handle the complex pipe chain safely
    cmd = 'sudo lspci -vvv | grep -P "[0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f]|LnkSta:" | grep -B 1 "downgraded" | grep -A 1 "AMD Pensando Systems Device"'
    
    try:
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # If the grep chain returns output, it means a downgraded Pensando device was found
        if process.stdout.strip():
            # Clean up output for the JSON file
            results = [line.strip() for line in process.stdout.splitlines() if line.strip()]
            
    except Exception as e:
        print(f"{hostname} | [ERROR] Failed to run lspci: {str(e)}")

    return hostname, results

def main():
    args = get_args()
    hostname, results = check_pcie_degraded()

    # Trigger 'fail' if any degraded devices were captured in the results list
    overall_status = "fail" if results else "pass"

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    json_filename = f"{hostname}-pciedegraded-{timestamp}.json"
    
    os.makedirs(args.outdir, exist_ok=True)
    out_filepath = os.path.join(args.outdir, json_filename)
    
    # Matches the meshpinger/ethtool structure for Ansible aggregation
    output_data = {
        hostname: {
            "tests": {
                "pciedegraded": {
                    timestamp: {
                        "status": overall_status,
                        "degraded_devices": results
                    }
                }
            }
        }
    }

    with open(out_filepath, 'w') as jf:
        json.dump(output_data, jf, indent=2)

    print(f"Node: {hostname} | Overall Status: {overall_status.upper()}")
    print(f"Results saved to {out_filepath}")

if __name__ == "__main__":
    main()
