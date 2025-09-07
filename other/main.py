
import logging
from config import settings
from src.cache.cache_manager import CacheManager
from rag_core import RAGCore
from speech_manager import SpeechManager
from document_manager import DocumentManager


def main():
    """Main function to run the voice chatbot."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        handlers=[logging.FileHandler(settings.LOG_FILE), logging.StreamHandler()],
    )

    logging.info("Starting the AI Chatbot...")

    doc_manager = DocumentManager(path=str(settings.DOCUMENTS_PATH))
    rag_system = RAGCore()
    speech_system = SpeechManager()
    cache = CacheManager(db_path=settings.DATABASE_PATH)

    docs = doc_manager.load_documents()
    chunks = doc_manager.split_documents(docs)

    if not chunks:
        error_message = "No documents loaded. Chatbot cannot function."
        logging.critical(error_message)
        speech_system.speak(error_message)
        return

    rag_system.create_vector_store(chunks)

    speech_system.speak("Hello! I am ready. How can I help you?")
    try:
        while True:
            question = speech_system.listen()

            if not question:
                continue

            if "exit" in question.lower() or "goodbye" in question.lower():
                logging.info("Exit command received. Shutting down.")
                speech_system.speak("Goodbye!")
                break

            cached_answer = cache.get_answer(question)

            if cached_answer:
                answer = cached_answer
            else:
                answer = rag_system.answer_question(question)
                cache.add_answer(question, answer)

            speech_system.speak(answer)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        speech_system.speak("I've encountered a critical error.")
    finally:
        cache.close()
        logging.info("Chatbot shutdown complete.")


if __name__ == "__main__":
    main()