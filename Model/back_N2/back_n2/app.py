from http import HTTPStatus

from fastapi import FastAPI

from back_n2.schemas import variables, result

app = FastAPI()

database = []


# @app.get('/', status_code=HTTPStatus.OK, response_model=Message)
# def read_root():
#     return {'message': 'Olá Mundo!'}


@app.post('/answer/', status_code=HTTPStatus.CREATED, response_model=variables)
def return_answer(variables: variables):

    database.append(variables)

    return variables

@app.get('/answer/', response_model = result)
def read_status():
    return  'yes'