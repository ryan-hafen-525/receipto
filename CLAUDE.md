# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a monorepo containing a receipt management application with:
- **Frontend**: Next.js 16 with React 19, TypeScript, and Tailwind CSS 4
- **API**: FastAPI backend with Python 3.12

## Development Commands

### Frontend (Next.js)

All frontend commands must be run from the `/workspace/frontend` directory:

- See @frontend/package.json for commands to run

### API (FastAPI)

All API commands must be run from the `/workspace/api` directory:

```bash
# Run development server (with auto-reload)
fastapi dev main.py

# Run production server
fastapi run main.py
```

The FastAPI server runs on `http://localhost:8000` by default. API documentation is automatically available at `/docs` (Swagger UI) and `/redoc` (ReDoc).


## Key Configuration Files

- `frontend/tsconfig.json`: TypeScript configuration with strict mode
- `frontend/next.config.ts`: Next.js configuration
- `frontend/eslint.config.mjs`: ESLint configuration using Next.js defaults
- `api/requirements.txt`: Python dependencies including FastAPI, Uvicorn, and Pydantic

## Development Environment

This project uses Claude Code Sandbox devcontainer with:
- Network capabilities (NET_ADMIN, NET_RAW)
- VSCode extensions for Claude Code, ESLint, Prettier, and GitLens
- Zsh as default shell

## Working with Both Frontend and API

When developing features that span both frontend and API:
1. Start the API server first from `/workspace/api`
2. Start the frontend dev server from `/workspace/frontend`
3. Frontend runs on port 3000, API on port 8000
4. Configure CORS in FastAPI when connecting frontend to API

## Spec Sheet
See @SPEC.md for the specsheet and technical details of the implementation.
