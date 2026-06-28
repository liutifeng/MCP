import json
from datetime import datetime
from typing import Literal

from mcp.server.fastmcp import FastMCP


# 创建一个 MCP Server 实例。
# 这个名称会作为服务标识出现在 MCP Client / AI 应用的工具列表中。
mcp = FastMCP("demo-platform-mcp")


# 这里用静态数据模拟企业内部的“工单平台”。
# 真实项目中，这部分通常会替换成数据库查询，或者调用现有 REST / RPC 接口。
TICKETS = [
    {
        "id": "T-1001",
        "title": "Order payment callback timeout",
        "status": "open",
        "priority": "P1",
        "owner": "payment-team",
        "order_id": "O-20260628-001",
    },
    {
        "id": "T-1002",
        "title": "Customer address field validation failed",
        "status": "processing",
        "priority": "P2",
        "owner": "platform-team",
        "order_id": "O-20260628-002",
    },
    {
        "id": "T-1003",
        "title": "Invoice data synchronization delay",
        "status": "closed",
        "priority": "P3",
        "owner": "finance-team",
        "order_id": "O-20260627-009",
    },
]


# 这里用静态数据模拟企业内部的“订单平台”。
# 做 MCP 化时，不需要重写原平台，只需要在 MCP Server 中包装这些已有能力。
ORDERS = {
    "O-20260628-001": {
        "order_id": "O-20260628-001",
        "status": "payment_pending",
        "customer": "Shanghai Demo Trading Co., Ltd.",
        "amount": 1280.50,
        "risk_level": "medium",
        "last_update": "2026-06-28 10:15:00",
    },
    "O-20260628-002": {
        "order_id": "O-20260628-002",
        "status": "address_check_failed",
        "customer": "Hangzhou Sample Technology Co., Ltd.",
        "amount": 760.00,
        "risk_level": "low",
        "last_update": "2026-06-28 11:20:00",
    },
}


def to_pretty_json(data: object) -> str:
    # MCP tool 返回字符串最通用；这里统一格式化成易读 JSON，方便 AI 理解结果。
    return json.dumps(data, ensure_ascii=False, indent=2)

# 装饰器
@mcp.tool()
def search_tickets(keyword: str = "", status: str = "all") -> str:
    """按关键字和状态查询工单。"""
    # @mcp.tool() 会把这个普通 Python 函数暴露成 MCP 工具。
    # AI 应用看到工具名称、参数和描述后，就可以在需要时发起调用。
    keyword_lower = keyword.lower().strip()
    status_lower = status.lower().strip()

    results = []
    for ticket in TICKETS:
        # 这里只做最简单的匹配：工单号、标题、订单号中包含关键字即可。
        matches_keyword = (
            not keyword_lower
            or keyword_lower in ticket["id"].lower()
            or keyword_lower in ticket["title"].lower()
            or keyword_lower in ticket["order_id"].lower()
        )
        # status 为 all 或空字符串时表示不过滤状态。
        matches_status = status_lower in ("", "all") or ticket["status"] == status_lower

        if matches_keyword and matches_status:
            results.append(ticket)

    return to_pretty_json(
        {
            "count": len(results),
            "items": results,
        }
    )


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """根据订单号查询订单状态。"""
    # 查询类接口最适合先做成只读 tool，风险低，也容易在 AI 应用中演示。
    order = ORDERS.get(order_id)
    if not order:
        return to_pretty_json(
            {
                "found": False,
                "message": f"Order {order_id} was not found in demo data.",
            }
        )

    return to_pretty_json(
        {
            "found": True,
            "order": order,
        }
    )


@mcp.tool()
def create_ticket(
    title: str,
    description: str,
    priority: Literal["P1", "P2", "P3"] = "P2",
) -> str:
    """创建模拟工单。"""
    # 真实系统里，这里一般会调用 POST /tickets 之类的平台接口。
    # 这个 demo 只返回模拟结果，不会真的写入任何业务系统。
    fake_id = f"T-DEMO-{datetime.now().strftime('%H%M%S')}"
    return to_pretty_json(
        {
            "created": True,
            "ticket": {
                "id": fake_id,
                "title": title,
                "description": description,
                "status": "open",
                "priority": priority,
                "owner": "demo-platform-team",
            },
            "note": "This is a demo response. No real platform data was changed.",
        }
    )


@mcp.resource("ticket://{ticket_id}")
def get_ticket(ticket_id: str) -> str:
    """通过资源 URI 读取工单详情。"""
    # Resource 更像“可读取的数据对象”。
    # 这里把工单详情暴露成 ticket://T-1001 这种资源地址。
    for ticket in TICKETS:
        if ticket["id"] == ticket_id:
            return to_pretty_json(ticket)

    return to_pretty_json(
        {
            "found": False,
            "message": f"Ticket {ticket_id} was not found in demo data.",
        }
    )


@mcp.prompt()
def ticket_triage_prompt(order_id: str) -> str:
    """订单问题排查提示词模板。"""
    # Prompt 用来沉淀可复用的业务提示词。
    # 它不会直接查询数据，而是告诉 AI 应用应该按什么思路调用工具和组织答案。
    return (
        "请根据 MCP 工具返回的数据，帮我排查订单问题。\n"
        f"订单号：{order_id}\n"
        "请先查询订单状态，再搜索相关工单，最后给出处理建议。"
    )


if __name__ == "__main__":
    # 使用 stdio 传输方式，适合被 Codex、Claude Desktop 等本地 AI 应用拉起。
    # 这类 MCP Server 不需要自己监听端口，而是通过标准输入输出和客户端通信。
    mcp.run(transport="stdio")
