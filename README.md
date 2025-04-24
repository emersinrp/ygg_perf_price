# Ygg Performance Price Tests

Teste de performance com [Locust](https://locust.io) para a API GraphQL de precificação da plataforma YGG.

---

## :package: Estrutura do Projeto
```
ygg_perf_price/
├── config/             # Configurações de URLs e headers
├── data/               # Dados de entrada (SKUs, buyer codes)
├── services/           # Serviços auxiliares (Auth, GraphQL)
├── tasks/              # Casos de teste Locust
├── utils/              # Utilitários (timer/token)
├── locustfile.py       # Entrypoint do Locust (comando principal que é executado quando um container é iniciado)
├── requirements.txt    # Dependências do projeto
```

---

## :rocket: Executando

Crie e ative o ambiente virtual:
```bash
python -m venv venv_ygg_perf_price
source venv_ygg_perf_price/bin/activate  # ou .\venv_ygg_perf_price\Scripts\activate no Windows
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

Execute o Locust:
```bash
locust
```

Acesse: [http://localhost:8089](http://localhost:8089)

---

## :gear: Variáveis de Ambiente
Você pode controlar os testes com:

```bash
# Ativa apenas o teste com blocos de 30 SKUs:
RUN_GET_PRICE=0 RUN_SKU_BLOCK=1 locust

# Ativa apenas o teste com todos os SKUs:
RUN_GET_PRICE=1 RUN_SKU_BLOCK=0 locust

# Executa em modo headless:
locust --headless -f locustfile.py --users 1 --spawn-rate 1

# Executa com interface grafica:
locust -f locustfile.py
```

Por padrão ambos estão ativos.

---

## :clipboard: Lógicas Implementadas
- Autenticação com `access_token` que se renova a cada 250s.
- Requisições com lista total de SKUs ou em blocos de 30 aleatórios.
- Buyer codes sorteados a cada execução.
- Logs com tempo de resposta e alerta para respostas vazias ou lentas (>10s).
- Indica o tempo do token em cada requisição.

---

## :mag: Logs
Todos os logs são emitidos no terminal:
- `INFO` para execuções normais.
- `⚠️ ALERT` para requisições lentas.
- `⚠️ EMPTY` quando a resposta não possui dados agregados.

---

## :memo: Exemplo de SKUs e Buyers
- SKUs: `data/skus.py`
- Buyer Codes: `data/buyers.py`

---

## :warning: Requisitos
- Python 3.8+
- Locust 2.20+