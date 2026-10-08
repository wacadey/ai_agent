# AI Agent 课程中文学习总览

> 本文件综合项目中的 `readme.MD`、`md/step1.md` 到 `md/step21.md` 和相关数据说明，提供中文翻译、代码关系、测试方法与排错指南。原始 Markdown 文件保持不变。

## 一、项目最终要完成什么

项目从一次最简单的 LLM 调用开始，逐步构建一个能够使用企业知识、查询业务数据库、调用外部工具、保存用户记忆、验证结果，并部署到云端的 Agent 服务。

整体路线：

```text
LLM API
  → Prompt 工程
  → LangChain Chain
  → 多 Agent 协作
  → Embedding
  → PostgreSQL + pgvector
  → 文档切分与入库
  → RAG
  → SQL/RAG/MCP Tools
  → LangGraph Agent
  → Memory
  → 结构化输出
  → 检索评估
  → LangSmith 观测
  → Agent Loop
  → Harness 护栏
  → FastAPI
  → Docker、Terraform、AWS
```

最终请求流程：

```text
用户问题
  ↓
LLM 判断是否需要工具
  ↓
Harness 检查权限、次数、时间
  ↓
SQL / RAG / Memory / MCP Tool
  ↓
LangGraph 继续推理
  ↓
结构化答案
  ↓
FastAPI /chat 返回 JSON
```

---

## 二、环境准备

### Python 虚拟环境

```powershell
python -m venv agent
.\\agent\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -c "import sys; print(sys.executable)"
```

路径应包含 `ai_agent\\agent\\Scripts\\python.exe`。如果虚拟环境指向不存在的 Python，需要用本机真实解释器重新创建；VS Code Python 插件不等于 Python 本体。

### AWS 和 .env

`.env` 保存本地配置，不应提交到 Git。典型值包括：

```text
AWS_REGION=us-east-1
BEDROCK_CHAT_MODEL=us.anthropic.claude-sonnet-5
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
DATABASE_URL=postgresql://agent:agent@localhost:5432/agentlab
USER_ID=de-ai-12
```

`.env` 会覆盖 `app/config.py` 的默认值，所以老师代码中的默认 `de-ai-25` 或 `de-ai-30` 不会强制替换本地 ID。

区域检查：

```powershell
aws configure get region
aws configure set region us-east-1
```

不要把长期密钥、Bearer Token、API Key 或完整 `.env` 写入学习文件。

---

## 三、Step 1：项目骨架和环境检查

目标是建立：

- `app/`：可复用的正式代码。
- `steps/`：每一步的实验入口。
- `scripts/`：迁移和诊断工具。
- `md/`：步骤说明。

运行：

```powershell
python -m steps.step1_check
```

这一步只确认 Python、Git、Docker、AWS CLI 是否可用。每个 Step 都能通过 `python -m steps.模块名` 独立运行，便于逐步理解。

---

## 四、Step 2：直接调用 AWS Bedrock

流程是：

```text
AWS 认证 → Bedrock Runtime Client → 发送 Prompt → 接收并解析响应
```

重点文件：

- `app/bedrock.py`：创建 Bedrock Runtime Client。
- `app/config.py`：统一读取区域和模型。
- `steps/step2_bedrock_llm_call.py`：调用测试。

运行：

```powershell
python -m steps.step2_bedrock_llm_call
```

这时只是“让模型回答”，还不是完整 Agent。Agent 还需要工具、状态、记忆和循环。

Agent 的五项能力是：感知、推理、行动、记忆、迭代。

---

## 五、Step 3：Prompt Engineering

Prompt 的四个基本部分：

- **Role**：模型扮演什么角色。
- **Context**：模型必须知道的背景。
- **Task**：要完成的任务。
- **Constraints**：格式、范围、语气和限制。

重点文件是 `app/prompts.py` 和 `steps/step3_prompt_engineering.py`。

```powershell
python -m steps.step3_prompt_engineering
```

Prompt 是应用的核心资产，应集中管理，不要把业务规则散落在多个测试文件中。必要时加入 Few-shot 示例，帮助模型理解期望格式。

---

## 六、Step 4：LangChain 和 LCEL Chain

把固定流程组合成：

```text
输入字典 → Prompt → ChatMessage → LLM → AIMessage → Parser → 字符串
```

重点文件：`app/llm.py`、`steps/step4_langchain_basic.py`。

```powershell
python -m steps.step4_langchain_basic
```

LCEL 使用 `|` 连接 Runnable：

```python
chain = prompt | model | output_parser
```

常见接口：

- `invoke()`：同步执行。
- `ainvoke()`：异步执行。
- `stream()`：流式输出。
- `batch()`：批量执行。

