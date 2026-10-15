<p>
<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/hero-dark-narrow.svg">
  <source media="(max-width: 600px)" srcset="assets/hero-light-narrow.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img src="assets/hero-light.svg" width="100%" alt="Berke Akyıldız. I build AI agent systems in Python: the tools an agent can call, the rules it can’t talk past, and the evals that check what it actually did. Antalya, Türkiye.">
</picture>
</p>

I started building with AI to automate my own notes and research. Once I saw that a model could call tools and change things inside a system, I wanted to learn how to build that properly. Each project below puts an agent inside a small working system, such as a hotel's front desk, a support inbox or a salon's calendar, and then pays close attention to the places where it could go wrong: a write it shouldn't make, a request that needs a person's approval, or a reply that reads fine while the trace shows something else.

Before this I worked at the front desk of a hotel in Antalya, and that job shaped the hotel agent below. I work mostly in Python with the OpenAI Agents SDK, LangGraph and LangChain on top of the OpenAI and Anthropic APIs, and Claude Code and Codex are part of how I work every day.

## Projects

### [Hotel Operations Agent](https://github.com/brkakyldz/Hotel_Operations_Agent)

<a href="https://github.com/brkakyldz/Hotel_Operations_Agent"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/glyph-hotel-dark.svg"><img align="right" width="176" src="assets/glyph-hotel-light.svg" alt="A guest's message passes the agent and reaches a code gate before it is written to the database; one branch goes to a manager's approval, and a change at the hotel sends a message back to the guest."></picture></a>

An AI concierge for a small fictional hotel, built on the OpenAI Agents SDK. Guests chat with it in any language and I play the manager. The hotel's rules for checkout, check-in and housekeeping run as code inside the database transaction, so the agent can file a late-checkout request but only a manager can approve it. When something changes at the hotel, code decides that the guest has to be told, and the agent writes the message.

