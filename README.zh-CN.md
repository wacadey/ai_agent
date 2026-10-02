# AI Agent 中文学习路线

本文件是老师原始 readme.MD 的中文学习说明。原始 README 保持不修改，本文件专门解释课程知识点、学习顺序和常用命令。

## 一、整体目标

本课程从基础 LLM 呼叫开始，逐步构建能够搜索知识、查询业务数据、自动选择工具、记住用户偏好、连接外部服务、输出结构化结果并监控运行过程的企业级 AI Agent。

核心组件的分工：

- LLM：理解问题、推理并生成回答。
- RAG：搜索公司文件、政策和知识。
- Database：保存订单、销售、退款等事实数据。
- Tools：把 SQL、RAG、Memory 和外部服务提供给 Agent。
- LangGraph：组织 Agent 的节点、条件和循环。
- MCP：按照统一协议连接外部工具和服务。
- LangSmith：记录和监控 Agent 的执行过程。

## 二、Step 1～18 学习路线

| Step | 知识点 | 作用 |
|---|---|---|
| 1 | Python 基础 | 学习模块、虚拟环境和命令行执行 |
| 2 | Bedrock LLM | 使用 AWS Bedrock 调用聊天模型 |
| 3 | Prompt Engineering | 通过提示词约束模型行为 |
| 4 | LangChain | 管理模型、消息和工具 |
| 5 | A2A | 理解 Agent 之间的协作 |
| 6 | Embedding | 把文字转换成向量 |
| 7 | PostgreSQL + pgvector | 保存和搜索向量 |
| 8 | 文件导入 | 切分文件并写入向量数据库 |
| 9 | 基础 RAG | 根据问题搜索相关文件并回答 |
| 10 | 进阶 RAG | 使用混合搜索和过滤提升检索质量 |
| 11 | Tools | 将 SQL 和 RAG 包装成 Agent 工具 |
| 12 | LangGraph Agent | 让 AI 自动选择和循环调用工具 |
| 13 | SQL + RAG Agent | 同时使用结构化和非结构化数据 |
| 14 | Memory | 保存并找回用户长期偏好 |
| 15 | MCP | 通过标准协议连接外部服务 |
| 16 | Structured Output | 按固定结构生成最终结果 |
| 17 | Evaluation | 用 HitRate、MRR 等指标评估 RAG |
| 18 | Observability | 用 LangSmith 追踪 Agent 运行状态 |

整体路线：

~~~text
LLM → RAG → Tools → LangGraph → Memory → MCP
    → Structured Output → Evaluation → Observability
~~~

## 三、环境建立

Windows PowerShell：

~~~powershell
python -m venv agent
.\agent\Scripts\Activate.ps1
pip install -r requirements.txt
~~~

如果终端前面出现 (agent)，表示虚拟环境已启用。

Docker PostgreSQL：

~~~powershell
docker compose up -d
docker ps --filter "name=agent-postgres"
python -m scripts.migrate
~~~

容器应显示 healthy。

## 四、Bedrock 和环境变量

老师示范使用 Amazon Bedrock。学习环境可以使用 Bedrock API Key；正式环境建议使用短期凭证或 IAM Role。

本地 .env 可以包含：

~~~env
AWS_REGION=us-east-1
AWS_BEARER_TOKEN_BEDROCK=你的_Bedrock_Key
BEDROCK_CHAT_MODEL=us.anthropic.claude-sonnet-5
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
DATABASE_URL=postgresql://agent:agent@localhost:5432/agentlab
USER_ID=de-ai-12
~~~

.env 已被 .gitignore 忽略，不要把真实 Key、密码或 Token 提交到 GitHub。

## 五、数据库和数据类型

主要表：

- documents、document_chunks：RAG 文件和文本片段。
- products、orders：商品和订单。
- refunds：退款数据。
- agent_memories：用户长期记忆。

数据类型的选择：

- 业务数字和订单事实放在 PostgreSQL。
- 公司政策和文档片段放在 RAG。
- 用户偏好保存为 Memory。
- 文本向量使用 pgvector。

## 六、Agent 的执行逻辑

LangGraph 的基本流程：

~~~text
START
  ↓
Agent 判断是否需要工具
  ├─ 不需要工具 → END
  └─ 需要工具 → ToolNode → Agent 再判断
~~~

Agent 会根据问题选择：

- 销售或退款数字：SQL Tool。
- 公司政策：RAG Tool。
- 用户偏好：Memory Tool。
- 外部服务：MCP Tool。

## 七、MCP 的执行逻辑

~~~text
Agent Host
  ↓
MCP Client
  ↓
MCP Server
  ↓
外部 API 或服务
~~~

当前示例是汇率 MCP。exchange_server.py 提供 get_exchange_rate，mcp_tools.py 将它包装成 LangChain Tool。当前汇率是测试数据，不是实时汇率。

## 八、评估和监控

Step 17 使用固定问题检查 RAG：

- HitRate@K：前 K 个结果中是否找到正确文件。
- MRR：正确文件是否排在靠前位置。

运行：

~~~powershell
python -m steps.step17_evaluation
~~~

Step 18 使用 LangSmith 观察：

- LLM 调用；
- Tool 调用；
- LangGraph 节点；
- Token；
- 延迟；
- 错误；
- 最终输出。

.env 需要配置：

~~~env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=你的_LangSmith_Key
LANGSMITH_PROJECT=ai-agent
~~~

运行：

~~~powershell
python -m steps.step18_observability
~~~

然后在 LangSmith 的 Tracing → ai-agent 项目查看 Trace。

## 九、推荐的代码学习顺序

每个 Step 都按下面顺序学习：

1. 阅读 md/stepN.md。
2. 找到 steps/stepN_*.py 测试入口。
3. 追踪到 app/main.py。
4. 阅读 app/agent/graph.py。
5. 查看 app/tools/ 中实际调用的工具。
6. 查看 database、retrieval 或 SQL migration。
7. 执行命令并根据输出验证结果。
8. 修改一个问题重新测试，测试后恢复文件。

常见代码阅读路径：

~~~text
steps/
→ app/main.py
→ app/agent/graph.py
→ app/tools/
→ app/retrieval.py 或 app/database.py
→ PostgreSQL
~~~

## 十、课程完成后的扩展

老师原 README 列出的后续方向：

- Agent Loop：验证结果、失败重试和停止条件。
- Harness Engineering：工具权限、执行预算、Prompt Injection 防护和测试隔离。
- 云端部署：使用 Terraform 建立基础设施。
- 将 PostgreSQL 迁移到 RDS。
- 将 Agent 和 MCP Server 部署为云端服务。
- 生产环境使用短期凭证、IAM Role、最小权限和密钥轮换。

