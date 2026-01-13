# Agent Plans

This directory contains implementation plans for features developed by agents.

## Structure

```
plans/
├── README.md                    # This file
├── TEMPLATE.md                  # Template for new plans
├── implemented/                 # Completed plans (archive)
│   ├── 001-agentic-platform.md
│   └── 002-azure-scheduling.md
└── proposed/                    # Plans awaiting approval
```

## Plan Lifecycle

```
proposed/ → (approved) → implemented/
```

1. **Proposed**: Agent creates plan, awaits user approval
2. **Approved**: User approves, agent begins implementation
3. **Implemented**: Work complete, plan moved to archive

## Naming Convention

```
NNN-short-description.md
```

- `NNN`: Sequential number (001, 002, etc.)
- `short-description`: Kebab-case feature name

Examples:
- `001-agentic-platform.md`
- `002-real-time-streaming.md`
- `003-data-quality-framework.md`

## Plan Requirements

Each plan must include:

1. **Summary**: One-paragraph overview
2. **Goals**: What success looks like
3. **Architecture**: Technical design
4. **Implementation Phases**: Step-by-step breakdown
5. **Files to Create/Modify**: Explicit file list
6. **Verification**: How to test the implementation
7. **Status**: Current state and completion date

## Usage

### Creating a New Plan

1. Copy `TEMPLATE.md` to `proposed/NNN-feature-name.md`
2. Fill in all sections
3. Present to user for approval
4. On approval, begin implementation
5. On completion, move to `implemented/`

### Referencing Plans

In code comments or commits, reference plans as:
```
# See: plans/implemented/001-agentic-platform.md
```

## Index

| # | Plan | Status | Date |
|---|------|--------|------|
| 001 | [Agentic Data Platform](implemented/001-agentic-platform.md) | Implemented | 2026-01-13 |
| 002 | [Azure Storage & Scheduling](implemented/002-azure-scheduling.md) | Implemented | 2026-01-13 |
