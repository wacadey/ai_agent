# AI Agent 课程中文学习总览

> 基于本仓库 `readme.MD`、`md/step1.md`～`md/step21.md`，并核对最新阶段的相关 Python、Docker 和 Terraform 代码整理。用于课后理解与练习，不代替原始步骤说明。
>
> 本次核对：2026-10-08，分支 `step21-service-cloud-`。代码会持续变化；命令、路径和默认值以你当前分支为准。

## 1. 这门课最终在做什么

从“Python 向模型发送一个问题”开始，逐步构建一个能够查询业务数据、检索公司文档、调用外部工具、保存用户偏好，并通过 API 提供服务的 Agent 应用。

课程使用产品、订单、退款和公司规定作为示例。SQL 中的业务记录、Markdown 中的政策、MCP 中的汇率都是练习数据，不能当成真实业务或实时信息。

| 学习阶段 | Step | 核心问题 |
|---|---|---|
| 模型调用与流程组合 | 1～5 | 如何调用模型、表达要求、连接多个处理步骤？ |
| 知识库与 RAG | 6～10 | 如何把文档变成可检索的知识，并据此回答？ |
| Agent 与工具 | 11～16 | 如何让模型选择工具、使用记忆、返回固定格式？ |
| 评估与执行控制 | 17～20 | 如何衡量效果、观察过程、验证结果、限制执行？ |
| 服务与部署 | 21 | 如何让其他程序通过 API 使用 Agent，并部署到 AWS？ |

**重要分界：Step 11 是直接测试工具，Step 12 开始让模型自主选择工具。** Step 19 在基础工具循环外，再增加计划、验证与重试。

## 2. 先分清这些概念

| 概念 | 可以怎样理解 | 在本项目中的作用 |
|---|---|---|
| LLM | 会理解语言、生成回答的模型 | 理解问题，提出工具调用，整理答案 |
| Prompt | 给模型的任务说明 | 提供角色、背景、要求和限制 |
| LangChain | 连接模型、提示词和工具的组件 | 创建 Chain、包装 Tool、统一调用接口 |
| Chain | 预先安排好的处理流程 | 按固定顺序传递输入和输出 |
| Tool | 程序提供的一项可执行功能 | 查询销售、检索规定、保存记忆等 |
| Agent | 根据任务选择行动的程序 | 让模型决定是否使用工具，再根据结果继续 |
| LangGraph | 管理节点、状态和分支的框架 | 组织 Agent 与 ToolNode 的循环 |
| Embedding | 把文字转换成数字向量 | 比较语义相似度 |
| pgvector | PostgreSQL 的向量扩展 | 存储向量并进行相似度检索 |
| RAG | 检索增强生成 | 先查相关资料，再让模型根据资料回答 |
| Memory | 保存并召回重要用户信息 | 延续偏好和背景；不同于公司知识库 |
| MCP | 连接工具和数据服务的标准协议 | 通过 Client 调用 MCP Server 提供的工具 |
| Structured Output | 按固定字段输出 | 让 API、前端和评估程序读取结果 |
| LangSmith | 调用追踪与观测平台 | 查看模型、工具、耗时和结果 |
| Agent Loop | 计划、执行、验证、重试的外层流程 | 检查任务是否完成，再决定是否重新规划 |
| Harness | 用代码约束执行的政策层 | 检查工具权限、轮次和时间 |
| FastAPI / Docker / Terraform | 接口、打包和基础设施工具 | 将 Agent 变成可部署的服务 |

Agent 不需要强制具备长期记忆或多个角色。先实现“选择工具 → 执行 → 根据结果回答”，就能理解本课程的基础 Agent。

## 3. 怎么自学这份仓库

课堂先抓住“输入是什么、处理了什么、输出是什么”；课后每次只补一个 Step，按下面的顺序完成。

1. **读说明：** 看对应 `md/stepN.md` 的目标。
2. **跑示例：** 从 `steps/` 入口运行，观察正常输出。
3. **顺着调用读：** 从入口跳转到 `app/` 中的函数，再看数据库或外部服务。
4. **改一个地方：** 换问题、日期、文档或参数，预测结果后运行。
5. **自己解释：** 用三句话说明新增能力、执行流程和验证结果。

