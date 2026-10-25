# 来源与致谢

## 工作流参考（非 fork）

- [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops)：经历证据、岗位跟踪、按JD准备材料；MIT。
- [sharzoy/auto-job-apply](https://github.com/sharzoy/auto-job-apply)：硬门槛优先及分级投递包；MIT。

以上用于设计参考，不表示复制它们的程序，也不是运行前置依赖。参考星数与核对范围见 [开源调研](references/oss-review.md)。其他早期参考如有列出，继续保留其原始出处，不把作者的个人信息或案例当成用户资料。

## 接口与宿主

模型API模式使用用户指定的OpenAI Chat Completions兼容服务；[DeepSeek文档](https://api-docs.deepseek.com/)与[Gemini兼容文档](https://ai.google.dev/gemini-api/docs/openai)用于协议核对。接口兼容不表示厂商背书，也不代表所有模型已经实测。

招聘信息来自职位原始发布方及招聘平台；岗位链接、JD、商标和招聘数据不属于本项目原创内容。请遵守相应站点规则。

## 香港雷达程序上游

[prui0474/hk-job-radar](https://github.com/prui0474/hk-job-radar)（MIT）是可选程序模式所操作的上游。**本仓库是技能封装，不是该抓取程序本体，也未捆绑上游源码。** `scripts/radar.sh`仅调用用户另行安装的应用；默认Codex模式无需安装上游。请勿将此仓库描述成上游作者的官方发行版。

本仓库原创代码与说明适用 [MIT](LICENSE)；第三方内容保留各自的授权与署名要求。
