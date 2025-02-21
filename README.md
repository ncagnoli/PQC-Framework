# Monitoramento de Desempenho com SSH e Perf

## Visão Geral
Este projeto contém dois scripts para medir o desempenho da execução de conexões SSH utilizando a ferramenta `perf`. Os scripts testam o impacto de diferentes algoritmos de troca de chave (`KEX`) e armazenam os resultados para análise posterior.

- **`server_perf.py`**: Executa um servidor SSH manualmente e mede o desempenho do lado do servidor.
- **`client_perf.py`**: Conecta-se ao servidor SSH repetidamente e mede o desempenho do lado do cliente.

Os resultados são salvos em arquivos CSV dentro da pasta `Results/`.

---
## Como Funciona
### `server_perf.py`
1. **Verifica se a porta 22 está em uso.**
2. **Inicia um servidor SSH manualmente**, sem depender do serviço do sistema.
3. **Executa o `perf`** para capturar métricas de desempenho durante a execução do servidor.
4. **Salva os resultados** no arquivo CSV.

### `client_perf.py`
1. **Executa conexões SSH repetidas** usando um algoritmo de troca de chaves (`KEX`) específico.
2. **Utiliza `perf`** para coletar métricas do lado do cliente.
3. **Garante conexões não interativas** com `BatchMode=yes`.
4. **Salva os resultados** no arquivo CSV.

---
## Como Executar
### Servidor
```bash
python3 server_perf.py
```

### Cliente
```bash
python3 client_perf.py
```

---
## Estrutura de Arquivos
```
/
├── server_perf.py  # Script para monitoramento do servidor SSH
├── client_perf.py  # Script para monitoramento do cliente SSH
├── Results/        # Pasta onde os CSVs são armazenados automaticamente
└── README.md       # Este arquivo
```

---
## Configuração Rápida
Cada script possui um **bloco de configuração** onde você pode alterar parâmetros como número de iterações, chaves SSH, algoritmos KEX, etc. Basta editar as variáveis no início do arquivo:

```python
# Exemplo de configuração no client_perf.py
DEBUG_MODE = True  # Exibe os comandos e saídas detalhadas
SSH_USER = "test1"
SSH_HOST = "localhost"
SSH_KEX = "mlkem768x25519-sha256"
SSH_KEY = "id_rsa"
ITERATIONS = 100
```
