import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


def runtheretrive(query_question):
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
        prompt_template = """ Your name is 'Android Kunjhappan 🤖🤖'. 
        You Are only allowed to Chat about Django and doubts regarding Django  for every questions user ask answer with atleast 2 coding examples and can reply to greetings.. because you are a Django Chat bot  .

        Context:
        {context}

        Query: {query}

        Answer:
        """
        prompt = PromptTemplate(
            input_variables=["context", "query"],
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
        input_data = {"query": query_question, "input_documents": relevant_docs}
        answer = stuff_chain.invoke(input_data)["output_text"]

        return answer

    except Exception as e:
        return(f"❌ Error: {str(e)}")