#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import a single PQC benchmarking CSV file into MariaDB (table: pqc_results).
- One file per run (--file)
- Robust logging and diagnostics
- Handles UTF-8 with BOM (utf-8-sig)
- Auto-detects client/server layout (validated against --role)
- Computes iteration for server (iteration = file_line - 1)
- Idempotent via SHA256 row_hash (UNIQUE in DB)
"""

import argparse
import csv
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

import mysql.connector
from dateutil import parser as dtparser


CLIENT_COLUMNS = [
    "iteration", "timestamp", "cycles", "instructions", "cache-misses",
    "branch-misses", "page-faults", "context-switches", "cpu-migrations"
]
SERVER_COLUMNS = [
    "timestamp", "cycles", "instructions", "cache-misses",
    "branch-misses", "page-faults", "context-switches", "cpu-migrations"
]

INSERT_SQL = """
INSERT IGNORE INTO pqc_results
(test_run_id, role, source_file, file_line, ts, iteration,
 test_type, openssh_branch,
 key_type_primary, key_size_primary, key_type_secondary, key_size_secondary,
 cycles, instructions, cache_misses, branch_misses, page_faults, context_switches, cpu_migrations,
 row_hash)
VALUES
(%(test_run_id)s, %(role)s, %(source_file)s, %(file_line)s, %(ts)s, %(iteration)s,
 %(test_type)s, %(openssh_branch)s,
 %(key_type_primary)s, %(key_size_primary)s, %(key_type_secondary)s, %(key_size_secondary)s,
 %(cycles)s, %(instructions)s, %(cache_misses)s, %(branch_misses)s, %(page_faults)s, %(context_switches)s, %(cpu_migrations)s,
 %(row_hash)s)
