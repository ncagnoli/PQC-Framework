#!/usr/bin/python3
#
# SERVER MONITOR
#

import subprocess
import csv
import sys
import os
import datetime

def is_port_in_use(port=22):
    result = subprocess.run(["ss", "-tln"], capture_output=True, text=True)
    return f":{port} " in result.stdout


def run_perf_ssh_server(iterations=100, sshd_config="/etc/ssh/sshd_config"):
    if is_port_in_use():
        print("Erro: Porta 22 em uso.", file=sys.stderr)
        sys.exit(1)

    # Criar diretório "Results" se não existir
    results_dir = "Results"
    os.makedirs(results_dir, exist_ok=True)

    # Gerar timestamp para o nome do arquivo
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    config_filename = os.path.basename(sshd_config)  # Pega apenas o nome do arquivo
    output_file = os.path.join(results_dir, f"{timestamp}-{"server"}-{config_filename}.csv")

    perf_command = [
        "sudo", "perf", "stat", "-e",
        "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations"
    ]
    sshd_command = [
        "/usr/sbin/sshd", "-D", "-e", "-f", sshd_config
    ]

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "iteration", "cycles", "instructions", "cache-misses", "branch-misses",
            "page-faults", "context-switches", "cpu-migrations"
        ])

        try:
            for i in range(iterations):
                print(f"Executando servidor SSH - Iteração {i}")

                command = perf_command + ["--"] + sshd_command
                result = subprocess.run(command, stderr=subprocess.PIPE, text=True)

                metrics = parse_perf_output(result.stderr)
                metrics["iteration"] = i

                writer.writerow([
                    metrics["iteration"], metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                    metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]
                ])
        except KeyboardInterrupt:
            print("\n[INFO] CTRL+C detectado! Finalizando teste com segurança...")
            sys.exit(0)

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

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "/etc/ssh/sshd_config"
    run_perf_ssh_server(sshd_config=config_file)
