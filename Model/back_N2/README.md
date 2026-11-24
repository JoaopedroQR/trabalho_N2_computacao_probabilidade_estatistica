# back-n2

API em **FastAPI** que recebe dados clínicos de um paciente e retorna a predição de risco de doença cardíaca usando um modelo **Naive Bayes** (`CategoricalNB`, Scikit-Learn).

## Sumário

- [Visão geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Executando o servidor](#executando-o-servidor)
- [Endpoint](#endpoint)
- [O modelo](#o-modelo)
- [Testes e qualidade de código](#testes-e-qualidade-de-código)
- [Atualizando o modelo](#atualizando-o-modelo)
- [Autor](#autor)

## Visão geral

O front-end envia as variáveis do formulário para a rota `POST /answer/`. A API:

1. Valida os dados de entrada com Pydantic (categorias inválidas retornam `422`);
2. Monta um DataFrame com os nomes de coluna usados no treino;
3. Executa a Pipeline treinada (imputação, faixas, codificação e Naive Bayes), que já faz todo o pré-processamento;
4. Retorna a classe prevista (nível de risco, mensagem de status) e a probabilidade.

> A API **não** converte as categorias em números antes do modelo. Isso é feito dentro da Pipeline salva no `.joblib`.

## Tecnologias

- Python `>=3.12, <4.0`
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [scikit-learn](https://scikit-learn.org/), [pandas](https://pandas.pydata.org/), [joblib](https://joblib.readthedocs.io/) (versões fixadas; veja [Atualizando o modelo](#atualizando-o-modelo))
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências
- [Pytest](https://docs.pytest.org/) + pytest-cov para testes e cobertura
- [Ruff](https://docs.astral.sh/ruff/) para lint e formatação
- [Typos](https://github.com/crate-ci/typos) para checagem ortográfica
- [Poe the Poet](https://poethepoet.natn.io/) para tarefas (`poe`)

## Estrutura do projeto

```
back_n2/
├── app.py                         # Aplicação FastAPI, carga do modelo e rota de predição
├── schemas.py                     # Schemas Pydantic (entrada e saída)
└── artifacts/
    ├── model_naive_bayes.joblib   # Pipeline treinada (entregue pelo notebook)
    ├── contrato.json              # Campos, categorias e exemplo de requisição
    ├── metricas_teste.json        # Métricas e matriz de confusão no teste
    └── model_naive_bayes.json     # Metadados do treino
tests/
├── conftest.py
├── test_app.py
└── data/test_predictions.csv      # Previsões do notebook, usadas para conferir a integração
pyproject.toml                     # Dependências e configurações das ferramentas
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

O servidor sobe em `http://127.0.0.1:8000`. A documentação interativa (Swagger) fica disponível em `http://127.0.0.1:8000/docs`. O modelo é carregado uma vez, na inicialização.

## Endpoint

### `POST /answer/`

Recebe as variáveis do paciente e retorna a predição. Responde com status `201 Created`.

#### Corpo da requisição

| Campo            | Tipo  | Valores aceitos                  | Descrição                                                    |
| ---------------- | ----- | -------------------------------- | ------------------------------------------------------------ |
| `sTSlope`        | `str` | `Up`, `Flat`, `Down`             | Inclinação do segmento ST no exercício                       |
| `cholesterol`    | `int` | `0` a `1000`                     | Colesterol sérico (mg/dl). `0` = não medido                  |
| `fastingBS`      | `int` | `0` ou `1`                       | Glicemia em jejum > 120 mg/dl (`1` = sim, `0` = não)         |
| `restingECG`     | `str` | `Normal`, `ST`, `LVH`            | Eletrocardiograma em repouso                                 |
| `restingBP`      | `int` | `0` a `300`                      | Pressão arterial em repouso (mm Hg). `0` = não medida        |
| `sex`            | `str` | `M`, `F`                         | Sexo registrado                                              |
| `exerciseAngina` | `str` | `N`, `Y`                         | Angina induzida por exercício (`N` = não, `Y` = sim)         |
| `chestPainType`  | `str` | `TA`, `ATA`, `NAP`, `ASY`        | Tipo de dor no peito                                         |

Valores fora dessas listas, campos ausentes ou tipos errados retornam `422 Unprocessable Entity`.

**Mudanças em relação à versão anterior:**

| Situação                | Campos                                                                          |
| ----------------------- | ------------------------------------------------------------------------------- |
| Novos                   | `sex`, `fastingBS`, `restingECG`, `restingBP`                                   |
| Removidos               | `age`, `maxhr`, `oldpeak` (se o front ainda enviar, a API os ignora sem erro)   |
| Mantidos                | `sTSlope`, `cholesterol`, `exerciseAngina`, `chestPainType`                     |

**Valores zerados:** colesterol `0` e pressão em repouso `0` são tratados pelo modelo como medição ausente e substituídos pela mediana do treino. Se o paciente não tem o exame, o front pode enviar `0`.

#### Exemplo de requisição

```bash
curl -X POST http://127.0.0.1:8000/answer/ \
  -H "Content-Type: application/json" \
  -d '{
    "sTSlope": "Flat",
    "cholesterol": 217,
    "fastingBS": 1,
    "restingECG": "ST",
    "restingBP": 139,
    "sex": "M",
    "exerciseAngina": "Y",
    "chestPainType": "ATA"
  }'
```

#### Exemplo de resposta

```json
{
  "status": "Presença de Doença Cardíaca",
  "risk_level": "Alto Risco",
  "probability": 0.93
}
```

| Campo         | Tipo    | Descrição                                                                  |
| ------------- | ------- | -------------------------------------------------------------------------- |
| `status`      | `str`   | `"Presença de Doença Cardíaca"` ou `"Resultado Normal"`                    |
| `risk_level`  | `str`   | `"Alto Risco"` ou `"Baixo Risco"`                                          |
| `probability` | `float` | Probabilidade da classe positiva (doença cardíaca), arredondada em 2 casas |

## O modelo

Base: [Heart Failure Prediction (fedesoriano)](https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction), 918 registros, 11 preditoras. O notebook `Modelo_Final_Colab.ipynb` remove duplicatas, separa 20% para teste (`random_state=42`, estratificado) e escolhe as variáveis por **seleção progressiva** (forward, validação cruzada de 3 partições, métrica F1).

As 8 variáveis escolhidas são as da tabela do endpoint. Idade, frequência máxima e `oldpeak` não foram selecionadas nesta busca.

Pré-processamento dentro da Pipeline:

- `Cholesterol` e `RestingBP`: zero vira ausente, imputado pela mediana, depois dividido em até 5 faixas por quantis;
- Categorias: `OrdinalEncoder` com a ordem fixa do contrato (os códigos não representam intensidade);
- Classificador: `CategoricalNB(alpha=1.0)`.

Desempenho no conjunto de teste reservado (184 registros; arquivo `artifacts/metricas_teste.json`):

| Métrica   | Valor |
| --------- | ----- |
| Acurácia  | 0,880 |
| Precisão  | 0,885 |
| Recall    | 0,902 |
| F1        | 0,893 |

**Limites:** o conjunto de teste já foi consultado em versões anteriores do projeto, então a avaliação é interna e exploratória. A seleção progressiva é gulosa e não garante o melhor subconjunto possível. Os resultados vêm de uma base pequena e **não validam uso clínico**; a probabilidade retornada é a saída do modelo, não um risco clínico calibrado.

## Testes e qualidade de código

As tarefas abaixo estão definidas no `pyproject.toml` via Poe:

| Comando                   | O que faz                                                        |
| ------------------------- | ---------------------------------------------------------------- |
| `poetry run poe lint`     | Roda o `ruff check`                                              |
| `poetry run poe format`   | Aplica `ruff check --fix` e `ruff format`                        |
| `poetry run poe test`     | Roda lint, executa o pytest com cobertura e gera o relatório HTML |
| `poetry run poe serve`    | Inicia o servidor de desenvolvimento                             |

O relatório de cobertura é gerado em `htmlcov/` (com contexto por teste).

Os testes cobrem predições de alto e baixo risco, valores zerados, validação de entradas inválidas e ausentes e a compatibilidade do schema com o `contrato.json`. Um teste também reenvia as 184 linhas de teste do notebook pela API e confere que as classes previstas são as mesmas do Colab.

## Atualizando o modelo

1. Rode o notebook no Colab e baixe o `entrega_modelo_final.zip`;
2. Copie `model_naive_bayes.joblib`, `contrato.json`, `metricas_teste.json` e `model_naive_bayes.json` para `back_n2/artifacts/` e `test_predictions.csv` para `tests/data/`;
3. Confira as versões em `requirements-modelo.txt` com as do `pyproject.toml`: o `.joblib` só é garantido com as **mesmas versões** de scikit-learn, pandas e numpy do treino;
4. Se a lista de variáveis mudou, atualize `schemas.py` e `API_TO_MODEL_COLUMNS` em `app.py`. O teste `test_api_matches_model_contract` falha enquanto o código e o `contrato.json` estiverem diferentes.

## Autor

**Joao Pedro Queiroz** — joaoprodrigues1108@gmail.com
