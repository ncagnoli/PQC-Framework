#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

int main() {
    FILE *fp;
    int pid;

    // Executa "pidof sshd" e captura a saída
    fp = popen("pidof sshd", "r");
    if (fp == NULL) {
        perror("Erro ao executar pidof");
        return 1;
    }

    // Lê o PID retornado pelo comando
    if (fscanf(fp, "%d", &pid) != 1) {
        printf("sshd não está rodando.\n");
        pclose(fp);
        return 1;
    }

    pclose(fp);

    // Envia SIGTERM para o PID encontrado
    if (kill(pid, SIGTERM) == 0) {
        printf("sshd (PID %d) parado com sucesso.\n", pid);
    } else {
        perror("Erro ao parar o sshd");
        return 1;
    }

    return 0;
}
