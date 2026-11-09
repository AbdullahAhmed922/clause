from services.ingestion import ingest
from services.chat import RAGService

def main() -> None:
    rag_service = RAGService()
    try:
        query = input("Enter your question (or 'exit' to quit): ").strip()
        result = rag_service.ask(query)
        print(f"AI: {result.answer}")

        if result.sources:
            pass
    except(KeyboardInterrupt, EOFError):
        print("Exiting...")

if __name__ == "__main__":
    # ingest()
    main()
