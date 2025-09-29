#!/bin/bash
python import_pqc_csv.py \
  --host 127.0.0.1 --port 3306 --user pqc --password pqc --db pqc_framework \
  --file ../Results-Static-Raw/server-results/srv1-202507-server-Test-H-Ed25519-sshd_config_h_ed25519.csv \
  --role server \
  --test-run-id 7 \
  --test-type hybrid \
  --openssh-branch Debian12 \
  --key-type-primary Ed25519 \
  --key-size-primary 256 