每天课后可先安排 45～60 分钟：10 分钟读流程、20 分钟运行和看代码、15 分钟修改、5 分钟总结。遇到环境问题时，先解决阻塞，不要求当天追完老师的进度。

**完成标准是能解释并修改一个小功能，不是同步抄完代码。**

### 分支与文件关系

- `app/`：可复用功能。
- `steps/`：各阶段练习入口。
- `scripts/`：环境诊断、数据库迁移等辅助程序。
- `md/`：原始步骤说明。
- `data/`：当前文档入库程序读取的政策文件。
- `data_short/`：较短的对照样例；当前入库入口默认不读取它。
- `sql/migrations/`：数据库结构与固定业务样例。
- `mcp_servers/`：课程自建 MCP Server。
- `infra/`：部署脚本和 Terraform。

各分支代表不同阶段的代码快照。最新分支保留早期入口，但共享模块已升级，因此早期入口的输出可能与当时的 MD 不完全相同。想复现某一步最初的行为，应使用对应阶段分支。

例如学习 Step 12，已有本地分支时：

```powershell
git status
git fetch origin
git switch step12-langgraph-agent
```

如果尚无该本地分支：

```powershell
git switch --track origin/step12-langgraph-agent
```

先查看并保存自己的改动，再切分支。`origin` 是个人仓库，`upstream` 是老师仓库；`git fetch upstream` 只更新远端跟踪引用，不会自动修改本地或个人远端的分支。

## 4. 环境准备

以下命令在项目根目录执行，除非另有说明。

### Python 虚拟环境

Windows PowerShell：

```powershell
python -m venv agent
.\agent\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -c "import sys; print(sys.executable)"
```

macOS / Linux：

```bash
python3 -m venv agent
source agent/bin/activate
python -m pip install -r requirements.txt
```

运行前确认解释器属于项目虚拟环境。VS Code Python 插件提供编辑支持，不等于安装了 Python 本体。

### 配置与认证

从 `.env.example` 复制一份本地 `.env`，按当前代码配置。主要配置项：

```dotenv
AWS_REGION=us-east-1
BEDROCK_CHAT_MODEL=填写当前账号可调用的模型ID
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
DATABASE_URL=postgresql://agent:agent@localhost:5432/agentlab
USER_ID=填写练习用用户ID
```

模型 ID 应以学校账号的可用模型和区域为准；代码默认值不代表你的账号一定有权限。按学校要求配置 Bedrock 认证；若使用 Bearer Token，填写 `AWS_BEARER_TOKEN_BEDROCK`。过期后需更新。

`app/config.py` 通过 `load_dotenv()` 加载配置，环境变量优先于 `os.getenv()` 的默认值。已存在的系统环境变量通常不会被默认的 `load_dotenv()` 覆盖。

查看 CLI 区域：

```powershell
aws configure get region
```

本项目客户端读取的是 `AWS_REGION`，因此 CLI 区域与程序配置都要检查。密钥、Token 和真实连接信息留在本地，不写入学习文档或提交到 Git。

### 启动数据库

最新 Compose 同时定义了数据库和 Agent。先只启动数据库，避免在准备基础数据时提前启动 Agent：

```powershell
docker compose up -d postgres
python -m scripts.migrate
docker exec -it agent-postgres psql -U agent -d agentlab
```

在 psql 中：

```sql
\dt
\q
```

Migration、文档入库和 Agent 服务启动是不同步骤。运行需要模型的示例或入库程序，会产生 API 调用；无需为了阅读代码运行全部示例。

## 5. Step 1：项目骨架与环境检查

**新增能力：** 建立目录结构，确认基本运行环境。

**代码入口：** `steps/step1_check.py`、`scripts/doctor.py`。

```powershell
python -m steps.step1_check
python -m scripts.doctor
```

前者输出 Python 和系统信息；后者检查 Git、Docker、AWS CLI 的命令路径。找到 Docker 命令不等于 Docker 引擎已启动，仍可用 `docker info` 检查。

**动手练习：** 找到当前 Python 解释器和三个命令的位置。
**检查点：** 能说明 `app/`、`steps/`、`scripts/` 分别放什么。

## 6. Step 2：直接调用 Bedrock LLM

**新增能力：** 将 Prompt 发给模型，接收并解析响应。

**重点文件：** `app/bedrock.py`、`app/config.py`、`steps/step2_bedrock_llm_call.py`。

