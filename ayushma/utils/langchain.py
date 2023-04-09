import os

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI


class LangChainHelper:
    def __init__(self):
        # 0 means more deterministic output, 1 means more random output
        llm = ChatOpenAI(temperature=0)
        template = """You are an AI assistant called Ayushma. You purpose is to assist people for medical queries. You are given a reference and are only allowed to use the reference while assisting a user and answering their queries.
query: {user_msg}
reference: {reference}
"""
        prompt = PromptTemplate(
            input_variables=["user_msg", "reference"], template=template
        )

        self.chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    def get_response(self, user_msg, reference):
        return self.chain.predict(user_msg=user_msg, reference=reference)
