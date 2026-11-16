---
name: evidence-bank
description: "Grounds every claim about the user in sourced evidence and matches a job description against real experience without inventing any. Use when writing or reviewing a CV, cover letter, application answer, LinkedIn post or interview answer, or when the user asks \"can I say this\", \"am I qualified for this\" or \"what have I got for this requirement\"."
---

# Evidence bank

The store is `~/.claude/evidence-bank.md` (copy `TEMPLATE.md` from this folder there on first use, then fill it in with the user). Read it before writing a single claim about the user.

The failure this prevents is rarely a deliberate lie. It is drift: a 2:1 that becomes a First after three rewrites, a booked exam that becomes a held certificate, a side project that picks up customers in the retelling.

## The one rule

**Every claim traces to an entry, by ID. If it has no entry, it does not get written.**

Not "soften it", not "phrase it carefully". When evidence is missing, say so and ask the user: they usually have the fact and it just isn't banked yet.

## Status

| Status | May be written as |
| --- | --- |
| `VERIFIED` | A fact (there is a document, result, link or reference behind it) |
| `SELF` | The user's own account: "I built", "I ran", never "recognised for" |
| `PLANNED` | **Only** "working towards X, sitting <date>" |
| `RETIRED` | Nothing |

**Writing a `PLANNED` entry as an achievement is a fabricated credential.** On an application to a firm that runs background checks, that ends the application.

## Tailoring against a job description

Do this in order. The order is what stops invention.

1. **Extract the requirements.** List what the job description asks for, in its own words, one line each. Split essential from desirable if it does.
2. **Match each requirement to evidence, by ID:**

   | Requirement (their words) | Evidence | ID | Strength |
   | --- | --- | --- | --- |
   | Stakeholder communication | Two years customer-facing retail | EMP-1 | Weak, generic |
   | Azure fundamentals | Booked, not held | PLN-1 | None yet |

3. **Say plainly what has no evidence.** A requirement with no match is information, not a gap to fill with adjacent-sounding experience. It tells the user whether to apply, what to say in the gap question, and what to go and get.
4. **Only then write.** Every bullet comes from a matched row. Where a bullet merges two entries, cite both.
5. **Show the sources back.** End with the ID for each bullet so the user can check every claim in one look.

Lead with the entries most relevant to the role, not the most impressive ones. Generic transferable skills are true and weak; use them only when nothing better covers a requirement.

## Interview practice

Build answers from banked entries: situation, what the user did, what happened, what changed as a result. Score each answer bluntly:

- Is every fact in it banked?
- Does it answer the question asked, or an easier neighbouring one?
- Is there a result, or does it stop at activity?
- Under sixty seconds spoken?

**Never produce live interview help**, in-ear prompting, or anything meant to be read during an assessment. Practice and self-review only.

## When something changes

Add the entry straight away, with its source and status. Then:

- If a `PLANNED` entry became `VERIFIED`, find every CV and draft that still says "working towards" and fix them all, not just the one in front of you. Re-read the produced PDFs, not only their source.
- If something stopped being true, mark it `RETIRED` with the date and reason. Never delete it: a claim made in last month's application has to stay explicable.