```powershell
python -m steps.step2_bedrock_llm_call
```

**动手练习：** 换成“用两句话解释数据管道”，观察回答。
**检查点：** 能指出认证、模型 ID、输入和响应解析所在的位置。这一步是模型调用，尚未加入工具选择。

## 7. Step 3：Prompt Engineering

**新增能力：** 将模糊的问题改写成明确任务。

| 部分 | 要写什么 |
|---|---|
| Role | 模型扮演什么角色 |
| Context | 完成任务需要的背景 |
| Task | 具体要做什么 |
| Constraints | 格式、长度、范围等限制 |
| Few-shot | 必要时给出期望输入与输出的示例 |

**重点文件：** `app/prompts.py`、`steps/step3_prompt_engineering.py`。

```powershell
python -m steps.step3_prompt_engineering
```

**动手练习：** 同一产品分别面向个人用户和企业运营团队生成文案。
**检查点：** 能解释哪项 Prompt 改动导致了语气、内容或格式的变化。Prompt 能约束表达，但不能保证事实正确。

## 8. Step 4：LangChain 与 Chain

**新增能力：** 用统一接口连接提示词、模型和输出处理。

**重点文件：** `app/llm.py`、`steps/step4_langchain_basic.py`。

```powershell
python -m steps.step4_langchain_basic
```

LCEL 可通过 `|` 组合组件，例如：

```python
chain = prompt | model | output_parser
```

这是概念示例；课程实际 Chain 以入口代码为准。`invoke()` 同步调用，`ainvoke()` 异步调用，`stream()` 流式输出，`batch()` 批量调用。

**动手练习：** 修改 Prompt 变量，观察输入如何进入模板。
**检查点：** 能说清每一环节接收与返回什么。Chain 的流程预先确定，Agent 会根据任务选择下一步。

## 9. Step 5：多个角色顺序协作

**新增能力：** 让不同职责的 Chain 顺序完成写代码、审查和修改。

**入口：** `steps/step5_a2a_basic.py`。

```powershell
python -m steps.step5_a2a_basic
```

课程将这些角色称为 Agent，并用 A2A 表达协作概念；本练习以多个 Chain 的顺序编排为主，不应仅凭名字认定已经实现标准 A2A 协议。

**动手练习：** 为 reviewer 增加“检查数据库连接是否关闭”的要求。
**检查点：** 能找出审查结果如何传入下一次修改。输出是模型生成的代码，审查文字本身不能代替实际验证。

## 10. Step 6：Embedding 与相似度

**新增能力：** 将文本变成向量，再比较语义相似度。

**重点文件：** `app/embedding.py`、`steps/step6_embedding_basic.py`。

```powershell
python -m steps.step6_embedding_basic
```

当前示例使用 Titan Embedding，代码注释和示例输出为默认 1024 维。**1024 是向量维度，不是文本最大 Token 数；Embedding 也不等于 Tokenizer。**

**动手练习：** 比较“想退货”“申请退款”“查询销售额”三句话。
**检查点：** 能解释向量和余弦相似度的作用。相似度是语义接近程度，不是答案正确率。

## 11. Step 7：PostgreSQL 与 pgvector

**新增能力：** 在数据库中保存向量，并按相似度查找。

**重点文件：** `app/database.py`、`sql/migrations/001_pgvector.sql`、`steps/step7_pgvector.py`。

```powershell
python -m scripts.migrate
python -m steps.step7_pgvector
```

psql 检查：

```sql
\d demo_vectors
SELECT id, content FROM demo_vectors;
```

**动手练习：** 更换查询句子，观察返回顺序。
**检查点：** 能说明文本、向量分别存在哪里，查询向量如何参与排序。

## 12. Step 8：文档切块与入库

**新增能力：** 将整份政策文档加工成可检索的知识库。

**重点文件：** `app/ingestion/loader.py`、`splitter.py`、`ingest.py`、`sql/migrations/002_documents.sql`。

```powershell
python -m steps.step8_document_ingestion
```

处理顺序：读取正文和元数据 → 切块 → 每块生成 Embedding → 保存到 `documents` 与 `document_chunks`。一份文档对应多个 Chunk。

早期 Step 8 练习基础切块；**最新分支的共享入库代码已默认使用语义切块，阈值为 0.55。** 同一文档重新入库时，会更新文档记录、删除旧 Chunk 并写入新 Chunk，不是单纯追加。

