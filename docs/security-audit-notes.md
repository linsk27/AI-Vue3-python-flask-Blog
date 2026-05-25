# Security Audit Notes

Last checked: 2026-05-25

## Current result

- `avue-cli`: `npm audit` reports 0 vulnerabilities after conservative dependency updates and removing the unused mock build plugin.
- `front`: `npm audit` reports 1 remaining moderate vulnerability from `quill@1.3.7`.

## Deferred item

- `quill <= 1.3.7` has a moderate XSS advisory. The available automated fix upgrades to `quill@2.0.3`, which is a breaking editor migration.
- This project keeps Quill 1.x in this round to avoid breaking the writing editor late in the stabilization pass.
- Next safe step: migrate the editor integration to Quill 2 in a dedicated branch, verify image/link/code-block behavior, and rerun the AI draft flow to ensure generated Markdown still becomes editable content rather than a raw JSON envelope.

## Guardrails

- Do not run `npm audit fix --force` in this repo without a separate migration/test pass.
- Treat editor HTML as user-controlled content when rendering outside the editor.
