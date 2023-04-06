import os

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI


class LangChainHelper:
    
    def __init__(self):
        
        # 0 means more deterministic output, 1 means more random output
        llm = ChatOpenAI(temperature=0)
        template = """You are an AI assistant for medical queries. You are given a reference from which you can take help to answer the user's query.
query: {user_msg}
reference: {reference}
"""
        prompt = PromptTemplate(input_variables=["user_msg", "reference"],template=template)

        self.chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    def get_response(self, user_msg, reference):
        return self.chain.predict(user_msg=user_msg, reference=reference)
            
        
        