**动手练习：** 在练习文档中增加一段内容，重新入库后查询 Chunk。
**检查点：** 能找出原文、元数据、Chunk、向量之间的对应关系。

## 13. Step 9：基础 RAG

**新增能力：** 先检索知识库，再根据相关资料生成回答。

**重点文件：** `app/retrieval.py`、`app/rag.py`、`steps/step9_rag_basic.py`。

```powershell
python -m steps.step9_rag_basic
```

提问时的问题也要生成向量；数据库返回相关 Chunk 后，将其与问题一起交给模型。文档入库是准备阶段，查询与回答是使用阶段。

**动手练习：** 分别问一个文档有依据的问题和一个文档没有依据的问题。
**检查点：** 能核对回答是否由检索内容支持。RAG 不会自动保证正确，应检查来源与原文。

## 14. Step 10：进阶 RAG

**新增能力：** 语义切块、元数据过滤、向量与关键词混合检索。

**重点文件：** 升级后的 `splitter.py`、`ingest.py`、`retrieval.py`。

```powershell
python -m steps.step10_rag_advanced
```

| 优化 | 解决什么问题 |
|---|---|
| 语义切块 | 在内容含义变化处切分，尽量保留连贯内容 |
| 元数据过滤 | 按部门、类别缩小搜索范围 |
| 混合检索 | 结合语义接近与关键词匹配 |

当前 `advanced_search()` 在 SQL 中使用向量权重 0.80、关键词权重 0.20；权重不是调用参数。改变切块策略后需重新入库；只改变查询权重或过滤条件通常无需重新生成文档向量。

**动手练习：** 对同一问题比较无部门过滤与 `HR` 过滤的结果。
**检查点：** 能解释结果为什么变化。切块阈值与权重是否更好，要用 Step 17 的评估验证。

## 15. Step 11：将功能封装成 Tool

**新增能力：** 把 SQL 查询和政策检索包装成可调用工具。

**重点文件：** `app/tools/sql_tools.py`、`rag_tools.py`、`sql/migrations/003_business.sql`。

```powershell
python -m scripts.migrate
python -m steps.step11_tools
```

该阶段示例直接调用 `sales_summary.invoke(...)`、`top_products.invoke(...)` 和 `search_company_policy.invoke(...)`。**调用哪个工具由测试代码决定。** 退款统计工具在 Step 13 加入。

工具名称、参数和 docstring 告诉模型“该功能能做什么、需要什么输入”。执行结果来自实际 Python 函数。

**动手练习：** 改查询日期、Top-N 或政策问题。
**检查点：** 能分别列出三个工具的输入与输出。

## 16. Step 12：LangGraph Agent

**新增能力：** 模型自主提出工具调用，程序执行工具，再将结果交给模型。

**重点文件：** `app/agent/graph.py`、`prompts.py`、`state.py`、`app/main.py`。

```powershell
python -m steps.step12_langgraph_agent
```

| 组件 | 作用 |
|---|---|
| StateGraph | 定义整体流程 |
| AgentState / MessagesState | 保存消息与状态 |
| Agent 节点 | 调用模型，获得回答或工具调用请求 |
| ToolNode | 执行工具，生成工具结果消息 |
| 条件边 | 判断继续调用工具还是结束 |

重点读懂消息顺序：`HumanMessage` → 带 `tool_calls` 的 `AIMessage` → `ToolMessage` → 最终 `AIMessage`。模型提出调用请求，真正执行的是程序。

**动手练习：** 分别问“年假规定”和“某段时间的销售额”，观察选择的工具。
**检查点：** 能解释 Step 11 与 Step 12 的差别，并在消息里找到调用参数与返回结果。

## 17. Step 13：SQL 与 RAG 联合分析

**新增能力：** 在一个问题中同时使用业务统计和政策依据。

**重点文件：** `sql/migrations/004_refunds.sql`、`app/tools/sql_tools.py` 中的 `refund_summary`、`app/agent/graph.py`。

```powershell
python -m scripts.migrate
python -m steps.step13_sql_rag_agent
```

例如“查询 2026-09-01～2026-09-05 的退款，并根据退款规定说明注意事项”：SQL 查实际退款记录，RAG 查规定，模型综合两种结果。

