# loterias-capture-results

Lambda (Python) que **captura os resultados oficiais** dos sorteios das loterias
brasileiras a partir de uma API externa (Caixa) e os armazena no **S3** para análise
posterior. É a fonte de dados histórica do ecossistema **Loterias Sim** —
alimenta o `loterias-ml-engine`.

> Parte do ecossistema **Loterias Sim**. Visão geral em [Arquitetura](#arquitetura-e-fluxo).

---

## Visão geral

| Item | Valor |
|------|-------|
| Runtime | Python (deploy atual: **3.9**) |
| Handler | `lambda_function.lambda_handler` |
| Função Lambda | `loterias-capture-results` |
| Fonte | API de loterias (Caixa) — `GET {BASE_URL}?loteria=..&token=..` |
| Destino | S3 `s3://{BUCKET}/results/{concurso}_{loteria}.json` |
| Loterias | `megasena`, `lotomania`, `lotofacil` |
| Dependências | `requests~=2.32.0`, `boto3~=1.26.108` |

---

## Como funciona

`lambda_function.py`:
1. Para cada loteria em `['megasena', 'lotomania', 'lotofacil']`:
   - Monta `payload = {loteria, token}` e faz `requests.get(BASE_URL, payload)`.
   - Extrai `dezenas` (números sorteados) e `numero_concurso` da resposta JSON.
   - Monta `data = {"dezenas": [...]}` e chama `upload(key_object, data)`.

`s3/put_file.py` (`upload`):
- Serializa o `data` em `/tmp/{concurso}_{loteria}.json`.
- Sobe para `s3://{BUCKET}/results/{concurso}_{loteria}.json`.

### Estrutura no S3
```
s3://<BUCKET>/results/
   ├── 2845_megasena.json    →  {"dezenas": [7, 14, 21, 35, 48, 52]}
   ├── 2845_lotomania.json
   └── 3100_lotofacil.json
```

> **Idempotência:** a chave do objeto é determinística (`{concurso}_{loteria}`),
> então reexecuções sobrescrevem o mesmo arquivo (last-write-wins), sem duplicar.

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|:-----------:|-----------|
| `BASE_URL` | sim | Endpoint da API de loterias (Caixa) |
| `TOKEN` | sim | Token de autenticação da API |
| `BUCKET` | sim | Bucket S3 de destino (ex.: `loterias-resultados`) |

> ⚠️ O `TOKEN` é segredo — prefira **AWS Secrets Manager / SSM Parameter Store** em
> vez de variável de ambiente em texto puro.

---

## Recursos AWS e permissões (IAM)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::loterias-resultados/results/*" }
  ]
}
```

---

## Agendamento (trigger)

Não há gatilho versionado no repositório; o ideal é uma regra **EventBridge (cron)**
após os horários de sorteio (fuso `America/Sao_Paulo`). Sugestão de frequências:

| Loteria | Sorteios |
|---------|----------|
| Mega-Sena | Ter/Qui/Sáb |
| Lotofácil | Seg–Sáb (diária) |
| Lotomania | Seg/Qua/Sex |

Uma execução diária após ~21h BRT cobre todos os jogos com folga.

---

## Deploy

Não há script de deploy no repositório. Empacotar e atualizar manualmente:

```bash
pip install -r requirements.txt -t build/
cp -r lambda_function.py s3/ build/
( cd build && zip -r ../function.zip . )
aws lambda update-function-code --function-name loterias-capture-results \
  --zip-file fileb://function.zip --region sa-east-1
```

---

## Arquitetura e fluxo

```
EventBridge (cron) ─► loterias-capture-results ─► API Caixa
                                │
                                ▼
                     S3 (loterias-resultados/results/*.json)
                                │
                                ▼
                        loterias-ml-engine
```

---

## Pontos de atenção e melhorias

- ⚠️ **Sem tratamento de erro:** qualquer falha (timeout, JSON inesperado, campo
  ausente, falha de S3) derruba a execução. Adicionar `try/except` por loteria + log.
- ⚠️ **Sem validação da resposta** da API (assume `dezenas` e `numero_concurso`
  sempre presentes).
- ⚠️ **Sem DLQ/retry** — sorteios podem ser perdidos se a Lambda falhar.
- 🔐 Mover `TOKEN` para Secrets Manager/SSM.
- 📦 Adicionar gatilho EventBridge versionado (IaC) e política de lifecycle no S3.
- 🧪 Sem testes — cobrir parsing e upload.
- Escrever direto via SDK (`put_object`) em vez de passar por `/tmp` evita I/O de disco.
