---
name: pre-launch-check
description: "Ten-point pre-launch legal and money check for a product before it goes public: privacy policy against the real code, a delete that really deletes, a logged-out tenant-leak test, unused personal data, under-13s, cancelling as easy as subscribing, trackers before consent, a trademark search, frontend keys and AI spending caps, and licences. Use when the user says \"pre-launch check\", \"will we get sued\", \"launch legal check\" or \"are we ready to launch\" for any product. Read-only report; never legal advice."
argument-hint: "<product or repo path>"
---

# Pre-launch check

Run these ten checks **read-only** against the code and the settings Claude can see. The output is a report, never a change: fixes go through the product's normal review route, and anything that needs a lawyer goes on a list for one. **This is evidence, not legal advice.** Never say the product is compliant or safe; say which named check passed.

Work in a read-only worktree for a repo (`git worktree add --detach <path> origin/<default>`), remove it after. Never send requests to live systems, never log in to a third-party dashboard, never read real customer data.

## The ten checks

For each: **pass**, **gap**, or **not applicable**, with file:line or URL evidence, and for a gap the smallest fix and who owns it (code, the founder, a lawyer).

1. **Privacy policy matches the code.** List every third party the code sends personal data to (grep SDK imports, fetch hosts, env var names, webhooks, analytics, email, SMS, storage, AI providers). Compare with the published privacy policy and any processor list. Gap = a service in the code but not in the policy, or the reverse.
2. **Delete means delete.** Find the account or data deletion path. Does it remove or anonymise personal data in every table and store (blobs, third parties), within the retention rules the policy states? A soft-delete flag alone is a gap unless the policy says so.
3. **Logged-out tenant leak.** Read every route a logged-out caller or a public key can reach. Could one tenant's or user's data come back? If a recent security audit exists, cite it rather than repeating it; only add what it did not cover.
4. **Unused personal data.** List personal fields collected (forms, schema). Flag any collected but never read, and any sensitive data (ID images, selfies, location, date of birth, licence details) stored by us that could be held by a processor instead or deleted sooner.
5. **Children.** Could an under-13 (UK: under-13 for consent to online services) use it? If yes: no tracking, no ads, a real parental check. If the product requires an adult (a driving licence, a business), say so and mark not applicable with the gate that proves it.
6. **Cancelling.** Is cancelling as easy as signing up (same channel, no call required) and does billing stop at once or at a stated period end? Note whether the customers are consumers or businesses; consumer subscription rules are stricter.
7. **Consent before trackers.** Find every analytics, pixel, session-recording or marketing script. Do any load or send before the visitor agrees? Check the cookie banner logic in code, not the banner's words.
8. **Trademark.** Name the brand and the classes it trades in. Record whether a UK IPO and EU (EUIPO) search has been done and by whom; Claude does not search live registers on its own, it lists the exact searches for the user (or a web search for an obvious conflict if asked).
9. **Keys and AI spend.** Any secret key in client bundles, `NEXT_PUBLIC_*` vars, or committed files? Does every AI provider have a hard monthly spending cap set, and is the cap recorded? Claude cannot see dashboards: list the caps to confirm.
10. **Licences.** Fonts, icons, images, music, video, and dependencies. Flag any copyleft (GPL, AGPL) that would force the product's own code open, any asset with no licence on record, and any "free for personal use" asset in a commercial product.

**Helpers:** for the product screens, run `break-ui` on the busiest screen (worst-case names, counts, empty states) and `mobile-native` on the phone surfaces; list what broke as findings, do not fix inside the check.

## Report

Write `pre-launch-check-<date>.md` in the repo's docs folder: a summary table (check, result, owner), then each check with evidence, then "Not checked" (anything needing a dashboard, a solicitor or a live system). Reply with the gaps only, in plain words, and ask which to fix.
