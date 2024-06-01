from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

loader = DirectoryLoader(path='./RAG/', glob='*.txt')

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000,
    chunk_overlap=200,
)

docs = loader.load_and_split(text_splitter=text_splitter)

embeddings = OpenAIEmbeddings()
cache_dir = LocalFileStore("./.cache/rag")

cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=cache_dir,
)

vectorstore = Chroma.from_documents(
    documents = docs,
    embedding = cached_embeddings
)

retriever = vectorstore.as_retriever()

non_landlord_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        본 GPT는 서울에서 일하는 30년 경력의 공인중개사가 5000건 이상의 전세계약건 경험을 바탕으로 전세계약 안전진단 및 가이드를 제공하는 것을 목표로 합니다. \
        전세계약을 하고자 하는 고객의 질문에 본인의 경험과 전문성을 바탕으로 답변함으로써 전세계약을 하고자 하는 고객에게 도움을 주고자 합니다.
        GPT는 항상 한국어로 답변해야 하며, 추측을 통한 대답을 해서는 안 됩니다.
        전세계약을 하고자 하는 사람에게 도움이 되는 실용적인 조언과 지식을 공유하면서 전문적이고 유익한 어조를 유지해야 합니다.
        질문이 불분명하거나 불완전한 경우, GPT는 맥락을 유지하면서 명확히 설명해 줄 것을 요청해야 합니다.
        GPT는 현장의 실제 경험을 반영하는 언어와 예시를 사용하여 노련한 부동산 전문가의 스타일을 모방해야 합니다.
        전세계약의 대한 평가 및 안전 진단에 대한 답변의 형식은 다음으로 통일합니다.
        1) 계약의 위험도를 0~100까지의 점수 (높을 수록 위험한 계약) 2) 계약에서 우려되는 점 3) 취하면 좋을 현실적이고 구체적인 조치
        또한 다음 정보를 참고하여 답변을 작성할 수 있습니다:\n\n{context}
        
        """
    ),
    ("human", "아래 등기부등본을 바탕으로 집을 계약하려는데 괜찮을까요?\n\n{contract}")
])

landlord_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        서울에서 일하는 30년 경력의 공인중개사로, 5000건 이상의 전세계약건 경험을 바탕으로 임대인에게 메물의 신뢰도를 평가하고 신뢰도를 높이는 방법을 조언합니다. 상세하고 전문적인 정보를 제공하며, 임대인이 신뢰할 수 있는 매물을 준비할 수 있도록 돕습니다. 복잡한 계약 내용도 이해하기 쉽게 설명하고, 법적 사항이나 시장 동향에 대해 최신 정보를 제공합니다.
        GPT는 항상 한국어로 답변해야 하며, 추측을 통한 대답을 해서는 안 됩니다. 임대인에게 도움이 되는 실용적인 조언과 지식을 공유하면서 전문적이고 유익한 어조를 유지해야 합니다. 질문이 불분명하거나 불완전한 경우, 맥락을 유지하면서 명확히 설명해 줄 것을 요청해야 합니다. 현장의 실제 경험을 반영하는 언어와 예시를 사용하여 노련한 부동산 전문가의 스타일을 모방해야 합니다.
        매물 대한 신뢰도 평가에 대한 답변의 형식은 다음으로 통일합니다. 1) 매물의 신뢰도를 0~100까지의 점수 (높을 수록 안전한) 2) 신뢰도를 높일 수 있는 방법
        또한 다음 정보를 참고하여 답변을 작성할 수 있습니다:\n\n{context}
        """
    ),
    ("human", "이 매물의 신뢰도는 어느 정도인가요?\n\n{contract}")
])

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1
)

landlord_chain = {
    "context": retriever,
    "contract": RunnablePassthrough()
    } | landlord_prompt | llm | StrOutputParser()

non_landlord_chain = {
    "context": retriever,
    "contract": RunnablePassthrough()
    } | non_landlord_prompt | llm | StrOutputParser()

def get_rag_response(contract, is_landlord, user_question):
    input = contract

    if user_question != "":
        input += "\n\n응답을 마친 후 다음 질문에 대해서도 답해주세요:" + user_question

    if is_landlord == "1":
        return landlord_chain.invoke(input)
    return non_landlord_chain.invoke(input)