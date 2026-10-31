# Jekyll migration and repository audit

## Status
Preparation only. This branch does not delete existing files, rewrite protocols, or turn on GitHub Pages.

## Repository findings
- The tracked tree contains more than 11,000 entries.
- `SoundCraft AI/$(python3 -m site --user-site)/` contains checked-in third-party Python package files and bytecode; review before removal, including licensing and reproducibility.
- Several Frequency Library entries appear twice with typography variations; verify file hashes and links before deduplication.
- `Smith Equivalence App/` includes historical script generations and zero-byte placeholder modules; identify the active code before archiving.
- `Outputs/Protection Chant.m4a` and `SoundCraft Audio Stamp.m4a` are production assets; preserve and assess whether they belong in repository releases or Git LFS.
- `README` has no .md suffix, making Markdown rendering less predictable; propose a move to `README.md` after reviewing references.
- Existing protocol revisions may conflict: do not merge or overwrite them without an authoritative version inventory.

## Proposed phases
1. Review and merge this documentation-only Jekyll foundation.
2. Audit file SHA hashes, provenance, and third-party licensing; create an approved deletion/move manifest.
3. Consolidate protocol documentation with explicit version metadata and redirect mappings.
4. Organize active source applications separately from historical releases and generated dependencies.
5. Only after reviewing what becomes publicly visible, configure GitHub Pages build and access.

## Publication caution
This repository is private and All Rights Reserved. Publishing GitHub Pages may expose site content to visitors depending on plan and configuration. Explicitly review and approve public content before enabling Pages.
