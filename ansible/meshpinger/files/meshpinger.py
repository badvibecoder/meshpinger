import yaml
import json
import socket
import subprocess
import threading
import argparse
import sys
from datetime import datetime
from queue import Queue

def get_args():
    parser = argparse.ArgumentParser(description="Node Mesh Ping Tester")
    parser.add_argument("--yaml", default="nodes.yaml", help="Path to the node YAML file")
    parser.add_argument("--fail-only", action="store_true", help="Only record failed pings in JSON")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent ping threads")
    return parser.parse_args()

def get_node_info(yaml_path):
    hostname = socket.gethostname().split('.')[0]
    local_ips = []
    remote_ips = []
    
    try:
        with open(yaml_path, mode='r') as f:
            inventory = yaml.safe_load(f)
            
            if not inventory or 'nodes' not in inventory:
                print(f"Error: Invalid structure in '{yaml_path}'. Expected 'nodes' root key.")
                sys.exit(1)

            for node in inventory['nodes']:
                node_name = node.get('name', '').strip()
                interfaces = node.get('interfaces', {})
                backend_ips = interfaces.get('backend', [])
                
                if node_name == hostname:
                    local_ips.extend(backend_ips)
                else:
                    remote_ips.extend(backend_ips)
                    
    except FileNotFoundError:
        print(f"Error: YAML file '{yaml_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        sys.exit(1)
                
    return hostname, local_ips, remote_ips

def ping_worker(q, hostname, fail_only, successes, failures, lock):
    while not q.empty():
        try:
            source_ip, target_ip = q.get_nowait()
        except:
            break
        
        cmd = ["ping", "-c", "2", "-W", "2", "-I", source_ip, target_ip]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            success = (result.returncode == 0)
            
            if success:
                # Print to console for real-time tracking
                print(f"{hostname} | [PASS] {source_ip} -> {target_ip}")
                
                # Only record success to JSON if --fail-only is NOT set
                if not fail_only:
                    with lock:
                        successes.append({"src": source_ip, "dst": target_ip})
            else:
                # Attempt to parse a meaningful error from ping output
                error_msg = "Ping failed"
                if "100% packet loss" in result.stdout:
                    error_msg = "Timeout / 100% packet loss"
                elif "Network is unreachable" in result.stderr or "unreachable" in result.stdout:
                    error_msg = "Network unreachable"
                
                print(f"{hostname} | [FAIL] {source_ip} -> {target_ip} ({error_msg})")
                with lock:
                    failures.append({
                        "src": source_ip, 
                        "dst": target_ip, 
                        "error": error_msg
                    })
                
        except Exception as e:
            print(f"{hostname} | [ERROR] {source_ip} -> {target_ip}: {str(e)}")
            with lock:
                failures.append({
                    "src": source_ip, 
                    "dst": target_ip, 
                    "error": f"Execution error: {str(e)}"
                })
        
        q.task_done()

def main():
    args = get_args()
    hostname, local_ips, remote_ips = get_node_info(args.yaml)
    
    if not local_ips:
        print(f"Error: Hostname '{hostname}' not found in {args.yaml} (or no backend IPs defined)")
        return

    # Tracking variables for JSON payload
    successes = []
    failures = []
    result_lock = threading.Lock()
    
    # Execution setup
    q = Queue()
    for target in remote_ips:
        for source in local_ips:
            q.put((source, target))

    total_tasks = q.qsize()
    print(f"Node: {hostname} | Mode: {'Failures Only' if args.fail_only else 'All'} | Tests: {total_tasks}")

    # Spin up threads
    for _ in range(min(args.threads, total_tasks)):
        t = threading.Thread(
            target=ping_worker, 
            args=(q, hostname, args.fail_only, successes, failures, result_lock), 
            daemon=True
        )
        t.start()

    q.join()

    # Build the JSON Output Structure
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    json_filename = f"{hostname}-pingtest-{timestamp}.json"
    
    output_data = {
        hostname: {
            "tests": {
                "backendpingtest": {
                    timestamp: {
                        "successes": successes,
                        "failures": failures
                    }
                }
            }
        }
    }

    # Dump to JSON file
    with open(json_filename, 'w') as jf:
        json.dump(output_data, jf, indent=2)

    print(f"\nComplete. JSON results saved to {json_filename}")

if __name__ == "__main__":
    main()