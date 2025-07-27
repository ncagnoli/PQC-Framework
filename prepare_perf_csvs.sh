#!/usr/bin/env bash
set -euo pipefail
BASE="Results-Static"               # pasta raiz

echo "➜ 1/3  Adicionando coluna iteration aos arquivos server..."
for f in "$BASE/server-results/"*.csv; do
  echo "   • $f"
  tmp=$(mktemp)
  awk 'BEGIN{FS=OFS=","}
       NR==1   {print "iteration,"$0; next}
       {print NR-2","$0}' "$f" > "$tmp"
  mv "$tmp" "$f"
done

echo "➜ 2/3  Padronizando cabeçalhos (hífen → sublinhado)..."
for dir in client-results server-results; do
  for f in "$BASE/$dir"/*.csv; do
    sed -i '1s/-/_/g' "$f"
  done
done

echo "➜ 3/3  Renomeando arquivos server (removendo -sshd_config_*)..."
for f in "$BASE/server-results/"*-sshd_config_*.csv; do
  new="$(echo "$f" | sed -E 's/-sshd_config[^/]*\.csv$/.csv/')"
  echo "   • $(basename "$f")  →  $(basename "$new")"
  mv "$f" "$new"
done

echo "✔  Concluído."

