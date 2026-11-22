from contextlib import asynccontextmanager
from http import HTTPStatus
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request

from back_n2.schemas import Result, VariablesInput

# =====================================================================
# MODELO NAIVE BAYES (carregado uma vez, na inicialização do servidor)
# =====================================================================
# O arquivo é uma Pipeline completa do scikit-learn (imputação, faixas,
# codificação das categorias e CategoricalNB). Por isso a API NÃO aplica
# mapas numéricos antes: ela só entrega um DataFrame com as colunas
# originais do treino.
MODEL_PATH = Path(__file__).parent / 'artifacts' / 'model_naive_bayes.joblib'

# Campo da API (camelCase) -> coluna usada no treino do modelo.
# Deve refletir `artifacts/contrato.json` (há um teste que confere).
API_TO_MODEL_COLUMNS = {
    'sTSlope': 'ST_Slope',
    'cholesterol': 'Cholesterol',
    'fastingBS': 'FastingBS',
    'restingECG': 'RestingECG',
    'restingBP': 'RestingBP',
    'sex': 'Sex',
    'exerciseAngina': 'ExerciseAngina',
    'chestPainType': 'ChestPainType',
}

POSITIVE_CLASS = 1


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    fastapi_app.state.model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(lifespan=lifespan)


@app.post('/answer/', status_code=HTTPStatus.CREATED, response_model=Result)
def create_prediction(variables: VariablesInput, request: Request):
    """
    Rota POST responsável por:
    1. Receber as variáveis do formulário Front-End (validadas no schema).
    2. Montar o DataFrame com as colunas esperadas pelo modelo.
    3. Retornar o resultado previsto e a probabilidade de doença cardíaca.
    """
    model = request.app.state.model

    row = {
        API_TO_MODEL_COLUMNS[field]: value
        for field, value in variables.model_dump().items()
    }
    frame = pd.DataFrame([row])

    probabilities = model.predict_proba(frame)[0]
    pred_class = model.classes_[probabilities.argmax()]
    positive_index = list(model.classes_).index(POSITIVE_CLASS)
    pred_proba = probabilities[positive_index]

    if pred_class == POSITIVE_CLASS:
        risk = 'Alto Risco'
        status_msg = 'Presença de Doença Cardíaca'
    else:
        risk = 'Baixo Risco'
        status_msg = 'Resultado Normal'

    # Retorna o contrato definido no response_model (Result)
    return Result(
        status=status_msg,
        risk_level=risk,
        probability=round(float(pred_proba), 2),
    )
