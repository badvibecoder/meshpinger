import json
import os
import glob
from datetime import datetime
from jinja2 import Template

# --- Configuration ---
BASE_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "report")

def get_latest_log():
    list_of_files = glob.glob(os.path.join(LOGS_DIR, "*.json"))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def generate_html():
    latest_log = get_latest_log()
    if not latest_log:
        print(f"Error: No log files found in {LOGS_DIR}")
        return

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"report-{timestamp}.html"
    output_path = os.path.join(REPORTS_DIR, output_filename)

    with open(latest_log, 'r') as f:
        data = json.load(f)

    # --- HELPER LOGIC ---
    def get_node_rollup_status(node_data):
        """
        Returns: 'red' (all fail), 'yellow' (mixed), 'green' (all pass)
        """
        test_results = []
        try:
            tests_dict = node_data.get('tests', {})
            for test_name, test_runs in tests_dict.items():
                # Get the latest run (the only key in the timestamped dict)
                for ts, run_data in test_runs.items():
                    test_results.append(run_data.get('status', 'fail'))
        except:
            return 'red'

        if not test_results:
            return 'red'
        
        passes = test_results.count('pass')
        total = len(test_results)

        if passes == total:
            return 'green'
        elif passes > 0:
            return 'yellow'
        else:
            return 'red'

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
        <div class="max-w-6xl mx-auto" x-data="{ search: '', filter: 'all' }">

            <header class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black text-white tracking-tighter italic">MESHPINGER <span class="text-blue-500 not-italic">V2</span></h1>
                    <p class="text-slate-500 text-sm mt-1 font-mono">Log: {{ log_source }}</p>
                </div>
                <div class="flex gap-4">
                    <div class="bg-slate-900 border border-slate-800 p-3 rounded-lg text-center min-w-[100px]">
                        <p class="text-[10px] uppercase text-slate-500 font-bold">Total Nodes</p>
                        <p class="text-2xl font-mono font-bold text-white">{{ node_count }}</p>
                    </div>
                </div>
            </header>

            <div class="sticky top-6 z-50 bg-slate-900/90 backdrop-blur-lg p-3 rounded-xl border border-slate-700 shadow-2xl mb-8 flex flex-col sm:flex-row gap-3">
                <input type="text" x-model="search" placeholder="Search hostname..."
                       class="flex-grow bg-slate-800 border-slate-600 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                
                <div class="flex rounded-lg overflow-hidden border border-slate-600 font-bold text-xs">
                    <button @click="filter = 'all'" :class="filter === 'all' ? 'bg-slate-600 text-white' : 'bg-slate-800 text-slate-400'" class="px-4 py-2">ALL</button>
                    <button @click="filter = 'red'" :class="filter === 'red' ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-400'" class="px-4 py-2">FAIL</button>
                    <button @click="filter = 'yellow'" :class="filter === 'yellow' ? 'bg-yellow-600 text-white' : 'bg-slate-800 text-slate-400'" class="px-4 py-2">MIXED</button>
                </div>
            </div>

            <div class="grid gap-3">
                {% for node_name, node_data in nodes.items() %}
                {% set status = get_rollup(node_data) %}
                <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg"
                     x-show="('{{ node_name }}'.toLowerCase().includes(search.toLowerCase())) && (filter === 'all' || filter === '{{ status }}')"
                     x-data="{ nodeOpen: false }">
                    
                    <div @click="nodeOpen = !nodeOpen" class="cursor-pointer p-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors">
                        <div class="flex items-center gap-4">
                            <div class="w-3 h-3 rounded-full 
                                {{ 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' if status == 'green' }}
                                {{ 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]' if status == 'yellow' }}
                                {{ 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse' if status == 'red' }}">
                            </div>
                            <span class="text-lg font-bold font-mono tracking-tight">{{ node_name }}</span>
                        </div>
                        <svg class="w-5 h-5 text-slate-500 transition-transform" :class="nodeOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path d="M19 9l-7 7-7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>

                    <div x-show="nodeOpen" x-cloak class="bg-black/30 border-t border-slate-800 p-4 space-y-3">
                        {% for test_name, test_runs in node_data.get('tests', {}).items() %}
                            {% for ts, run_data in test_runs.items() %}
                            <div x-data="{ modOpen: false }" class="border border-slate-700/50 rounded-lg overflow-hidden">
                                <div @click="modOpen = !modOpen" class="flex items-center justify-between p-3 bg-slate-800/40 cursor-pointer hover:bg-slate-800/80">
                                    <div class="flex items-center gap-3">
                                        <span class="text-[10px] px-2 py-0.5 rounded font-black {{ 'bg-emerald-500/20 text-emerald-400' if run_data.status == 'pass' else 'bg-red-500/20 text-red-400' }}">
                                            {{ run_data.status | upper }}
                                        </span>
                                        <span class="text-sm font-semibold text-slate-300">{{ test_name }}</span>
                                    </div>
                                    <span class="text-[10px] font-mono text-slate-500">{{ ts }}</span>
                                </div>
                                <div x-show="modOpen" class="p-3 bg-slate-950 text-[11px] font-mono border-t border-slate-700">
                                    <pre class="text-blue-300/80 overflow-auto max-h-96">{{ run_data | tojson(indent=2) }}</pre>
                                </div>
                            </div>
                            {% endfor %}
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>

            <footer class="mt-12 text-center text-slate-600 text-xs font-mono">
                Report Generated at {{ timestamp }} | Data Source: {{ log_source }}
            </footer>
        </div>
    </body>
    </html>
    """

    template = Template(template_str)
    html_output = template.render(
        nodes=data,
        node_count=len(data),
        timestamp=timestamp,
        log_source=os.path.basename(latest_log),
        get_rollup=get_node_rollup_status
    )

    with open(output_path, 'w') as f:
        f.write(html_output)

    print(f"Report generated: {output_path}")

if __name__ == "__main__":
    generate_html()
