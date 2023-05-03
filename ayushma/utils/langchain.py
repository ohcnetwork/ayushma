import os

from django.conf import settings
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage


class LangChainHelper:
    def __init__(self, openai_api_key=settings.OPENAI_API_KEY, prompt_template=None):
        # 0 means more deterministic output, 1 means more random output
        llm = ChatOpenAI(temperature=0.3, openai_api_key=openai_api_key)

        template = """You are a medical assistant called Ayushma in this conversation between you and a nurse. 
            Your purpose is to assist emergency nurses in ICUs and help them with the patients they are handling. 
            You are given a reference and are only allowed to use the reference material and the conversation history while assisting a nurse and answering their queries. 
            You are also given the conversation history at the end with the nurse for better understanding of the query.
            Output Format:
            Ayushma: <enter_Ayushma_reponse_here>
            
            references: [{reference}]        
            """
        if prompt_template:
            template = prompt_template

        system_prompt = PromptTemplate(template=template, input_variables=["reference"])
        system_message_prompt = SystemMessagePromptTemplate(
            prompt=system_prompt,
        )

        human_prompt = PromptTemplate(
            template="{user_msg}", input_variables=["user_msg"]
        )
        human_message_prompt = HumanMessagePromptTemplate(
            prompt=human_prompt,
        )

        message_prompt = MessagesPlaceholder(variable_name="chat_history")

        chat_prompt = ChatPromptTemplate.from_messages(
            [
                system_message_prompt,
                message_prompt,
                human_message_prompt,
            ]
        )

        self.chain = LLMChain(llm=llm, prompt=chat_prompt, verbose=True)

    def get_response(self, user_msg, reference, chat_history):

        print("chat_history", chat_history)
        
        return self.chain.predict(
            user_msg=f"Nurse: {user_msg}",
            reference=reference,
            chat_history=chat_history,
        )
