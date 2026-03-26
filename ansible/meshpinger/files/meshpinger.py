import argparse
import csv
import json
import logging
import socket
import subprocess
import sys
import threading
from datetime import datetime
from queue import Queue

def get_args():
    parser = argparse.ArgumentParser(description="Node Mesh Ping Tester")
    parser.add_argument("--csv", default="nodes.csv", help="Path to the node CSV file")
    parser.add_argument("--fail-only", action="store_true", help="Only log failed pings")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent ping threads")
    parser.add_argument(
        "--json-output",
        default=None,
        help="Optional path to write structured JSON results",
    )
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


def build_success_result(hostname, source_ip, target_ip, result):
    success = result.returncode == 0
    status = "pass" if success else "fail"
    return {
        "hostname": hostname,
        "source_ip": source_ip,
        "target_ip": target_ip,
        "status": status,
        "return_code": result.returncode,
        "error": None,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def build_error_result(hostname, source_ip, target_ip, error):
    return {
        "hostname": hostname,
        "source_ip": source_ip,
        "target_ip": target_ip,
        "status": "error",
        "return_code": None,
        "error": str(error),
        "stdout": "",
        "stderr": "",
    }


def ping_worker(q, hostname, fail_only, detailed_results, results_lock):
    while not q.empty():
        try:
            source_ip, target_ip = q.get_nowait()
        except Exception:
            break

        # -c: count, -I: source address, -W: timeout in seconds
        cmd = ["ping", "-c", "2", "-W", "2", "-I", source_ip, target_ip]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            task_result = build_success_result(hostname, source_ip, target_ip, result)
            success = task_result["status"] == "pass"
            status = "[PASS]" if success else "[FAIL]"

            log_msg = f"{hostname} | {status} {source_ip} -> {target_ip}"

            # Logic for --fail-only
            if not fail_only or (fail_only and not success):
                logging.info(log_msg)
                print(log_msg)

        except Exception as e:
            task_result = build_error_result(hostname, source_ip, target_ip, e)
            err_msg = f"{hostname} | [ERROR] {source_ip} -> {target_ip}: {str(e)}"
            logging.error(err_msg)
            print(err_msg)

        with results_lock:
            detailed_results.append(task_result)

        q.task_done()


def summarize_results(detailed_results):
    summary = {"total": 0, "pass": 0, "fail": 0, "error": 0}
    for result in detailed_results:
        summary["total"] += 1
        if result["status"] in summary:
            summary[result["status"]] += 1
        else:
            summary["error"] += 1
    return summary


def write_json_output(json_path, hostname, args, local_ips, remote_ips, detailed_results):
    generated_at = datetime.now().isoformat(timespec="seconds")
    output_data = {
        "run_metadata": {
            "generated_at": generated_at,
            "hostname": hostname,
            "csv_path": args.csv,
            "threads": args.threads,
            "fail_only": args.fail_only,
            "source_ip_count": len(local_ips),
            "target_ip_count": len(remote_ips),
        },
        "summary": summarize_results(detailed_results),
        "results": detailed_results,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"Structured JSON written to {json_path}")

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
    detailed_results = []
    results_lock = threading.Lock()

    print(f"Node: {hostname} | Log: {log_file} | Mode: {'Failures Only' if args.fail_only else 'All'}")
    print(f"Executing {total_tasks} path tests...")

    for _ in range(min(args.threads, total_tasks)):
        t = threading.Thread(
            target=ping_worker,
            args=(q, hostname, args.fail_only, detailed_results, results_lock),
            daemon=True,
        )
        t.start()

    q.join()
    summary = summarize_results(detailed_results)
    print(
        "Summary: total={total} pass={pass_count} fail={fail_count} error={error}".format(
            total=summary["total"],
            pass_count=summary["pass"],
            fail_count=summary["fail"],
            error=summary["error"],
        )
    )

    if args.json_output:
        write_json_output(args.json_output, hostname, args, local_ips, remote_ips, detailed_results)

    print(f"Complete. Results in {log_file}")

if __name__ == "__main__":
    main()
