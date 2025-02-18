import subprocess
import csv
import sys
import os

def is_port_in_use(port=22):
    """Verifica se a porta 22 já está em uso."""
    result = subprocess.run(["ss", "-tln"], capture_output=True, text=True)
    return f":{port} " in result.stdout

def run_perf_ssh_server(iterations=1000, output_file="perf_server.csv", sshd_config="/etc/ssh/sshd_config"):
    if is_port_in_use():
        print("Erro: A porta 22 já está em uso. Finalizando script.", file=sys.stderr)
        sys.exit(1)

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
