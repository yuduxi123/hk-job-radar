# 离线跟踪与资格证据

Python 3.9+，仅用标准库，不连接招聘网站。

```bash
python3 scripts/job_store.py --store /path/to/private-workspace/jobs.jsonl ingest --input /path/to/jobs.json
python3 scripts/job_store.py --store /path/to/private-workspace/jobs.jsonl list
python3 scripts/match_evidence.py /path/to/evidence.json
```

job_store 的 types 沿用 daily_internship/summer_internship/campus/unknown。无法明确归类的香港兼职用 unknown，并在 employment_type 写 part_time，不能把兼职伪装日常实习。必填 company/title/url/types/verified_at，时间含时区。可补充 source_url/official_url/job_id/location/employment_type/requirements/uncertainties。数据只支持本机原子写入，不是实时数据库。

证据文件格式：`{"status":"open","core_match":true,"requirements":[{"requirement":"每周4天","hard":true,"state":"unknown","evidence":"尚未确认"}]}`。脚本只检查结构与分级，不读取简历、不推断能力，不证明网站仍在招。必须先由助手用原始资料建立证据。
