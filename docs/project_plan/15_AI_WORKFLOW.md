# MediSign-AI: AI Agent Workflow Guidelines

This document outlines the workflow guidelines for AI coding assistants working on the MediSign-AI repository.

---

## 1. Code-First Research Rule

AI agents must read the codebase before modifying any files. Do not make assumptions about directory layouts, file paths, or class names.

* **Action Plan**:
  1. Search for existing symbols (classes, functions, files) using grep tools.
  2. Read configuration files (`config.toml`) to check parameter names.
  3. Inspect existing test suites to understand input/output structures.

---

## 2. Integrity and Preservation Rule

Do not rewrite working modules or delete code to implement new features.

* **Action Plan**:
  1. Build on top of the existing API layer. Keep the Flask (`:5000`) and FastAPI (`:8000`) engines independent.
  2. Implement features in separate modules or packages rather than editing existing ones.
  3. Ensure that all modifications preserve backward compatibility.

---

## 3. Test-Driven Development (TDD) Rule

Every new feature must be accompanied by appropriate tests.

* **Action Plan**:
  1. Verify that the backend test coverage remains above 90%.
  2. Write unit tests for new services and widget tests for new UI screens in Flutter.
  3. Run the test suite before submitting work.

---

## 4. Documentation Maintenance Rule

Keep project documentation updated after completing tasks.

* **Action Plan**:
  1. Update `AI_PROGRESS.md` with details of the completed phase.
  2. Record key architectural decisions in `AI_DECISIONS.md`.
  3. Log bug reports in `BUGS.md` and document any limitations in `KNOWN_LIMITATIONS.md`.
