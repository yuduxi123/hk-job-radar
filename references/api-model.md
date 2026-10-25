# 可选外部模型 API 评分

默认继续使用当前 Codex。只有用户选择外部模型模式并明确允许发送所选画像/JD时，才执行带 `--send` 的命令。该模式只评分，不抓取网站、不投递、不发送邮件，也不替换宿主的搜索或调度器。

## 兼容范围

Python 3.9+，标准库，无需安装SDK。接口为非流式 `POST <base_url>/chat/completions`，Bearer认证，返回 `choices[0].message.content` JSON文本。支持符合此格式的服务（例如DeepSeek或Gemini官方兼容入口）；不是“任意模型都适配”。Anthropic原生Messages、OpenAI Responses专用模型、云厂商独有签名和非文本结果当前不支持。需提供兼容代理时自行核对其信任范围。

官方文档：[DeepSeek](https://api-docs.deepseek.com/) · [Gemini兼容入口](https://ai.google.dev/gemini-api/docs/openai)。模型名按服务商当前可用列表填写，不保证某个模型一直可用。

## 本地填写 Key

配置与Key放技能仓库之外的私有目录，例如 `~/.config/career-assistant/`。每个助手可使用不同配置。不要把Key放命令行、聊天、Git或截图里。

推荐隐藏输入，Key保存在同目录独立 `.key` 文件（权限600），配置只引用文件名：

```bash
python3 scripts/model_score.py configure \
  --config ~/.config/career-assistant/model-config-hk.json \
  --base-url https://api.deepseek.com --model YOUR_AVAILABLE_MODEL --prompt-key
```

运行后在终端提示处填写自己的Key，输入不回显。`YOUR_AVAILABLE_MODEL`是需要替换的模型名，不是实际模型。大陆配置可换成 `model-config-cn.json`。不覆盖已有配置/Key；更新普通地址/模型字段可编辑配置，替换Key使用私有编辑器，保持权限600。

若已在本地环境设置 `CAREER_MODEL_API_KEY`，可用 `--api-key-env CAREER_MODEL_API_KEY` 代替 `--prompt-key`。不读ChatGPT/Codex登录凭据。配置不接受明文 `api_key` 字段。

Gemini兼容入口的 base URL 为 `https://generativelanguage.googleapis.com/v1beta/openai`，填写自己的Gemini模型和Key。其他兼容服务同理。base URL不能包含最终 `/chat/completions`、查询参数或凭据。HTTPS默认必需；本机兼容服务可以显式 `--allow-local-http`，仅限localhost/127.0.0.1/::1。

## 输入与调用

输入是单岗位JSON；只填写你允许发给该服务的最小必要画像，不自动读取整份简历、邮箱、电话、浏览器会话或本地文件。`evidence`由助手先对照可信资料生成，模型不能自行改写门槛判断：

```json
{
  "profile": "虚构示例：计算机硕士在读，熟悉Python与RAG；毕业时间未确认。",
  "job": {"title":"AI实习","description":"要求Python、RAG及2027年毕业。","url":"https://example.com/jobs/1"},
  "evidence": {"status":"open","core_match":true,"requirements":[
    {"requirement":"2027年毕业","hard":true,"state":"unknown","evidence":"用户尚未确认毕业年月"}
  ]}
}
```

先保存到私有 `model-input.json`，预览无需Key，不发请求：

```bash
python3 scripts/model_score.py score --config ~/.config/career-assistant/model-config-hk.json --input /path/to/private/model-input.json
```

核对目标服务和共享内容后，显式发送（可能按API用量计费）：

```bash
python3 scripts/model_score.py score --config ~/.config/career-assistant/model-config-hk.json --input /path/to/private/model-input.json --output /path/to/private/model-score.json --send
```

原始模型分数`model_score`与约束后`score`均保留。资格B最高79，C最高59；低匹配分可继续降级，已关闭/过期岗位不调用API。分数是匹配参考，不是录用概率。模型可能出错，需核对其理由与缺口，不将返回文本当操作指令。

默认60秒超时；不自动重试、不切换服务、不回退模型，避免重复计费或意外共享数据。拒绝HTTP重定向以免将认证头转发到别处。401/429/网络/格式错误返回非零，不记录伪分数。输出文件权限600且不覆盖。HTTP错误不打印服务响应体/Key。Windows需另外配置文件ACL，不能把POSIX权限视为Windows安全保证。

## 自动任务接入

在现有自动任务中明确写配置路径和已授权的数据范围；先搜索核验，再逐岗评分，最后去重/保存。只增加配置不会修改已有自动任务，当前已建的香港监控仍按Codex分析。API只负责评分，不会赋予模型浏览网站能力。批量循环需在原有站点/服务额度内，由宿主控制，不做无人值守重试。

## 验证范围

离线测试覆盖请求构造、模型JSON解析、硬门槛限分、错误脱敏、重定向拒绝、私有文件与无Key预览。未提供真实Key，未调用收费服务；不能宣称各厂商端到端实测通过。
