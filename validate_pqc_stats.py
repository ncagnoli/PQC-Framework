#!/usr/bin/env python3
import os, math, argparse
import pymysql
import pandas as pd
import numpy as np

# ---------- Config por env/flags ----------
def parse_args():
    p = argparse.ArgumentParser(description="Valida pqc_stats contra pqc_results")
    p.add_argument("--host", default=os.getenv("DB_HOST", "localhost"))
    p.add_argument("--port", type=int, default=int(os.getenv("DB_PORT", "3306")))
    p.add_argument("--user", default=os.getenv("DB_USER", "pqc"))
    p.add_argument("--password", default=os.getenv("DB_PASS", "pqc"))
    p.add_argument("--database", default=os.getenv("DB_NAME", "pqc_framework"))
    p.add_argument("--role-filter", nargs="*", default=None, help="Ex.: --role-filter client server")
    p.add_argument("--test-run-id", nargs="*", default=None, help="Filtra test_run_id (ex.: --test-run-id 1 2 3)")
    p.add_argument("--write-csv", default=None, help="Se definido, grava discrepâncias em CSV")
    p.add_argument("--eps-rel", type=float, default=1e-9, help="Tolerância relativa para comparação de DOUBLE")
    p.add_argument("--eps-abs", type=float, default=1e-9, help="Tolerância absoluta para comparação de DOUBLE")
    return p.parse_args()

# ---------- Conexão ----------
def get_conn(args):
    return pymysql.connect(
        host=args.host, port=args.port, user=args.user, password=args.password,
        database=args.database, cursorclass=pymysql.cursors.DictCursor, autocommit=True
    )

# ---------- Percentis iguais ao SQL (rn = CEIL(p*n)) ----------
def pct_ceiling(arr, p):
    n = len(arr)
    if n == 0:
        return np.nan
    k = int(math.ceil(p * n))
    if k < 1: k = 1
    if k > n: k = n
    return float(arr[k-1])

def agg_series(series):
    """Retorna dict com avg, std (amostral), p50, p95, p99, min, max usando o método do SQL."""
    a = series.dropna().to_numpy()
    n = a.size
    if n == 0:
        return dict(avg=np.nan, std=np.nan, p50=np.nan, p95=np.nan, p99=np.nan, min=np.nan, max=np.nan)
    a_sorted = np.sort(a)
    avg = float(a.mean())
    std = float(a.std(ddof=1)) if n >= 2 else None  # STDDEV_SAMP retorna NULL com n<2
    return dict(
        avg=avg,
        std=(np.nan if std is None else std),
        p50=pct_ceiling(a_sorted, 0.50),
        p95=pct_ceiling(a_sorted, 0.95),
        p99=pct_ceiling(a_sorted, 0.99),
        min=float(a_sorted[0]),
        max=float(a_sorted[-1]),
    )

def almost_equal(a, b, eps_rel=1e-9, eps_abs=1e-9):
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return abs(a - b) <= max(eps_abs, eps_rel * max(1.0, abs(a), abs(b)))

