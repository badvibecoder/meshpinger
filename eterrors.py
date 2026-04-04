import json
import socket
import subprocess
import argparse
import sys
import os
import re
from datetime import datetime

def get_args():
    parser = argparse.ArgumentParser(description="Node Ethtool Error Gatherer")
    # Updated default directory name
    parser.add_argument("--outdir", default="/var/tmp/ethtool_errors", help="Directory to save JSON output")
    return parser.parse_args()

def get_interfaces():
    try:
        interfaces = os.listdir('/sys/class/net/')
        return [iface for iface in interfaces if iface != 'lo']
    except FileNotFoundError:
        print("Error: /sys/class/net/ not found.")
        sys.exit(1)

def gather_ethtool_stats(interfaces):
    hostname = socket.gethostname().split('.')[0]
    error_pattern = re.compile(
        r'err|over|drop|bad|pause|full|busy|exhausted|not_reusable|aborted|invalid|no_buff|colli', 
        re.IGNORECASE
    )
    
    interface_results = {}
    for iface in interfaces:
        cmd = ["ethtool", "-S", iface]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                stats = {}
                for line in result.stdout.splitlines():
                    if error_pattern.search(line):
                        parts = line.split(':')
                        if len(parts) == 2:
                            metric_name = parts[0].strip()
                            metric_value = parts[1].strip()
                            if metric_value != "0":
                                try:
                                    stats[metric_name] = int(metric_value)
                                except ValueError:
                                    stats[metric_name] = metric_value
                if stats:
                    interface_results[iface] = stats
        except Exception as e:
            print(f"{hostname} | [ERROR] {iface}: {str(e)}")

    return hostname, interface_results

def main():
    args = get_args()
    interfaces = get_interfaces()
    hostname, results = gather_ethtool_stats(interfaces)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    # Updated filename naming convention
    json_filename = f"{hostname}-eterrors-{timestamp}.json"
    
    os.makedirs(args.outdir, exist_ok=True)
    out_filepath = os.path.join(args.outdir, json_filename)
    
    output_data = {
        hostname: {
            "tests": {
                "ethtool_errors": {
                    timestamp: results
                }
            }
        }
    }

    with open(out_filepath, 'w') as jf:
        json.dump(output_data, jf, indent=2)

    print(f"Results saved to {out_filepath}")

if __name__ == "__main__":
    main()
