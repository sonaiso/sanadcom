# Security remediation record — committed database dumps (2026-11-02)

## Finding
The public repository tracked live database backups:

| File | Size | Content (verified by restoring locally, identities not recorded here) |
|---|---|---|
| `local_db_backup.dump` | 19.1 MB | PostgreSQL custom dump: `iam_user` (9 rows, 20 argon2id password hashes across user tables), `knox_authtoken` (11 rows), `django_session` (96 rows), `auditlog_logentry` (762 rows), account e-mail tables, applied controls, answers |
| `sanadcom-postgres-20260701-110303.dump`, `…-111128.dump` | 19.1 MB each | Same schema, two snapshots |
| `db-backup-sqlite-20260312-103213/` | 3.5 MB | SQLite WAL/SHM files of `ciso-assistant.sqlite3` and `huey.db` (contain `admin@example.com` rows) |
| `provision_role_users.py` | — | Hard-coded shared demo password for seven role accounts |

`.gitignore` already listed `*.dump`; the files had been force-added. E-mail domains observed are mostly demo (`example.com`, `sico.sa`), but session keys and token digests are live secrets regardless of whether the accounts are demo accounts.

## Done in this change
- Removed the dumps and the SQLite backup directory from the tree.
- Added `scripts/check_repo_hygiene.py` to CI: tracked database dumps, SQL files, SQLite stores and WAL/SHM files, `backup-*.json`, keys, `.env` files, and files over 15 MB fail the build. `all_frameworks_export.csv` (22 MB) is listed as a legacy debt, not an allowance.
- `provision_role_users.py` now requires `SANADCOM_DEMO_PASSWORD` from the environment and refuses to run without it.

## Required owner actions (cannot be done from a pull request)
1. **Purge history.** The files remain in every clone's history until rewritten:
   ```bash
   pip install git-filter-repo
   git filter-repo --invert-paths \
     --path local_db_backup.dump \
     --path sanadcom-postgres-20260701-110303.dump \
     --path sanadcom-postgres-20260701-111128.dump \
     --path backup-20260312-103121.json \
     --path db-backup-sqlite-20260312-103213
   git push --force --all && git push --force --tags
   ```
   Then ask GitHub Support to purge cached views of the old objects, and have every collaborator re-clone.
2. **Rotate** the Django `SECRET_KEY`, the database credentials used by those instances, and every API key or OIDC secret that existed on those instances.
3. **Invalidate** all Knox tokens and Django sessions on any instance that was restored from these dumps (`knox_authtoken`, `django_session`), and force a password reset for the nine accounts.
4. **Decide** whether the seven `*.sa` demo accounts in `provision_role_users.py` ever existed on a reachable instance; if so, treat their shared password as compromised.
5. Review `all_frameworks_export.csv` for personal data before deciding whether it stays.

## What this record is not
This is a hygiene and incident record. It is not a compliance judgment about Sanadcom or any framework control; those pass through the constitutional transition chain like everything else.
