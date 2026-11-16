# Claude kit

Khalid's Claude Code setup, with everything personal taken out: 137 skills, 63 agents, the plugins and MCP servers he uses, and a template for your own `CLAUDE.md`.

## Install

You need Claude Code installed first (https://claude.com/claude-code).

**Mac or Linux**

```bash
git clone https://github.com/kalmehdar/claude-kit.git
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R claude-kit/skills/* ~/.claude/skills/
cp -R claude-kit/agents/* ~/.claude/agents/
```

**Windows (Git Bash)**: the same commands work. In PowerShell:

```powershell
git clone https://github.com/kalmehdar/claude-kit.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills","$HOME\.claude\agents" | Out-Null
Copy-Item -Recurse -Force claude-kit\skills\* "$HOME\.claude\skills\"
Copy-Item -Recurse -Force claude-kit\agents\* "$HOME\.claude\agents\"
```

Restart Claude Code. Skills load when a request matches their description, or by name (`/humanizer`). Copying over a skill you already have replaces it.

To update later: `git pull` in `claude-kit`, then copy again.

## What's in it

| Folder | What it is |
| --- | --- |
| `skills/` | One folder per skill. `SOURCES.md` says where each came from. |
| `agents/` | Subagent definitions by team (engineering, design, marketing, product, testing and more). `agents/extra/` holds nine more. |
| `CLAUDE-template.md` | How Khalid structures his `CLAUDE.md`, with the personal parts blanked. Copy it to `~/.claude/CLAUDE.md` and fill it in. |

Some skills are worth starting with:

| Skill | Use it for |
| --- | --- |
| `humanizer` | Rewrites text so it doesn't read like AI wrote it |
| `brainstorming` | Talks through a feature before any code is written |
| `owasp-security`, `never-get-hacked`, `security-audit` | Security while writing code, a quick pre-deploy sweep, and a deep review |
| `frontend-design`, `hallmark`, `taste-skill` | Web pages that look designed |
| `webapp-testing` | Testing a local web app with Playwright |
| `deep-research` | Researching a question across many sources |
| `caveman` | Much shorter answers, when you ask for them |

## Plugins

Install these from inside Claude Code with `/plugin`. Add the marketplace first, then the plugin.

| Plugin | Marketplace |
| --- | --- |
| `ponytail` (keeps code minimal) | `DietrichGebert/ponytail` |
| `chrome-devtools-mcp`, `discord`, `aikido` | `anthropics/claude-plugins-official` |
| `cloudflare` | `cloudflare/skills` |
| `hyperframes` (HTML to video) | `heygen-com/hyperframes` |
| `claude-hud` (status line) | `jarrodwatts/claude-hud` |
| `pmo`, `security`, `legal-risk`, `revenue`, `executive`, `customer-experience`, `it-operations`, finance | `cbrock84/headcount` |

## MCP servers

Only one is public and needs no account: Front-End Checklist.

```bash
claude mcp add --transport http frontend-checklist https://mcp.frontendchecklist.io/mcp
```

Khalid also uses Notion, Google Drive, Google Calendar, Figma and Vercel through Claude's own connectors (claude.ai, Settings, Connectors). Sign in with your own accounts.

## Not included

- Khalid's `CLAUDE.md`, context files, memory and notes: they're personal.
- His own skills about his CV, uni, KeyProof, Bygild and his machines.
- Any API key, password or login. Never paste a key into a chat with Claude or commit one to a repo.
