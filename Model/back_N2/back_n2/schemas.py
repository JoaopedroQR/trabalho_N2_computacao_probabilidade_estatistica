from typing import Literal

from pydantic import BaseModel, Field


class VariablesInput(BaseModel):
    """Entrada da API. Os campos seguem o `contrato.json` do modelo."""

    sTSlope: Literal['Up', 'Flat', 'Down']
    cholesterol: int = Field(
        ge=0, le=1000, description='Colesterol sérico (mg/dl). 0 = não medido.'
    )
    fastingBS: Literal[0, 1] = Field(
        description='Glicemia em jejum > 120 mg/dl: 1 = sim, 0 = não.'
    )
    restingECG: Literal['Normal', 'ST', 'LVH']
    restingBP: int = Field(
        ge=0,
        le=300,
        description='Pressão arterial em repouso (mm Hg). 0 = não medida.',
    )
    sex: Literal['M', 'F']
    exerciseAngina: Literal['N', 'Y']
    chestPainType: Literal['TA', 'ATA', 'NAP', 'ASY']


class Result(BaseModel):
    status: str
    risk_level: str
    probability: float
