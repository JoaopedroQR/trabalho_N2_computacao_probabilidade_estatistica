from pydantic import BaseModel


# class Message(BaseModel):
#     message: str


class variables(BaseModel):
    age: int
    cholesterol: int
    maxhr: int
    oldpeak: float
    chestPainType: str
    sTSlope: str
    exerciseAngina: str


class result(BaseModel):
    status: str