**75 of 75** cases passed in the live eval, across 108 model runs, with no forbidden change to the database.<br>
`Python` · `OpenAI Agents SDK` · `FastAPI` · `SQLAlchemy` · `React` &nbsp;→&nbsp; [how it works](https://brkakyldz.github.io/isler/hotel-operations-agent/) <sub>(Turkish)</sub>

### [LLM Experiments](https://github.com/brkakyldz/llm-experiments)

<a href="https://github.com/brkakyldz/llm-experiments"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/glyph-experiments-dark.svg"><img align="right" width="176" src="assets/glyph-experiments-light.svg" alt="An agent's run goes from the request through three tool calls to its reply. A judge reads only the reply and passes it; a plain check over the trace stops at the second tool call and flags it."></picture></a>

Small experiments on how agents behave when they do real work. In the first one, *said-vs-did*, a support agent correctly refused a refund on someone else's order, but in the same reply it told the customer what was inside that order. An LLM judge that read only the reply gave it 7/10 and a pass, while a plain-code check over the trace flagged the leak. Every run is kept, and the saved traces can be re-scored offline without an API key.

**11 runs**, each graded three ways: a judge on the reply, and code checks on the outcome and on the order of tool calls.<br>
`Python` · `OpenAI and Anthropic APIs` · `LLM-as-judge` &nbsp;→&nbsp; [open the trace viewer](https://brkakyldz.github.io/llm-experiments/said-vs-did/trace-viewer.html)

### [AI Digest](https://github.com/brkakyldz/ai-research-agent)

<a href="https://github.com/brkakyldz/ai-research-agent"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/glyph-digest-dark.svg"><img align="right" width="176" src="assets/glyph-digest-light.svg" alt="A pipeline: collect, dedupe and enrich, then summarise in parallel branches, rank and persist."></picture></a>

A local LangGraph pipeline that reads the day's AI news for me. It polls RSS feeds every three hours, merges the same story told by different outlets, summarises and ranks what is left, and serves the day as a single page. Polling costs nothing, so it runs on a timer. The steps that call a model only run when I press the button, which keeps the bill around a dollar a month.

**About $1 a month** to run, on one machine and one container.<br>
`Python` · `LangGraph` · `FastAPI` · `HTMX` · `SQLite` &nbsp;→&nbsp; [how it works](https://brkakyldz.github.io/isler/ai-digest/) <sub>(Turkish)</sub>

### [Second Brain OS](https://github.com/brkakyldz/second-brain-os)

<a href="https://github.com/brkakyldz/second-brain-os"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/glyph-brain-dark.svg"><img align="right" width="176" src="assets/glyph-brain-light.svg" alt="Three inputs, one output: notes pass a check before they reach the memory file that every session loads."></picture></a>

A memory for coding agents that a person can read, correct and undo. Claude Code and Codex share one Obsidian vault that is also a Git repository. The facts that matter are loaded when a session starts, the rest is read when a question needs it, and every change the agent makes is a commit. This repo is the public template of the vault I have used every day since August.

**v1.1**, MIT licensed, runs on Windows, macOS and Linux with nothing to install beyond Node.<br>
`Markdown` · `Git` · `Node` · `Claude Code` · `Codex` · `Obsidian` &nbsp;→&nbsp; [how it works](https://brkakyldz.github.io/isler/second-brain-os/) <sub>(Turkish)</sub>

### [TechInves](https://github.com/brkakyldz/tech_inves)

<a href="https://github.com/brkakyldz/tech_inves"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/glyph-techinves-dark.svg"><img align="right" width="176" src="assets/glyph-techinves-light.svg" alt="Two pipelines: model-free scoring along the top, and a researched report below that passes a rule gate before it is published."></picture></a>

Scores US tech companies against their own peers and writes a research report on top. The score comes from deterministic code over SEC EDGAR filings and market data, with no model involved. A LangGraph pipeline researches the week and drafts the report, and a verifier made of rules and an LLM judge grades the draft before it is published, so a serious problem stops it.

**0 to 100** percentile scores across valuation, growth, quality and financial health, plus a separate risk score.<br>
`Python` · `LangGraph` · `FastAPI` · `SQLAlchemy` · `Next.js` &nbsp;→&nbsp; [how it works](https://brkakyldz.github.io/isler/techinves/) <sub>(Turkish)</sub>

### Smaller agents

Each of these applies one framework to one job, with a human approval step and a recorded acceptance run against the real model.

- **[GitHub Issue Triage Agent](https://github.com/brkakyldz/github-issue-triage-agent)** · Deep Agents · acceptance run 5 / 5<br>
  Labels new issues, finds duplicates and drafts replies, then shows the maintainer the whole batch on one review screen before anything is written to GitHub. Its work is visible in a [public sandbox](https://github.com/brkakyldz/issue-triage-sandbox/issues?q=is%3Aissue).
- **[Support Ticket Router](https://github.com/brkakyldz/support-ticket-router)** · LangGraph · acceptance run 6 / 6<br>
  Sends a store's support tickets to one of four teams. When the model is unsure, the graph pauses for a person and resumes on the same thread.
- **[Salon Booking Agent](https://github.com/brkakyldz/salon-booking-agent)** · LangChain · acceptance run 7 / 7<br>
  Books salon appointments in English or Turkish. Each booking waits for the owner's approval and is checked against opening hours and overlaps in one transaction.

## Tools I work with

- **Agents and models:** OpenAI Agents SDK, LangGraph, LangChain, Deep Agents, MCP, OpenAI and Anthropic APIs
- **Backend and data:** Python, TypeScript, FastAPI, SQLAlchemy, Pydantic, SQLite, PostgreSQL
- **Testing and tracing:** pytest, evals that check tool calls and database state, LangSmith
- **Every day:** Claude Code, Codex, Git, Docker, GitHub Actions, Obsidian

## Certificates

- **Anthropic, Claude Academy:** Building with the Claude API · Claude Code in Action · Introduction to Model Context Protocol · Model Context Protocol: Advanced Topics
- **LangChain, Foundation:** Introduction to LangGraph (Python) · Building Reliable Agents · Introduction to Deep Agents

<br>

<img src="https://raw.githubusercontent.com/brkakyldz/brkakyldz/output/activity.svg" width="100%" alt="My GitHub contributions over the last year, drawn as light on the sea: each day is one mark, and busier days are longer and brighter. A GitHub Action redraws it every day.">

I'd like to join a team that builds AI products people use every day. You can reach me by email or on LinkedIn, and my portfolio has a longer write-up of each project, in Turkish.

**[Portfolio](https://brkakyldz.github.io/)** &nbsp;·&nbsp; **[LinkedIn](https://www.linkedin.com/in/berkeakyildiz/)** &nbsp;·&nbsp; **[berkeakyildz@gmail.com](mailto:berkeakyildz@gmail.com)**
