from pydantic import BaseModel


class ChatRequest(BaseModel):
    mensagem: str


class ChatResponse(BaseModel):
    texto: str
    acao_ui: list[str] | None = None
    dados: list[dict] | None = None


class MilesQueryRequest(BaseModel):
    mensagem: str


class MilesQueryResponse(BaseModel):
    texto: str
    acao_ui: list[str] | None = None
    dados: list[dict] | None = None
