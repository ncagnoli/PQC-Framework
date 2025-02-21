#!/usr/bin/python3
#
# SERVER MONITOR
#       by Nestor Cagnoli

import subprocess
import csv
import sys
import os
import datetime
import socket

# ---------------- CONFIGURAÇÕES ---------------- #
DEBUG_MODE = True  # Defina como True para ver os comandos e saídas detalhadas
ITERATIONS = 100  # Número de iterações do teste
SSHD_CONFIG = "./sshd_config_mlkem768x25519-sha256"  # Caminho do arquivo de configuração do SSHD
RESULTS_DIR = "Results"  # Diretório onde os resultados serão armazenados
PORT = 22 # Porta que o SSH vai escutar
# ---------------------------------------------- #

def debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def is_port_in_use(port=PORT):
    result = subprocess.run(["ss", "-tln"], capture_output=True, text=True)
    return f":{port} " in result.stdout

def setup_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_output_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    config_filename = os.path.basename(SSHD_CONFIG)
    hostname = socket.gethostname()
    return os.path.join(RESULTS_DIR, f"{hostname}-{timestamp}-server-{config_filename}.csv")

def execute_perf(command):
    debug(f"Executando comando: {' '.join(command)}")
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    debug(f"Saída de erro do perf:\n{result.stderr}")
    return result.stderr

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

def run_perf_ssh_server():
    if is_port_in_use():
        print("Erro: Porta 22 em uso.", file=sys.stderr)
        sys.exit(1)

    setup_results_dir()
    output_file = generate_output_filename()

    perf_command = [
        "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    sshd_command = ["/usr/sbin/sshd", "-D", "-e", "-p", str(PORT), "-f", SSHD_CONFIG]
    command = perf_command + ["--"] + sshd_command

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
            "page-faults", "context-switches", "cpu-migrations"
        ])
        try:
            for i in range(ITERATIONS):
                print(f"Executando servidor SSH - Iteração {i}")
                perf_output = execute_perf(command)
                metrics = parse_perf_output(perf_output)
                metrics["iteration"] = i
                writer.writerow([
                    metrics["iteration"], metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                    metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
                ])
        except KeyboardInterrupt:
            print("\n[INFO] CTRL+C detectado! Finalizando teste com segurança...")
            sys.exit(0)

if __name__ == "__main__":
    run_perf_ssh_server()