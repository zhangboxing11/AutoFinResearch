# 📈 AutoFinResearch: 基于 LangGraph 的多智能体深度投研系统

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-green)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_V3-black)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

**AutoFinResearch** 是一个基于 LangGraph 构建的 Plan-and-Solve（规划与执行）架构多智能体协作系统。针对传统 AI 搜索信息碎片化、易产生数据幻觉的痛点，本项目实现了从“宏观主题拆解 → 全网多源数据抓取 → 事实交叉核验 → 深度长文生成”的全自动闭环。

---

## 🌟 核心特性与工程亮点

- **🧠 复杂工作流编排 (Graph Orchestration)**
  摒弃单体大模型调用，基于 LangGraph 搭建涵盖 `Planner`、`Researcher`、`Writer`、`FactChecker` 四个核心节点的循环图状态机 (Cyclic StateGraph)，实现长序列任务的稳定流转。

- **🔍 意图拆解与动态记忆 (Plan & Memory)**
  `Planner` 节点将宏观投研主题降维拆解为具体的搜索 Query；实现 **Global Context** 全局记忆机制，支持跨节点的上下文挂载，彻底解决多轮搜索中的信息丢失问题。

- **⚖️ 事实核查与反思纠错 (Reflexion)**
  独立的 `FactChecker` 节点充当合规审查员。通过对比原始网页摘要与生成草稿，拦截数值篡改与逻辑谬误，并触发 `Writer` 节点的**带反馈重试 (Retry with Feedback)**，显著降低大模型幻觉。

- **🌐 高质量全网信息抓取**
  接入专为 LLM 优化的 **Tavily API**，代替传统爬虫，实现结构化、去噪的高信噪比网页摘要提取。

- **🎨 开箱即用的交互界面**
  基于 Gradio Blocks 架构打造的沉浸式前端界面，提供 SaaS 级的用户交互体验。

---

## ⚙️ 系统架构流转

当用户输入一个研究主题时，系统内部将触发以下流转闭环：

1. **User Input** -> 传入初始研究主题。
2. **Planner Node** -> 大脑节点，将其拆分为 3-5 个具体的底层检索任务。
3. **Researcher Node** -> 循环调用 Tavily 引擎，并发抓取全网最新数据并清洗，沉淀为全局记忆。
4. **Writer Node** -> 根据全量数据库，撰写结构化的深度研报初稿。
5. **FactChecker Node** -> 将初稿与数据库进行交叉比对：
   - ❌ **若发现幻觉：** 附带修改建议，将状态流转回 `Writer Node` 重新生成。
   - ✅ **若审核通过：** 结束图循环，输出最终研报。

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/zhangboxing11/AutoFinResearch.git
cd AutoFinResearch
```

### 2. 配置环境
```bash
conda create -n autofin python=3.10 -y
conda activate autofin
```
#### 安装核心依赖库
```bash
pip install -r requirements.txt
```

### 3. 配置密钥
在项目根目录复制环境变量模板，并填入您的真实 API 密钥（本项目推荐使用高性价比的 DeepSeek 作为底层驱动）：

```bash
cp .env.example .env
```

#### 编辑env文件

```bash
DEEPSEEK_API_KEY="sk-您的真实密钥"
DEEPSEEK_BASE_URL="https://api.deepseek.com"
TAVILY_API_KEY="tvly-您的真实密钥"
```

### 4. 运行应用
```bash
python app.py
```
终端将输出一个本地链接（通常为 http://127.0.0.1:7860），在浏览器中打开即可开始您的深度投研之旅！