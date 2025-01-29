import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class ChatLLM:
    def __init__(self, model_name="hf.co/LoupGarou/deepseek-coder-6.7b-instruct-pythagora-v3-gguf:Q4_K_M"):
        # Initialize LLM
        self.llm = OllamaLLM(model=model_name, base_url="http://127.0.0.1:11434/")

        # Prompt template for answering the question
        self.answer_prompt = PromptTemplate.from_template(
            "Given the following user question, answer it in a concise manner.\n"
            "Question: {question}\n"
            "Answer:"
        )

        # Create the LLM chain
        self.chain = self._create_chain()

    def _create_chain(self):
        # Combine everything into a chain
        chain = (
            self.answer_prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def get_response(self, question):
        # Call the chain with the user question
        print("question" + question)
        response = self.chain.invoke({"question": question})
        print("answer" + response)
        return response

    def get_response_with_index(self, question, index):
        # Retrieve context from the index
        context = index.query(question)
        # Combine question and context
        combined_input = f"{question}\nContext: {context}\nAnswer:"
        return self.chain.invoke({"question": combined_input})

# Now you can call this class in your Streamlit app