Chain 是固定管线，Agent 则会根据问题决定下一步行动。

---

## 七、Step 5：A2A / 多 Agent 协作

把多个职责不同的 Chain 组织成顺序协作：

```text
新手开发 Agent → 专业 Review Agent → 反馈修改 Agent → 最终代码
```

运行：

```powershell
python -m steps.step5_a2a_basic
```

示例会让 Agent 编写保存密码的函数，再由 Review Agent 检查：

- 数据库连接是否关闭，避免泄漏。
- 异常类型是否过于宽泛。
- 服务代码是否使用 logging。
- bcrypt 的 72 字节限制。
- 是否把密码或哈希写入日志。
- 表初始化是否应该只在应用启动时进行。

多 Agent 的重点是职责、输入、输出和协作顺序清晰，而不是 Agent 数量越多越好。

---

## 八、Step 6：Embedding 向量化

Embedding 把文本转换为向量，使文本能够进行数值相似度比较。项目使用：

```text
amazon.titan-embed-text-v2:0
```

重点文件：`app/embedding.py`、`steps/step6_embedding_basic.py`。

```powershell
python -m steps.step6_embedding_basic
```

通常会看到向量维度（项目中为 1024）和余弦相似度分数。相似度高代表模型认为文本接近，但不等于事实正确；模型、领域词汇、文本长度和切分方式都会影响结果。

---

## 九、Step 7：PostgreSQL + pgvector

让 PostgreSQL 同时保存关系数据和向量：

```powershell
docker compose up -d
python -m scripts.migrate
docker exec -it agent-postgres psql -U agent -d agentlab
```

在 psql 中：

```sql
\\dt
\\d demo_vectors
select * from demo_vectors;
```

运行向量测试：

```powershell
python -m steps.step7_pgvector
```

`sql/migrations/001_pgvector.sql` 创建扩展和基础向量表。`schema_migrations` 记录已执行 Migration，避免重复执行。

---

## 十、Step 8：文档入库和基础 Chunking

流程：

```text
Markdown
  → 读取 Metadata
  → 切成 Chunk
  → 每个 Chunk 生成 Embedding
  → 写入 documents 和 document_chunks
```

重点文件：

- `app/ingestion/loader.py`：读取文档和 Metadata。
- `app/ingestion/splitter.py`：文本切分。
- `app/ingestion/ingest.py`：入库。
- `sql/migrations/002_documents.sql`：表结构。
- `steps/step8_document_ingestion.py`：测试。

运行：

```powershell
python -m scripts.migrate
python -m steps.step8_document_ingestion
```

数据在 `data/` 和 `data_short/`，包括 CS、HR、Sales 政策。这些是仓库提供的课程测试数据，不是每次随机生成的。

常见切分方式：

| 方式 | 思路 | 适合 |
|---|---|---|
| Fixed-size | 按字符或 Token 数 | 基础实验 |
| Recursive | 段落→句子→字符 | 通用 RAG |
| Sentence | 按句子 | FAQ |
| Structure-based | 按标题和 Markdown | 企业制度 |
| Semantic | 语义变化处切分 | 高级 RAG |
| Parent-Child | 小块搜索、大块回答 | 长文档 |
| Agentic | 让 Agent 动态切分 | 高级实验 |

---

## 十一、Step 9：基础 RAG

RAG 是 Retrieval-Augmented Generation（检索增强生成）：

```text
问题 → 向量搜索 → 取相关 Chunk → 与问题组合 → LLM 根据证据回答
```

重点文件：

- `app/retrieval.py`：向量搜索 Top-K。
- `app/rag.py`：搜索、Prompt 和 LLM 的连接。
- `steps/step9_rag_basic.py`：测试。

```powershell
python -m steps.step9_rag_basic
```

对 Agent 来说，RAG 是一种 Tool。问题有知识库依据时应给出来源；没有依据时应说明“没有相关文档”，不能编造答案。

---

## 十二、Step 10：高级 RAG

高级 RAG 增加：

- 语义切分。
- Metadata 过滤。
- 向量 + 关键词 Hybrid Search。
- 可调的混合权重。

语义切分流程：

```text
句子/小段 → Embedding → 相邻相似度 → 低于阈值处切断 → 语义完整 Chunk
```

重点文件：升级后的 `splitter.py`、`ingest.py`、`retrieval.py`，以及 `steps/step10_rag_advanced.py`。

```powershell
python -m steps.step10_rag_advanced
python -m steps.step8_document_ingestion
```

阈值不是永远正确的常量，会受到模型、原文结构、查询类型和成本影响，应通过 Step 17 评估调整。

