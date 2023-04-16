import os

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI


class LangChainHelper:
    def __init__(self):
        # 0 means more deterministic output, 1 means more random output
        llm = ChatOpenAI(temperature=0)
        template = """You are a medical assistant called Ayushma in this conversation between you and a nurse. 
            Your purpose is to assist emergency nurses in ICUs and help them with the patients they are handling. 
            You are given a reference and are only allowed to use the reference material and the conversation history while assisting a nurse and answering their queries. 
            You are also given the conversation history at the end with the nurse for better understanding of the query.
            Output Format(sould contain only one line):
            Ayushma: <enter_Ayushma_reponse_here>
            
            query: {user_msg}
            reference: {reference}

            Conversation history with the nurse:
            {chat_history}
            """
        prompt = PromptTemplate(
            input_variables=["user_msg", "reference", "chat_history"], template=template
        )

        self.chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    def get_response(self, user_msg, reference, chat_history):
        return self.chain.predict(
            user_msg=user_msg, reference=reference, chat_history=chat_history
        )
