import re
import os
from langchain_ollama import OllamaLLM
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings # Use an embedding model compatible with your setup
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

#Graph
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from dotenv import load_dotenv

load_dotenv()

class ChatLLM:
    def __init__(self, model_name=os.getenv("model_name"),
                 db_uri=os.getenv("db_uri"), 
                 document_path=None, faiss_index_path=None ):
        # Initialize LLM and database
        self.llm = OllamaLLM(model=model_name, base_url="http://127.0.0.1:11434/")
        self.db = SQLDatabase.from_uri(db_uri)
        self.figures = []

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer")

        # Store the database description
        self.database_description = """
            The database consists of two tables: `"public"."nodes"` and `"public"."edges"`. This is a PostgreSQL database.

            The `"public"."nodes"` table contains:
            - `"id"`: A unique identifier for each node (auto-increment, `SERIAL`).
            - `"label"`: The label of the node (`TEXT`).
            - `"mindmap_id"`: The ID of the associated mindmap (`TEXT`).

            The `"public"."edges"` table contains:
            - `"id"`: A unique identifier for each edge (auto-increment, `SERIAL`).
            - `"source"`: The ID of the source node (`INTEGER`), references `"public"."nodes"("id")`.
            - `"target"`: The ID of the target node (`INTEGER`), references `"public"."nodes"("id")`.
            - `"mindmap_id"`: The ID of the associated mindmap (`TEXT`).

            Foreign keys:
            - `"public"."edges"."source"` and `"public"."edges"."target"` reference `"public"."nodes"."id"`.

            Use standard PostgreSQL queries.
            """


        self.sql_prompt = PromptTemplate(
            input_variables=["database_description", "chat_history", "question"],
            template="""
        {database_description}

        {chat_history}
        Given the above database schema and conversation history, create a syntactically correct SQL query to answer the following question.

        - Include all relevant columns in the SELECT statement.
        - Use double quotes around table and column names to preserve case sensitivity.
        - **Do not include any backslashes or escape characters in the SQL query.**
        - **Provide the SQL query as a plain text without any additional formatting or quotes.**
        - Ensure that the SQL query is compatible with PostgreSQL.
        - Only use the tables and columns listed in the database schema.

        Question: {question}

        Provide the SQL query in the following format:

        SQLQuery:
        SELECT "Column1", "Column2" FROM "public"."Table" WHERE "Condition";

        Now, generate the SQL query to answer the question.
        """
        )


        # Prompt template for answering the question
        self.answer_prompt = PromptTemplate.from_template(
            """Database Description:
        {database_description}

        {chat_history}
        Given the following user question, corresponding SQL query, and SQL result, answer the user question.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}

        If the SQL Result is "Graph has been generated and stored.", respond only and only with "Here's is the graph you asked for." only.

        Otherwise, provide a detailed answer.

        Answer:"""
        )
        
        # Prompt template for generating plotting code
        self.plot_code_prompt = PromptTemplate(
            input_variables=["sql_result", "question"],
            template="""
            Given the SQL result and user's question, generate **correct** Python code to plot the data.

            - Use `matplotlib` for standard charts.
            - Use `networkx` if the data represents a graph (nodes + edges).
            - Ensure the code is syntactically correct.
            - **Do NOT include plt.show()**.
            - Always define `fig, ax = plt.subplots()` if using matplotlib.
    
            SQL Result:
            {sql_result}

            Question:
            {question}

            Python Code:
            ```python
            import matplotlib.pyplot as plt
            import pandas as pd
            import networkx as nx
    
            fig, ax = plt.subplots(figsize=(10, 6))

            if isinstance(sql_result, list) and sql_result and "source" in sql_result[0] and "target" in sql_result[0]:
                G = nx.Graph()
                for edge in sql_result:
                    G.add_edge(edge["source"], edge["target"])

                pos = nx.spring_layout(G)
                nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=1500, font_weight="bold", ax=ax)
            else:
                df = pd.DataFrame(sql_result)
                df.plot(kind='bar', ax=ax)

            ```
            """
        )


        # Create a prompt for classification
        self.classification_prompt = PromptTemplate.from_template(
            """
            Given the user's question and the assistant's answer, determine whether the assistant's answer addresses the user's question, it is okay even if the answer is only partially correct, as long as it is not completely empty of any information, in such cases start your answer with yes, otherwise no.

            Question: {question}
            Answer: {answer}
            """
        )

        # Create an LLM chain for classification
        self.classification_chain = LLMChain(
            llm=self.llm,
            prompt=self.classification_prompt
        )

        # Create the SQL query chain
        self.write_query = LLMChain(
            llm=self.llm,
            prompt=self.sql_prompt
        )

        # Chain to generate plotting code
        self.generate_plot_code_chain = LLMChain(
            llm=self.llm,
            prompt=self.plot_code_prompt
        )

        # Create the LLM chain
        self.chain = self._create_chain()
        
        self.faiss_index_path = faiss_index_path  # Dynamischer Indexpfad
        self.vectorstore = None
        self.retriever = None
        if self.faiss_index_path:
            self.vectorstore = FAISS.load_local(self.faiss_index_path, HuggingFaceEmbeddings())
            self.retriever = self.vectorstore.as_retriever()
        
        self.document_path = document_path if document_path else []
         # Load the text document if provided
        if self.document_path and not self.faiss_index_path:
            documents = []
            if isinstance(self.document_path, list):
                for path in self.document_path:
                    loader = TextLoader(path)
                    documents.extend(loader.load())
            else:
                loader = TextLoader(self.document_path)
                documents = loader.load()

            if documents:
                # Create embeddings and vectorstore
                embeddings = HuggingFaceEmbeddings()
                self.vectorstore = FAISS.from_documents(documents, embeddings)
                self.retriever = self.vectorstore.as_retriever()

            # Create a RetrievalQA chain
            self.retrieval_qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True
            )
        else:
            self.retrieval_qa_chain = None

    def detect_graph_intent(self, question):
        # Check if the user intends to draw a graph by looking for specific keywords
        graph_keywords = ["graph", "plot", "chart", "visualize", "display", "show"]
        return any(keyword in question.lower() for keyword in graph_keywords)

    def _create_chain(self):
        # Function to generate SQL query with context
        def write_query_with_question(inputs):
            chat_history = self.memory.load_memory_variables({}).get('chat_history', '')
            inputs['chat_history'] = chat_history
            inputs['database_description'] = self.database_description
            response = self.write_query.run(inputs)
            return {'response': response, 'question': inputs['question']}

        write_query_runnable = RunnableLambda(write_query_with_question)

        # Function to extract and execute the SQL query
        def extract_and_execute_sql(inputs):
            response = inputs.get('response', '')
            question = inputs.get('question', '')

            # Print the LLM's response for debugging
            print("LLM Response:")
            print(response)

            # Updated regex pattern
            pattern = re.compile(r'SQLQuery:\s*\n(.*)', re.DOTALL)
            match = pattern.search(response)

            if match:
                sql_query = match.group(1).strip()
                print("Extracted SQL Query:")
                print(sql_query)
                if not sql_query.lower().startswith("select"):
                    result = "Invalid SQL query generated by the LLM."
                else:
                    try:
                        new_result = self.db._execute(sql_query)
                        print(new_result)
                        result = str(new_result)
                    except Exception as e:
                        result = f"Error executing SQL query: {e}"
                # If graph intent is detected, plot the result
                if self.detect_graph_intent(question):
                    # Prepare inputs for plotting code generation
                    plot_code_inputs = {
                        'sql_result': str(new_result),
                        'question': question
                    }
                    # Generate the plotting code
                    plot_code_response = self.generate_plot_code_chain.run(plot_code_inputs)

                    print("Plot Code Response:" + plot_code_response)
                    # Extract the code from the response
                    plot_code = extract_code_from_response(plot_code_response)
                    # Execute the plotting code
                    execute_plot_code(plot_code, new_result)
                    # Return the result indicating that the graph was displayed
                    return {
                        "question": question,
                        "query": sql_query,
                        "result": "Graph has been generated and stored"
                    }
                else:
                    return {
                        "question": question,
                        "query": sql_query,
                        "result": result
                    }
            else:
                print("No SQL query found in the response.")
                return {
                    "question": question,
                    "query": None,
                    "result": "No SQL query found in the response."
                }

        extract_and_execute = RunnableLambda(extract_and_execute_sql)

        def extract_code_from_response(response):
            # Use regex to extract code within code blocks
            code_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
            match = code_pattern.search(response)
            if match:
                code = match.group(1).strip()
            else:
                # If no code block, just return the response
                code = response.strip()
            return code
        
        def execute_plot_code(code, sql_result):
            # Create a local namespace for exec()
            local_vars = {
                'sql_result': sql_result,
                'pd': pd,
                'plt': plt,
                'nx': nx
                }
            if not sql_result:  # ✅ Keine Daten? Kein Diagramm generieren
                print("⚠️ Kein SQL-Ergebnis, daher wird kein Diagramm generiert.")
                return None
            try:
                exec(code, {}, local_vars)
                fig = local_vars.get('fig', None)
                if fig is None:
                    fig = plt.gcf()
                    
                if fig:
                    self.figures.append(fig) # Speichern für Anzeige in Streamlit
                else:
                    print("⚠️ Kein Figure-Objekt wurde erstellt.")

            except Exception as e:
                print(f"❌ Fehler beim Ausführen des Plot-Codes: {e}")
        
        # Function to add context before generating the final answer
        def add_context(inputs):
            chat_history = self.memory.load_memory_variables({}).get('chat_history', '')
            inputs['chat_history'] = chat_history
            inputs['database_description'] = self.database_description
            return inputs

        add_context_runnable = RunnableLambda(add_context)

        # Combine everything into a chain
        chain = (
            write_query_runnable
            | extract_and_execute
            | add_context_runnable
            | self.answer_prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def get_response(self, question):
        # If the retrieval QA chain is available, try to answer using the text document
        if self.retrieval_qa_chain:
            try:
                # Get answer from RetrievalQA chain
                response = self.retrieval_qa_chain({"query": question})
                answer = response["result"]
                print('RetrievalQA answer:', answer)
                source_documents = response["source_documents"]

                # Use the LLM to classify whether the answer contains the information
                classification_input = {
                    "question": question,
                    "answer": answer
                }
                classification_result = self.classification_chain.run(classification_input).strip().lower()

                print('Classification result:', classification_result)

                if "yes" in classification_result:
                    # Update memory
                    self.memory.save_context({"question": question}, {"answer": answer})
                    return answer
                else:
                    # Proceed to SQL chain
                    pass
            except Exception as e:
                # If there is any error, proceed to SQL chain
                print(f"Error in RetrievalQA chain: {e}")

        # If answer not acceptable or error occurs, proceed with existing chain
        # Prepare the inputs
        inputs = {
            "question": question,
        }

        # Call the chain
        response = self.chain.invoke(inputs)

        # Update memory
        self.memory.save_context({"question": question}, {"answer": response})

        return response
    
    #  To use it run `pip install -U :class:`~langchain-huggingface` and import as `from :class:`~langchain_huggingface import HuggingFaceEmbeddings``.