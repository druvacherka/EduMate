# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.

## Backend database setup

The backend uses PostgreSQL for persistent, multi-user storage. Copy `.env.example`
to `.env`, set `DATABASE_URL` to your PostgreSQL connection string, and generate a
strong signing key for `JWT_SECRET_KEY` (for example,
`python -c "import secrets; print(secrets.token_urlsafe(48))"`). Create the
`edumate` database, install backend dependencies with
`pip install -r backend/requirements.txt`, then start the API with
`python -m uvicorn backend.main:app --reload`.

The API creates or upgrades its PostgreSQL tables at startup and enables the
`vector` extension. The PostgreSQL server must have pgvector installed, and the
database role must be allowed to enable the extension. Embeddings use
`vector(768)` with a cosine HNSW index and are filtered by the authenticated
student profile. Accounts use Argon2 password hashes and bearer tokens.

To copy existing SQLite records, first create an account in EduMate, then run
`python -m backend.migrate_sqlite_to_postgres --email your-account@example.com`.
The script reads `backend/edumate.db` by default and commits the relational data
to that account in one transaction. Back up the SQLite file before migrating.
Existing Qdrant embeddings are not imported by this script. Re-upload your
source PDFs after PostgreSQL is configured; uploads are embedded and stored in
the PostgreSQL `study_embeddings` table. The old local Qdrant store was
ephemeral, so embeddings that were not otherwise persisted cannot be recovered.
