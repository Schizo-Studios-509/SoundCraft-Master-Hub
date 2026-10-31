# SoundCraft Master Hub — Website branch

This is the **website-only** `publish` branch of the SoundCraft Master Hub repository, maintained by **Schizo Studios 509** and **Dictation2897**.

- **`main`** contains authoritative SoundCraft source material, application code, protocols, and audio assets.
- **`publish`** contains only Jekyll source files intended for the documentation site.

Do not copy the complete `main` source tree into this branch. Public documentation should be curated, checked for attribution and licensing, and synchronized selectively.

## Validate

The GitHub Actions workflow `.github/workflows/jekyll-build.yml` builds the site on pushes to `publish`, and its `workflow_dispatch` option allows a manual run.

To build locally:

```sh
gem install bundler
bundle install
bundle exec jekyll build --trace
```

The output is placed in `_site/`, which should never be committed.

## Hosting

The Jekyll configuration assumes the GitHub Pages project URL:

`https://schizo-studios-509.github.io/SoundCraft-Master-Hub/`

If using a custom domain, update `url` and `baseurl` first. **Publishing is not enabled by this branch**; review public visibility before configuring GitHub Pages deployment.

The repository is currently private and uses an All Rights Reserved license.
