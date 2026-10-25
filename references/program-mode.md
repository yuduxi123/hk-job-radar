# 香港岗位雷达

这是 prui0474/hk-job-radar 的本机封装，不是官方 Skill。上游：https://github.com/prui0474/hk-job-radar 。

## 本机布局

- 应用：`~/.local/share/hk-job-radar/app`
- 独立 Python：`~/.local/share/hk-job-radar/venv/bin/python`
- 统一入口：`bash ~/.codex/skills/hk-job-radar/scripts/radar.sh <参数>`，可从任意项目使用。
- 配置：应用目录 `config.yaml`；画像：`data/profiles/profile.yaml`；数据库：`data/radar.db`；日志：`data/logs/`。
- 原仓库的源码、README 和 docs 是命令及版本限制的依据，按需读取，不根据宣传推断功能。

## 使用

首次配置时先运行 `doctor --no-llm`，报告缺项。询问目标岗位、求职阶段、背景及希望使用的推送渠道；不要把示例画像当成用户真实背景。可以运行 `setup --no-browser` 开启本地配置页面，让用户自己填写 API Key 和推送凭据。API Key 由上游读取环境变量 `DEEPSEEK_API_KEY` 或应用目录 `api_key.txt`；凭据文件权限使用 600，不在聊天、日志或版本控制中展示密钥。

常用参数：

- `--help`：列出命令。
- `doctor --no-llm`：不调用模型的环境检查；普通 `doctor` 会做模型 API 测试。
- `stats`：查看本地岗位统计。
- `setup --no-browser`：配置向导，返回本地地址，结束后关闭本次进程。
- `login jobsdb` / `login linkedin` / `login indeed`：打开浏览器供用户完成验证或登录，不绕过验证码。
- `once`：抓取一轮、调用模型评分并可能推送日报。
- `run`：常驻监控；记录进程如何停止。
- `report now`：立即推送日报；`notify test`：发送测试消息。
- `apply <job_uid>`：半自动填表，由用户核对并亲自提交。

安装 Skill 不等于授权对外发送消息、上传简历或投递申请。执行 `once`、`run`、`report now`、`notify test` 前确认用户已授权对应推送；填表或上传材料须在用户要求的申请范围内，最终提交遵循用户明确授权和宿主规则。说明模型 API 按用量收费。免费版限制以当前上游 tier.py 和 README 为准，不修改授权校验来启用高级版。

仅在用户要求定时监控时配置计划任务；不要直接执行 `install.command`，它还会注册定时任务、打开向导并进入登录流程。更新时先检查本地源码改动，保留配置、画像、会话、数据库和凭据；不要自动重置应用目录。

## 验证

安装验证用 `--help`、`doctor --no-llm` 和本地浏览器启动测试。没有真实画像、API Key、推送凭据及站点会话时，准确报告“环境已安装，业务尚待配置”，不能宣称岗位监控已运行。


本文件仅适用于可选上游程序，不是默认 Codex 搜索的依赖。不得将其 doctor 的 API Key 缺项当作 Codex 模式的故障。
