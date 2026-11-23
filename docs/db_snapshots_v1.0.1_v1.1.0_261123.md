# Database snapshots around the v1.1.0 release

Recorded 2026-11-23, when v1.1.0 (new user interface) was merged to `main` and tagged.

## Location

iCloud Drive, written from m1:

`/Users/harry/Library/Mobile Documents/com~apple~CloudDocs/1drive_ic_aproject_imac/cognosa/cognosa_db_backups`

## Files

| File | Source | Version | Notes |
|---|---|---|---|
| `cwa_db_261122_with_version+login_updates_v1.1.0.dump` | local m1 | 1.1.0 | Initialized for v1.1.0: `app_version` set to 1.1.0 and the new `index_page` login HTML in `api_settings` |
| `dev_cwa_db_261120_2306_v1.0.1.dump` | dev (AWS) | 1.0.1 | |
| `demo_cwa_db_261120_2303_v1.0.1.dump` | demo (AWS) | 1.0.1 | |
| `local_m1_cwa_db_261120_v1.0.1.dump` | local m1 | 1.0.1 | Last local database at v1.0.1 |

## Rolling back to v1.0.1

The code is at tag `v1.0.1` (`git checkout v1.0.1`), which includes its built
`backend/static`. Restore the matching v1.0.1 snapshot with it, rather than editing
`app_version` and `index_page` by hand. v1.1.0 made no schema change.

Restore procedure: see `DB_BACKUP_RESTORE_PLAN.md`.
