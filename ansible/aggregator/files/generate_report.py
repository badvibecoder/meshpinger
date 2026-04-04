import json
import os
import glob
from datetime import datetime
from jinja2 import Template

# --- Configuration ---
# Finds paths relative to where this script is located in the Ansible role
BASE_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "report")

def get_latest_log():
    """Finds the most recently created JSON file in the logs directory."""
    list_of_files = glob.glob(os.path.join(LOGS_DIR, "*.json"))
    if not list_of_files:
        return None
    # Sort by creation time to get the absolute latest fetch
    return max(list_of_files, key=os.path.getctime)

def generate_html():
    latest_log = get_latest_log()

    if not latest_log:
        print(f"Error: No log files found in {LOGS_DIR}")
        return

    # Ensure the report directory exists
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    # Define the single filename format: report-YYYY-MM-DD-HH-MM.html
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"report-{timestamp}.html"
    output_path = os.path.join(REPORTS_DIR, output_filename)

    with open(latest_log, 'r') as f:
        data = json.load(f)

    # The HTML Template (Same high-performance NOC dashboard)
    template_str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Meshpinger Report | {{ timestamp }}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
        <style>
            [x-cloak] { display: none !important; }
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: #0f172a; }
            ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        </style>
    </head>
    <body class="bg-slate-950 text-slate-200 min-h-screen p-4 md:p-8">
        <div class="max-w-6xl mx-auto" x-data="{ search: '', showOnlyFailures: false }">

            <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tighter">MESHPINGER <span class="text-blue-500 underline decoration-blue-500/30">DASHBOARD</span></h1>
                    <p class="text-slate-500 text-sm mt-1 font-mono">Source Log: {{ log_source }}</p>
                </div>
                <div class="flex items-center gap-6">
                    <div class="text-right">
                        <p class="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">Node Count</p>
                        <p class="text-3xl font-mono font-bold text-blue-400">{{ node_count }}</p>
                    </div>
                </div>
            </header>

            <div class="sticky top-6 z-50 bg-slate-900/90 backdrop-blur-lg p-3 rounded-xl border border-slate-700 shadow-2xl mb-8 flex flex-col sm:flex-row gap-3">
                <div class="relative flex-grow">
                    <input type="text" x-model="search" placeholder="Filter by hostname..."
                           class="w-full bg-slate-800 border-slate-600 rounded-lg pl-10 pr-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
                    <svg class="w-5 h-5 absolute left-3 top-2.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoi
n="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>

                <button @click="showOnlyFailures = !showOnlyFailures"
                        :class="showOnlyFailures ? 'bg-red-600 text-white shadow-[0_0_15px_rgba(220,38,38,0.4)]' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'"
                        class="px-5 py-2 rounded-lg font-bold transition-all flex items-center justify-center gap-2 whitespace-nowrap">
                    <span x-text="showOnlyFailures ? 'Showing Errors Only' : 'Show All Nodes'"></span>
                </button>
            </div>

            <div class="grid gap-2">
                {% for node_name, node_data in nodes.items() %}
                {% set failed = has_failures(node_data) %}
                <div class="bg-slate-900 border border-slate-800 rounded-lg hover:border-slate-600 transition-colors"
                     x-show="('{{ node_name }}'.toLowerCase().includes(search.toLowerCase())) && (!showOnlyFailures || {{ 'true' if failed else 'false' }})"
                     x-data="{ open: false }" x-cloak>

                    <div @click="open = !open" class="cursor-pointer p-4 flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-2.5 h-2.5 rounded-full {{ 'bg-red-500 animate-pulse' if failed else 'bg-emerald-500' }}"></div>
                            <span class="font-mono text-md tracking-tight font-semibold {{ 'text-red-400' if failed else 'text-slate-200' }}">{{ node_name }}</span>
                        </div>
                        <div class="flex items-center gap-4">
                             <span class="text-[10px] font-bold text-slate-600 uppercase">{{ 'Issue Detected' if failed else 'Healthy' }}</span>
                             <svg class="w-4 h-4 text-slate-500 transition-transform duration-200" :class="open ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0
 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                        </div>
                    </div>

                    <div x-show="open" class="p-4 bg-black/40 border-t border-slate-800">
                        <h4 class="text-[10px] font-bold uppercase text-slate-500 mb-2 tracking-widest">Expanded Node Detail</h4>
                        <pre class="text-[11px] leading-relaxed text-blue-300/80 bg-slate-950 p-4 rounded border border-slate-800 overflow-auto max-h-[500px]">{{ node_data | toj
son(indent=2) }}</pre>
                    </div>
                </div>
                {% endfor %}
            </div>

            <footer class="mt-12 text-center text-slate-600 text-xs font-mono">
                Generated by Meshpinger v2 Aggregator | {{ timestamp }}
            </footer>
        </div>
    </body>
    </html>
    """

    def has_failures(node_data):
        try:
            for test_cat in node_data.get('tests', {}).values():
                for test_run in test_cat.values():
                    if test_run.get('failures'):
                        return True
        except: pass
        return False

    template = Template(template_str)
    html_output = template.render(
        nodes=data,
        node_count=len(data),
        timestamp=timestamp,
        log_source=os.path.basename(latest_log),
        has_failures=has_failures
    )

    with open(output_path, 'w') as f:
        f.write(html_output)

    print(f"Report generated: {output_path}")

if __name__ == "__main__":
    generate_html()
