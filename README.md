# 香港求职助手 · hk-job-radar

[项目导航](https://github.com/yuduxi123) · [来源与致谢](ATTRIBUTION.md)

支持 Codex 的香港岗位搜索、资格核验、简历匹配及去重跟踪。**默认不需要 DeepSeek API Key**。这是独立的 Skill 封装，不是 [prui0474/hk-job-radar](https://github.com/prui0474/hk-job-radar) 抓取程序本体，也不捆绑其源码。

## 安装与使用

```bash
git clone https://github.com/yuduxi123/hk-job-radar.git
cd hk-job-radar
python3 scripts/install.py
```

Python 3.9+；安装后重新打开助手。安装器不会覆盖已有技能，升级前将旧目录移到技能目录外备份。其他宿主可用 `--target agents` 或 `--dest /path/to/skills`，是否发现技能取决于宿主。

对助手说：

> 使用 hk-job-radar，按我的简历查香港 AI 工程实习及兼职。请核对官方详情，标明每周工时、毕业时间和工作资格未知项，去重后给出链接，不投递。

## 两种模式

| 模式 | 需要什么 | 能做什么 |
|---|---|---|
| 默认 Codex 模式 | 当前宿主的搜索/浏览器工具 | 按需搜索、核验、匹配；不需要额外模型 Key，仍占用宿主额度 |
| 可选上游程序 | 用户另行安装的上游应用、Python及相应凭据 | doctor、抓取、模型评分、推送；按上游当前版本限制 |

上游命令用 `bash scripts/radar.sh --help`。默认路径为 `~/.local/share/hk-job-radar/app` 与同级 `venv/bin/python`，可用 `HK_JOB_RADAR_APP_DIR`、`HK_JOB_RADAR_PYTHON` 覆盖。本技能不会自动安装、登录或修改上游授权校验。

## 离线数据工具

数据格式、证据分级和命令见 [tracking](references/tracking.md)。不自带常驻服务；每日监控需用户明确要求后，由宿主实际配置调度器。电脑/网络/宿主条件影响执行，聊天结束本身不代表继续运行。

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖身份去重、时间顺序、历史维护与资格分级，不证明招聘站点全部适配或真实投递成功。明确不满足硬门槛为C，未知为B；不编造工作许可、毕业日期和薪资。

## 隐私与发布边界

真实简历、画像、浏览器会话、凭据和申请日志放在独立私有工作台。不要提交到技能仓库。支持助手准备申请，只有明确授权的具体操作才能执行；最终状态以官方回执为准。

[开源调研](references/oss-review.md) · [MIT](LICENSE)

## 可选：使用其他模型 API 评分

保留默认Codex模式，新增可配置的OpenAI Chat Completions兼容接口。可填写服务地址、模型名，并在本机终端隐藏输入API Key；无需额外Python依赖。支持环境变量或权限600的独立Key文件，真实Key不写仓库。

```bash
python3 scripts/model_score.py configure --config ~/.config/career-assistant/model-config.json --base-url https://api.deepseek.com --model YOUR_AVAILABLE_MODEL --prompt-key
```

将模型名替换为服务商实际可用模型。默认评分命令只预览，明确添加 `--send` 才传输所选画像/JD并产生可能的API费用。模型输出0–100匹配分，硬门槛未知最多B/79分，明确不符最多C/59分；分数不是录用概率。接口兼容不等于已经实测所有厂商，原生Anthropic Messages等不同协议不直接支持。

详见[配置、输入格式与调用说明](references/api-model.md)。未提供真实Key，本次仅进行离线协议与安全行为测试；不会自动修改已配置的每日任务。
