# InsightHub Web Application

## Architecture

```text
Browser
   |
Next.js web application
   |
FastAPI Intelligence Service
   |
AI Analyst Agent
```

The application in `apps/web` is a small Next.js App Router frontend. The home page provides the analyst question flow and renders the answer as safe GitHub-flavored Markdown. Citations are normalized from the backend `sources` response. The dashboard reads the existing sales, inventory, and discount endpoints in parallel.

The current `/api/v1/agent/query` response exposes `answer` and `sources`, but not tool calls or execution traces. The chat therefore shows a clearly labeled execution metadata placeholder rather than inventing tool activity. It is ready to display future trace metadata when the API contract exposes it.

## API Communication

All browser requests go through the Next.js `/backend` rewrite, which targets `NEXT_PUBLIC_API_URL`. Components call functions in `apps/web/lib/api.ts`; response contracts are defined in `apps/web/lib/types.ts`. The client applies a 30-second timeout and converts unavailable or malformed responses into user-facing errors.

## Local Development

From the repository root:

```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

The FastAPI service must be available at `http://localhost:8000` unless `NEXT_PUBLIC_API_URL` is changed. Use `npm run build` for a production build and `npm start` to serve it.

## Deployment

The root Docker Compose file builds the frontend from `apps/web`, publishes port `3000`, and waits for the healthy intelligence service. Run:

```bash
docker compose --env-file .env -f deployment/docker-compose.yml up --build
```

No secrets are copied into the frontend image. `NEXT_PUBLIC_API_URL` is a public routing value only; provider and database credentials remain in the backend environment.