---

## 十三、Step 11：LangChain Tools

把外部能力包装为 Agent 可以调用的工具：

- `sql_tools.py\)：产品、订单、销售、退款查询。
- `rag_tools.py\)：公司政策搜索。
- 后续可连接 MCP：Notion、Slack、外部软件等。

业务数据由 `sql/migrations/003_business.sql` 提供。运行：

```powershell
python -m scripts.migrate
python -m steps.step11_tools
```

工具的意义是把模型无法凭空知道的实时业务数据变成可调用能力。销售、订单和政策示例数据都来自 SQL 或文档，而不是模型记忆。

---

## 十四、Step 12：LangGraph Agent

LangGraph 将模型和工具组织成有状态循环：

```text
Agent → 判断是否需要工具 → ToolNode → 工具结果 → Agent → 结束或继续
```

核心概念：

- **StateGraph**：定义图。
- **Node**：Agent、ToolNode、格式化节点。
- **Edge**：固定方向。
- **Conditional Edge**：根据消息决定下一节点。
- **MessagesState**：按顺序保存消息。

重点文件：`app/agent/graph.py`、`prompts.py`、`state.py`、`app/main.py`。

```powershell
python -m steps.step12_langgraph_agent
```

重点观察：

```text
HumanMessage → AIMessage（tool call）→ ToolMessage → AIMessage（最终答案）
```

这一步标志着系统从“直接回答”进入“自主决定是否使用工具”。

---

## 十五、Step 13：退款业务 SQL

`sql/migrations/004_refunds.sql` 创建退款表和示例记录，字段包括订单、时间、原因、金额和状态。

```powershell
python -m scripts.migrate
docker exec agent-postgres psql -U agent -d agentlab -c "SELECT refund_id, order_id, requested_at, reason, amount, status FROM refunds;"
```

课程示例中的产品缺陷退款是 Migration 明确写入的测试数据，不是随机生成的。

---

## 十六、Step 14：Memory 表

Memory 用于保存用户偏好、背景和重要历史信息。

重点文件：

- `sql/migrations/005_memory.sql`：`agent_memories`。
- `app/tools/memory_tools.py`：保存和召回。
- `app/agent/state.py`：状态字段。

```powershell
python -m scripts.migrate
docker exec agent-postgres psql -U agent -d agentlab -c "\\d agent_memories"
docker exec agent-postgres psql -U agent -d agentlab -c "SELECT id, user_id, memory_type, content, importance FROM agent_memories;"
```

核心字段：

- `user_id`
- `memory_type`
- `content`
- `embedding`
- `importance`
- `created_at`
- `last_accessed_at`

表为空只代表还没有保存记忆，不代表表坏了。用户 ID 由本地 `.env` 覆盖默认值。

---

## 十七、Step 15：记忆工具

Memory 变成 Agent 可以自主调用的工具：

```text
Agent 判断是否值得记住 → remember_user_preference → 保存
Agent 判断是否需要回忆 → recall_user_memory → 相似度检索
```

记忆不是把全部聊天记录无条件塞回 Prompt，而是根据用户、类型、重要性和相似度选择性读取。测试时观察工具名、user_id、数据库新增记录，以及下一次问题是否能召回内容。

---

## 十八、Step 16：结构化输出

统一返回：

```json
{
  "answer": "最终回答",
  "sources": ["CS-REFUND-2026"],
  "tools_used": ["search_company_policy"],
  "confidence": 0.9
}
```

重点文件：`app/output.py`、`app/agent/graph.py`、`steps/step16_structured_output.py`。

```powershell
python -m steps.step16_structured_output
```

结构化输出让 API、前端、评估和监控都能可靠读取字段。模型版本对结构化 API 支持可能不同，因此项目可能使用额外格式化步骤来保证符合 Pydantic 模型。

---

## 十九、Step 17：检索评估

不要凭感觉判断 RAG 好不好，要用固定问题、期望文档和指标重复测量。

重点文件：

- `app/evaluation/dataset.py`：测试问题和期望文档。
- `app/evaluation/retrieval_eval.py`：评估逻辑。
- `steps/step17_evaluation.py`：入口。

```powershell
python -m steps.step17_evaluation
```

指标：

| 指标 | 问题 |
|---|---|
| HitRate@K | Top-K 中有没有正确文档？ |
| MRR | 第一个正确文档排第几？ |
| Precision@K | 找到的有多少真正相关？ |
| Recall@K | 相关文档找回了多少？ |
| NDCG@K | 高相关文档是否靠前？ |
| MAP | 多个相关文档的排序整体如何？ |