**动手练习：** 更换日期，比较有数据与无数据时的回答。
**检查点：** 能区分统计事实和政策条件。MD 中先展示缺少工具时无法查询，再展示注册退款工具后的结果。

## 18. Step 14：长期记忆

**新增能力：** 保存并检索用户偏好，辅助后续回答。

**重点文件：** `sql/migrations/005_memory.sql`、`app/tools/memory_tools.py`、`app/config.py`。

```powershell
python -m scripts.migrate
python -m steps.step14_memory
```

本步已经包含 `remember_user_preference` 和 `recall_user_memory` 两个工具。当前召回按 `USER_ID` 过滤并按向量距离排序；`importance` 被保存、返回，但未参与排序。

**动手练习：** 保存“回答用简短列表”，再询问相关偏好。
**检查点：** 查看 `agent_memories` 是否新增记录，能区分“本次请求的消息状态”和“数据库里的长期记忆”。

当前 `USER_ID` 来自环境配置，属于练习用单用户设置；尚未实现请求级用户认证。保存记忆也不意味着自动缓存答案或省略后续 LLM 调用。

## 19. Step 15：MCP 外部工具连接

**新增能力：** 理解 MCP Host、Client、Server，并通过协议调用工具。

| 角色 | 本项目对应 |
|---|---|
| Host：使用 MCP 的应用 | Agent 应用 |
| Client：连接与调用 Server | `app/tools/mcp_tools.py` 中的 FastMCP Client |
| Server：提供 MCP Tool | `mcp_servers/exchange_server.py` |

```powershell
python -m steps.step15_mcp
```

当前 Client 通过本地 Python 文件连接 Server，不是已经部署好的远程汇率服务。Server 返回固定模拟汇率，仅用于演示调用过程。

**动手练习：** 先问支持的货币对，再问不支持的货币对，观察工具结果或错误处理。
**检查点：** 能说明本地 Tool 如何经 Client 到达 MCP Server。MCP 是通信协议，不是模型，也不保证数据质量。

## 20. Step 16：结构化输出

**新增能力：** 按固定结构返回结果。

**重点文件：** `app/output.py`、`app/agent/graph.py`。

```powershell
python -m steps.step16_structured_output
```

```json
{
  "answer": "最终回答",
  "sources": ["文档或工具来源"],
  "tools_used": ["实际使用的工具"],
  "confidence": 0.8
}
```

当前图增加格式化节点，再调用一次模型生成 JSON，随后用 `AgentResponse.model_validate_json()` 验证字段。Pydantic 验证结构，不验证事实。

**动手练习：** 对比政策问题和销售问题的 `sources`、`tools_used`。
**检查点：** 能解释为什么 API 需要固定字段。`confidence` 是模型生成的自评值，不是经过校准的正确概率；结构化 API 支持也不能仅凭课程注释概括所有模型版本。

## 21. Step 17：检索评估

**新增能力：** 用固定问题与期望来源评估检索结果。

**重点文件：** `app/evaluation/dataset.py`、`retrieval_eval.py`。

```powershell
python -m steps.step17_evaluation
```

当前代码实际计算：

| 指标 | 含义 |
|---|---|
| HitRate@K | 测试问题中，Top-K 包含期望文档的问题比例 |
| MRR | 第一个正确结果的逆排名均值；未找到计 0 |

例如三个问题的正确文档分别排第 1、第 2、未找到，MRR 为 `(1 + 1/2 + 0) / 3 = 0.5`。当前按文档代码评估，多个 Chunk 可能来自同一文档。

原 MD 还介绍 Precision、Recall、NDCG、MAP、回答忠实度等扩展指标，**当前评估入口未全部实现。**

**动手练习：** 添加两条改写问题，再比较搜索参数调整前后的指标。
**检查点：** 能说明检索成功不等于答案正确，少量测试达到 1.0 也不代表真实场景全部可靠。

## 22. Step 18：LangSmith 追踪

**新增能力：** 观察模型与工具的实际调用过程。

**重点文件：** `app/observability.py`、`steps/step18_observability.py`。

