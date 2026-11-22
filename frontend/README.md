# DocReader BD Frontend

Next.js 14 app for building templates and extracting fields.

## Setup
```bash
npm install
npm run dev
```

Copy `.env.local.example` to `.env.local`. ShobdoOCR runs directly through its
Hugging Face Space. Template storage uses same-origin Next.js API routes and
Google Cloud Firestore.

Set `FIREBASE_CREDENTIALS_JSON` locally and in the Vercel project environment to
the Firebase service-account JSON. Keep this variable server-side; never prefix
it with `NEXT_PUBLIC_`.
