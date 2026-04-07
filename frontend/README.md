This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Backend configuration

The frontend chooses its backend through public environment variables.

1. `frontend/.env.local` is the local developer file for backend selection.
2. Set `NEXT_PUBLIC_USE_LOCAL_BACKEND=true` to use your local backend, or `false` to use production.
3. Adjust `NEXT_PUBLIC_LOCAL_API_BASE_URL` if your local backend runs on a different port.

Example:

```bash
NEXT_PUBLIC_USE_LOCAL_BACKEND=true
NEXT_PUBLIC_LOCAL_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_PROD_API_BASE_URL=https://api.gidgraph.com
```

If no env vars are set, development defaults to `http://localhost:8000` and production builds default to `https://api.gidgraph.com`.
Restart the Next.js dev server after changing any `NEXT_PUBLIC_*` value.

## Local development workflow

1. Start the backend:

```bash
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

2. Start the frontend from the `frontend` folder:

```bash
npm run dev
```

3. Open `http://localhost:3000`.

The backend allows both localhost frontend origins and the deployed frontend origins by default, so the frontend can switch between local and production API targets without code changes.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
