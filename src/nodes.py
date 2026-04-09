import json
import os
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.llm import get_deepseek_llm


def planner_node(state: AgentState):
    """节点 1：任务规划师 (Planner) - 将大问题拆解为具体的搜索任务"""
    topic = state["topic"]
    print(f"\n🧠 [Agent: Planner] 接到宏观主题：【{topic}】，正在进行任务拆解...")

    llm = get_deepseek_llm(temperature=0.3)
    sys_msg = SystemMessage(
        content="""你是一位顶级投行首席分析师。
请将用户输入的研究主题，拆解为 3 个最核心、最具体的底层搜索关键词（Query）。
要求：
1. 涵盖：行业现状/政策、核心玩家/财务数据、潜在风险。
2. 强制返回严格的 JSON 字符串数组格式，例如：["关键词1", "关键词2", "关键词3"]，不要任何多余的废话和 Markdown 标记。"""
    )

    try:
        response = llm.invoke([sys_msg, HumanMessage(content=topic)])
        # 清理可能带有的 ```json 标记
        result_str = response.content.replace("```json", "").replace("```", "").strip()
        queries = json.loads(result_str)
        print(f"🧠 [Agent: Planner] 拆解完成，生成的任务队列：{queries}")
        return {"search_queries": queries, "research_context": ""}  # 初始化上下文
    except Exception as e:
        print(f"🧠 [Agent: Planner] ❌ 拆解失败，使用默认退化策略: {e}")
        return {"search_queries": [f"{topic} 现状", f"{topic} 财务表现", f"{topic} 风险"], "research_context": ""}


def data_researcher_node(state: AgentState):
    """节点 2：资料检索员 (Researcher) - 连入真实互联网进行多轮搜索"""
    queries = state.get("search_queries", [])
    print(f"\n🔍 [Agent: Researcher] 正在连入真实互联网执行深度检索...")

    #工具会自动从.env 中读取 TAVILY_API_KEY,初始化 Tavily 搜索工具，设置每次查询返回最相关的 3 条深度网页摘要
    search_tool = TavilySearch(max_results=3)

    accumulated_context = ""

    for i, query in enumerate(queries):
        print(f"   -> 🌐 正在全网检索子任务 {i + 1}/{len(queries)}: '{query}'")
        try:
            # 真正触发网络请求，抓取全网最新信息
            results = search_tool.invoke({"query": query})

            accumulated_context += f"【真实互联网资料 {i + 1}：关于 '{query}'】\n"

            # Tavily 会自动清洗网页，返回包含 url 和 content(摘要) 的结构化数据
            if isinstance(results, list):
                for idx, res in enumerate(results):
                    # 把抓取到的干货拼接到全局大脑中
                    snippet = res.get('content', '无内容')
                    accumulated_context += f"  - 来源片段 {idx + 1}: {snippet}\n"
            else:
                accumulated_context += str(results) + "\n"

            accumulated_context += "\n"

        except Exception as e:
            print(f"   -> ⚠️ 搜索 '{query}' 时发生网络异常: {e}")
            accumulated_context += f"【关于 '{query}' 的资料获取失败】\n\n"

    print("🔍 [Agent: Researcher] 真实网络检索完毕，海量新鲜资料已装载进 Agent 大脑！")

    # 将真实的互联网数据覆盖进状态机的 context 中，交给下一个节点的 Writer 去写
    return {"research_context": accumulated_context}


def report_writer_node(state: AgentState):
    """节点 3：研报主笔 (Writer) - 基于全局记忆撰写长文"""
    print("\n✍️  [Agent: Writer] 正在研读全量资料，撰写深度分析报告...")

    context = state.get("research_context", "")
    feedback = state.get("fact_check_feedback", "")

    llm = get_deepseek_llm(temperature=0.5)

    sys_msg = SystemMessage(
        content="""你是一位严谨的金融研报主笔。
请基于用户提供的【检索资料库】，撰写一篇结构化的深度研究报告（300字左右）。
要求包含：核心观点、数据支撑、风险提示三个段落。不允许捏造资料库中没有的数值。"""
    )

    if feedback and not state.get("is_valid", True):
        print(f"✍️  [Agent: Writer] 接收到审核退回意见，正在重写：{feedback}")
        prompt_content = f"请务必修复以下审核问题：\n【审核意见】：{feedback}\n\n【检索资料库】：\n{context}"
    else:
        prompt_content = f"【检索资料库】：\n{context}"

    try:
        response = llm.invoke([sys_msg, HumanMessage(content=prompt_content)])
        print("✍️  [Agent: Writer] 报告撰写完成！")
        return {"report_draft": response.content}
    except Exception as e:
        return {"report_draft": f"大模型生成失败: {e}"}


def fact_checker_node(state: AgentState):
    """节点 4：合规审核员 (Fact Checker)"""
    print("\n⚖️  [Agent: FactChecker] 正在校验报告数据与原始资料库的一致性...")

    draft = state.get("report_draft", "")
    context = state.get("research_context", "")
    revision_count = state.get("revision_count", 0)

    if revision_count >= 2:
        print("⚖️  [Agent: FactChecker] ⚠️ 达到最大重试次数，强制放行。")
        return {"is_valid": True, "revision_count": revision_count + 1}

    llm = get_deepseek_llm(temperature=0.1)

    sys_msg = SystemMessage(
        content="""你是一个严苛的合规审核员。
请对比【检索资料库】和【报告草稿】。重点检查数值（如百分比、倍数等）是否完全一致。
请输出 JSON 格式：{"is_valid": true或false, "feedback": "修改意见或填无"}。不准输出其他字符。"""
    )

    try:
        response = llm.invoke([sys_msg, HumanMessage(content=f"【检索资料库】:\n{context}\n\n【报告草稿】:\n{draft}")])
        result_str = response.content.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(result_str)

        is_valid = result_json.get("is_valid", False)
        feedback = result_json.get("feedback", "")

        if is_valid:
            print("⚖️  [Agent: FactChecker] ✅ 审核通过：未发现数据幻觉！")
        else:
            print(f"⚖️  [Agent: FactChecker] ❌ 审核拦截！发现问题：{feedback}")

        return {"is_valid": is_valid, "fact_check_feedback": feedback, "revision_count": revision_count + 1}
    except Exception:
        return {"is_valid": True, "revision_count": revision_count + 1}