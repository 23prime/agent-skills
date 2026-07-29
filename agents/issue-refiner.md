---
name: issue-refiner
description: Use ONLY when the user explicitly asks to run GitHub Issue refinement with maximum reasoning effort (Opus / xhigh), instead of the default refining-github-issue skill on the main thread. This wraps an interactive, one-question-at-a-time interview — invoke it in the foreground (run_in_background: false), and once dispatched, relay every turn: forward the subagent's question to the user as your own message, then send the user's answer back to the same agent via SendMessage. Do not treat this as a fire-and-forget dispatch, and do not paraphrase or summarize turns away — the subagent's questions and the user's answers must reach each other unchanged, in both directions, for every question in the interview.
model: opus
effort: xhigh
skills:
  - refining-github-issue
color: purple
---

# Issue Refiner

Follow the preloaded `refining-github-issue` skill's workflow exactly, start to finish. Do not add, skip, or reinterpret any step.
