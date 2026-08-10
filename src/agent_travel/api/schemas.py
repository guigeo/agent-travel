from pydantic import BaseModel, ConfigDict


class ResultadoFerramentaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ferramenta: str
    dados: list[dict]


class ChatRequest(BaseModel):
    mensagem: str


class ChatResponse(BaseModel):
    texto: str
    resultados: list[ResultadoFerramentaSchema] = []


class MilesQueryRequest(BaseModel):
    mensagem: str


class MilesQueryResponse(BaseModel):
    texto: str
    resultados: list[ResultadoFerramentaSchema] = []
