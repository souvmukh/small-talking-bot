import time
from pydantic import BaseModel, HttpUrl
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logger import log

# ----------------------------
# 1. Pydantic Configuration Model
# ----------------------------


class LLMConfig(BaseModel):
    """
    A Pydantic model to hold and validate the configuration for the LLM.
    Using Pydantic ensures that the configuration is type-safe and valid
    before it's used by the application, preventing common errors.
    """

    model_name: str = "phi3:mini"  # model name
    base_url: HttpUrl = "http://localhost:11434"


# ----------------------------
# 2. Main Processor Class
# ----------------------------
class LLMProcessor:
    """
    Handles all interactions with the local LLM (Phi-3 via Ollama).

    This class is responsible for:
    - Creating a prompt from user input.
    - Invoking the LLM.
    - Parsing the output.
    - It follows SRP by focusing solely on LLM text processing.
    """

    def __init__(self, config: LLMConfig):
        """
        Initializes the LLM processor with a validated configuration.

        Args:
            config (LLMConfig): A Pydantic model containing the LLM settings.
        """
        self.config = config
        log.info(
            f"Initializing LLM Processor with model '{self.config.model_name}' at {self.config.base_url}"
        )

        # Define the system prompt - this guides the AI's personality and task.
        system_prompt = (
            "Your name is Plu, You are a helpful, concise, and friendly voice assistant robot."
            "You are learned and witty, and you love to help people." \
            "You only answer question in English."
            "Respond to the user's query directly and clearly. Do not use markdown or any special formatting in your response."
            "All your responses should be child appropriate, no adult content, no violent and non racist."
            "For questions you cannot answer, respond with 'I don't know'."
            "You must answer in the same language as the question."
            "You can ask for clarifications if needed."
        )

        # Create a prompt template using LangChain
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{user_input}"),
            ]
        )

        # Initialize the Ollama LLM through LangChain
        try:
            llm = Ollama(
                model=self.config.model_name, base_url=str(self.config.base_url)
            )
        except Exception as e:
            log.error(
                f"Failed to connect to Ollama at {self.config.base_url}. "
                f"Please ensure Ollama is running and the model '{self.config.model_name}' is pulled. Error: {e}"
            )
            raise

        # Define the output parser to get a clean string
        output_parser = StrOutputParser()

        # Chain the components together using LangChain Expression Language (LCEL)
        self.chain = prompt_template | llm | output_parser
        log.info("LLM interaction chain created successfully.")

    def generate_response(self, user_text: str) -> str:
        """
        Generates a response from the LLM based on the user's text.

        Args:
            user_text (str): The transcribed text from the user.

        Returns:
            str: The LLM's generated response.
        """
        if not user_text:
            log.warning("Received empty text for processing. Returning empty response.")
            return ""

        log.info(f"Generating response for user input: {user_text}")

        # For performance visualization, we can log the response time.
        start_time = time.time()

        try:
            # The `invoke` method runs the entire chain.
            response = self.chain.invoke({"user_input": user_text}) # this is where the magic happens
            end_time = time.time()
            processing_time = (
                end_time - start_time
            )  # in seconds, total time taken by llm
            log.info(f"LLM response time: {processing_time:.2f} seconds")
            log.info(f"LLM Output: '{response}'")
            return response
        except Exception as e:
            log.error(f"Error during LLM invocation: {e}")
            return "I'm sorry, I encountered an error while processing your request."
