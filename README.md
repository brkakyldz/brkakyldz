## Berke Akyıldız

I build AI agents and the backends they run on, mostly in Python. I work with
the OpenAI Agents SDK, LangGraph and LangChain, different model APIs, and
FastAPI, and I write evals and tests to check that each system does what it's
supposed to. Below are the four projects I've built: an AI concierge for a
hotel, a daily AI news pipeline, a memory system for AI agents, and a scoring
and report engine for US tech companies.

### Projects

**[Hotel Operations Agent](https://github.com/brkakyldz/Hotel_Operations_Agent)** — *in development*
An AI concierge for a hotel's guests. It takes requests in chat and writes them
into the hotel's records, hands anything that needs approval to a manager, and
messages the guest on its own when something changes at the hotel. The rules are
enforced in code and only a manager can approve, so the agent can't grant itself
anything. It passes 75 of 75 cases in the live eval, backed by 386 automated tests.
`Python` · `OpenAI Agents SDK` · `FastAPI` · `SQLAlchemy` · `React` · [how it works →](https://brkakyldz.github.io/isler/hotel-operations-agent/)

**[AI Digest](https://github.com/brkakyldz/ai-research-agent)** — *done, running*
Collects the day's AI news from many sources, merges the stories that cover the
same event, summarises and ranks them, and puts the day on a single page. No step
that calls a model runs on its own, which keeps the monthly bill around one dollar.
More than 600 tests cover it.
`Python` · `LangGraph` · `FastAPI` · `HTMX` · `SQLite` · [how it works →](https://brkakyldz.github.io/isler/ai-digest/)

**[Second Brain OS](https://github.com/brkakyldz/second-brain-os)** — *in use, in development*
Long-term project memory for AI agents that a person can also open, read and
correct. There's no database: memory is plain Markdown in a Git repo, only the
part a session needs gets loaded, and a character budget keeps it from growing
without limit. This is the open template of the memory I use every day with
Claude Code and Codex.
`Markdown` · `Git` · `Claude Code` · `Codex` · `Obsidian` · [how it works →](https://brkakyldz.github.io/isler/second-brain-os/)

**[TechInves](https://github.com/brkakyldz/tech_inves)** — *done*
Scores US tech companies against their own peers and writes a research report on
top. The score comes entirely from deterministic code; the model only writes the
report text, and the report goes through a rule layer before it's published —
a serious violation stops it.
`Python` · `LangGraph` · `FastAPI` · `SQLAlchemy` · `Next.js` · [how it works →](https://brkakyldz.github.io/isler/techinves/)

### Working with

`Python` · `TypeScript` · `SQL` · agent SDKs · `LangGraph` · `LangChain` · model APIs · `MCP` · `FastAPI` · `SQLAlchemy` · `Pydantic` · `SQLite / PostgreSQL` · `Docker` · `GitHub Actions` · `pytest`

### Elsewhere

[Portfolio](https://brkakyldz.github.io/) · [LinkedIn](https://www.linkedin.com/in/berkeakyildiz/) · berkeakyildz@gmail.com
