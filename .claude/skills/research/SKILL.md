---
name: research
description: Research a topic in the codebase using a subagent. Use when the user wants to explore or understand code.
---

# Research Skill

A skill that spawns a subagent to research and explore topics in the codebase.

## Instructions

When this skill is invoked:

1. Use the **Task tool** to spawn an Explore subagent
2. Pass the user's query or topic as the prompt
3. Set `subagent_type` to "Explore" for codebase exploration
4. Wait for results and summarize findings for the user

### Example Usage

If the user runs `/research authentication flow`, spawn an agent like:

```
Task tool call:
- subagent_type: "Explore"
- description: "Research authentication flow"
- prompt: "Find and explain how authentication works in this codebase. Look for login handlers, auth middleware, token management, and session handling."
```

### Available Subagent Types

- **Explore**: Fast codebase exploration (finding files, searching code, answering questions)
- **general-purpose**: Complex multi-step tasks requiring various tools
- **Bash**: Command execution (git, npm, docker, etc.)
- **Plan**: Designing implementation strategies

### Tips

- For quick searches, use `model: "haiku"` to reduce latency
- For thorough analysis, specify thoroughness in the prompt: "quick", "medium", or "very thorough"
- Use `run_in_background: true` for long-running research tasks
