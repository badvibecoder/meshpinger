import csv
import socket
import subprocess
import threading
import logging
import argparse
import sys
from datetime import datetime
from queue import Queue

def get_args():
    parser = argparse.ArgumentParser(description="Node Mesh Ping Tester")
    parser.add_argument("--csv", default="nodes.csv", help="Path to the node CSV file")
    parser.add_argument("--fail-only", action="store_true", help="Only log failed pings")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent ping threads")
    return parser.parse_args()

def get_node_info(csv_path):
    # Get short hostname
    hostname = socket.gethostname().split('.')[0]
    local_ips = []
    remote_ips = []
    
    try:
        with open(csv_path, mode='r') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2: continue
                node = row[0].strip()
                ip = row[1].strip()
                
                if node == hostname:
                    local_ips.append(ip)
                else:
                    remote_ips.append(ip)
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_path}' not found.")
        sys.exit(1)
                
    return hostname, local_ips, remote_ips

def setup_logging(hostname):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_filename = f"{hostname}-pingtest-{timestamp}.log"
    
    # Thread-safe logging configuration
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return log_filename

def ping_worker(q, hostname, fail_only):
    while not q.empty():
        try:
            source_ip, target_ip = q.get_nowait()
        except:
            break
        
        # -c: count, -I: source address, -W: timeout in seconds
        cmd = ["ping", "-c", "2", "-W", "2", "-I", source_ip, target_ip]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            success = (result.returncode == 0)
            status = "[PASS]" if success else "[FAIL]"
            
            log_msg = f"{hostname} | {status} {source_ip} -> {target_ip}"
            
            # Logic for --fail-only
            if not fail_only or (fail_only and not success):
                logging.info(log_msg)
                print(log_msg)
                
        except Exception as e:
            err_msg = f"{hostname} | [ERROR] {source_ip} -> {target_ip}: {str(e)}"
            logging.error(err_msg)
            print(err_msg)
        
        q.task_done()

def main():
    args = get_args()
    hostname, local_ips, remote_ips = get_node_info(args.csv)
    
    if not local_ips:
        print(f"Error: Hostname '{hostname}' not found in {args.csv}")
        return

    log_file = setup_logging(hostname)
    
    # Populate queue: Every local IP pings every remote IP
    q = Queue()
    for target in remote_ips:
        for source in local_ips:
            q.put((source, target))

    total_tasks = q.qsize()
    print(f"Node: {hostname} | Log: {log_file} | Mode: {'Failures Only' if args.fail_only else 'All'}")
    print(f"Executing {total_tasks} path tests...")

    for _ in range(min(args.threads, total_tasks)):
        t = threading.Thread(target=ping_worker, args=(q, hostname, args.fail_only), daemon=True)
        t.start()

    q.join()
    print(f"Complete. Results in {log_file}")

if __name__ == "__main__":
    main()
