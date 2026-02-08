---
id: 002
title: Update constitution for Phase IV Kubernetes deployment
stage: constitution
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: claude
command: /sp.constitution
labels: [constitution, phase-iv, kubernetes, deployment, minikube]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

PHASE IV – LOCAL KUBERNETES DEPLOYMENT
CLOUD NATIVE TODO CHATBOT
PROMPT SET (SPEC-DRIVEN)
PROMPT 1: PROJECT CONSTITUTION (PHASE IV)

PROJECT CONSTITUTION – PHASE IV
Local Kubernetes Deployment using Minikube and AI DevOps Tools

PURPOSE

This constitution defines the strict rules, principles, and constraints for Phase IV of the Hackathon project.

The goal of Phase IV is to deploy the existing AI-powered Todo Chatbot (Phase III) on a local Kubernetes cluster using Minikube, Helm Charts, and AI-assisted DevOps tools.

This phase focuses on infrastructure automation and deployment discipline, not feature development.

DEVELOPMENT PHILOSOPHY

This project strictly follows Spec-Driven Development (SDD).

All work must follow this exact order:

Specify → Plan → Tasks → Implement

Skipping any step is strictly forbidden.

RULES FOR AGENTS AND DEVELOPERS

No deployment action may occur without an approved task.

No Kubernetes or Docker configuration may be written without specification.

No manual trial-and-error deployment is allowed.

Docker images must be generated via AI agents where possible.

Helm charts must be generated via kubectl-ai or kagent where possible.

Existing application code must not be modified.

Phase III functionality must remain unchanged.

If Gordon is unavailable, fallback must be documented, not improvised.

SOURCE OF TRUTH HIERARCHY

Constitution

Specification

Plan

Tasks

Implementation

ARCHITECTURE PRINCIPLES

Kubernetes is the single runtime target.

Docker images must be immutable.

Configuration must be externalized.

Services must be deployable independently.

Helm charts define the deployment contract.

AI DevOps tools assist but do not replace validation.

SCOPE BOUNDARIES

IN SCOPE:

Dockerizing frontend and backend

Helm chart creation

Minikube deployment

AI-assisted Docker and Kubernetes operations

OUT OF SCOPE:

Feature changes

Kafka or Dapr

Cloud providers

CI/CD pipelines

AGENT BEHAVIOR

If an agent encounters ambiguity:

It must stop

Ask for clarification

Not guess or invent configuration

END GOAL

A fully working Todo Chatbot running locally on Minikube using Helm charts and AI-assisted DevOps tools.

## Response snapshot

Updated project constitution to version 1.1.0 with comprehensive Phase IV principles for Local Kubernetes Deployment. Added nine new principle sections covering strict spec-driven deployment, prohibition of manual trial-and-error, application code immutability, AI DevOps tools integration, Kubernetes architecture requirements, Docker image immutability, configuration externalization, independent service deployment, and Helm chart standards. Defined clear scope boundaries for Phase IV including what is in scope (Dockerizing, Helm charts, Minikube deployment) and out of scope (feature changes, cloud providers, CI/CD). Enhanced governance section to include Phase IV deployment discipline and agent behavior requirements.

## Outcome

- ✅ Impact: Constitution updated from v1.0.0 to v1.1.0 with Phase IV deployment principles
- 🧪 Tests: none
- 📁 Files: 1 file modified (constitution.md)
- 🔁 Next prompts: Ready for Phase IV specification prompt
- 🧠 Reflection: Constitution now provides clear governance for Kubernetes deployment phase while maintaining existing Phase II and III principles.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): not applicable
- Prompt variant (if applicable): not applicable
- Next experiment (smallest change to try): not applicable
