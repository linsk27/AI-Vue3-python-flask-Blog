# Final Stabilization Report

Last checked: 2026-05-25

## Completed

- Backend tests pass: `27 passed`.
- Frontend production build passes.
- Frontend UI smoke verification passes on desktop and mobile, with no horizontal overflow or console errors.
- Real authenticated E2E flow passes:
  - login with `admin / admin123`
  - create temporary article
  - create temporary context pack
  - attach sources
  - rebuild RAG index
  - preview RAG retrieval
  - open the AI draft panel in the browser
  - clean up temporary article and context pack
- Avue admin production build passes.
- Avue admin authenticated browser smoke test passes:
  - login succeeds
  - admin menus render
  - dashboard loads real backend data
  - no browser console errors
- `avue-cli npm audit` reports 0 vulnerabilities.

## Dependency Security

- `front npm audit` has 1 remaining moderate advisory from `quill@1.3.7`.
- The automated fix requires `quill@2.0.3`, a breaking editor migration, so it is intentionally deferred.
- Details are recorded in `docs/security-audit-notes.md`.

## Avue Build Notes

- Removed production mock wiring and removed `mockjs` / `vite-plugin-mock`.
- Upgraded Avue admin dependencies conservatively, including Axios 1.x and Vite 6.4.2.
- Removed the accidental `package-lock.json` production chunk from the Avue about page.
- Remaining build warnings are upstream or legacy-framework related:
  - `@smallwei/avue` bundle contains internal `eval`.
  - Avue layout/router modules mix static and dynamic imports, so Rollup warns that some modules cannot be split as intended.
  - Avue and Element Plus remain large admin-only vendor chunks. They are gzip-compressed and isolated from the public frontend.

## Runtime Defaults

- Frontend dev server: `http://127.0.0.1:8080`
- Flask backend used by local verification: `http://127.0.0.1:5100`
- Avue admin dev server: `http://127.0.0.1:5001`
- Avue proxy target can be overridden with `VITE_API_TARGET`; default is `http://127.0.0.1:5100`.

## Useful Commands

```bash
cd backend && pytest
cd front && npm run build
cd front && npm run verify:ui
cd front && npm run verify:e2e
cd avue-cli && npm run build
cd front && npm audit
cd avue-cli && npm audit
```
