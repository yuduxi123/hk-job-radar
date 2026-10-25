#!/bin/bash
set -euo pipefail
app_dir="${HK_JOB_RADAR_APP_DIR:-${HOME}/.local/share/hk-job-radar/app}"
radar_python="${HK_JOB_RADAR_PYTHON:-${HOME}/.local/share/hk-job-radar/venv/bin/python}"
if [[ ! -x "$radar_python" || ! -f "$app_dir/run.py" ]]; then
  echo '香港岗位雷达环境缺失，请检查应用和独立 Python 路径。' >&2
  exit 1
fi
cd "$app_dir"
export PYTHONUTF8=1
exec "$radar_python" "$app_dir/run.py" "$@"
