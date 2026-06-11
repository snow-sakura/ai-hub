"""AI Testing 用例生成 - 4 步 Prompt 模板"""

from langchain_core.prompts import ChatPromptTemplate

# ─── Step 1: 需求分析 ─────────────────────────────────────────────────────────
ANALYZE_SYSTEM = """\
你是一名资深软件 QA 架构师，擅长从需求文档中提取测试要点。
你的分析需要全面、细致，不遗漏任何边界情况和异常场景。"""

ANALYZE_PROMPT = """\
请对以下需求进行深入分析，提取关键功能点、边界条件和异常场景。

{project_context}

## 需求内容
{requirement_text}

请按以下结构输出分析报告：

### 1. 功能点分解
（列出所有核心功能点，每个功能点用一句话描述其测试要点）

### 2. 边界条件
（列出边界值、极端输入、并发场景、性能边界等）

### 3. 异常场景
（列出可能的异常情况：网络故障、数据不一致、权限问题、超时等）

### 4. 前置依赖
（列出测试所需的环境、数据、账号等前置条件）

### 5. 测试范围建议
（建议的用例数量和优先级分布，例如：P0×3, P1×5, P2×8）"""

analyze_prompt = ChatPromptTemplate.from_messages([
  ("system", ANALYZE_SYSTEM),
  ("human", ANALYZE_PROMPT),
])

# ─── Step 2: 用例编写 ─────────────────────────────────────────────────────────
WRITE_SYSTEM = """\
你是一名资深测试工程师，擅长编写高质量、结构清晰的测试用例。
每条用例必须具备完整的可执行性——任何测试人员拿到用例后都能直接执行。"""

WRITE_PROMPT = """\
基于以下需求分析结果，编写测试用例。

{project_context}

## 需求原文
{requirement_text}

## 需求分析
{analysis_result}

请编写测试用例，每条用例严格按以下格式输出：

---
**用例 ID**: TC-001
**标题**: [简洁描述测试目的]
**优先级**: P0 / P1 / P2 / P3
**用例类型**: functional / boundary / exception / performance / security
**前置条件**: [执行前必须满足的条件，多条用分号分隔]
**测试步骤**:
1. [步骤 1]
2. [步骤 2]
3. ...
**预期结果**: [可验证的预期输出或系统行为，多条用分号分隔]
**标签**: [tag1, tag2]
---

要求：
1. 覆盖分析中识别的所有功能点、边界条件和异常场景
2. 优先级分布合理：P0 覆盖核心路径，P1 覆盖重要功能，P2 覆盖边界，P3 覆盖低概率场景
3. 每条用例独立可执行，不依赖其他用例的执行结果
4. 步骤描述使用祈使句，具体到可操作
5. 预期结果必须可验证，避免模糊描述"""

write_prompt = ChatPromptTemplate.from_messages([
  ("system", WRITE_SYSTEM),
  ("human", WRITE_PROMPT),
])

# ─── Step 3: AI 评审 ──────────────────────────────────────────────────────────
REVIEW_SYSTEM = """\
你是一名独立的测试评审专家，负责对测试用例进行质量评审。
评审必须客观、有建设性，给出具体的改进建议而非笼统意见。"""

REVIEW_PROMPT = """\
请对以下测试用例进行专业评审，给出评分和改进建议。

## 原始需求
{requirement_text}

## 测试用例
{test_cases}

请严格按以下 JSON 格式输出（不要输出其他内容）：
```json
{{
  "overall_score": 8,
  "review_passed": false,
  "dimensions": {{
    "coverage": {{"score": 8, "comment": "功能点覆盖率"}},
    "completeness": {{"score": 8, "comment": "用例完整性"}},
    "accuracy": {{"score": 8, "comment": "步骤与预期结果准确性"}},
    "priority": {{"score": 8, "comment": "优先级分配合理性"}},
    "edge_cases": {{"score": 7, "comment": "边界与异常覆盖"}},
    "clarity": {{"score": 8, "comment": "表达清晰度"}},
    "maintainability": {{"score": 8, "comment": "可维护性"}}
  }},
  "issues": [
    {{"severity": "critical|major|minor", "description": "问题描述", "affected_cases": ["TC-001"]}}
  ],
  "improvement_suggestions": ["具体改进建议1", "具体改进建议2"],
  "summary": "整体评审总结（1-2 句话）"
}}
```

评审标准（每项 1-10 分）：
- coverage: 是否覆盖分析中的所有功能点、边界、异常
- completeness: 每条用例是否包含完整的前置条件、步骤、预期结果
- accuracy: 步骤是否可操作，预期结果是否可验证
- priority: P0 是否对应核心路径，P3 是否对应低概率场景
- edge_cases: 是否包含边界值和异常场景用例
- clarity: 描述是否清晰无歧义
- maintainability: 用例是否独立、不耦合

**passed 判定规则**: overall_score >= 7 且没有 severity=critical 的 issue"""

review_prompt = ChatPromptTemplate.from_messages([
  ("system", REVIEW_SYSTEM),
  ("human", REVIEW_PROMPT),
])

# ─── Step 4: 用例修订 ─────────────────────────────────────────────────────────
REVISE_SYSTEM = """\
你是一名资深测试工程师，擅长根据评审反馈精准修订测试用例。
修订必须逐条回应评审意见，不能忽略任何 critical 或 major 问题。"""

REVISE_PROMPT = """\
请根据评审反馈修订以下测试用例。

## 原始需求
{requirement_text}

## 当前测试用例
{test_cases}

## 评审结果
- 综合评分: {review_score}/10
- 问题列表:
{issues}
- 改进建议:
{suggestions}

修订要求：
1. 逐条回应评审中发现的所有问题（特别是 critical 和 major 级别）
2. 采纳合理的改进建议
3. 保持与原始用例相同的格式（--- 分隔，字段结构不变）
4. 如有新增用例，续接编号（TC-xxx）
5. 在每条修订用例末尾添加一行：**修订说明**: [简述修改原因]
6. 不要删除原有用例，只能修改或新增"""

revise_prompt = ChatPromptTemplate.from_messages([
  ("system", REVISE_SYSTEM),
  ("human", REVISE_PROMPT),
])