def main():
    args = parse_args()
    conn = get_conn(args)

    # ----- Carrega pqc_results -----
    where = ["1=1"]
    params = {}
    if args.role_filter:
        where.append("role IN %(roles)s")
        params["roles"] = tuple(args.role_filter)
    if args.test_run_id:
        where.append("test_run_id IN %(runs)s")
        params["runs"] = tuple(args.test_run_id)

    sql_results = f"""
      SELECT
        test_run_id, role, test_type, openssh_branch, key_label,
        cycles, instructions, branch_misses, ipc, bpc
      FROM pqc_results
      WHERE {' AND '.join(where)}
    """
    with conn.cursor() as cur:
        cur.execute(sql_results, params)
        rows = cur.fetchall()
    if not rows:
        print("Nenhuma linha em pqc_results com os filtros fornecidos.")
        return

    df = pd.DataFrame(rows)

    # ----- Agrupa e calcula métricas por grupo -----
    keys = ["test_run_id","role","test_type","openssh_branch","key_label"]
    metrics = {
        "cycles": "cycles",
        "instructions": "instructions",
        "branch_misses": "branch_misses",
        "ipc": "ipc",
        "bpc": "bpc",
    }

    groups = df.groupby(keys, dropna=False)
    records = []
    for grp_key, g in groups:
        rec = dict(zip(keys, grp_key))
        rec["n_rows"] = int(len(g))

        for mname, col in metrics.items():
            stats = agg_series(g[col])
            prefix = {
                "cycles":"cycles",
                "instructions":"instr",
                "branch_misses":"br",
                "ipc":"ipc",
                "bpc":"bpc"
            }[mname]
            rec[f"{prefix}_avg"] = stats["avg"]
            rec[f"{prefix}_std"] = stats["std"]
            rec[f"{prefix}_p50"] = stats["p50"]
            rec[f"{prefix}_p95"] = stats["p95"]
            rec[f"{prefix}_p99"] = stats["p99"]
            rec[f"{prefix}_min"] = stats["min"]
            rec[f"{prefix}_max"] = stats["max"]
        records.append(rec)

    df_calc = pd.DataFrame.from_records(records)

    # ----- Carrega pqc_stats -----
    where_stats = ["1=1"]
    params_stats = {}
    if args.role_filter:
        where_stats.append("role IN %(roles)s")
        params_stats["roles"] = tuple(args.role_filter)
    if args.test_run_id:
        where_stats.append("test_run_id IN %(runs)s")
        params_stats["runs"] = tuple(args.test_run_id)

    sql_stats = f"""
      SELECT *
      FROM pqc_stats
      WHERE {' AND '.join(where_stats)}
    """
    with conn.cursor() as cur:
        cur.execute(sql_stats, params_stats)
        st = cur.fetchall()
    df_stats = pd.DataFrame(st) if st else pd.DataFrame(columns=df_calc.columns)

    # ----- Join para comparar -----
    merge_cols = keys
    merged = df_calc.merge(df_stats, on=merge_cols, suffixes=("_calc", "_stored"), how="outer", indicator=True)

    # detecta grupos faltantes / extras
    missing_in_stats = merged[merged["_merge"] == "left_only"][merge_cols]
    extra_in_stats   = merged[merged["_merge"] == "right_only"][merge_cols]

    # compara valores
    compare_fields = ["n_rows"] + [
        f"{p}_{suf}"
        for p in ("cycles","instr","br","ipc","bpc")
        for suf in ("avg","std","p50","p95","p99","min","max")
    ]

    mismatches = []
    for idx, row in merged[merged["_merge"]=="both"].iterrows():
        row_mismatch = []
        for f in compare_fields:
            f_calc   = f"{f}_calc"
            f_stored = f"{f}_stored"
            vcalc   = row.get(f_calc, np.nan)
            vstored = row.get(f_stored, np.nan)
            ok = (vcalc == vstored) if f=="n_rows" else almost_equal(vcalc, vstored, args.eps_rel, args.eps_abs)
            if not ok:
                row_mismatch.append({
                    **{k: row[k] for k in keys},
                    "field": f,
                    "calc": vcalc,
                    "stored": vstored,
                    "abs_err": (np.nan if (pd.isna(vcalc) or pd.isna(vstored)) else abs(vcalc - vstored)),
                })
        if row_mismatch:
            mismatches.extend(row_mismatch)

    # ----- Saída -----
    total_groups_calc = len(df_calc)
    total_groups_stats = len(df_stats)
    matched_groups = total_groups_calc - len(missing_in_stats) - len({tuple(r) for r in [tuple(x) for x in extra_in_stats.values]})
    groups_with_mismatch = len({tuple((m[k] for k in keys)) for m in mismatches})

    print("==== Resumo ====")
    print(f"Grupos calculados (pqc_results): {total_groups_calc}")
    print(f"Grupos na pqc_stats:            {total_groups_stats}")
    print(f"Grupos faltando em pqc_stats:   {len(missing_in_stats)}")
    print(f"Grupos extras em pqc_stats:     {len(extra_in_stats)}")
    print(f"Grupos com discrepâncias:       {groups_with_mismatch}")
    print(f"Métricas com discrepância:      {len(mismatches)}")
    print()

    if len(missing_in_stats):
        print(">> Faltando em pqc_stats (primeiros 10):")
        print(missing_in_stats.head(10).to_string(index=False))
        print()
    if len(extra_in_stats):
        print(">> Extras em pqc_stats (primeiros 10):")
        print(extra_in_stats.head(10).to_string(index=False))
        print()

    if mismatches:
        df_mm = pd.DataFrame(mismatches)
        # ordena por grupo e nome de campo
        df_mm = df_mm.sort_values(keys + ["field"]).reset_index(drop=True)
        print(">> Discrepâncias (primeiras 20):")
        print(df_mm.head(20).to_string(index=False))
        if args.write_csv:
            df_mm.to_csv(args.write_csv, index=False)
            print(f"\nArquivo CSV escrito: {args.write_csv}")
    else:
        print("Tudo OK: pqc_stats confere com os cálculos do Python dentro das tolerâncias.")

if __name__ == "__main__":
    main()

