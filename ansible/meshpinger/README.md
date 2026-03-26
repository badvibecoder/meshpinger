# meshpinger role

Runs meshpinger on each target host, emits per-host JSON test results, and fetches those artifacts to the controller for cluster-level aggregation.

## Requirements

- `python3` and `ping` available on target hosts.
- `nodes.csv` in the role files directory (or set `meshpinger_csv_filename` to another deployed file).

## Variables

Defaults are defined in `defaults/main.yml`.

- `meshpinger_remote_work_dir`: remote working directory for script/files.
- `meshpinger_csv_filename`: CSV copied to remote and passed to meshpinger.
- `meshpinger_fail_only`: when `true`, suppresses PASS lines in text logs.
- `meshpinger_threads`: worker thread count for ping execution.
- `meshpinger_artifact_root`: controller-side root for run artifacts.
- `meshpinger_report_run_id`: run identifier used for artifact directory layout.
- `meshpinger_report_name`: base name for aggregated report outputs.
- `meshpinger_controller_staging_dir`: controller path for fetched per-host JSON.
- `meshpinger_keep_legacy_logs`: fetch text logs to `legacy-logs/` when `true`.

## Artifact layout

For a run ID `20260326-140501`, artifacts are written under:

- `ansible/artifacts/20260326-140501/hosts/*.json` (fetched per-host results)
- `ansible/artifacts/20260326-140501/legacy-logs/*.log` (optional, when enabled)

## Per-host JSON schema

Each host writes `<inventory_hostname>-pingtest-results.json` with:

- `run_metadata`: host, timestamp, execution options, source/target counts.
- `summary`: `total`, `pass`, `fail`, `error`.
- `results[]`: detailed entries with `source_ip`, `target_ip`, `status`, `return_code`, and error/debug fields.

Status values are `pass`, `fail`, or `error`.
