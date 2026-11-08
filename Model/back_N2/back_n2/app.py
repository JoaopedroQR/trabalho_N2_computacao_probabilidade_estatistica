from http import HTTPStatus

from fastapi import FastAPI

from back_n2.schemas import Result, VariablesInput

app = FastAPI()

# =====================================================================
# CARGA DO MODELO NAIVE BAYES (Carregado na inicialização do servidor)
# =====================================================================
# Exemplo de carregamento do artefato salvo via joblib:
# naive_bayes_model = joblib.load("model_naive_bayes.joblib")

# Mapeamentos para transformar strings em entradas numéricas para o Naive Bayes
CHEST_PAIN_MAP = {"TA": 0, "ATA": 1, "NAP": 2, "ASY": 3}
ST_SLOPE_MAP = {"Up": 0, "Flat": 1, "Down": 2}
EXERCISE_ANGINA_MAP = {"N": 0, "Y": 1}


@app.post('/answer/', status_code=HTTPStatus.CREATED, response_model=Result)
def create_prediction(variables: VariablesInput):

    """
    Rota POST responsável por:
    1. Receber as variáveis do formulário Front-End.
    2. Processar e mapear os tipos para o modelo Naive Bayes.
    3. Retornar a classe prevista e as estatísticas.
    """

    cp_code = CHEST_PAIN_MAP.get(variables.chestPainType)
    slope_code = ST_SLOPE_MAP.get(variables.sTSlope)
    angina_code = EXERCISE_ANGINA_MAP.get(variables.exerciseAngina)

    features_list = [[
        variables.age,
        variables.cholesterol,
        variables.maxhr,
        variables.oldpeak,
        cp_code,
        slope_code,
        angina_code
    ]]

    # -----------------------------------------------------------------
    # ETAPA DE EXECUÇÃO DO NAIVE BAYES (Scikit-Learn)
    # -----------------------------------------------------------------
    # Exemplo de execução real com o modelo carregado:
    # pred_class = naive_bayes_model.predict(features_list)[0]
    # pred_proba = naive_bayes_model.predict_proba(features_list)[0][1]

    # Formatação das respostas
    if pred_class == 1:
        risk = "Alto Risco"
    else:
        risk = "Baixo Risco"

    if pred_class == 1:
        status_msg = "Presença de Doença Cardíaca"
    else:
        status_msg = "Resultado Normal"

    # Retorna o contrato definido no response_model (Result)
    return Result(
        status=status_msg,
        risk_level=risk,
        probability=round(float(pred_proba), 2)
    )
