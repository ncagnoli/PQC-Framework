-- Gera /tmp/pqc_stats_ptBR.csv no servidor MariaDB
-- Ajuste o caminho conforme seu secure_file_priv:
--   SHOW VARIABLES LIKE 'secure_file_priv';
--   Se não for NULL, escolha um diretório permitido.

SELECT
  test_run_id,
  role,
  test_type,
  openssh_branch,
  key_label,
  n_rows,

  /* cycles* */
  REPLACE(REPLACE(FORMAT(cycles_avg,  6), ',', ''), '.', ',') AS cycles_avg,
  REPLACE(REPLACE(FORMAT(cycles_std,  6), ',', ''), '.', ',') AS cycles_std,
  REPLACE(REPLACE(FORMAT(cycles_p50,  6), ',', ''), '.', ',') AS cycles_p50,
  REPLACE(REPLACE(FORMAT(cycles_p95,  6), ',', ''), '.', ',') AS cycles_p95,
  REPLACE(REPLACE(FORMAT(cycles_p99,  6), ',', ''), '.', ',') AS cycles_p99,
  REPLACE(REPLACE(FORMAT(cycles_min,  6), ',', ''), '.', ',') AS cycles_min,
  REPLACE(REPLACE(FORMAT(cycles_max,  6), ',', ''), '.', ',') AS cycles_max,

  /* instr* */
  REPLACE(REPLACE(FORMAT(instr_avg,   6), ',', ''), '.', ',') AS instr_avg,
  REPLACE(REPLACE(FORMAT(instr_std,   6), ',', ''), '.', ',') AS instr_std,
  REPLACE(REPLACE(FORMAT(instr_p50,   6), ',', ''), '.', ',') AS instr_p50,
  REPLACE(REPLACE(FORMAT(instr_p95,   6), ',', ''), '.', ',') AS instr_p95,
  REPLACE(REPLACE(FORMAT(instr_p99,   6), ',', ''), '.', ',') AS instr_p99,
  REPLACE(REPLACE(FORMAT(instr_min,   6), ',', ''), '.', ',') AS instr_min,
  REPLACE(REPLACE(FORMAT(instr_max,   6), ',', ''), '.', ',') AS instr_max,

  /* br* */
  REPLACE(REPLACE(FORMAT(br_avg,      6), ',', ''), '.', ',') AS br_avg,
  REPLACE(REPLACE(FORMAT(br_std,      6), ',', ''), '.', ',') AS br_std,
  REPLACE(REPLACE(FORMAT(br_p50,      6), ',', ''), '.', ',') AS br_p50,
  REPLACE(REPLACE(FORMAT(br_p95,      6), ',', ''), '.', ',') AS br_p95,
  REPLACE(REPLACE(FORMAT(br_p99,      6), ',', ''), '.', ',') AS br_p99,
  REPLACE(REPLACE(FORMAT(br_min,      6), ',', ''), '.', ',') AS br_min,
  REPLACE(REPLACE(FORMAT(br_max,      6), ',', ''), '.', ',') AS br_max,

  /* ipc* */
  REPLACE(REPLACE(FORMAT(ipc_avg,     6), ',', ''), '.', ',') AS ipc_avg,
  REPLACE(REPLACE(FORMAT(ipc_std,     6), ',', ''), '.', ',') AS ipc_std,
  REPLACE(REPLACE(FORMAT(ipc_p50,     6), ',', ''), '.', ',') AS ipc_p50,
  REPLACE(REPLACE(FORMAT(ipc_p95,     6), ',', ''), '.', ',') AS ipc_p95,
  REPLACE(REPLACE(FORMAT(ipc_p99,     6), ',', ''), '.', ',') AS ipc_p99,
  REPLACE(REPLACE(FORMAT(ipc_min,     6), ',', ''), '.', ',') AS ipc_min,
  REPLACE(REPLACE(FORMAT(ipc_max,     6), ',', ''), '.', ',') AS ipc_max,

  /* bpc* */
  REPLACE(REPLACE(FORMAT(bpc_avg,     6), ',', ''), '.', ',') AS bpc_avg,
  REPLACE(REPLACE(FORMAT(bpc_std,     6), ',', ''), '.', ',') AS bpc_std,
  REPLACE(REPLACE(FORMAT(bpc_p50,     6), ',', ''), '.', ',') AS bpc_p50,
  REPLACE(REPLACE(FORMAT(bpc_p95,     6), ',', ''), '.', ',') AS bpc_p95,
  REPLACE(REPLACE(FORMAT(bpc_p99,     6), ',', ''), '.', ',') AS bpc_p99,
  REPLACE(REPLACE(FORMAT(bpc_min,     6), ',', ''), '.', ',') AS bpc_min,
  REPLACE(REPLACE(FORMAT(bpc_max,     6), ',', ''), '.', ',') AS bpc_max

FROM pqc_stats
INTO OUTFILE 'pqc_stats_ptBR.csv'
FIELDS TERMINATED BY ';' ENCLOSED BY '"'
LINES  TERMINATED BY '\n';

