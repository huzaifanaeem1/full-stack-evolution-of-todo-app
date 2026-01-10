---
id: 001
title: Update constitution for Phase II web app
stage: constitution
date: 2026-01-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: claude
command: /sp.constitution
labels: [constitution, web-app, todo, phase2]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
 - .specify/templates/spec-template.md
 - .specify/templates/tasks-template.md
tests:
 - none
---

## Prompt

Create speckit.constitution for Phase II: Todo Full-Stack Web Application.

Principles:
- Strict Spec-Driven Development (Specify → Plan → Tasks → Implement)
- No manual coding by the user
- Phase I (CLI) is complete and separate
- Phase II is a fresh full-stack web app
- Backend and frontend are separate services
- Authentication is mandatory
- All data access must be user-isolated

Technology Constraints:
- Frontend: Next.js 16+ (App Router)
- Backend: FastAPI (Python)
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT-based)
- API: REST only

Security Rules:
- All API endpoints require JWT
- JWT must be verified in FastAPI
- User ID must be extracted from token
- Users can only access their own tasks

Non-Negotiables:
- No AI features in Phase II
- No UI overengineering
- No feature beyond requirements
- Same JWT secret shared via env variable

Goal:
Deliver a working, secure, multi-user Todo web application.

## Response snapshot

Updated the constitution file and aligned templates to reflect the new requirements for the Todo Full-Stack Web Application. The new constitution includes detailed principles around spec-driven development, technology stack requirements, security requirements, and non-negotiable constraints. Template files were updated to include constitution compliance checks and specific requirements from the constitution.

## Outcome

- ✅ Impact: Updated constitution and aligned templates for Phase II web app
- 🧪 Tests: none
- 📁 Files: 4 files updated (.specify/memory/constitution.md, .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md)
- 🔁 Next prompts: none
- 🧠 Reflection: Successfully created a comprehensive constitution that enforces the specified requirements and updated templates to ensure compliance.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): not applicable
- Prompt variant (if applicable): not applicable
- Next experiment (smallest change to try): not applicable