from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Request
from pydantic import BaseModel, StringConstraints

from app.services.chat import RAGService, Answer

@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None,Any,None]:
    app.state.rag_service = RAGService()
    yield
    app.state.rag.close()

app = FastAPI(title="Clause API",lifespan=lifespan)

class AskQuestion(BaseModel):
    question:Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]
@app.get("/")
def health() -> dict[str:str]:
   return {"status": "ok"}

@app.post("/ask", response_model=Answer)
def ask_query(body: AskQuestion,req: Request) -> None:
    return req.app.state.rag.ask(body.question)
