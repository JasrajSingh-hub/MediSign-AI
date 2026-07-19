# MediSign-AI: Documentation Templates

This document provides reusable templates for tracking project progress, changelogs, tasks, bugs, and known limitations.

---

## 1. `AI_PROGRESS.md` Template

```markdown
# AI Progress Log

Track completed implementation phases and milestones here.

| Phase | Feature Name | Status | Completion Date | Notes |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Feature A | Completed | YYYY-MM-DD | Summarize what was built and verified. |
| 2 | Feature B | In Progress | - | Details of current focus. |

## Verification Details
- **Command Run**: `flutter test` or `pytest`
- **Result**: Details of test coverage or test run outputs.
```

---

## 2. `AI_CHANGELOG.md` Template

```markdown
# AI Changelog

Log all code modifications and additions.

## [Version] - YYYY-MM-DD
### Added
- Describe new files or features.
### Changed
- Describe modifications to existing files.
### Fixed
- Describe bug fixes.
```

---

## 3. `TODO.md` Template

```markdown
# Project TODO List

- [ ] High Priority
  - [ ] Subtask 1
  - [ ] Subtask 2
- [ ] Medium Priority
- [ ] Low/Future Ideas
```

---

## 4. `BUGS.md` Template

```markdown
# Bug Tracker

| Bug ID | Description | Severity | Status | Fix Action |
| :--- | :--- | :--- | :--- | :--- |
| BUG-001| Camera controller throws error on rotate | High | Open | Describe mitigation steps. |
```

---

## 5. `KNOWN_LIMITATIONS.md` Template

```markdown
# Known Limitations

Record known limitations of the application.

* **Limitation 1**: Describe limitation (e.g. "Low-light prediction accuracy drops below 50%").
* **Limitation 2**: Describe limitation (e.g. "ADB reverse tunneling requires an active physical USB connection").
```
