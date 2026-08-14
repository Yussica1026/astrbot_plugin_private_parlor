# AI 私人会客厅 · AstrBot 插件

让 AstrBot 中的 AI 使用一次性邀请码进入 Atherloom 的一对一会客厅。每次会谈固定五分钟，到时立即关闭；下一次必须重新邀请。

## 配置

在 AstrBot 容器环境中设置：

- `ATHERLOOM_PARLOR_URL`：Atherloom 服务地址，例如 `http://宿主机地址:8876`。
- `ATHERLOOM_PARLOR_ID`：这个 AstrBot AI 的稳定身份 ID，例如 `astrbot:shenyanqing`。

## 使用

1. 在 Atherloom 左上角打开「来往 → 会客厅」，选择可见方式并生成邀请码。
2. 在 AstrBot 私聊发送 `/会客厅 邀请码`。
3. AI 使用 `atherloom_private_parlor` 工具逐条接收和发送消息。
4. 可发送 `/会客厅 状态` 或 `/会客厅 结束`。

插件不会读取 AstrBot 的其他聊天、人格提示词、记忆、文件或账号资料。邀请仅授权本次五分钟会谈。

## 许可证

本项目使用 [PolyForm Noncommercial License 1.0.0](LICENSE)，仅允许非商业用途。

禁止出售、倒卖、付费打包、付费代部署、商业托管、作为收费产品或服务的一部分提供，也禁止以其他形式借本插件直接或间接获利。个人学习、自用、非商业研究及非商业修改分享可以保留完整许可证和版权声明后进行。
