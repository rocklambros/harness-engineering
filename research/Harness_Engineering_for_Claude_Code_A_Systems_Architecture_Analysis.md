```yaml
---
sage_version: "1.0"
document_type: "whitepaper"
document_id: "ROCKCYBER-2026-WP-001"
title: "Harness Engineering for Claude Code: A Systems Architecture Analysis"
version: "0.1"
status: "draft"
date: "2026-05-07"
authors:
  - "Rock Lambros"
  - "Claude (Anthropic)"
organization: "RockCyber"
content_domain:
  - "ai_security"
  - "application_security"
  - "agentic_systems"
keywords:
  - "harness engineering"
  - "Claude Code"
  - "agentic AI"
  - "agent scaffolding"
  - "tool use"
  - "context engineering"
  - "MCP"
  - "Claude Agent SDK"
  - "agent governance"
frameworks_referenced:
  - "OWASP_AGENTIC_TOP10"
  - "OWASP_LLM_TOP10"
  - "NIST_AI_RMF"
  - "MITRE_ATLAS"
  - "ISO_42001"
generation_metadata:
  authored_by: "human_ai_collaborative"
  model_id: "claude-opus-4-7"
  model_version: "claude-opus-4-7"
  human_review: "none"
  review_attestation: "Pending review by Rock Lambros (RockCyber). Document is foundational research notes for downstream dissertation chapter."
abstract_for_rag: "A systems-architecture analysis of harness engineering for Claude Code and the Claude Agent SDK. Defines a harness as the deterministic substrate (agent loop, tool pool, permission system, context pipeline, sandbox, MCP layer, subagent delegation, persistence) surrounding a stochastic language model. Anchors the analysis in Liu et al. (2026) source-level study of Claude Code v2.1.88, Anthropic engineering essays on building agents and harness design, and ten-plus practitioner harness repositories, with explicit attention to security, evaluation, and open research problems."
token_estimate: 24000
recommended_chunk_level: "h2"
content_hash: ""
---

# Harness Engineering for Claude Code: A Systems Architecture Analysis

## Abstract

This document treats Claude Code, the Claude Agent SDK, and the agent design patterns codified in Anthropic's engineering literature as a single empirical substrate for studying what we call harness engineering. A harness, in the agent sense, is the deterministic code that surrounds a stochastic language model and turns its outputs into safe, auditable actions in the world. The term is unsettled. We propose a working definition with an explicit Bayesian confidence rating, distinguish it from agent scaffolding, agentic runtime, agent framework, and the older eval harness lineage represented by EleutherAI's lm-evaluation-harness, and decompose the Claude Code harness into nine load-bearing components. We trace each component to primary-source evidence in the Liu et al. (2026) reverse-engineering study of Claude Code v2.1.88, Anthropic's "Building Effective Agents" (Schluntz and Zhang, 2024), "Harness Design for Long-Running Application Development" (Rajasekaran, 2026), "Scaling Managed Agents" (Martin, Cemaj, and Cohen, 2026), and the official Claude Code and Agent SDK documentation. We then survey five design tradeoffs, examine the methodological state of harness evaluation, devote a balanced section to security and governance with named CVEs and the deny-rule bypass class, and close with six open research problems and a set of practical recommendations for designing a personal harness. Empirical claims are tied to specific studies, dates, and conditions. Counterarguments are presented before they are answered.

## 1. Introduction and Scope

Anthropic shipped Claude Code as a developer-facing agentic coding tool. Liu, Zhao, Shang, and Shen [1] reverse-engineered version 2.1.88 of its TypeScript source and reported that approximately 1,900 files and 512,000 lines of code resolve into five architectural layers, twenty-one subsystems, fifty-four tools, seven permission modes, and a five-layer compaction pipeline. Their headline statistic is that roughly 1.6 percent of the codebase is AI decision logic and 98.4 percent is deterministic infrastructure, a community-estimated split that we treat with appropriate caution in Section 6. This finding, whatever its precise number, points at a real shift. As frontier models converge on similar baseline reasoning, the differentiator for autonomous system reliability is the engineering substrate around the model.

This document is a standalone systems-architecture chapter aimed at readers who design or audit Claude-based harnesses. It is not the security chapter of a longer agentic security arc. Security framing is one section among many. The empirical anchor is broad. We treat Claude Code, the Claude Agent SDK [2], the patterns documented in Schluntz and Zhang [3], the harness essay by Rajasekaran [4], the Managed Agents engineering post by Martin, Cemaj, and Cohen [5], the official Claude Code documentation [6], McCain et al. [7] on agent autonomy, Hughes [8] on the auto-mode classifier, and Anthropic's internal engineering survey [9] as a single body of evidence about how Anthropic and the surrounding practitioner community currently build harnesses for production-grade language-model agents.

OpenClaw is out of scope. Comparative grounding instead comes from widely-starred Claude Code configuration repositories including Affaan Mustafa's everything-claude-code [10], Jesse Vincent's Superpowers [11], the awesome-harness-engineering compilation [12], and the awesome-agent-harness list [13]. These appear as evidence of practitioner harness patterns, not as alternative architectures.

The document proceeds as follows. Section 2 fixes terminology. Section 3 places harness engineering in the context of ReAct, tool use, and eval harness lineages. Section 4 decomposes the Claude Code harness into nine components. Section 5 names five tradeoffs that recur across harness decisions. Section 6 surveys evaluation. Section 7 covers security and governance. Section 8 names six open problems. Section 9 closes with practical recommendations for a personal harness spanning Claude Code and the Agent SDK.

## 2. Definition and Conceptual Boundaries

### 2.1 Working definition

We propose the following working definition.

**A Claude harness is the deterministic software envelope that converts a language model's tokens into safe, observable, recoverable actions on a host system. It minimally comprises an agent loop that interleaves model calls and tool executions, a tool pool with permission gates, a context construction and management pipeline, a sandbox or execution environment, an extensibility surface, and a persistence layer.**

Bayesian confidence in the existence of a coherent referent for "harness engineering" as distinct from existing terms: roughly 0.7. The evidence supporting a positive rating is concrete. Anthropic publishes engineering essays under that title [4][5]. Liu et al. [1] use the word repeatedly to describe the Claude Code substrate. Multiple practitioner repositories [10][12][13] use "harness" to label what they ship. The evidence pulling the rating away from 1.0 is that no peer-reviewed academic paper has yet locked the term down, several adjacent terms describe overlapping concepts, and the word is also in active use in a different sense for benchmarking infrastructure such as EleutherAI's lm-evaluation-harness [14].

### 2.2 Distinction from adjacent terms

**Agent scaffolding** is the closest synonym. Yang et al. [15] introduced the agent-computer interface concept in SWE-Agent and showed that scaffolding choices, not model changes, drove a tripling of SWE-bench performance. Scaffolding usage in academic literature tends to emphasize the prompt and tool-interface design that lets a model take actions. Harness, in Anthropic's usage [4], emphasizes the runtime envelope including process orchestration, context resets, and multi-agent handoffs. The two overlap heavily. The distinction we propose is that scaffolding is the prompt-and-tool-interface subset, harness is the broader runtime envelope including persistence, sandboxing, and permission enforcement.

**Agentic runtime** appears in some practitioner writing and refers to the same artifact viewed as an execution environment rather than as a layer of code. We treat runtime and harness as near-synonyms with runtime emphasizing the platform-as-service aspect and harness emphasizing the engineered code envelope.

**Agent framework** refers to libraries such as LangChain, LangGraph, or AutoGen that provide reusable abstractions for building agents. Schluntz and Zhang [3] explicitly argue against heavy frameworks in favor of composable patterns built on direct API calls, on the grounds that framework abstractions make it harder to inspect what is happening at the prompt and token level. A harness can use a framework, can be a framework, or can be neither.

**Eval harness** is a separate lineage. EleutherAI's lm-evaluation-harness [14] is benchmarking infrastructure that runs a fixed set of tasks against a model under controlled prompts and metrics. It does not let the model take actions in the world. It runs the model. The shared word "harness" reflects a shared engineering aesthetic of a controlled wrapper around a model, not a shared technical artifact. Confusing the two is a common error in the literature and we flag it explicitly.

### 2.3 The strongest argument that harness engineering is redundant or premature

The strongest counterargument is that "harness engineering" is a marketing rebrand of agent scaffolding combined with the discipline of writing good tools and good system prompts, and that a separate label is premature. Anthropic itself blurs the terms across blog posts. Academic work continues to use "scaffolding" without loss of meaning. The risk of the term is concept inflation that obscures the underlying engineering moves.

The response is that the Liu et al. [1] decomposition shows the Claude Code substrate is structurally larger than what scaffolding traditionally describes, with seven permission modes, an ML-based prompt-injection classifier, a five-layer compaction pipeline, a subagent delegation system with worktree isolation, and an append-oriented session log. If the term scaffolding is stretched to cover all of that, a clarifying label is useful. We adopt harness while acknowledging that the boundary with scaffolding is graded, not sharp.

## 3. Related Work and Intellectual Lineage

### 3.1 Tool use and the ReAct lineage

The conceptual root is Yao et al. [16] on ReAct, which interleaves reasoning traces and actions in a single language-model loop and showed measurable gains on HotpotQA, Fever, ALFWorld, and WebShop. Schick et al. [17] on Toolformer extended this by training a model to call tools. Shinn et al. [18] on Reflexion added verbal self-reflection on failed trajectories. Madaan et al. [19] on Self-Refine added iterative self-feedback. Zhou et al. [20] on LATS integrated Monte Carlo Tree Search with reflection. Wu et al. [21] on AutoGen formalized multi-agent conversation patterns. The Liu et al. [1] description of the Claude Code while-loop as a ReAct generator is direct lineage.

### 3.2 Agent scaffolding research

Yang et al. [15] on SWE-Agent showed that custom agent-computer interfaces, not better models, tripled SWE-bench performance. The paper explicitly framed agents as a new category of end users that benefit from purpose-built interfaces. This is the point Rajasekaran [4] generalizes when he writes that every harness component encodes an assumption about what the model cannot do and that those assumptions go stale as models improve.

### 3.3 Eval harness lineage

EleutherAI's lm-evaluation-harness [14] is the de-facto standard benchmarking framework for language models and powers Hugging Face's Open LLM Leaderboard. It runs a model on a fixed task suite under controlled prompts. It is not an agent system. It does not interface with tools, files, shells, or external services. The shared word "harness" reflects the shared idea of a controlled wrapper around a model. The artifacts have nothing in common at the architectural level.

### 3.4 Operating-system framings

Karpathy's 2023 sketch of an "LLM OS" [22] proposed that the model is the CPU, the context window is the RAM, embeddings are the file system, and tools are I/O. Packer et al. [23] formalized one strand of this with MemGPT, which treats the context window as physical memory and external storage as disk, with the model managing paging. Martin, Cemaj, and Cohen [5] explicitly invoke the OS analogy for Anthropic's Managed Agents, virtualizing the session, harness, and sandbox as durable abstractions outside the container. The harness, in this lineage, is the kernel.

## 4. Anatomy of a Claude Code Harness

This section follows the decomposition in Liu et al. [1] and validates each component against Anthropic documentation [6][2] and practitioner repositories [10][11].

### 4.1 The agent loop (queryLoop pattern)

The core is a while-loop, formally an asynchronous generator, that calls the model, executes any tool calls in the response, returns results to the model, and repeats until the model produces a stop signal. Liu et al. [1] formalize this as a state vector S_t containing assembled context, available tools, and permission configuration. Anthropic's official documentation [6] describes the same loop in three phases: gather context, take action, verify results. The Agent SDK [2] exposes the same loop programmatically through the query() async iterator. Bedwards' Agent SDK guide [24] notes that the loop's shape is identical between the CLI and the SDK, which is the point.

### 4.2 System prompt and instruction layer (CLAUDE.md hierarchy)

Claude Code reads instructions from a hierarchy of CLAUDE.md files: user-level (~/.claude/CLAUDE.md), project-level (./CLAUDE.md), and project-private (.claude/CLAUDE.md). A critical detail captured by HumanLayer [25] and the official issue tracker [26] is that CLAUDE.md content is injected as the first user message wrapped in a system-reminder block, not as part of the system prompt. The wrapper text reads "this context may or may not be relevant to your tasks." This means CLAUDE.md instructions are advisory. The model can decide they do not apply. Hooks, by contrast, are deterministic shell scripts that run unconditionally on tool events. Skills [27] are loaded on demand via tool calls and have zero system-prompt footprint until activated. The probabilistic-versus-deterministic distinction is one of the most consequential design decisions in the entire harness because it determines which controls the model can route around.

### 4.3 Tool definitions and tool pool assembly

Liu et al. [1] count fifty-four tools across the v2.1.88 source. The Claude Code documentation [6] describes the built-in tool families: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, plus the Task tool for subagent delegation. Tool pool assembly is dynamic. The agent loop selects which tools to expose based on permission mode, plugin and skill activation, and MCP server connections. The Agent SDK exposes this through the allowed_tools option [2]. Schluntz and Zhang [3] argue that tool design is agent UX and that naming, schema, and error surfaces matter more than most teams realize. Anthropic's bash tool philosophy, captured by Bedwards [24], is that bash plus a file system obviates most specialized tools because the model can compose functionality through pipes.

### 4.4 Permission and authorization layer (deny-first)

Liu et al. [1] document seven permission modes plus an ML-based classifier. The configuration model accepts allow rules, deny rules, and ask rules. Default mode prompts the user before file writes and shell commands. The --dangerously-skip-permissions flag disables prompts entirely. Auto mode, introduced in March 2026 [8], replaces blanket bypass with a two-stage classifier: a fast single-token filter and a chain-of-thought check that runs only if the first filter flags an action. Hughes [8] reports a 0.4 percent false positive rate against ten thousand real internal tool calls and notes that the threat model includes scope escalation, credential exploration, agent-inferred parameters, data exfiltration, and safety-check bypass. The deny-first stance is also where the most significant failure modes have appeared, treated in Section 7.

### 4.5 Context construction and compaction (5-layer pipeline)

Liu et al. [1] describe a five-layer compaction pipeline. Anthropic's "Effective Context Engineering for AI Agents" [28] frames context as a finite resource subject to context rot, the empirical pattern that recall accuracy degrades as context length grows. The pipeline includes: token counting, tool-result trimming, conversation summarization, automatic compaction near the context limit, and full context resets. Rajasekaran [4] reports that Claude Sonnet 4.5 exhibited "context anxiety," prematurely wrapping up tasks as it sensed the limit approaching, which made resets essential. He also reports that Opus 4.5 largely removed this behavior, which made resets unnecessary. The harness assumption expired in one model generation.

### 4.6 Sandbox and execution environment

Sandboxing isolates tool execution at the OS level. Penligent's reverse-engineering analysis [29] notes that Claude Code uses platform-specific sandboxing primitives plus a permission layer plus prompting plus model alignment as a "Swiss cheese" defense. Each layer has holes but they are arranged so that no single hole goes through all the layers. The Agent SDK supports explicit sandbox paths and the Claude Code on Web product runs sessions in isolated VMs on Anthropic-managed infrastructure [30].

### 4.7 MCP integration layer

The Model Context Protocol [31] is an open standard, originally introduced by Anthropic in November 2024 and donated to the Linux Foundation under the Agentic AI Foundation in December 2025, that defines how host applications connect language models to external tools and data sources via JSON-RPC over stdio or HTTP with Server-Sent Events. MCP defines three primitives: tools (model-controlled), resources (application-controlled), and prompts (user-controlled). Claude Code is an MCP host. The MCP server ecosystem is large and growing. The protocol's authoritative specification [31] explicitly notes that tool descriptions should be considered untrusted unless obtained from a trusted server, and that hosts must obtain explicit user consent before invoking any tool. This consent boundary is exactly where the CVE-2025-59536 class of vulnerability lives.

### 4.8 Subagent delegation

Claude Code's Task tool launches subagents that operate in their own context windows and return summaries to the main session. Liu et al. [1] document worktree isolation as a key feature, which gives each subagent its own filesystem view. Anthropic's best-practices documentation [32] describes patterns including writer/reviewer pairs and parallelized migrations across thousands of files. Rajasekaran's harness essay [4] generalizes this to a planner-generator-evaluator architecture where each role has a separate context and communicates through files rather than through shared memory.

### 4.9 Persistence layer (append-only JSONL transcripts)

Sessions are stored as append-only JSONL files in ~/.claude/projects/ by default [2]. The Managed Agents architecture [5] generalizes this to a durable session log that lives outside any container, with the harness fetching and transforming events into the model's context window on demand. The session is the only durable component. The harness and sandbox are explicitly disposable. This "from pets to cattle" framing [5] is the point at which the harness becomes a kernel-style abstraction layer rather than a single process.

### 4.10 Validation against community repositories

The everything-claude-code repository [10] organizes its configuration along the same axes: skills, agents, hooks, commands, rules, MCP configurations. The Superpowers framework [11] adds a SessionStart hook that loads a getting-started skill, encoding a brainstorm-plan-implement workflow before any code is written. Both repositories validate that the components named above are not just artifacts of one paper's analytical framework. They are the surface that practitioners actually configure.

## 5. Design Principles and Tradeoffs

### 5.1 Principles from the primary literature

Schluntz and Zhang [3] argue four points. Start simple. Prefer composable patterns over heavy frameworks. Tool design is agent UX. Maintain agent-computer ground truth at every step through tool results.

Rajasekaran [4] adds five. Decompose builds into tractable chunks. Use structured artifacts to hand off context between sessions. Separate the agent doing the work from the agent judging it. Use context resets, not just compaction, when models exhibit context anxiety. Stress-test every harness component against the current model because every component encodes an assumption that will go stale.

Liu et al. [1] derive thirteen design principles from five values: human decision authority, safety and security, reliable execution, capability amplification, and contextual adaptability. The thirteen principles include least-privilege defaults, transparent state, recoverability, deterministic infrastructure around stochastic decision logic, and graceful degradation under context pressure.

### 5.2 Five tradeoffs

**Latency versus accuracy.** Rajasekaran [4] reports that the planner-generator-evaluator harness was twenty times more expensive than a single-pass run for a retro game maker prompt and produced materially better output. The single pass cost nine dollars and produced a broken application. The full harness cost two hundred dollars and produced a working one. The choice is not free.

**Autonomy versus control.** McCain et al. [7] report that median Claude Code turn duration is around forty-five seconds and is stable, while ninety-ninth-percentile duration nearly doubled between October 2025 and January 2026. New users grant full auto-approve about twenty percent of the time. By the seven-hundred-fiftieth session, users grant it more than forty percent of the time. Calibration evolves through experience, not through configuration.

**Context economy versus capability.** Anthropic's context engineering essay [28] frames context as a finite resource with diminishing returns. HumanLayer's analysis [25] reports that the Claude Code system prompt already contains roughly fifty individual instructions and that each additional CLAUDE.md instruction reduces overall instruction-following uniformly, not just at the margin.

**Defense in depth versus performance.** The Adversa.ai disclosure of the fifty-subcommand bypass [33][34] traced directly to a performance optimization. Anthropic's internal ticket CC-643 documented that complex compound commands froze the UI because each subcommand was being individually analyzed against deny rules. The fix capped analysis at fifty subcommands. The cap became a vulnerability because AI-generated commands from prompt injection routinely exceed it. Security and product delivery competed for the same CPU and security lost silently.

**Transparency versus efficiency.** CLAUDE.md as a user-message-not-system-prompt is the canonical example. Wrapping CLAUDE.md in a "may or may not be relevant" reminder gives the model permission to skip instructions that would otherwise constrain it [25]. This improves task adaptability and degrades determinism. There is no way to have both at the prompt layer. The Superpowers approach [11] of injecting an EXTREMELY_IMPORTANT block at session start is a practitioner workaround that buys a few additional points of compliance at the cost of context budget.

### 5.3 Practitioner evidence

The everything-claude-code release notes [10] explicitly position the project as a "performance optimization system" for AI agent harnesses, with a security guide covering attack vectors, sandboxing, sanitization, and CVEs. The Superpowers methodology [11] specifies a brainstorm-plan-implement workflow with subagent-driven development and a private journaling MCP for cross-session memory. Both systems converge on the same primitives that Anthropic ships: skills, hooks, subagents, and MCP servers. The convergence is empirical evidence that the design space identified by Liu et al. [1] is the design space the community is actually exploring.

## 6. Evaluation

### 6.1 Benchmarks

SWE-bench Verified [35] is a five-hundred-task human-curated subset of real Python GitHub issues. As of early 2026, leading models score in the high eighties to low nineties on the verified split, with Claude Mythos Preview reported at 93.9 percent and Opus 4.7 at 87.6 percent on Vellum's tracking [36]. SWE-bench Pro is a harder multi-language variant where Opus 4.7 reaches 64.3 percent. Terminal-Bench tests command-line proficiency. MLE-bench from OpenAI tests machine-learning engineering tasks. HumanEval [37] tests function-level code generation and is largely saturated. METR's time-horizon study [38][39] measures the duration of human professional tasks an AI can complete with fifty percent reliability and reports a doubling time of approximately seven months from 2019 to 2025, with possible acceleration to four months in 2024.

### 6.2 Harness quality versus model quality

This is the methodologically critical distinction. SWE-bench scores conflate the model and the harness. Anthropic's own SWE-bench analysis [40] notes that custom harnesses can produce ten-percentage-point gains over baseline configurations. Yang et al. [15] showed that a better agent-computer interface tripled performance on the same model. Aider's documentation [41] shows that the harness retries failed attempts up to six times alternating between models, which is a harness move, not a model move. A given benchmark number is a joint output of model, harness, retry policy, prompt, and tool design. Decomposing the contribution of each is largely ungrounded in published work.

### 6.3 Methodological limitations

Kapoor, Stroebl, Siegel, Nadgir, and Narayanan [42] document four problems with current agent benchmarks. Narrow focus on accuracy without cost. Inadequate or absent holdout sets, leading to overfitting. Lack of standardization, leading to non-reproducibility. Cost variance up to fifty times across leading agents on the same task. The Holistic Agent Leaderboard [43] required roughly forty thousand dollars to evaluate agents on nine benchmarks under a single configuration each, which makes statistically robust evaluation prohibitive for small labs.

### 6.4 The 1.6 percent / 98.4 percent ratio

Liu et al. [1] report that approximately 1.6 percent of the Claude Code v2.1.88 codebase is AI decision logic and 98.4 percent is deterministic infrastructure. We treat this as community-estimated and indicative rather than definitive. The exact split depends on what counts as decision logic, how the count handles minified bundles versus source files, and whether vendored binaries such as ripgrep are included. The qualitative claim that the harness dominates the codebase is well-supported. The specific percentages should not be treated as a precision number.

### 6.5 The empirical productivity question

Becker, Rush, Barnes, and Rein [44] ran a randomized controlled trial on sixteen experienced open-source developers across two hundred forty-six tasks in mature projects with February-to-June 2025 frontier AI tools, primarily Cursor with Sonnet 3.5/3.7. Developers expected AI to make them twenty-four percent faster. They reported afterward that AI made them twenty percent faster. The measured result was that AI made them nineteen percent slower, with a confidence interval between two and thirty-nine percent slowdown. The result is a snapshot of one tool generation in one experimental setting. METR's February 2026 update [45] reports that for the same developers, the estimated effect with later-2025 tools was an eighteen-percent speedup with a wide confidence interval that crossed zero. This is a moving target and the only honest summary is that we do not yet have settled evidence on harness-mediated productivity in the wild.

He et al. [46] analyzed eight hundred seven repositories using Cursor and reported a 40.7 percent increase in cyclomatic complexity in AI-assisted commits. A 2026 large-scale study of AI-generated code in real-world repositories [47] examines code-level and commit-level characteristics across hundreds of thousands of commits but does not yet report a settled effect size. The relevant claim for this document is that harness design influences the kind of code that lands in repositories, not just whether it lands.

## 7. Security and Governance Implications

### 7.1 Authorization scope and least agency

OWASP's 2026 Top 10 for Agentic Applications [48][49] introduces the concept of least agency, the principle that agents should be granted the minimum autonomy required for safe bounded tasks. The risks include agent goal hijack, identity and privilege abuse, supply-chain compromise of tools and skills, and confused-deputy scenarios. The Claude Code permission system maps onto these directly. Allow lists, deny lists, and ask rules implement least agency at the per-tool level. Permission modes implement it at the session level. Auto mode [8] implements it through a learned classifier rather than a static rule.

### 7.2 The pre-trust initialization vulnerability class

Check Point Research disclosed CVE-2025-59536 (CVSS 8.7) and CVE-2026-21852 (CVSS 5.3) [50][51]. The first allowed arbitrary shell execution through hooks, MCP servers, and environment variables in a project's .claude/settings.json before the trust dialog appeared. The second allowed API-key exfiltration through ANTHROPIC_BASE_URL override before the trust dialog appeared. Both were patched, the first in version 1.0.111 and the second in version 2.0.65. CVE-2025-54794 and CVE-2025-54795 are related disclosures in the same family. The class is configuration-as-code where configuration files were treated as passive metadata but were actually execution paths. The architectural fix described by Anthropic was to ensure no settings file logic runs before user consent. The structural fix described by Check Point is to treat repository-scoped configuration files with the same suspicion as executable code.

The Adversa.ai TrustFall disclosure [52] argues that even with the post-CVE-2025-59536 patch, the workspace trust dialog asks "Is this a project you created or one you trust?" without disclosing that trusting a folder grants execution to .mcp.json servers with full access to ~/.ssh/, ~/.aws/, and shell history. Anthropic declined this as out of threat model on the grounds that informed consent is the user's responsibility post-dialog. This is a defensible position. It is also a position that places non-trivial burden on developers who are not equipped to perform a configuration audit on every cloned repository.

### 7.3 The 93 percent approval rate finding and HITL degradation

Hughes [8] reports that Claude Code users approve 93 percent of permission prompts. The number is the empirical motivation for auto mode. If users approve nearly everything, the prompt is friction rather than safety. Auto mode replaces the prompt with a two-stage classifier on Sonnet 4.6, escalating to humans only on flagged actions. The approval-rate data is consistent with the broader literature on automation bias and approval fatigue. Human-in-the-loop is not a fixed protection. It degrades through use. McCain et al. [7] explicitly report that "oversight requirements that prescribe specific interaction patterns, such as requiring humans to approve every action, will create friction without necessarily producing safety benefits."

### 7.4 Defense in depth with shared failure modes (50-subcommand bypass)

Adversa.ai [33] disclosed in April 2026 that Claude Code silently dropped deny-rule enforcement once a shell command exceeded fifty subcommands joined by &&, ||, or ;. The fix existed in Anthropic's own codebase but had not been deployed. The vulnerability was traced to a performance optimization in bashPermissions.ts that capped analysis at fifty subcommands and fell back to a generic ask prompt. AI-generated commands from prompt injection routinely exceed this threshold. The Adversa proof-of-concept used fifty no-op true subcommands followed by a curl command that should have been denied. The fix shipped in version 2.1.90. The lesson is that defense-in-depth layers can share a failure mode (the assumption that humans authored the command) and that an attacker only needs to find one path through all the layers.

### 7.5 CLAUDE.md as user message, not system prompt

Section 4.2 noted that CLAUDE.md is injected as a user message wrapped in a system-reminder block that tells the model the contents may not be relevant. From a security standpoint, this means CLAUDE.md is probabilistic guidance, not deterministic enforcement. An organization that writes "never commit to main" in CLAUDE.md is making a request the model will probably honor, not enforcing a rule the model cannot violate. Hooks are the deterministic enforcement layer. A pre-commit hook that blocks pushes to main is a guarantee. A CLAUDE.md instruction that says do not push to main is a probability. Conflating the two is one of the most common security-design errors we observe in practitioner repositories.

### 7.6 Mapping to frameworks

NIST AI RMF places the harness in the Manage and Map functions, since the harness is where governance controls take effect. ISO/IEC 42001's AI management system clauses on operational planning and control map onto the permission system, the hook system, and the audit trail. MITRE ATLAS techniques for prompt injection (T1606), tool abuse, and credential access map onto the CVEs above. OWASP LLM Top 10 (2025) covers the model layer. OWASP Agentic Top 10 (2026) [48] covers what we have called the harness layer. The two are complementary, not redundant.

## 8. Open Problems and Research Gaps

**Cross-session persistence and trust accumulation.** Liu et al. [1] note that Claude Code's persistence is append-only JSONL transcripts plus working memory in CLAUDE.md. There is no first-class memory subsystem. Packer et al. [23] proposed MemGPT-style virtual context management. Chhikara et al. and others have proposed graph-structured memory layers. None are integrated into Claude Code or the Agent SDK as of May 2026. The gap between session-scoped memory and durable cross-session learning is the largest unaddressed problem named in the literature we surveyed.

**Observability-evaluation gap.** LangChain's State of Agent Engineering report [53] documents that 89 percent of organizations claim some form of agent observability and only 62 percent have step-level tracing. The gap between knowing what happened and knowing whether what happened was good is wide. Galileo's reporting [54] indicates that elite teams achieve roughly 2.2x better reliability than non-elite teams and that 72 percent of teams believe testing drives reliability while only 15 percent achieve elite evaluation coverage. Observability is necessary but not sufficient.

**Horizon scaling.** METR's time-horizon work [38][39] predicts that one-month tasks may be reachable within years if current trends hold. METR's own clarifications [55] flag external validity concerns and the possibility of compute slowdowns. Whether the harness layer or the model layer is the binding constraint at one-month horizons is genuinely open. Rajasekaran's [4] observation that Opus 4.6 made the V1 sprint construct unnecessary is empirical evidence that the binding constraint moves.

**Long-term human capability preservation.** Becker et al. [44], Kosmyna et al. [56], and Anthropic's own internal survey [9] all surface concerns about cognitive offloading. Anthropic's survey reports that 27 percent of Claude-assisted work would not have been done without it (capability amplification), while engineers also worry about supervision atrophy. Kosmyna et al. report EEG-measured reductions in neural connectivity for ChatGPT users versus search-engine users versus unassisted writers in essay tasks. Whether the same effect appears in coding remains untested. The long-run effect on the developer pipeline is unmeasured.

**Harness virtualization.** Martin, Cemaj, and Cohen [5] frame Managed Agents as virtualizing the session, harness, and sandbox so each can evolve independently. The OS analogy is suggestive but not yet validated at scale. Whether harness-as-service becomes the dominant deployment model or whether per-application harnesses dominate is open.

**Memory as a first-class subsystem.** Practitioner repositories [10][11] include private journaling, semantic search over past sessions, and continuous learning skills. These are not native Claude features. The Anthropic memory tool described in API documentation [27] is an early step. Whether memory will be standardized at the protocol layer (an MCP extension) or at the harness layer (per-implementation) is not yet decided.

## 9. Conclusions and Recommendations

A Claude harness is the deterministic substrate that turns a stochastic model into a controllable agent. The substrate dominates the codebase, the security surface, and the design discussion in roughly equal measure. The Liu et al. [1] decomposition, the Anthropic engineering essays [3][4][5], and the practitioner repositories [10][11] converge on the same nine components: agent loop, instruction layer, tool pool, permission layer, context pipeline, sandbox, MCP integration, subagent delegation, and persistence. Designing a personal harness is mostly a matter of making nine load-bearing decisions explicitly rather than letting them be made implicitly by defaults.

Recommendations for designing a personal harness spanning Claude Code and the Claude Agent SDK:

1. Treat CLAUDE.md as advisory and put any rule that must hold every time into a hook or a deny rule. The probabilistic-versus-deterministic boundary is the most consequential design line in the harness.

2. Keep the system-prompt instruction count low. HumanLayer's analysis [25] suggests that instruction-following degrades uniformly with instruction count. A short focused CLAUDE.md outperforms a long thorough one.

3. Use auto mode plus an explicit deny list rather than --dangerously-skip-permissions. Hughes' 0.4 percent false-positive rate [8] is an acceptable tradeoff for the threat-model coverage that bypass loses.

4. Audit .claude/settings.json and .mcp.json files in any cloned repository before opening it. The CVE-2025-59536 class of vulnerability survives in user habit even after Anthropic's patches.

5. Prefer one continuous session with automatic compaction on Opus 4.5 or later. Rajasekaran's evidence [4] that context resets became unnecessary on 4.6 is the cleanest example in the literature of a harness assumption expiring across a model generation.

6. Use the Task tool for verifiable subtasks (test writing, code review, migration) rather than for high-judgment subtasks. Anthropic's best practices [32] note that fresh context produces unbiased reviews because the reviewer was not the writer.

7. Persist plans, decisions, and lessons to files in the repository, not in the agent session. Both Rajasekaran [4] and the Superpowers methodology [11] converge on this point.

8. Track which deny rules and hooks are actually firing. The fifty-subcommand bypass [33] is a reminder that silent failure of a security control is worse than an explicit one. Logging is cheap.

9. Re-evaluate the harness against each new model release. The space of useful harness configurations does not shrink as models improve. It moves [4]. A harness built for Sonnet 4.5 may carry dead weight on Opus 4.7 and may need new components to access capabilities that did not exist on 4.5.

10. Treat the OWASP Agentic Top 10, NIST AI RMF, and ISO 42001 controls as design inputs, not audit outputs. The CVEs that have actually shipped on Claude Code map onto these frameworks cleanly. Mapping forward at design time is cheaper than mapping back at incident time.

## 10. References

[1] Liu, J., Zhao, X., Shang, X., and Shen, Z. "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems." arXiv:2604.14228, MBZUAI VILA Lab, April 2026. https://arxiv.org/abs/2604.14228

[2] Anthropic. "Agent SDK Overview." Claude API Docs, 2026. https://platform.claude.com/docs/en/agent-sdk/overview

[3] Schluntz, E., and Zhang, B. "Building Effective Agents." Anthropic, December 2024. https://www.anthropic.com/research/building-effective-agents

[4] Rajasekaran, P. "Harness Design for Long-Running Application Development." Anthropic Engineering, March 24, 2026. https://www.anthropic.com/engineering/harness-design-long-running-apps

[5] Martin, L., Cemaj, G., and Cohen, M. "Scaling Managed Agents: Decoupling the Brain from the Hands." Anthropic Engineering, 2026. https://www.anthropic.com/engineering/managed-agents

[6] Anthropic. "How Claude Code Works." Claude Code Docs. https://code.claude.com/docs/en/how-claude-code-works

[7] McCain, M., Millar, T., Huang, S., Eaton, J., Handa, K., Stern, M., Tamkin, A., et al. "Measuring AI Agent Autonomy in Practice." Anthropic Research, 2026. https://www.anthropic.com/research/measuring-agent-autonomy

[8] Hughes, J. "Claude Code Auto Mode: A Safer Way to Skip Permissions." Anthropic Engineering, March 25, 2026. https://www.anthropic.com/engineering/claude-code-auto-mode

[9] Anthropic. "How AI Is Transforming Work at Anthropic." Internal survey of 132 engineers, 2025. https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic

[10] Mustafa, A. "everything-claude-code." GitHub. https://github.com/affaan-m/everything-claude-code

[11] Vincent, J. "Superpowers: An Agentic Skills Framework." GitHub. https://github.com/obra/superpowers

[12] "awesome-harness-engineering." GitHub. https://github.com/ai-boost/awesome-harness-engineering

[13] "awesome-agent-harness." GitHub. https://github.com/AutoJunjie/awesome-agent-harness

[14] EleutherAI. "lm-evaluation-harness." GitHub. https://github.com/EleutherAI/lm-evaluation-harness

[15] Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O. "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering." NeurIPS 2024. arXiv:2405.15793

[16] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., and Cao, Y. "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629, October 2022

[17] Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., Cancedda, N., and Scialom, T. "Toolformer: Language Models Can Teach Themselves to Use Tools." arXiv:2302.04761, 2023

[18] Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., and Yao, S. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023. arXiv:2303.11366

[19] Madaan, A., Tandon, N., Gupta, P., et al. "Self-Refine: Iterative Refinement with Self-Feedback." arXiv:2303.17651, 2023

[20] Zhou, A., Yan, K., Shlapentokh-Rothman, M., Wang, H., and Wang, Y.-X. "Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models." arXiv:2310.04406, 2023

[21] Wu, Q., Bansal, G., Zhang, J., et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." 2024

[22] Karpathy, A. "LLM OS." X (Twitter), November 10, 2023. https://x.com/karpathy/status/1723140519554105733

[23] Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., and Gonzalez, J. E. "MemGPT: Towards LLMs as Operating Systems." arXiv:2310.08560, October 2023

[24] Bedwards, B. "Claude Agent SDK Documentation." 2026. https://bedwards.github.io/anthropic-claude-agent-sdk/

[25] HumanLayer. "Writing a Good CLAUDE.md." HumanLayer Blog, 2026. https://www.humanlayer.dev/blog/writing-a-good-claude-md

[26] Anthropic. "Issue #6973: Docs: Clarify how CLAUDE.md and --append-system-prompt influence Claude's instructions." anthropics/claude-code, GitHub. https://github.com/anthropics/claude-code/issues/6973

[27] Anthropic. "Agent Skills." Claude API Docs. https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

[28] Anthropic. "Effective Context Engineering for AI Agents." September 29, 2025. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

[29] Penligent. "Inside Claude Code: The Architecture Behind Tools, Memory, Hooks, and MCP." 2026. https://www.penligent.ai/hackinglabs/inside-claude-code-the-architecture-behind-tools-memory-hooks-and-mcp/

[30] Anthropic. "Claude Code on Web." Product page. https://www.anthropic.com/product/claude-code

[31] Model Context Protocol. "Specification." 2025-11-25. https://modelcontextprotocol.io/specification/2025-11-25

[32] Anthropic. "Best Practices for Claude Code." Claude Code Docs. https://code.claude.com/docs/en/best-practices

[33] Adversa.ai Red Team. "Critical Claude Code Vulnerability: Deny Rules Silently Bypassed Because Security Checks Cost Too Many Tokens." April 2026. https://adversa.ai/blog/claude-code-security-bypass-deny-rules-disabled/

[34] Claburn, T. "Claude Code Bypasses Safety Rule If Given Too Many Commands." The Register, April 1, 2026. https://www.theregister.com/2026/04/01/claude_code_rule_cap_raises/

[35] Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770, 2023

[36] Vellum. "Claude Opus 4.7 Benchmarks Explained." 2026. https://www.vellum.ai/blog/claude-opus-4-7-benchmarks-explained

[37] Chen, M., Tworek, J., Jun, H., et al. "Evaluating Large Language Models Trained on Code." arXiv:2107.03374 (HumanEval), 2021

[38] Kwa, T., West, B., Becker, J., Deng, A., Garcia, K., et al. "Measuring AI Ability to Complete Long Software Tasks." METR, March 19, 2025. https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

[39] METR. "Task-Completion Time Horizons of Frontier AI Models." https://metr.org/time-horizons/

[40] Anthropic. "Claude SWE-Bench Performance." https://www.anthropic.com/research/swe-bench-sonnet

[41] Aider AI. "aider-swe-bench." GitHub. https://github.com/paul-gauthier/aider-swe-bench

[42] Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., and Narayanan, A. "AI Agents That Matter." arXiv:2407.01502, July 2024

[43] Kapoor, S., et al. "Holistic Agent Leaderboard (HAL)." 2026

[44] Becker, J., Rush, N., Barnes, B., and Rein, D. "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity." METR, July 10, 2025. arXiv:2507.09089

[45] METR. "We Are Changing Our Developer Productivity Experiment Design." February 24, 2026. https://metr.org/blog/2026-02-24-uplift-update/

[46] He, Y., et al. "AI Code Complexity Study Across 807 Cursor Repositories." 2025

[47] "A Large-Scale Empirical Study of AI-Generated Code in Real-World Repositories." arXiv:2603.27130, 2026

[48] OWASP Gen AI Security Project. "OWASP Top 10 for Agentic Applications 2026." https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/

[49] Practical DevSecOps. "OWASP Top 10 for Agentic Applications for 2026." https://www.practical-devsecops.com/owasp-top-10-agentic-applications/

[50] Donenfeld, A., and Vanunu, O. "RCE and API Token Exfiltration Through Claude Code Project Files: CVE-2025-59536 and CVE-2026-21852." Check Point Research, 2026. https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/

[51] SentinelOne. "CVE-2025-59536: Anthropic Claude Code RCE Vulnerability." Vulnerability Database. https://www.sentinelone.com/vulnerability-database/cve-2025-59536/

[52] Adversa.ai. "TrustFall: Coding Agent Security Flaw Enables One-Click RCE in Claude, Cursor, Gemini CLI and GitHub Copilot." 2026. https://adversa.ai/blog/trustfall-coding-agent-security-flaw-rce-claude-cursor-gemini-cli-copilot/

[53] LangChain. "AI Agent Observability: Tracing, Testing, and Improving Agents." State of Agent Engineering Report. https://www.langchain.com/articles/agent-observability

[54] Galileo. "The Enterprise Guide to AI Agent Observability." https://galileo.ai/blog/ai-agent-observability

[55] METR. "Clarifying Limitations of Time Horizon." January 22, 2026. https://metr.org/notes/2026-01-22-time-horizon-limitations/

[56] Kosmyna, N., Hauptmann, E., Yuan, Y. T., Situ, J., et al. "Your Brain on ChatGPT: Accumulation of Cognitive Debt When Using an AI Assistant for Essay Writing Task." MIT Media Lab, arXiv:2506.08872, June 2025

[57] Anthropic. "Our Framework for Developing Safe and Trustworthy Agents." 2025. https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents

---

## CHALLENGER PASS NOTE

A self-attack pass identified the following weak points and the responses applied.

**Weakest claim challenged.** The 1.6 percent / 98.4 percent split from Liu et al. [1] was the most quotable single number in the document and would be the first thing a hostile committee would attack. The number is community-estimated, depends on how decision logic is counted, and was derived from a single version (v2.1.88) of a single product. Response: Section 6.4 was rewritten to flag the number as community-estimated and indicative rather than definitive, separated the qualitative claim (the harness dominates the codebase, well-supported) from the quantitative claim (the specific percentages, less well-supported), and removed any rhetorical reliance on the precise ratio elsewhere.

**Section a hostile committee would attack first.** Section 7 on security would be attacked on the grounds that "harness engineering" is being used as a frame to repackage well-known issues such as prompt injection, configuration-as-code attacks, and approval fatigue, and that the framework adds no analytical value. Response: Section 7 was reinforced with named CVEs, named primary sources (Check Point Research, Adversa.ai, Anthropic engineering posts), explicit CVSS scores, and explicit mappings to OWASP Agentic Top 10, NIST AI RMF, and MITRE ATLAS. The pre-trust-initialization vulnerability class was presented as a class with multiple named instances rather than as a single bug. The CLAUDE.md probabilistic-versus-deterministic distinction was carried through Section 4.2, Section 5.2, and Section 7.5 as a recurring analytical move rather than a one-off observation.

**Counterargument added in Section 2.3.** The strongest internal counterargument is that "harness engineering" is concept inflation over agent scaffolding and that a separate label is premature. The argument is presented before its response and the response acknowledges the counterargument has force, settling on a Bayesian confidence of roughly 0.7 rather than asserting the term is fully established.

**Empirical productivity claims downgraded.** Section 6.5 was rewritten to present Becker et al. [44] as a snapshot of one tool generation in one experimental setting and to note that METR's own February 2026 update [45] reported a different effect for the same developers with later tools. The claim is that we do not yet have settled evidence on harness-mediated productivity, not that AI tools harm productivity.

**Sections deferred to downstream work.** A comprehensive comparison with LangChain, LangGraph, AutoGen, OpenHands, and AutoGPT was scoped to a one-paragraph treatment in Section 3 because a full comparator analysis would change the document's character from a Claude-substrate analysis to a framework survey. The scope decision is explicit and the missing comparison is named as an open task for the downstream dissertation chapter.

---

## INSTRUCTION TO PUBLISHER

The `content_hash` field in the frontmatter is empty. Before publishing this document, compute the SHA-256 hash of the body content (everything below the closing `---` of the frontmatter, with LF line endings and NFC Unicode normalization applied) and populate the `content_hash` field. Recommended command on a Unix-like system:

```
tail -n +N document.md | iconv -f UTF-8 -t UTF-8 | python3 -c "import sys, unicodedata; print(unicodedata.normalize('NFC', sys.stdin.read()), end='')" | tr -d '\r' | shasum -a 256
```

where N is the line number immediately after the closing frontmatter `---`.
```
