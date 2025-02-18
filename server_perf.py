import subprocess
import csv

def run_perf_ssh_server(iterations=1000, output_file="perf_server.csv"):
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["iteration", "cycles", "instructions", "cache-misses", "branch-misses", "page-faults", "context-switches", "cpu-migrations"])
        
        for i in range(0, iterations + 1):
            print(f"Executando servidor SSH - Iteração {i}")
            
            command = [
                "sudo", "perf", "stat", "-e", "cycles,instructions,cache-misses,branch-misses,page-faults,context-switches,cpu-migrations",
                "--", "/usr/sbin/sshd", "-D", "-e"
            ]
            
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            metrics = parse_perf_output(result.stderr)
            metrics["iteration"] = i
            writer.writerow([metrics["iteration"], metrics["cycles"], metrics["instructions"], metrics["cache-misses"],
                             metrics["branch-misses"], metrics["page-faults"], metrics["context-switches"], metrics["cpu-migrations"]])

def parse_perf_output(output):
    metrics = {
        "cycles": 0, "instructions": 0, "cache-misses": 0,
        "branch-misses": 0, "page-faults": 0, "context-switches": 0, "cpu-migrations": 0
    }
    
    for line in output.split('\n'):
        for key in metrics.keys():
            if key in line:
                value = line.split()[0].replace(',', '').replace('.', '')  # Remove pontos e vírgulas
                try:
                    metrics[key] = int(value)
                except ValueError:
                    metrics[key] = 0  # Em caso de erro, define como 0 para evitar falhas
                
    return metrics

if __name__ == "__main__":
    run_perf_ssh_server()
