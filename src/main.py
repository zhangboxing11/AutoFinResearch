from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import planner_node, data_researcher_node, report_writer_node, fact_checker_node


def build_workflow():
    workflow = StateGraph(AgentState)

    # 注册 4 个核心节点
    workflow.add_node("Planner", planner_node)
    workflow.add_node("Researcher", data_researcher_node)
    workflow.add_node("Writer", report_writer_node)
    workflow.add_node("FactChecker", fact_checker_node)

    # 定义标准执行流：起始 -> 规划师 -> 检索员 -> 主笔 -> 审核员
    workflow.add_edge(START, "Planner")
    workflow.add_edge("Planner", "Researcher")
    workflow.add_edge("Researcher", "Writer")
    workflow.add_edge("Writer", "FactChecker")

    # 定义自纠错反思循环
    def check_routing(state: AgentState):
        if state.get("is_valid"):
            print("🚀 [Workflow] 研报审核完美，流程彻底结束！")
            return END
        else:
            print("🔄 [Workflow] 研报存在瑕疵，流转回 Writer 重新改写！")
            return "Writer"

    workflow.add_conditional_edges("FactChecker", check_routing)

    return workflow.compile()


if __name__ == "__main__":
    print("========================================")
    print("   V2.0 深度研究智能体引擎启动   ")
    print("========================================\n")

    app = build_workflow()

    # 我们随便给它一个宏大的主题，测试大模型的拆解能力
    initial_state = {
        "topic": "比亚迪固态电池技术的商业化前景与投资风险",
        "revision_count": 0,
        "is_valid": False
    }

    final_state = app.invoke(initial_state)

    print("\n================ 最终通过合规的深度研报 ================\n")
    print(final_state["report_draft"])
    print("\n====================================================")