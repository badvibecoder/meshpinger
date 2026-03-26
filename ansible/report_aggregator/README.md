# report_aggregator role

Aggregates per-host meshpinger JSON artifacts into one cluster report JSON and one HTML report focused on node-level failures.

## Inputs

- Host artifacts in `{{ report_aggregator_host_artifact_dir }}`
- Files matching `*-pingtest-results.json`

## Outputs

- `{{ report_aggregator_json_output_path }}`
- `{{ report_aggregator_html_output_path }}`

Both paths default to `ansible/artifacts/<run_id>/`.

## Variables

Defaults are in `defaults/main.yml`.

- `report_aggregator_artifact_root`: artifact root directory.
- `report_aggregator_run_id`: run identifier to aggregate.
- `report_aggregator_report_name`: base filename for generated reports.
- `report_aggregator_cluster_label`: cluster/inventory label in report metadata.
- `report_aggregator_title`: HTML report title.
- `report_aggregator_host_artifact_dir`: host JSON source directory.
- `report_aggregator_output_dir`: output directory for generated artifacts.
- `report_aggregator_json_output_path`: cluster JSON output path.
- `report_aggregator_html_output_path`: cluster HTML output path.

## Cluster report schema (extensible)

Top-level envelope:

- `run_metadata`: run timestamp, title, run ID, cluster label, playbook.
- `nodes[]`: per-node summary and failure details.
- `checks.meshpinger`: cluster totals for `total`, `pass`, `fail`, `error`.

Additional checks can be added under `checks.<future_role_name>` without changing existing keys.
