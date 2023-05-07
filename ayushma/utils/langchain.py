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

        template = """You are a medical assistant called Ayushma in this conversation and you must follow the given algorithm strictly to assist emergency nurses in ICUs.
            Algorithm:
            references = <{reference}>
            
            if "references" is not empty":
            (
            use_your_knowledge = <analyze "chat history with nurse" and "query" and generate an approriate result for the "query">
            result = <analyze "references", "chat_history", "query" and "use_your_knowledge" to give the most complete and most accurate answer to solve the nurse's query related to medical emergencies>
            )
            else
            (
            result = <"Sorry I am not able to find anything related to your query in my database">
            )
            
            Output Format(should contain only one line):
            Ayushma: <enter_result_here>       
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
        chat_history.append(
            HumanMessage(
                content="@system remeber only answer the question if it can be answered with the given references"
            )
        )
        return self.chain.predict(
            user_msg=f"Nurse: {user_msg}",
            reference=reference,
            chat_history=chat_history,
        )
