#!/usr/bin/env python3
import os, math, argparse
import numpy as np
import pandas as pd
import pymysql

METRICS = ["cycles", "instructions", "branch_misses", "ipc", "bpc"]
KEYS = ["test_run_id","role","test_type","openssh_branch","key_label"]

def parse_args():
    p = argparse.ArgumentParser(description="Detecta linhas que distorcem o STD por grupo")
    p.add_argument("--host", default=os.getenv("DB_HOST","localhost"))
    p.add_argument("--port", type=int, default=int(os.getenv("DB_PORT","3306")))
    p.add_argument("--user", default=os.getenv("DB_USER","pqc"))
    p.add_argument("--password", default=os.getenv("DB_PASS","pqc"))
    p.add_argument("--database", default=os.getenv("DB_NAME","pqc_framework"))
    p.add_argument("--role-filter", nargs="*", default=None)
    p.add_argument("--test-run-id", nargs="*", default=None)
    p.add_argument("--cv-th", type=float, default=0.05, help="limiar de coeficiente de variação (std/mean) para marcar grupo")
    p.add_argument("--z-th", type=float, default=3.0, help="limiar de |z|")
    p.add_argument("--mz-th", type=float, default=3.5, help="limiar de |modified z|")
    p.add_argument("--iqr-k", type=float, default=1.5, help="multiplicador do IQR")
    p.add_argument("--write-csv", default=None, help="salva CSV com outliers")
    return p.parse_args()

def get_conn(a):
    return pymysql.connect(host=a.host, port=a.port, user=a.user, password=a.password,
                           database=a.database, cursorclass=pymysql.cursors.DictCursor, autocommit=True)

def modified_z_scores(x):
    # x: 1D np.array
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    if mad == 0:
        return np.zeros_like(x, dtype=float)
    return 0.6745 * (x - med) / mad

def group_percentiles(arr, ps):
    a = np.sort(arr)
    n = len(a)
    out = {}
    for p in ps:
        k = int(math.ceil(p * n))
        k = min(max(k,1), n)
        out[p] = float(a[k-1])
    return out

def describe_vector(x):
    x = x.astype(float)
    n = x.size
    mean = float(x.mean())
    std  = float(x.std(ddof=1)) if n >= 2 else float("nan")
    med  = float(np.median(x))
    q1, q3 = np.percentile(x, [25, 75], method="linear")
    iqr = q3 - q1
    cv = (std/mean) if (not np.isnan(std) and mean != 0) else float("inf")
    return dict(n=n, mean=mean, std=std, median=med, q1=q1, q3=q3, iqr=iqr, cv=cv)

def main():
    args = parse_args()
    conn = get_conn(args)

    # ---------- carrega dados ----------
    where = ["1=1"]
    params = {}
    if args.role_filter:
        where.append("role IN %(roles)s"); params["roles"] = tuple(args.role_filter)
    if args.test_run_id:
        where.append("test_run_id IN %(runs)s"); params["runs"] = tuple(args.test_run_id)

    sql = f"""
      SELECT
        id, source_file, file_line, ts, iteration,
        test_run_id, role, test_type, openssh_branch, key_label,
        cycles, instructions, branch_misses, ipc, bpc
      FROM pqc_results
      WHERE {' AND '.join(where)}
    """
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    if not rows:
        print("Sem linhas com os filtros dados."); return

    df = pd.DataFrame(rows)
    # sanity básica: remove linhas com NaN nas métricas
    df = df.dropna(subset=METRICS)

    # ---------- avalia std global por métrica p/ limiar de topo (p95) ----------
    std_globais = {}
    for m in METRICS:
        # std por grupo
        stds = df.groupby(KEYS)[m].std(ddof=1)
        std_globais[m] = np.nanpercentile(stds.to_numpy().astype(float), 95)

    # ---------- varredura por grupo ----------
    outlier_rows = []
    group_summary = []

    for gkey, g in df.groupby(KEYS, dropna=False):
        rec_sum = dict(zip(KEYS, gkey))
        rec_sum["n_rows"] = int(len(g))

        for m in METRICS:
            x = g[m].to_numpy(dtype=float)
            stats = describe_vector(x)

            # limites robustos
            mz = modified_z_scores(x)
            z  = (x - stats["mean"]) / stats["std"] if (not np.isnan(stats["std"]) and stats["std"] > 0) else np.zeros_like(x)
            lo = stats["q1"] - args.iqr_k * stats["iqr"]
            hi = stats["q3"] + args.iqr_k * stats["iqr"]

            # marca outliers por qualquer critério
            is_out = (np.abs(z) >= args.z_th) | (np.abs(mz) >= args.mz_th) | (x < lo) | (x > hi)

            # registra grupo "ruim" se CV alto OU std acima do p95 global da métrica
            flag_group = (stats["cv"] >= args.cv_th) or (not np.isnan(stats["std"]) and stats["std"] >= std_globais[m])

            rec_sum[f"{m}_mean"] = stats["mean"]
            rec_sum[f"{m}_std"]  = stats["std"]
            rec_sum[f"{m}_cv"]   = stats["cv"]
            rec_sum[f"{m}_p95_std_glob"] = std_globais[m]
            rec_sum[f"{m}_flag"] = bool(flag_group)

            if flag_group and is_out.any():
                contrib = (x - stats["mean"])**2  # contribuição para a variância
                order = np.argsort(contrib)[::-1]
                # captura todos outliers; se preferir top-k, fatie order[:k]
                for idx in order:
                    if not is_out[idx]:
                        continue
                    row = g.iloc[idx]
                    outlier_rows.append({
                        **{k: row[k] for k in ["id","source_file","file_line","ts","iteration"]},
                        **rec_sum,  # chaves do grupo
                        "metric": m,
                        "value": float(x[idx]),
                        "mean": stats["mean"],
                        "std": stats["std"],
                        "z": float(z[idx]) if np.isfinite(z[idx]) else np.nan,
                        "modified_z": float(mz[idx]),
                        "iqr_lo": lo, "iqr_hi": hi,
                        "contrib_var": float(contrib[idx]),
                    })

        group_summary.append(rec_sum)

    df_grp = pd.DataFrame(group_summary)
    df_out = pd.DataFrame(outlier_rows)

    # ---------- saída ----------
    # resumo rápido: quantos grupos por métrica com flag
    print("==== Resumo por métrica (grupos com STD alto) ====")
    for m in METRICS:
        cnt = int(df_grp[f"{m}_flag"].fillna(False).sum())
        print(f"{m:16s}: {cnt} grupo(s) marcados")

    print("\n==== Top 15 outliers por contribuição ao STD (qualquer métrica) ====")
    if not df_out.empty:
        cols_show = (KEYS + ["n_rows","metric","value","mean","std","z","modified_z","iqr_lo","iqr_hi",
                             "id","source_file","file_line","ts","iteration","contrib_var"])
        print(df_out.sort_values("contrib_var", ascending=False)[cols_show].head(15).to_string(index=False))
    else:
        print("Nenhum outlier encontrado nos grupos marcados.")

    # grava CSV se pedido
    if args.write_csv and not df_out.empty:
        df_out.sort_values(["metric","contrib_var"], ascending=[True, False]).to_csv(args.write_csv, index=False)
        print(f"\nCSV salvo: {args.write_csv}")

if __name__ == "__main__":
    main()

