-- pqc_results schema (MariaDB)
-- All comments in this file are in English as requested.

-- Optional: choose a database first
-- USE pqc_framework;

-- Optional: drop the table if you need a clean re-create
-- DROP TABLE IF EXISTS pqc_results;

CREATE TABLE IF NOT EXISTS pqc_results (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- Identification of the run (user-provided at import time)
  test_run_id VARCHAR(64) NOT NULL,

  -- Data source information
  role ENUM('client','server') NOT NULL,         -- measurement side: client or server
  source_file VARCHAR(255) NOT NULL,             -- original CSV file name
  file_line INT UNSIGNED NOT NULL,               -- 1-based data line number (header excluded)

  -- Time and iteration
  ts DATETIME(6) NULL,                           -- normalized timestamp (microseconds precision)
  iteration SMALLINT UNSIGNED NOT NULL,          -- 0..999 (client from CSV; server derived from file_line - 1)

  -- Test characterization
  test_type ENUM('classical','pqc','hybrid') NOT NULL,  -- test type: classical, PQC, or hybrid
  openssh_branch VARCHAR(64) NOT NULL,           -- OpenSSH branch/version label (e.g., LibOQS-Debian12, Debian13, OpenSSH_9.9p1)

  -- Key material (hybrid uses both primary and secondary; otherwise secondary is NULL)
  key_type_primary  VARCHAR(16) NOT NULL,        -- e.g., RSA | ECDSA | ML-KEM
  key_size_primary  INT UNSIGNED NOT NULL,       -- e.g., 2048 | 3072 | 44
  key_type_secondary VARCHAR(16) NULL,           -- e.g., RSA (hybrid only)
  key_size_secondary INT UNSIGNED NULL,          -- e.g., 44 (hybrid only)

  -- Convenience label for queries/plots; STORED so it can be indexed on all MariaDB versions that support generated columns
  key_label VARCHAR(64) GENERATED ALWAYS AS (
    CASE
      WHEN key_type_secondary IS NULL
        THEN CONCAT(key_type_primary, '(', key_size_primary, ')')
      ELSE CONCAT(key_type_primary, '(', key_size_primary, ')+', key_type_secondary, '(', key_size_secondary, ')')
    END
  ) STORED,

  -- Metrics
  cycles BIGINT UNSIGNED NULL,
  instructions BIGINT UNSIGNED NULL,
  cache_misses BIGINT UNSIGNED NULL,
  branch_misses BIGINT UNSIGNED NULL,
  page_faults INT UNSIGNED NULL,
  context_switches INT UNSIGNED NULL,
  cpu_migrations INT UNSIGNED NULL,

  -- Integrity / idempotency
  row_hash CHAR(64) NOT NULL,                    -- SHA256 of normalized row content

  PRIMARY KEY (id),

  -- Prevent duplicates across re-imports of the same data
  UNIQUE KEY uq_rowhash (row_hash),

  -- Useful indexes for analysis
  KEY idx_run_role_iter (test_run_id, role, iteration),
  KEY idx_type (test_type),
  KEY idx_branch (openssh_branch),
  KEY idx_keylabel (key_label),
  KEY idx_ts (ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
