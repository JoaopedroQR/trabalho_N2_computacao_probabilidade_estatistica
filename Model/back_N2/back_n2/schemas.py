from pydantic import BaseModel


class VariablesInput(BaseModel):
    age: int
    cholesterol: int
    maxhr: int
    oldpeak: float
    chestPainType: str
    sTSlope: str
    exerciseAngina: str


class Result(BaseModel):
    status: str
    risk_level: str
    probability: float