后续还要评估 Faithfulness、Answer Relevance、Latency、Token 和 Cost。小数据集达到 1.0 不代表生产系统一定可靠。

---

## 二十、Step 18：LangSmith 观测

LangSmith 用于追踪 Prompt、模型、工具、耗时和结果。

```text
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=你的密钥
LANGSMITH_PROJECT=ai-agent
```

重点文件：`app/observability.py`、`steps/step18_observability.py`。

```powershell
python -m steps.step18_observability
```

状态检查前应确保 `app.config` 已加载，这样 `.env` 才会被读取。最终还要登录 LangSmith 项目确认 Trace，而不能只看本地配置字符串。

---

## 二十一、Step 19：Agentic Loop

普通 Agent：

```text
问题 → 工具 → 答案
```

Agentic Loop：

```text
计划 → 执行 → 验证 → 反馈 → 重新计划 → 执行 → 验证
```

重点文件：`app/loop_engine.py`、`steps/step19_agent_loop.py`。

```powershell
python -m steps.step19_agent_loop
```

``max_attempts=2`` 控制整个循环最多两轮；``recursion_limit=18`` 限制每个子问题内部 LangGraph 的步骤数，防止工具调用死循环。

```text
[PLAN]
Q1...
[VERIFY] passed=False
[FEEDBACK]
[REPLAN]
```

失败反馈会交给下一轮 Planner。循环仍需有最终综合 Agent，否则可能出现子答案拼接、上下文没有复用、年份不一致或结果被截断等问题。超过上限时可以转人工。

---

## 二十二、Step 20：Harness 安全护栏

Harness 是包围 Agent 的政策层，不是 Prompt。Prompt 说明“应该做什么”，Harness 决定“最多能做什么”。

```text
Agent 判断调用工具
  → Harness 检查权限、次数、时间
  → ToolNode
  → Agent
```

重点文件：

- `app/harness.py`：`ALLOWED_TOOLS`、`Limits`、`Budget`、`assert_allowed_tool()`。
- `app/agent/state.py`：`tool_rounds`、`start_at`。
- `app/agent/graph.py`：`harness` 节点。
- `steps/step20_harness_guardrail.py`：测试。

默认限制通常是最多 6 个工具轮次、最多 120 秒。运行：

```powershell
python -m steps.step20_harness_guardrail
```

看到 `하네스 체크 통과` 表示检查通过；未授权工具会抛出 `PermissionError`，超出次数或时间会抛出 `RuntimeError`。

---

## 二十三、Step 21：FastAPI、Docker 和 AWS

### 1. 本地 FastAPI

重点文件：

- `app/main.py`：公共 `invoke_agent()`。
- `app/service.py`：FastAPI、`/chat`、`/health`。
- `steps/step21_agent_service.py`：Uvicorn 入口。

启动：

```powershell
python -m steps.step21_agent_service
```

打开：

```text
http://localhost:8000/docs
```

接口：

- `GET /health`：`{"status":"ok"}`。
- `POST /chat`：请求 `{"message":"问题"}`，返回结构化答案。

文档中的 `/heath` 是拼写错误，实际是 `/health`。访问根路径 `/` 返回 404 是正常的，因为没有定义根路由。

### 2. Docker

`Dockerfile` 将 Python、FastAPI、Agent 和依赖打包成镜像。`docker-compose.yml` 启动 PostgreSQL 和 Agent 服务。

容器内数据库地址应使用 Compose 服务名，而不是 localhost：

```text
postgresql://agent:agent@postgres:5432/agentlab
```

启动：

```powershell
docker compose up --build
```

### 3. Terraform 基础设施

进入：

```powershell
cd infra\\terraform
```

通常顺序：

```powershell
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

文件职责：

- `versions.tf`：Terraform 和 Provider 版本。
- `provider.tf`：AWS Provider 与区域。
- `variables.tf`：项目、区域、实例规格、数据库、模型等变量。
- `network.tf`：VPC、两个公共子网、路由表、IGW。
- `security.tf`：EC2/RDS 安全组。
- `rds.tf`：RDS、随机密码、SSM 数据库 URL。
- `deploy.tf`：项目 ZIP 和私有 S3。
- `iam.tf`：EC2 Role 和权限。
- `ec2.tf`：Amazon Linux 2023、User Data、Agent EC2。
- `outputs.tf`：API、健康检查、RDS 和 SSM 输出。
- `infra/scripts/bootstrap.sh/.bat`：安装 Docker、下载代码、Migration、入库、启动服务。

云端流程：

```text
Terraform 创建 VPC/RDS/S3/IAM/EC2
  → ZIP 上传私有 S3
  → EC2 下载代码
  → 从 SSM 读取数据库 URL
  → 构造 .env
  → Docker build
  → SQL Migration 和文档入库
  → 启动 Agent
  → /health 检查
