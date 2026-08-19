#!/usr/bin/env python3
"""Apply a SQL script to cwa_db using the app's DATABASE_URL (backend/.env).

Usage (from backend/):
    ../venv/bin/python tools/sql/apply_sql.py tools/sql/<script>.sql [--dry-run]

Statements are split on ';'. Rows returned by SELECT statements are printed, so
the verification query at the end of each script shows the resulting state.
--dry-run executes inside a transaction and rolls back at the end.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine, text  # noqa: E402
from common import DATABASE_SYNC_URL  # noqa: E402


def split_statements(sql: str) -> list[str]:
    stmts = []
    for raw in sql.split(';'):
        lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.strip().startswith('--')]
        if lines:
            stmts.append('\n'.join(lines))
    return stmts


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    sql = open(path, encoding='utf8').read()
    stmts = [s for s in split_statements(sql) if s.strip().upper() not in ('BEGIN', 'COMMIT')]

    engine = create_engine(DATABASE_SYNC_URL)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for stmt in stmts:
                result = conn.execute(text(stmt))
                first = stmt.strip().split()[0].upper()
                if result.returns_rows:
                    rows = result.mappings().all()
                    if rows:
                        cols = list(rows[0].keys())
                        print(' | '.join(cols))
                        for r in rows:
                            print(' | '.join(str(r[c]) for c in cols))
                    print(f"({len(rows)} rows)")
                else:
                    print(f"{first}: {result.rowcount} row(s) affected")
            if dry_run:
                trans.rollback()
                print("DRY RUN — rolled back")
            else:
                trans.commit()
                print("COMMITTED")
        except Exception:
            trans.rollback()
            raise
    return 0


if __name__ == '__main__':
    sys.exit(main())
