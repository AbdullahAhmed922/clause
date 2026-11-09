from langchain.chat_models import init_chat_model
from langchain_qdrant import QdrantVectorStore
from pydantic import BaseModel, Field
from sqlalchemy import ValuesBase

from core.config import get_settings, get_embeddings, get_qdrant_client


NO_ANSWER = "I don't know. The clause shop handbook doesn't cover that."

class Source(BaseModel):
    source: str
    page: int | None = None
    score: float

class Answer(BaseModel):
    answer: str
    sources: list[Source]

class RAGService:
    def __init__(self) -> None:
        self.settings = get_settings()

        self.client =  get_qdrant_client(self.settings)
        if not self.client.collection_exists(self.settings.collection):
            raise RuntimeError(f"Collection {self.settings.collection} not found.")

        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=self.settings.collection,
            embedding=get_embeddings(self.settings)
        )

        self.llm = init_chat_model(
            model=self.settings.chat_model,
            model_provider=self.settings.chat_provider,
            temperature=self.settings.chat_temperature
        )

    def ask(self, question: str):
        question = question.strip()

        if not question:
            raise ValueError("Question must not be empty.")

        results = self.store.similarity_search_with_score(
            query=question, k=self.settings.top_k
        )

        if not results:
            return Answer(answer=NO_ANSWER, sources=[])

        context = "\n\n".join(doc.page_content for doc, _ in results)  # strin

        messages = [
            {"role": "system", "content": self.settings.system_prompt},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ]

        return Answer(
            answer=self.llm.invoke(messages).text,
            sources=[
                Source(
                    source=doc.metadata.get("source", "unknown"),
                    page=doc.metadata.get("page"),
                    score=round(score, 4)
                )
                for doc, score in results
            ]
        )


    def close(self):
        self.client.close()
