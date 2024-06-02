from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import ChatPromptTemplate
from langchain_cohere import CohereEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os,streamlit as st

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("langchain_api_key")
os.environ["LANGCHAIN_PROJECT"] = "RAG"

template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
Follow Up Input: {question}
Standalone question:"""

# retrievar code

def get_unique_documents(docs:list):
    _docs = set([doc.page_content for doc in docs])
    return "\n".join(_docs)

def retriever():
    embeddings = CohereEmbeddings(model="embed-english-light-v3.0",cohere_api_key=os.getenv("cohere_api_key"))
    index_name = "rag"    
    retriever = PineconeVectorStore(index_name=index_name, embedding=embeddings).as_retriever(search_kwargs={"k":3})
    return retriever | get_unique_documents

	# The Code of Criminal Procedure (Punjab Amendment) Act, 1940(Last updated on 06-12-2003)

    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",google_api_key=os.getenv("google_api_key"))
    # generate_queries = (
    #     ChatPromptTemplate.from_template(template)
    #     | llm
    #     | StrOutputParser())
    
    # return generate_queries | retriever

prompt = ChatPromptTemplate.from_template("""Generate the summmary of this given Pakistan Punjab law:\n<<{law}>>""")

# Streamlit Code

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",google_api_key=os.getenv("google_api_key"))

chain = prompt | llm | StrOutputParser()

# streamlit
st.set_page_config(page_title="Law Shield",page_icon="💬")
st.markdown("### Welcome To LawShield")

multi = '''You just need to enter the law title [You can find any law from here](http://punjablaws.gov.pk/chron.php) or describe your issue, and you will receive relevant documents. You can then gain insights from the documents, summarize them, and discuss further.
'''
st.markdown(multi)

if title := st.chat_input("Enter Law Title or Describe Your Issue"):
    title = title.strip()
    st.session_state["title"] = title
    with st.spinner("Please Wait..."):
        st.session_state["content"] = retriever().invoke(title)

if "content" in st.session_state:
    if content:=st.session_state["content"]:
        st.markdown(f"#### Your Query ({st.session_state['title']})")    
        with st.expander(content[:200]):
            st.write(content[200:])
        if "summary" in st.session_state:
            del st.session_state["summary"]

        if st.button("Summarize It"):
            if "summary" not in st.session_state:
                with st.spinner("Generating Summary Please Wait..."):
                    message_placeholder = st.empty()
                    full_response = ""
                    summary = chain.stream(st.session_state["content"])
                    for res in summary:
                        full_response += res or "" 
                        message_placeholder.markdown(full_response + "|")
                        message_placeholder.markdown(full_response)
                st.session_state["summary"] = full_response

            else:
                st.write(st.session_state["summary"])