# MCP Demo Server

这个目录是一个最小 MCP Server 示例，用静态数据模拟“内部平台接口 MCP 化”。

## 包含的 MCP 能力

- `search_tickets`：按关键字和状态查询静态工单
- `get_order_status`：按订单号查询静态订单状态
- `create_ticket`：创建一个模拟工单，不会修改真实系统
- `ticket://{ticket_id}`：按资源 URI 读取工单详情
- `ticket_triage_prompt`：一个排查订单问题的提示词模板

## 本地运行

先进入目录：

```powershell
cd D:\project\MCP\code
```

创建虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

启动 MCP Server：

```powershell
.\.venv\Scripts\python.exe .\platform_mcp_server.py
```

注意：这个服务使用 `stdio` 传输方式。正常情况下它启动后不会打印业务日志，而是等待 MCP Client 通过标准输入输出通信。

## 注册到 Codex 桌面版

可以在 Codex 桌面版中打开：

```text
Settings -> Integrations & MCP -> Add MCP Server
```

本地命令填写：

```text
D:\project\MCP\code\.venv\Scripts\python.exe
```

参数填写：

```text
D:\project\MCP\code\platform_mcp_server.py
```

也可以写到 Codex 的 `config.toml` 中，例如：

```toml
[mcp_servers.demo_platform]
command = "D:\\project\\MCP\\code\\.venv\\Scripts\\python.exe"
args = ["D:\\project\\MCP\\code\\platform_mcp_server.py"]
startup_timeout_sec = 20
tool_timeout_sec = 60
default_tools_approval_mode = "prompt"
```

如果需要项目级配置，可以放在：

```text
D:\project\MCP\.codex\config.toml
```

如果需要全局配置，可以放在：

```text
C:\Users\ltf\.codex\config.toml
```

## 可触发 MCP 工具的提示词

查询订单状态：

```text
帮我通过 demo_platform MCP 查询订单 O-20260628-001 的状态，并说明现在卡在哪一步。
```

搜索工单：

```text
帮我查一下 demo 平台里和 payment 相关的未关闭工单。
```

组合排查：

```text
请使用 demo_platform MCP：先查询订单 O-20260628-001 的状态，再搜索这个订单相关工单，最后给我一个处理建议。
```

模拟创建工单：

```text
请使用 demo_platform MCP 创建一个 P2 工单，标题是“订单地址校验失败”，描述是“用户提交的收货地址缺少城市字段，需要平台团队排查”。
```