"""

def parse_int(v: Optional[str]) -> Optional[int]:
    """Parse integer or return None."""
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if s == "":
        return None
    return int(s)

def parse_ts_iso_to_dt6(v: Optional[str]) -> Optional[datetime]:
    """Parse ISO-like timestamp into Python datetime; return None on failure."""
    if not v:
        return None
    try:
        return dtparser.parse(v)
    except Exception:
        return None

def build_row_hash(payload: Dict[str, Any]) -> str:
    """Build a stable SHA256 hash of normalized content."""
    parts = [f"{k}={'' if payload[k] is None else payload[k]}" for k in sorted(payload.keys())]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

def print_preview(label: str, row: Dict[str, Any]):
    """Pretty-print a small subset for diagnostics."""
    keys = ["file_line","iteration","ts","cycles","instructions","cache_misses","branch_misses","page_faults","context_switches","cpu_migrations"]
    subset = {k: (row.get(k).isoformat(timespec="microseconds") if isinstance(row.get(k), datetime) else row.get(k)) for k in keys}
    print(f"[PREVIEW] {label}: {subset}")

def main():
    ap = argparse.ArgumentParser(description="Import a single PQC CSV into MariaDB (pqc_results).")
    # DB
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--db", required=True)
    # File
    ap.add_argument("--file", required=True, help="Path to the CSV file to import")
    # Metadata
    ap.add_argument("--role", required=True, choices=["client", "server"], help="Measurement side")
    ap.add_argument("--test-run-id", required=True, help="Identifier for this run/batch")
    ap.add_argument("--test-type", required=True, choices=["classical", "pqc", "hybrid"], help="Test type")
    ap.add_argument("--openssh-branch", required=True, help="OpenSSH branch/version label")
    ap.add_argument("--key-type-primary", required=True, help="Primary key type (e.g., RSA, ECDSA, ML-KEM)")
    ap.add_argument("--key-size-primary", required=True, help="Primary key size (e.g., 2048, 3072, 44)")
    ap.add_argument("--key-type-secondary", default=None, help="Secondary key type (for hybrid)")
    ap.add_argument("--key-size-secondary", default=None, help="Secondary key size (for hybrid)")
    # Behavior
    ap.add_argument("--dry-run", action="store_true", help="Parse/validate only; do not write to DB")
    ap.add_argument("--progress-every", type=int, default=200, help="Print progress every N rows")
    ap.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = ap.parse_args()

    print("=== import_pqc_csv_v2 ===")
    print(f"[ARGS] host={args.host} port={args.port} user={args.user} db={args.db}")
    print(f"[ARGS] file={args.file}")
    print(f"[META] role={args.role} test_run_id={args.test_run_id} test_type={args.test_type} branch={args.openssh_branch}")
    print(f"[META] key_primary={args.key_type_primary}/{args.key_size_primary} key_secondary={args.key_type_secondary}/{args.key_size_secondary}")
    print(f"[MODE] dry_run={args.dry_run} verbose={args.verbose}")

    csv_path = Path(args.file)
    if not csv_path.is_file():
        raise SystemExit(f"[FATAL] CSV not found: {csv_path}")

    # Connect
    print("[DB] Connecting…")
    cnx = mysql.connector.connect(
        host=args.host, port=args.port, user=args.user,
        password=args.password, database=args.db, autocommit=False
    )
    cur = cnx.cursor()
    cur.execute("SELECT VERSION()")
    print(f"[DB] Connected. Server version: {cur.fetchone()[0]}")
    cur.execute("SELECT DATABASE()")
    print(f"[DB] Current database: {cur.fetchone()[0]}")

    inserted = ignored = errors = total = 0

    # Open CSV with utf-8-sig to strip BOM if present
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
        print(f"[CSV] Header: {header}")

        role = args.role.lower()
        required = set(CLIENT_COLUMNS if role == "client" else SERVER_COLUMNS)

        # Layout detection (allow any order; require all names)
        if not required.issubset(set(header)):
            raise SystemExit(f"[FATAL] Unexpected header for role={role}. Found: {header}")

        print(f"[CSV] Layout detected OK for role={role}. Starting parse…")

        try:
            for file_line, raw in enumerate(reader, start=1):
                total += 1
                try:
                    ts = parse_ts_iso_to_dt6(raw.get("timestamp"))
                    row = {
                        "test_run_id": args.test_run_id,
                        "role": role,
                        "source_file": csv_path.name,
                        "file_line": file_line,
                        "ts": ts,
                        "iteration": None,  # set below
                        "test_type": args.test_type.lower(),
                        "openssh_branch": args.openssh_branch,
                        "key_type_primary": args.key_type_primary,
                        "key_size_primary": parse_int(args.key_size_primary),
                        "key_type_secondary": args.key_type_secondary,
                        "key_size_secondary": parse_int(args.key_size_secondary) if args.key_size_secondary else None,
                        "cycles": parse_int(raw.get("cycles")),
                        "instructions": parse_int(raw.get("instructions")),
                        "cache_misses": parse_int(raw.get("cache-misses")),
                        "branch_misses": parse_int(raw.get("branch-misses")),
                        "page_faults": parse_int(raw.get("page-faults")),
                        "context_switches": parse_int(raw.get("context-switches")),
                        "cpu_migrations": parse_int(raw.get("cpu-migrations")),
                        "row_hash": None,
                    }

                    if role == "client":
                        row["iteration"] = parse_int(raw.get("iteration"))
                    else:
                        row["iteration"] = file_line - 1

                    payload = {
                        "test_run_id": row["test_run_id"],
                        "role": row["role"],
                        "source_file": row["source_file"],
                        "file_line": row["file_line"],
                        "ts": row["ts"].isoformat(timespec="microseconds") if row["ts"] else "",
                        "iteration": row["iteration"],
                        "test_type": row["test_type"],
                        "openssh_branch": row["openssh_branch"],
                        "key_type_primary": row["key_type_primary"],
                        "key_size_primary": row["key_size_primary"],
                        "key_type_secondary": row["key_type_secondary"] or "",
                        "key_size_secondary": row["key_size_secondary"] if row["key_size_secondary"] is not None else "",
                        "cycles": row["cycles"],
                        "instructions": row["instructions"],
                        "cache_misses": row["cache_misses"],
                        "branch_misses": row["branch_misses"],
                        "page_faults": row["page_faults"],
                        "context_switches": row["context_switches"],
                        "cpu_migrations": row["cpu_migrations"],
                    }
                    row["row_hash"] = build_row_hash(payload)

                    if total <= 3 or args.verbose:
                        print_preview("row", row)

                    if not args.dry_run:
                        cur.execute(INSERT_SQL, row)
                        if cur.rowcount == 1:
                            inserted += 1
                        else:
                            ignored += 1

                    if args.progress_every and (total % args.progress_every == 0):
                        print(f"[PROGRESS] processed={total} inserted={inserted} ignored={ignored} errors={errors}")

                except Exception as e:
                    errors += 1
                    print(f"[ERROR] {csv_path.name}:{file_line}: {e}")

            if not args.dry_run:
                cnx.commit()
                print("[DB] COMMIT done.")

        except Exception as e:
            print(f"[FATAL] Exception during import, rolling back: {e}")
            cnx.rollback()
            raise
        finally:
            cur.close()
            cnx.close()
            print("[DB] Connection closed.")

    print(f"[SUMMARY] file={csv_path.name} total={total} inserted={inserted} ignored={ignored} errors={errors}")
    if args.dry_run:
        print("[NOTE] DRY-RUN mode: no data written to DB.")

if __name__ == "__main__":
    main()