在本地 `.env` 配置自己的项目和密钥：

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=填写自己的密钥
LANGSMITH_PROJECT=ai-agent
```

```powershell
python -m steps.step18_observability
```

**动手练习：** 发起一次工具查询，在 LangSmith 中找到对应 Trace。
**检查点：** 能定位模型输入、工具参数、工具结果与耗时。配置显示开启，不等于 Trace 已成功上传，仍要查看平台记录。

## 23. Step 19：计划、执行、验证与重试

**新增能力：** 将任务拆成子问题，执行后验证，不充分时根据反馈重新规划。

**实际文件名：** `app/loog_engine.py`，不是 `app/loop_engine.py`。

```powershell
python -m steps.step19_agent_loop
```

Planner 生成 1～4 个子问题；基础 Agent 逐个执行；Verifier 输出 `passed` 和 `gaps`；未通过时进入下一轮。当前 `max_attempts` 默认 2，超过次数后返回最后一轮拼接结果，并不保证通过验证。

**动手练习：** 明确指定 2026 年和查询日期，观察计划与验证反馈。
**检查点：** 能区分基础 Agent 的工具循环与外层任务验证循环。

已知限制：子问题各自创建消息状态，没有自动共享前一子问题得到的事实；缺少最终综合回答步骤。当前该文件还将配置键写为 `recusion_limit`，标准键应为 `recursion_limit`，因此不能将这里的 18 当成已确认生效的限制。MD 中的失败案例可用于理解这些问题。

## 24. Step 20：Harness 执行护栏

**新增能力：** 在执行工具前检查允许范围、轮次和时间。

**重点文件：** `app/harness.py`、`app/agent/graph.py`、`state.py`。

```powershell
python -m steps.step20_harness_guardrail
```

当前实现包括工具白名单、默认 6 个工具轮次、120 秒的运行时间检查。一个工具轮次可以包含多个工具调用，不等于单个工具调用次数。

**动手练习：** 阅读白名单和 `Budget.check()`，解释什么情况下会抛出异常。
**检查点：** 能指出检查发生在何处。该实现不包含完整的 Token / 费用预算、提示注入防护或强制中断超时调用。

当前 `graph.py` 读取 `started_at`，却返回并在状态中使用 `start_at`，存在键名不一致；可能导致计时起点被重新设置。这里描述的是设计目的和现有实现边界，不代表完整的 120 秒总超时已经验证。

## 25. Step 21：FastAPI、Docker 与 AWS 部署

**新增能力：** 通过 HTTP 提供 Agent 接口，并部署运行环境。

### 本地 API

**重点文件：** `app/main.py`、`app/service.py`、`steps/step21_agent_service.py`。

```powershell
python -m steps.step21_agent_service
```

打开 [本地 Swagger 文档](http://localhost:8000/docs)。

| 接口 | 用途 |
|---|---|
| `GET /health` | 返回进程健康响应 |
| `POST /chat` | 接收 `message`，调用 Agent 并返回结果 |

请求示例：

```json
{"message": "查询2026年9月的销售额"}
```

原 MD 的 `/heath` 是拼写错误，实际接口是 `/health`。根路径 `/` 没有定义，返回 404 正常。`/health` 当前只返回固定状态，不检查 Bedrock、数据库或完整 Agent 链路。

### Docker

先完成 Migration 和文档入库，再启动服务：

```powershell
docker compose up --build
```

本机 Python 连接数据库使用 `localhost`；Compose 中 Agent 连接数据库使用服务名 `postgres`：

```text
postgresql://agent:agent@postgres:5432/agentlab
```

最新 Compose 会等待数据库健康，但并未自动执行 Migration 与文档入库；云端 bootstrap 脚本另有初始化步骤。

### Terraform 与云端

```powershell
cd infra\terraform
terraform init
terraform fmt
terraform validate
terraform plan
```

查看计划后再执行 `terraform apply`。部署流程是创建 VPC、RDS、S3、IAM 和 EC2，将项目 ZIP 上传到 S3，再由 EC2 bootstrap 下载、生成配置、构建镜像、迁移数据库、入库并启动服务。本课程没有配置完整 CI/CD。

| 文件 | 职责 |
|---|---|
| `versions.tf` / `provider.tf` | Provider 与区域 |
| `variables.tf` | 项目名、实例规格、模型等配置 |
| `network.tf` / `security.tf` | 网络与安全组 |
| `rds.tf` | 数据库和连接信息配置 |
| `deploy.tf` | 打包代码并上传 S3 |
| `iam.tf` | EC2 角色与权限 |
| `ec2.tf` | EC2 与启动脚本 |
| `outputs.tf` | 输出服务与连接地址 |
| `infra/scripts/bootstrap.sh` | 初始化与启动服务 |

**动手练习：** 先本地调用 `/chat`，再对照 Terraform 解释每个资源如何支持服务。
**检查点：** 本地和云端都应通过实际 `/chat` 请求检查完整链路，不能只看 `/health`。当前 API 未提供请求级用户认证，长期记忆仍使用配置中的固定用户 ID。

## 26. 数据库与知识库速查

| Migration | 内容 |
|---|---|
| `001_pgvector.sql` | 扩展与演示向量表 |
| `002_documents.sql` | 文档与 Chunk 表 |
| `003_business.sql` | 产品、订单及固定样例 |
| `004_refunds.sql` | 退款及固定样例 |
| `005_memory.sql` | 长期记忆表 |

常用检查：

```sql
SELECT * FROM schema_migrations ORDER BY version;
SELECT document_code, title FROM documents;
SELECT document_id, COUNT(*) FROM document_chunks GROUP BY document_id;
SELECT * FROM refunds;
SELECT id, user_id, content, importance FROM agent_memories;
```

Migration 用于按版本建立结构与样例；Embedding 入库用于加工文档；Memory 用于保存用户信息。不要把这三种数据来源混为一谈。

## 27. 常见问题与排查顺序

| 现象 | 先检查什么 |
|---|---|
| `ModuleNotFoundError` | 虚拟环境、解释器路径、当前分支的依赖安装 |
| Bedrock 认证或权限错误 | Token 是否过期、程序区域、模型 ID、账号权限 |
| 数据库连接失败 | Docker 是否启动、5432 端口、`DATABASE_URL` |
| 表不存在 | 是否运行 `python -m scripts.migrate` |
| RAG 结果不相关 | 文档是否入库、检索条件、切块内容、查询措辞 |
| Memory 为空 | 是否真正调用保存工具、当前 `USER_ID` 是否一致 |
| JSON 验证失败 | 格式化节点原始输出是否为字符串及有效 JSON、字段是否完整 |
| MCP 失败 | 本地 Server 路径、依赖、参数和支持的货币对 |
| LangSmith 无 Trace | 配置是否加载、密钥和项目、网络、是否真正发起调用 |
| API 根路径 404 | 使用 `/docs`、`/health` 或 `/chat` |
| Terraform Provider 下载失败 | Registry 网络、代理、初始化是否完成 |
| RDS 容量不足 | 区域与规格，修改配置后重新检查计划 |

当前 Terraform 变量名确实是 `db_instalce_class`，虽然拼写有误，命令仍需与代码一致。例如调整规格后生成计划：

```powershell
terraform plan -var="db_instalce_class=db.t3.micro" -out retry.tfplan
```

是否采用该规格，应根据区域可用性和项目要求判断。部分部署成功时，先查看 `terraform state list` 与 `terraform output`，保留状态文件。

Git 出现改动时先看：

```powershell
git status --short --branch
git diff
```

区分自己的修改、老师更新和生成文件，再决定如何同步。

## 28. 补课优先级与学习记录

**第一轮重点：** Step 2 → 3 → 4 → 6 → 7 → 8 → 9 → 11 → 12 → 13 → 16。先完成“模型调用、知识库、工具选择、固定输出”的主线。

**第二轮深化：** Step 10 → 14 → 15 → 17 → 18。学习检索优化、记忆、MCP、评估和追踪。

**第三轮工程化：** Step 19 → 20 → 21。学习验证重试、执行限制和部署。Step 1 按环境需要补，Step 5 用于理解角色协作。

每次练习记录以下内容：

| 项目 | 要记录什么 |
|---|---|
| 当前 Step / 分支 | 避免把不同阶段代码混在一起 |
| 新增能力 | 一句话说明这一步解决什么问题 |
| 执行流程 | 输入 → 主要处理 → 输出 |
| 修改内容 | 今天改了哪个问题、参数或文档 |
| 验证结果 | 实际输出是否符合预期，有什么证据 |
| 未解决问题 | 卡在哪个文件、哪条错误或哪个概念 |

学完一轮后，应能自己解释：问题怎样进入 Agent，模型为什么选择某个工具，工具从哪里得到数据，结果如何回到模型，以及最终 API 如何返回答案。
