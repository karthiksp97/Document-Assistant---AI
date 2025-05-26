import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

history = []

def format_chat_history(history):
    formatted = ""
    for user_msg, bot_msg in history:
        formatted += f"User: {user_msg}\nBot: {bot_msg}\n"
    return formatted.strip()


def runtheretrive(query_question):
    global history
    try:
        # Load the embedding model used during indexing
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"}  # Use "cuda" for GPU if available
        )

        # Verify FAISS index exists
        faiss_index_path = "faiss_index"
        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at {faiss_index_path}")

        # Load the saved FAISS index
        vectorstore = FAISS.load_local(
            faiss_index_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        print("✅ Loaded FAISS index successfully")

        # Prepare retriever with adjusted parameters
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve 5 documents for broader context
        )

        # Define prompt template for StuffDocumentsChain

        if history:
            prompt_template = """
        You are a document analyzer chatbot. You must answer **only** based on the provided document context and conversation history. For each question, you must provide at least **2 examples** when possible. You can respond to greetings.

        If a question is unrelated to the provided context or history, you should reply:
        **"I know the answer, but I can't tell you here because I am trained to only provide answers from the document you shared."**

        **Conversation History:**  
        {history}

        **Document Context:**  
        {context}

        **User Query:**  
        {query}

        **Answer:**  
        """
        else:
            prompt_template = """
        Your name is **Android Kunjhappan 🤖🤖**, and you are a document analyzer chatbot. You must answer **only** based on the uploaded document context and conversation history. For each question, provide at least **2 examples** when applicable. You can respond to greetings.

        If a question is unrelated to the provided context or history, you should reply:
        **"I know the answer, but I can't tell you here because I am trained to only provide answers from the document you shared."**

        **Conversation History:**  
        {history}

        **Document Context:**  
        {context}

        **User Query:**  
        {query}

        **Answer:**  
        """

        prompt = PromptTemplate(
            input_variables=["context", "query","history"],
            template=prompt_template
        )

        # Instantiate Ollama LLM
        llm = ChatOllama(
            model="llama3",
            temperature=0.8,
            num_predict=512,  # Increased for longer answers
            verbose=True
        )

        # Create LLMChain
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        # Create StuffDocumentsChain
        stuff_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_variable_name="context",  # Matches {context} in prompt
            document_separator="\n\n"  # Separates documents in the context
        )

        # Query input
        query = "Will this candiate be good for the job role : python Django devloper with 2 years expirence should know the following html, css, python, Django, Rest"

        # Retrieve relevant docs
        relevant_docs = retriever.invoke(query)  # Use invoke for modern LangChain
        if not relevant_docs:
            raise ValueError("No relevant documents found for the query")

        # Run stuff chain
        formatted_history = format_chat_history(history)
        input_data = {"query": query_question, "input_documents": relevant_docs,"history": formatted_history}
        answer = stuff_chain.invoke(input_data)["output_text"]
        history.append((query_question, answer))
        print(formatted_history)
        return answer

    except Exception as e:
        return(f"❌ Error: {str(e)}")