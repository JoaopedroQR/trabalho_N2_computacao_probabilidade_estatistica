# back-n2

API em **FastAPI** que recebe dados clínicos de um paciente e retorna a predição de risco de doença cardíaca usando um modelo **Naive Bayes** (Scikit-Learn).

## Sumário

- [Visão geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Executando o servidor](#executando-o-servidor)
- [Endpoint](#endpoint)
- [Testes e qualidade de código](#testes-e-qualidade-de-código)
- [Status do projeto](#status-do-projeto)
- [Autor](#autor)

## Visão geral

O front-end envia as variáveis do formulário para a rota `POST /answer/`. A API:

1. Valida os dados de entrada com Pydantic;
2. Converte as variáveis categóricas (strings) em valores numéricos;
3. Executa o modelo Naive Bayes;
4. Retorna a classe prevista (nível de risco, mensagem de status) e a probabilidade.

## Tecnologias

- Python `>=3.12, <4.0`
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências
- [Pytest](https://docs.pytest.org/) + pytest-cov para testes e cobertura
- [Ruff](https://docs.astral.sh/ruff/) para lint e formatação
- [Typos](https://github.com/crate-ci/typos) para checagem ortográfica
- [Poe the Poet](https://poethepoet.natn.io/) para tarefas (`poe`)

## Estrutura do projeto

```
back_n2/
├── app.py        # Aplicação FastAPI e rota de predição
└── schemas.py    # Schemas Pydantic (entrada e saída)
pyproject.toml    # Dependências e configurações das ferramentas
poetry.lock
```

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd back-n2

# Instale as dependências (incluindo as de desenvolvimento)
poetry install
```

## Executando o servidor

```bash
poetry run poe serve
```

ou, diretamente:

```bash
poetry run fastapi dev back_n2/app.py
```

O servidor sobe em `http://127.0.0.1:8000`. A documentação interativa (Swagger) fica disponível em `http://127.0.0.1:8000/docs`.

## Endpoint

### `POST /answer/`

Recebe as variáveis do paciente e retorna a predição. Responde com status `201 Created`.

#### Corpo da requisição

| Campo            | Tipo    | Descrição                                                  |
| ---------------- | ------- | ---------------------------------------------------------- |
| `age`            | `int`   | Idade do paciente                                          |
| `cholesterol`    | `int`   | Colesterol sérico                                          |
| `maxhr`          | `int`   | Frequência cardíaca máxima atingida                        |
| `oldpeak`        | `float` | Depressão do segmento ST induzida pelo exercício           |
| `chestPainType`  | `str`   | Tipo de dor no peito: `TA`, `ATA`, `NAP` ou `ASY`          |
| `sTSlope`        | `str`   | Inclinação do segmento ST: `Up`, `Flat` ou `Down`          |
| `exerciseAngina` | `str`   | Angina induzida por exercício: `N` (não) ou `Y` (sim)      |

#### Mapeamento das variáveis categóricas

| Campo            | Mapeamento                                      |
| ---------------- | ----------------------------------------------- |
| `chestPainType`  | `TA` → 0, `ATA` → 1, `NAP` → 2, `ASY` → 3       |
| `sTSlope`        | `Up` → 0, `Flat` → 1, `Down` → 2                |
| `exerciseAngina` | `N` → 0, `Y` → 1                                |

#### Exemplo de requisição

```bash
curl -X POST http://127.0.0.1:8000/answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "age": 54,
    "cholesterol": 240,
    "maxhr": 150,
    "oldpeak": 1.5,
    "chestPainType": "ASY",
    "sTSlope": "Flat",
    "exerciseAngina": "Y"
  }'
```

#### Exemplo de resposta

```json
{
  "status": "Presença de Doença Cardíaca",
  "risk_level": "Alto Risco",
  "probability": 0.87
}
```

| Campo         | Tipo    | Descrição                                                             |
| ------------- | ------- | --------------------------------------------------------------------- |
| `status`      | `str`   | `"Presença de Doença Cardíaca"` ou `"Resultado Normal"`               |
| `risk_level`  | `str`   | `"Alto Risco"` ou `"Baixo Risco"`                                     |
| `probability` | `float` | Probabilidade da classe positiva (doença cardíaca), arredondada em 2 casas |

## Testes e qualidade de código

As tarefas abaixo estão definidas no `pyproject.toml` via Poe:

| Comando                   | O que faz                                                        |
| ------------------------- | ---------------------------------------------------------------- |
| `poetry run poe lint`     | Roda o `ruff check`                                              |
| `poetry run poe format`   | Aplica `ruff check --fix` e `ruff format`                        |
| `poetry run poe test`     | Roda lint, executa o pytest com cobertura e gera o relatório HTML |
| `poetry run poe serve`    | Inicia o servidor de desenvolvimento                             |

O relatório de cobertura é gerado em `htmlcov/` (com contexto por teste).

## Status do projeto

🚧 **Em desenvolvimento.** Pontos pendentes:

- [ ] Carregar o modelo treinado (`joblib.load("model_naive_bayes.joblib")`) na inicialização do servidor;
- [ ] Ativar a execução real da predição (`predict` e `predict_proba`) na rota `/answer/`;
- [ ] Tratar valores inválidos nos campos categóricos (hoje `.get()` retornaria `None` para valores fora do mapa; considere usar `Literal`/`Enum` nos schemas);
- [ ] Escrever os testes automatizados.

## Autor

**Joao Pedro Queiroz** — joaoprodrigues1108@gmail.com