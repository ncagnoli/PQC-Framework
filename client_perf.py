#!/usr/bin/python3
#
# CLIENT MONITOR
#       by Nestor Cagnoli

import subprocess
import csv
import sys
import signal
import os
import datetime
import socket

# ---------------- CONFIGURAÇÕES ---------------- #
DEBUG_MODE = True  # Defina como True para ver os comandos e saídas detalhadas
SSH_USER = "test1"
SSH_HOST = "localhost"
SSH_PORT = 22
SSH_COMMAND = "kill_sshd"
SSH_KEX = "mlkem768x25519-sha256"
SSH_KEY = "id_rsa"
ITERATIONS = 100  # Número máximo de tentativas bem-sucedidas
RESULTS_DIR = "Results"  # Diretório onde os resultados serão armazenados
# ---------------------------------------------- #

def debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def setup_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_output_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    hostname = socket.gethostname()
    return os.path.join(RESULTS_DIR, f"{hostname}-{timestamp}-client-{SSH_KEX}-{SSH_KEY}.csv")

def execute_perf(command):
    debug(f"Executando comando: {' '.join(command)}")
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True, timeout=5)
    debug(f"Saída de erro do perf:\n{result.stderr}")
    return result.stderr, result.returncode

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

def cleanup_and_exit(signum, frame):
    print("\n[INFO] Interrupção detectada! Finalizando script com segurança...")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

def run_perf_ssh_client():
    setup_results_dir()
    output_file = generate_output_filename()
    
    perf_command = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    ssh_command_list = [
        "ssh", "-p", str(SSH_PORT), "-i", str(SSH_KEY), "-o", "BatchMode=yes", "-o", "ForwardX11=no", 
        "-o", f"KexAlgorithms={SSH_KEX}", f"{SSH_USER}@{SSH_HOST}", SSH_COMMAND
    ]
    command = perf_command + ["--"] + ssh_command_list

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
            "page-faults", "context-switches", "cpu-migrations"
        ])
        
        iteration = 0
        while iteration < ITERATIONS:
            print(f"\nTentando conexão SSH - Iteração {iteration}")
            try:
                perf_output, return_code = execute_perf(command)
                print(perf_output)
                print(return_code)
                if return_code == 0:
                    print(f"Conexão bem-sucedida! Iteração {iteration} registrada.")
                    metrics = parse_perf_output(perf_output)
                    metrics["iteration"] = iteration
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
    print(f"Iniciando testes do cliente. Resultados serão salvos em: {generate_output_filename()}")
    run_perf_ssh_client()
