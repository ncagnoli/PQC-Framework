/* ===== Popula pqc_stats para TODOS os test_run_id e roles ===== */
REPLACE INTO pqc_stats (
  test_run_id, role, test_type, openssh_branch, key_label, n_rows,
  cycles_avg, cycles_std, cycles_p50, cycles_p95, cycles_p99, cycles_min, cycles_max,
  instr_avg,  instr_std,  instr_p50,  instr_p95,  instr_p99,  instr_min,  instr_max,
  br_avg,     br_std,     br_p50,     br_p95,     br_p99,     br_min,     br_max,
  ipc_avg,    ipc_std,    ipc_p50,    ipc_p95,    ipc_p99,    ipc_min,    ipc_max,
  bpc_avg,    bpc_std,    bpc_p50,    bpc_p95,    bpc_p99,    bpc_min,    bpc_max
)
WITH
filtered AS (
  SELECT
    test_run_id, role, test_type, openssh_branch, key_label,
    cycles, instructions, branch_misses, ipc, bpc
  FROM pqc_results
  WHERE role IN ('client','server')
),
base AS (
  SELECT
    test_run_id, role, test_type, openssh_branch, key_label,
    COUNT(*) AS n_rows,
    AVG(cycles)        AS cycles_avg,
    STDDEV_SAMP(cycles) AS cycles_std,
    MIN(cycles)        AS cycles_min,
    MAX(cycles)        AS cycles_max,

    AVG(instructions)         AS instr_avg,
    STDDEV_SAMP(instructions) AS instr_std,
    MIN(instructions)         AS instr_min,
    MAX(instructions)         AS instr_max,

    AVG(branch_misses)         AS br_avg,
    STDDEV_SAMP(branch_misses) AS br_std,
    MIN(branch_misses)         AS br_min,
    MAX(branch_misses)         AS br_max,

    AVG(ipc)         AS ipc_avg,
    STDDEV_SAMP(ipc) AS ipc_std,
    MIN(ipc)         AS ipc_min,
    MAX(ipc)         AS ipc_max,

    AVG(bpc)         AS bpc_avg,
    STDDEV_SAMP(bpc) AS bpc_std,
    MIN(bpc)         AS bpc_min,
    MAX(bpc)         AS bpc_max
  FROM filtered
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
),

/* percentis por grupo */
r_cycles AS (
  SELECT f.*,
         ROW_NUMBER() OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label ORDER BY cycles) AS rn,
         COUNT(*)    OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label) AS n
  FROM filtered f
),
p_cycles AS (
  SELECT test_run_id, role, test_type, openssh_branch, key_label,
         MAX(CASE WHEN rn = CEIL(0.50*n) THEN cycles END) AS cycles_p50,
         MAX(CASE WHEN rn = CEIL(0.95*n) THEN cycles END) AS cycles_p95,
         MAX(CASE WHEN rn = CEIL(0.99*n) THEN cycles END) AS cycles_p99
  FROM r_cycles
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
),

r_instr AS (
  SELECT f.*,
         ROW_NUMBER() OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label ORDER BY instructions) AS rn,
         COUNT(*)    OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label) AS n
  FROM filtered f
),
p_instr AS (
  SELECT test_run_id, role, test_type, openssh_branch, key_label,
         MAX(CASE WHEN rn = CEIL(0.50*n) THEN instructions END) AS instr_p50,
         MAX(CASE WHEN rn = CEIL(0.95*n) THEN instructions END) AS instr_p95,
         MAX(CASE WHEN rn = CEIL(0.99*n) THEN instructions END) AS instr_p99
  FROM r_instr
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
),

r_br AS (
  SELECT f.*,
         ROW_NUMBER() OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label ORDER BY branch_misses) AS rn,
         COUNT(*)    OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label) AS n
  FROM filtered f
),
p_br AS (
  SELECT test_run_id, role, test_type, openssh_branch, key_label,
         MAX(CASE WHEN rn = CEIL(0.50*n) THEN branch_misses END) AS br_p50,
         MAX(CASE WHEN rn = CEIL(0.95*n) THEN branch_misses END) AS br_p95,
         MAX(CASE WHEN rn = CEIL(0.99*n) THEN branch_misses END) AS br_p99
  FROM r_br
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
),

r_ipc AS (
  SELECT f.*,
         ROW_NUMBER() OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label ORDER BY ipc) AS rn,
         COUNT(*)    OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label) AS n
  FROM filtered f
),
p_ipc AS (
  SELECT test_run_id, role, test_type, openssh_branch, key_label,
         MAX(CASE WHEN rn = CEIL(0.50*n) THEN ipc END) AS ipc_p50,
         MAX(CASE WHEN rn = CEIL(0.95*n) THEN ipc END) AS ipc_p95,
         MAX(CASE WHEN rn = CEIL(0.99*n) THEN ipc END) AS ipc_p99
  FROM r_ipc
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
),

r_bpc AS (
  SELECT f.*,
         ROW_NUMBER() OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label ORDER BY bpc) AS rn,
         COUNT(*)    OVER (PARTITION BY test_run_id, role, test_type, openssh_branch, key_label) AS n
  FROM filtered f
),
p_bpc AS (
  SELECT test_run_id, role, test_type, openssh_branch, key_label,
         MAX(CASE WHEN rn = CEIL(0.50*n) THEN bpc END) AS bpc_p50,
         MAX(CASE WHEN rn = CEIL(0.95*n) THEN bpc END) AS bpc_p95,
         MAX(CASE WHEN rn = CEIL(0.99*n) THEN bpc END) AS bpc_p99
  FROM r_bpc
  GROUP BY test_run_id, role, test_type, openssh_branch, key_label
)

SELECT
  b.test_run_id, b.role, b.test_type, b.openssh_branch, b.key_label, b.n_rows,
  b.cycles_avg, b.cycles_std, pc.cycles_p50, pc.cycles_p95, pc.cycles_p99, b.cycles_min, b.cycles_max,
  b.instr_avg,  b.instr_std,  pi.instr_p50,  pi.instr_p95,  pi.instr_p99,  b.instr_min,  b.instr_max,
  b.br_avg,     b.br_std,     pb.br_p50,     pb.br_p95,     pb.br_p99,     b.br_min,     b.br_max,
  b.ipc_avg,    b.ipc_std,    pip.ipc_p50,   pip.ipc_p95,   pip.ipc_p99,   b.ipc_min,    b.ipc_max,
  b.bpc_avg,    b.bpc_std,    pbp.bpc_p50,   pbp.bpc_p95,   pbp.bpc_p99,   b.bpc_min,    b.bpc_max
FROM base b
JOIN p_cycles pc USING (test_run_id, role, test_type, openssh_branch, key_label)
JOIN p_instr  pi USING (test_run_id, role, test_type, openssh_branch, key_label)
JOIN p_br     pb USING (test_run_id, role, test_type, openssh_branch, key_label)
JOIN p_ipc   pip USING (test_run_id, role, test_type, openssh_branch, key_label)
JOIN p_bpc  pbp USING (test_run_id, role, test_type, openssh_branch, key_label)
;

