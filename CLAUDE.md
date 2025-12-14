# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a monorepo containing a receipt management application with:
- **Frontend**: Next.js 16 with React 19, TypeScript, and Tailwind CSS 4
- **API**: FastAPI backend with Python 3.12

## Repository Structure

```
/workspace
├── frontend/         # Next.js application
│   ├── app/         # Next.js App Router pages and layouts
│   ├── public/      # Static assets
│   └── package.json
├── api/             # FastAPI backend
│   ├── main.py      # FastAPI application entry point
│   ├── requirements.txt
│   └── .venv/       # Python virtual environment (gitignored)
└── .devcontainer/   # Claude Code Sandbox devcontainer setup
```

## Development Commands

### Frontend (Next.js)

All frontend commands must be run from the `/workspace/frontend` directory:

```bash
cd /workspace/frontend

# Install dependencies
npm install

# Development server (runs on http://localhost:3000)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint
npm run lint
```

### API (FastAPI)

All API commands must be run from the `/workspace/api` directory:

```bash
cd /workspace/api

# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (with auto-reload)
fastapi dev main.py

# Run production server
fastapi run main.py
```

The FastAPI server runs on `http://localhost:8000` by default. API documentation is automatically available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Architecture Notes

### Frontend
- Uses Next.js App Router (not Pages Router)
- TypeScript with strict mode enabled
- Tailwind CSS 4 with PostCSS for styling
- Path alias `@/*` maps to the frontend root directory
- Geist Sans and Geist Mono fonts from next/font/google

### API
- FastAPI application instance created in `main.py`
- Currently minimal setup with a single root endpoint
- Virtual environment located in `.venv/` (gitignored)

## Key Configuration Files

- `frontend/tsconfig.json`: TypeScript configuration with strict mode
- `frontend/next.config.ts`: Next.js configuration
- `frontend/eslint.config.mjs`: ESLint configuration using Next.js defaults
- `api/requirements.txt`: Python dependencies including FastAPI, Uvicorn, and Pydantic

## Development Environment

This project uses Claude Code Sandbox devcontainer with:
- Network capabilities (NET_ADMIN, NET_RAW)
- VSCode extensions for Claude Code, ESLint, Prettier, and GitLens
- Firewall initialization script
- Zsh as default shell

## Working with Both Frontend and API

When developing features that span both frontend and API:
1. Start the API server first from `/workspace/api`
2. Start the frontend dev server from `/workspace/frontend`
3. Frontend runs on port 3000, API on port 8000
4. Configure CORS in FastAPI when connecting frontend to API
