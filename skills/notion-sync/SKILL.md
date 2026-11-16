---
name: notion-sync
description: "Use this skill when syncing information to or from Notion. Triggers include: \"update Notion\", \"sync to Notion\", \"push to Notion\", \"update the Notion [page]\", \"reflect this in Notion\", \"sync Notion\". Fetches the current page, identifies what changed, and pushes exact old_str→new_str updates via the Notion MCP tool."
---

# Skill: Notion Sync

Syncs changes between local context files and Notion pages using the MCP integration.

## Finding the page

Search Notion for the page by title with the Notion connector's search tool, and confirm the title before editing. If the user syncs the same pages often, list their IDs in their own CLAUDE.md.

## Process

### 1. Fetch before updating
Always fetch the page first:
```
mcp__claude_ai_Notion__notion-fetch(id: "<page_id>")
```
Extract the exact current text for any section being changed. The `old_str` in `update_content` must match character-for-character.

### 2. Use update_content, not replace_content
Use `update_content` with precise `old_str`/`new_str` pairs. Never use `replace_content` unless rebuilding the entire page from scratch (rare, check for child pages first).

### 3. Update in batches
Multiple `content_updates` can be passed in a single `update_content` call. Group related changes together. Unrelated pages should be updated in parallel calls.

### 4. Parallel updates across pages
When syncing multiple pages at once, make all `notion-fetch` calls in parallel first, then all `notion-update-page` calls in parallel.

## Common Update Patterns

### Updating a status or value
```
old_str: "Not started"
new_str: "In progress, booked 1 April"
```

### Updating a table cell
Match the entire row:
```
old_str: "<tr>\n<td>First Aid course</td>\n<td>Not started</td>..."
new_str: "<tr>\n<td>First Aid course</td>\n<td>In progress</td>..."
```

### Adding to a checklist
```
old_str: "- [ ] Book the First Aid course"
new_str: "- [x] Book the First Aid course, done 1 April"
```

### Updating the footer timestamp
Always update the "Last updated" line at the bottom of each page after making changes.

## Troubleshooting

**`validation_error: No matches found`**: The `old_str` doesn't match exactly. Re-fetch the page and copy the exact text including all whitespace, tabs, and escape characters (`\[`, `\~` etc).

**MCP not connected**: Save changes to `staging/notion-[page]-opt.json` with `old_str`/`new_str` pairs. Push when MCP reconnects.

**Child page deletion error on `replace_content`**: Include child page references using `<page url="...">` tags, or switch to `update_content`.

## Notes

- Fetch → update → verify (re-fetch a section to confirm the change landed)
- If Notion MCP drops mid-session, continue locally and push at session end
- After every Notion update, update the local context file too so they stay in sync
