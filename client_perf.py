#!/usr/bin/python3

#
# CLIENT MONITOR
#

import subprocess
import csv
import sys
import signal
import time
import os
import datetime

# Configurações de conexão SSH
SSH_USER = "test1"
SSH_HOST = "localhost"
SSH_PORT = 22
SSH_COMMAND = "kill_sshd"
SSH_KEX = "mlkem768x25519-sha256"
SSH_KEY = "id_rsa"

# Número máximo de tentativas bem-sucedidas
ITERATIONS = 100

# Criar diretório "Results" se não existir
RESULTS_DIR = "Results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Gerar timestamp para o nome do arquivo
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
OUTPUT_FILE = os.path.join(RESULTS_DIR, f"{timestamp}-client-{SSH_KEX}-{SSH_KEY}.csv")

# Comando base do perf
PERF_COMMAND = [
    "sudo", "perf", "stat", "-e",
    "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
]

# Comando SSH
SSH_COMMAND_LIST = [
    "ssh", "-p", str(SSH_PORT), "-i", str(SSH_KEY), "-o", "BatchMode=yes", "-o", "ForwardX11=no", 
    "-o", f"KexAlgorithms={SSH_KEX}", f"{SSH_USER}@{SSH_HOST}", SSH_COMMAND
]

# Função para extrair métricas do perf
def parse_perf_output(output):
    metrics = {
        "cycles": 0, "instructions": 0, "cache-misses": 0,
        "branch-misses": 0, "page-faults": 0, "context-switches": 0, "cpu-migrations": 0
    }
    
    for line in output.split('\n'):
        for key in metrics.keys():
            if key in line:
                value = line.split()[0].replace(',', '').replace('.', '')
                try:
                    metrics[key] = int(value)
                except ValueError:
                    metrics[key] = 0
                
    return metrics

# Tratamento para interrupção (CTRL+C)
def cleanup_and_exit(signum, frame):
    print("\n[INFO] Interrupção detectada! Finalizando script com segurança...")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

# Criar e abrir o arquivo CSV
with open(OUTPUT_FILE, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
        "page-faults", "context-switches", "cpu-migrations"
    ])

    iteration = 0
    while iteration < ITERATIONS:
        print(f"\nTentando conexão SSH - Iteração {iteration}")

        try:
            # Combina os comandos
            command = PERF_COMMAND + ["--"] + SSH_COMMAND_LIST
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True, timeout=5)

            # Verifica se a conexão foi bem-sucedida
            if result.returncode == 0:
                print(f"Conexão bem-sucedida! Iteração {iteration} registrada.")
                metrics = parse_perf_output(result.stderr)
                metrics["iteration"] = iteration

                # Escreve no CSV apenas conexões bem-sucedidas
                writer.writerow([
                    metrics["iteration"], metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                    metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
                ])
                iteration += 1  # Só incrementa se a conexão foi bem-sucedida

            else:
                print("========== Falha na conexão. Tentando novamente ==========")

        except subprocess.TimeoutExpired:
            print("========== Tempo limite atingido. Tentando novamente ==========")

        except Exception as e:
            print(f"====== Erro inesperado: {e}. Tentando novamente ===== ")

if __name__ == "__main__":
    print(f"Iniciando testes do cliente. Resultados serão salvos em: {OUTPUT_FILE}")
