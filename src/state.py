from typing import TypedDict, List

class AgentState(TypedDict):
    """
    V2.0 深度研究智能体状态图
    """
    topic: str                  # 用户输入的宏大研究主题
    search_queries: List[str]   # Planner 拆解出的具体搜索任务列表
    research_context: str       # 【全局记忆】存放所有检索回来的资料片段
    report_draft: str           # Writer 生成的深度报告初稿
    fact_check_feedback: str    # Fact Checker 给出的修改建议
    is_valid: bool              # 是否通过审核
    revision_count: int         # 反思重写的次数