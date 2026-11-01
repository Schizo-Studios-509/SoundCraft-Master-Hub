# Source cleanup — completed

This cleanup was merged into `main` through [pull request #4](https://github.com/Schizo-Studios-509/SoundCraft-Master-Hub/pull/4) on October 31, 2026 (merge commit `02a38a1c3369a6da3611076057aa7760f23bc003`).

## 1. SoundCraft AI
Removed the accidentally committed `SoundCraft AI/$(python3 -m site --user-site)/` directory from the current `main` tree. It contained **10,506 tracked dependency/cache files** (roughly 132 MB). Git history retains previous objects. Do not remove application code from `SoundCraft AI/`; review external dependency licenses and install requirements separately.

## 2. Frequency Library
Verified matching Git blob SHA values and eliminated six redundant paths across five sets of identical entries (including the extra extensionless golden-ratio file). Original canonical documents remain in `Frequency Library/`. File-name hyperlinks to removed aliases must be updated if referenced outside the repo.

## 3. Smith Equivalence App
Moved v2, v3, v4, v5, and v6.1 scripts without changing their contents into `Smith Equivalence App/Archive/`. Kept `SEA_v7.1.py`, `birth_harmonics_7to1.py`, `smith_equivalence_pyto_app.py`, and the original unnumbered script in place until dependencies are verified. Removed six empty (zero-byte) Python placeholder modules. No active Python implementations were overwritten.

## Notes
- The current Git tree is reduced to approximately 114 files/directories.
- Existing Git history still contains earlier large files; this cleanup does *not* rewrite history or reduce remote Git storage immediately.
- All Rights Reserved and third-party license rights remain in effect.
- Pull request #4 did not change the website branch or publication settings.