```

RDS 实例容量可能因区域而失败，例如：

```text
InsufficientDBInstanceCapacity
```

这表示当前区域没有某种规格的可用容量，不一定是代码错误。可先用另一个规格生成新计划：

```powershell
terraform plan -var="db_instalce_class=db.t3.micro" -out step21-t3.tfplan
terraform apply step21-t3.tfplan
```

每次 apply 前必须检查 `add/change/destroy`。RDS、EC2 会产生费用。

---

## 二十四、数据库 Migration

Migration 是按版本执行的数据库变更，不是随机数据生成器：

```text
001_pgvector.sql  → pgvector 和向量表
002_documents.sql → 文档和 Chunk 表
003_business.sql  → 产品、订单、业务示例
004_refunds.sql   → 退款表和示例退款
005_memory.sql    → Agent 记忆表和向量索引
```

运行：

```powershell
python -m scripts.migrate
docker exec agent-postgres psql -U agent -d agentlab -c "SELECT * FROM schema_migrations ORDER BY version;"
```

Migration 的意义是让开发、测试和生产环境按同样顺序获得同样的数据库结构。课程数据是为了测试 Agent 的固定样例。

---

## 二十五、建议学习顺序

1. Step 1：确认环境。
2. Step 2：成功调用 Bedrock。
3. Step 3：理解 Prompt。
4. Step 4：理解 Chain 和 LCEL。
5. Step 5：理解多 Agent 协作。
6. Step 6：理解 Embedding。
7. Step 7：理解 pgvector。
8. Step 8：文档切分和入库。
9. Step 9：基础 RAG。
10. Step 10：语义切分和混合搜索。
11. Step 11：SQL/RAG Tools。
12. Step 12：LangGraph Agent。
13. Step 13：退款业务数据。
14. Step 14–15：Memory。
15. Step 16：结构化输出。
16. Step 17：检索评估。
17. Step 18：运行追踪。
18. Step 19：计划、验证、重试。
19. Step 20：权限、预算、时间护栏。
20. Step 21：服务化、容器化和云部署。

每一步都回答四个问题：

1. 新增了什么能力？
2. 哪个文件负责？
3. 上一步输出如何成为这一步输入？
4. 测试输出如何证明成功？

---

## 二十六、常见问题

### FastAPI 找不到

```text
ModuleNotFoundError: No module named 'fastapi'
```

检查虚拟环境并安装：

```powershell
.\\agent\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

### FastAPI 返回 404

- `/` 没有定义，404 正常。
- 文档是 `/docs`。
- 健康接口是 `/health`，不是 `/heath`。

### Terraform Provider 下载失败

先处理 Terraform Registry 的网络、代理或防火墙。Provider 没装好时，`validate` 也可能无法完整执行。

### RDS 容量失败

先生成新计划，不要直接反复 apply：

```powershell
terraform plan -var="db_instalce_class=db.t3.micro" -out retry.tfplan
terraform apply retry.tfplan
```

### Terraform 部分成功

查看状态：

```powershell
terraform state list
terraform output
```

不要删除 `.tfstate`，也不要未经确认执行 `terraform destroy`。

### RAG 没有找到文档

按顺序检查：PostgreSQL 是否运行、Migration 是否完成、`documents/document_chunks` 是否有数据、Embedding 区域和模型是否正确、Metadata 筛选是否匹配。

### Git 同步出现 Changes

```powershell
git status --short --branch
git diff
```

不要用 `reset --hard` 覆盖 `.env`、配置或 Terraform 计划文件。需要同步老师分支时，应暂存特定 tracked 配置，快进后恢复并解决冲突。

---

## 二十七、整体结论

这个项目不是把很多库简单堆在一起，而是在逐层解决 Agent 工程问题：

- LLM：语言理解和推理。
- Prompt：任务规则和输出要求。
- Chain：固定处理管线。
- Tools：访问实时数据和外部服务。
- RAG：基于企业知识回答。
- Memory：保持用户上下文。
- LangGraph：状态、节点和循环。
- Structured Output：稳定的程序接口。
- Evaluation：量化搜索质量。
- LangSmith：观察运行过程。
- Agent Loop：验证失败后重新规划。
- Harness：限制权限、时间和成本。
- FastAPI/Docker/Terraform：服务化、容器化和云端部署。

最终的 Agent 不是“会聊天的模型”，而是一个有知识来源、有工具权限、有状态、有评估、有日志、有安全边界、可以部署和维护的软件系统。

