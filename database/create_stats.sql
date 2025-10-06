INSERT INTO pqc_results_stats (
  test_run_id, role, test_type, openssh_branch, key_label, n_rows, n_iters,
  cycles_avg, cycles_std, cycles_cv, cycles_p50, cycles_p95, cycles_p99, cycles_min, cycles_max, cycles_ci95_low, cycles_ci95_high,
  instr_avg,  instr_std,  instr_cv,  instr_p50,  instr_p95,  instr_p99,  instr_min,  instr_max,  instr_ci95_low,  instr_ci95_high,
  cache_misses_avg, cache_misses_std, cache_misses_cv, cache_misses_p50, cache_misses_p95, cache_misses_p99, cache_misses_min, cache_misses_max,
  branch_misses_avg, branch_misses_std, branch_misses_cv, branch_misses_p50, branch_misses_p95, branch_misses_p99, branch_misses_min, branch_misses_max,
  page_faults_avg,  page_faults_std,  page_faults_cv,  page_faults_p50,  page_faults_p95,  page_faults_p99,  page_faults_min,  page_faults_max,
  context_switches_avg, context_switches_std, context_switches_cv, context_switches_p50, context_switches_p95, context_switches_p99, context_switches_min, context_switches_max,
  cpu_migrations_avg, cpu_migrations_std, cpu_migrations_cv, cpu_migrations_p50, cpu_migrations_p95, cpu_migrations_p99, cpu_migrations_min, cpu_migrations_max,
  cpi_avg, cpi_p50, cpi_p95, ipc_avg, ipc_p50, ipc_p95, mpki_avg, mpki_p50, mpki_p95, bmr_avg,  bmr_p50,  bmr_p95, pfk_avg,  pfk_p50,  pfk_p95
)
WITH
meta AS (
  SELECT
    test_run_id, role,
    MIN(test_type) AS test_type,
    MIN(openssh_branch) AS openssh_branch,
    MIN(key_label) AS key_label,
    COUNT(*) AS n_rows,
    COUNT(DISTINCT iteration) AS n_iters
  FROM pqc_results
  GROUP BY test_run_id, role
),
perf AS (
  SELECT test_run_id, role, 'cycles' AS m, cycles AS v FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'instructions', instructions FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'cache_misses', cache_misses FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'branch_misses', branch_misses FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'page_faults', page_faults FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'context_switches', context_switches FROM pqc_results
  UNION ALL SELECT test_run_id, role, 'cpu_migrations', cpu_migrations FROM pqc_results
),
perf_cnt AS (
  SELECT test_run_id, role, m, COUNT(*) AS n
  FROM perf WHERE v IS NOT NULL
  GROUP BY test_run_id, role, m
),
perf_base AS (
  SELECT
    p.test_run_id, p.role, p.m,
    AVG(p.v) AS avg_v,
    STDDEV_SAMP(p.v) AS std_v,
    MIN(p.v) AS min_v,
    MAX(p.v) AS max_v
  FROM perf p
  WHERE p.v IS NOT NULL
  GROUP BY p.test_run_id, p.role, p.m
),
perf_rnk AS (
  SELECT
    p.test_run_id, p.role, p.m, p.v,
    ROW_NUMBER() OVER (PARTITION BY p.test_run_id, p.role, p.m ORDER BY p.v) AS rn,
    COUNT(*)    OVER (PARTITION BY p.test_run_id, p.role, p.m) AS cnt
  FROM perf p
  WHERE p.v IS NOT NULL
),
p50 AS (
  SELECT test_run_id, role, m, AVG(v) AS p50
  FROM perf_rnk
  WHERE rn IN (FLOOR((cnt+1)/2), CEIL((cnt+1)/2))
  GROUP BY test_run_id, role, m
),
p95 AS (
  SELECT t.test_run_id, t.role, t.m, MAX(t.v) AS p95
  FROM (SELECT *, CEIL(0.95*cnt) AS pos FROM perf_rnk) t
  WHERE t.rn = t.pos
  GROUP BY t.test_run_id, t.role, t.m
),
p99 AS (
  SELECT t.test_run_id, t.role, t.m, MAX(t.v) AS p99
  FROM (SELECT *, CEIL(0.99*cnt) AS pos FROM perf_rnk) t
  WHERE t.rn = t.pos
  GROUP BY t.test_run_id, t.role, t.m
),
perf_all AS (
  SELECT
    b.test_run_id, b.role, b.m,
    b.avg_v, b.std_v, c.n, p50.p50, p95.p95, p99.p99, b.min_v, b.max_v
  FROM perf_base b
  JOIN perf_cnt c USING (test_run_id, role, m)
  LEFT JOIN p50 USING (test_run_id, role, m)
  LEFT JOIN p95 USING (test_run_id, role, m)
  LEFT JOIN p99 USING (test_run_id, role, m)
),
rat AS (
  SELECT
    test_run_id, role,
    CASE WHEN instructions > 0 THEN cycles/instructions ELSE NULL END AS cpi,
    CASE WHEN cycles > 0 THEN instructions/cycles ELSE NULL END AS ipc,
    CASE WHEN instructions > 0 THEN 1000.0*cache_misses/instructions ELSE NULL END AS mpki,
    CASE WHEN instructions > 0 THEN branch_misses/instructions ELSE NULL END AS bmr,
    CASE WHEN instructions > 0 THEN 1000.0*page_faults/instructions ELSE NULL END AS pfk
  FROM pqc_results
),
rat_unp AS (
  SELECT test_run_id, role, 'cpi'  AS m, cpi  AS v FROM rat
  UNION ALL SELECT test_run_id, role, 'ipc',  ipc  FROM rat
  UNION ALL SELECT test_run_id, role, 'mpki', mpki FROM rat
  UNION ALL SELECT test_run_id, role, 'bmr',  bmr  FROM rat
  UNION ALL SELECT test_run_id, role, 'pfk',  pfk  FROM rat
),
rat_rnk AS (
  SELECT
    r.test_run_id, r.role, r.m, r.v,
    ROW_NUMBER() OVER (PARTITION BY r.test_run_id, r.role, r.m ORDER BY r.v) AS rn,
    COUNT(*)    OVER (PARTITION BY r.test_run_id, r.role, r.m) AS cnt
  FROM rat_unp r
  WHERE r.v IS NOT NULL
),
rat_base AS (
  SELECT test_run_id, role, m, AVG(v) AS avg_v
  FROM rat_unp
  WHERE v IS NOT NULL
  GROUP BY test_run_id, role, m
),
rat_p50 AS (
  SELECT test_run_id, role, m, AVG(v) AS p50
  FROM rat_rnk
  WHERE rn IN (FLOOR((cnt+1)/2), CEIL((cnt+1)/2))
  GROUP BY test_run_id, role, m
),
rat_p95 AS (
  SELECT t.test_run_id, t.role, t.m, MAX(t.v) AS p95
  FROM (SELECT *, CEIL(0.95*cnt) AS pos FROM rat_rnk) t
  WHERE t.rn = t.pos
  GROUP BY t.test_run_id, t.role, t.m
),
rat_all AS (
  SELECT b.test_run_id, b.role, b.m, b.avg_v, p50.p50, p95.p95
  FROM rat_base b
  LEFT JOIN rat_p50 p50 USING (test_run_id, role, m)
  LEFT JOIN rat_p95 p95 USING (test_run_id, role, m)
)
SELECT
  m.test_run_id, m.role, m.test_type, m.openssh_branch, m.key_label, m.n_rows, m.n_iters,

  MAX(CASE WHEN a.m='cycles' THEN a.avg_v END),
  MAX(CASE WHEN a.m='cycles' THEN a.std_v END),
  MAX(CASE WHEN a.m='cycles' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='cycles' THEN a.p50 END),
  MAX(CASE WHEN a.m='cycles' THEN a.p95 END),
  MAX(CASE WHEN a.m='cycles' THEN a.p99 END),
  MAX(CASE WHEN a.m='cycles' THEN a.min_v END),
  MAX(CASE WHEN a.m='cycles' THEN a.max_v END),
  MAX(CASE WHEN a.m='cycles' THEN a.avg_v - 1.96*(a.std_v/SQRT(a.n)) END),
  MAX(CASE WHEN a.m='cycles' THEN a.avg_v + 1.96*(a.std_v/SQRT(a.n)) END),

  MAX(CASE WHEN a.m='instructions' THEN a.avg_v END),
  MAX(CASE WHEN a.m='instructions' THEN a.std_v END),
  MAX(CASE WHEN a.m='instructions' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='instructions' THEN a.p50 END),
  MAX(CASE WHEN a.m='instructions' THEN a.p95 END),
  MAX(CASE WHEN a.m='instructions' THEN a.p99 END),
  MAX(CASE WHEN a.m='instructions' THEN a.min_v END),
  MAX(CASE WHEN a.m='instructions' THEN a.max_v END),
  MAX(CASE WHEN a.m='instructions' THEN a.avg_v - 1.96*(a.std_v/SQRT(a.n)) END),
  MAX(CASE WHEN a.m='instructions' THEN a.avg_v + 1.96*(a.std_v/SQRT(a.n)) END),

  MAX(CASE WHEN a.m='cache_misses' THEN a.avg_v END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.std_v END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.p50 END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.p95 END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.p99 END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.min_v END),
  MAX(CASE WHEN a.m='cache_misses' THEN a.max_v END),

  MAX(CASE WHEN a.m='branch_misses' THEN a.avg_v END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.std_v END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.p50 END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.p95 END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.p99 END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.min_v END),
  MAX(CASE WHEN a.m='branch_misses' THEN a.max_v END),

  MAX(CASE WHEN a.m='page_faults' THEN a.avg_v END),
  MAX(CASE WHEN a.m='page_faults' THEN a.std_v END),
  MAX(CASE WHEN a.m='page_faults' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='page_faults' THEN a.p50 END),
  MAX(CASE WHEN a.m='page_faults' THEN a.p95 END),
  MAX(CASE WHEN a.m='page_faults' THEN a.p99 END),
  MAX(CASE WHEN a.m='page_faults' THEN a.min_v END),
  MAX(CASE WHEN a.m='page_faults' THEN a.max_v END),

  MAX(CASE WHEN a.m='context_switches' THEN a.avg_v END),
  MAX(CASE WHEN a.m='context_switches' THEN a.std_v END),
  MAX(CASE WHEN a.m='context_switches' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='context_switches' THEN a.p50 END),
  MAX(CASE WHEN a.m='context_switches' THEN a.p95 END),
  MAX(CASE WHEN a.m='context_switches' THEN a.p99 END),
  MAX(CASE WHEN a.m='context_switches' THEN a.min_v END),
  MAX(CASE WHEN a.m='context_switches' THEN a.max_v END),

  MAX(CASE WHEN a.m='cpu_migrations' THEN a.avg_v END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.std_v END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.std_v/a.avg_v END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.p50 END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.p95 END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.p99 END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.min_v END),
  MAX(CASE WHEN a.m='cpu_migrations' THEN a.max_v END),

  MAX(CASE WHEN rr.m='cpi'  THEN rr.avg_v END),
  MAX(CASE WHEN rr.m='cpi'  THEN rr.p50   END),
  MAX(CASE WHEN rr.m='cpi'  THEN rr.p95   END),

  MAX(CASE WHEN rr.m='ipc'  THEN rr.avg_v END),
  MAX(CASE WHEN rr.m='ipc'  THEN rr.p50   END),
  MAX(CASE WHEN rr.m='ipc'  THEN rr.p95   END),

  MAX(CASE WHEN rr.m='mpki' THEN rr.avg_v END),
  MAX(CASE WHEN rr.m='mpki' THEN rr.p50   END),
  MAX(CASE WHEN rr.m='mpki' THEN rr.p95   END),

  MAX(CASE WHEN rr.m='bmr'  THEN rr.avg_v END),
  MAX(CASE WHEN rr.m='bmr'  THEN rr.p50   END),
  MAX(CASE WHEN rr.m='bmr'  THEN rr.p95   END),

  MAX(CASE WHEN rr.m='pfk'  THEN rr.avg_v END),
  MAX(CASE WHEN rr.m='pfk'  THEN rr.p50   END),
  MAX(CASE WHEN rr.m='pfk'  THEN rr.p95   END)

FROM meta m
LEFT JOIN perf_all a  ON a.test_run_id=m.test_run_id AND a.role=m.role
LEFT JOIN rat_all  rr ON rr.test_run_id=m.test_run_id AND rr.role=m.role
GROUP BY m.test_run_id, m.role, m.test_type, m.openssh_branch, m.key_label, m.n_rows, m.n_iters
ORDER BY CAST(m.test_run_id AS UNSIGNED), m.role;

