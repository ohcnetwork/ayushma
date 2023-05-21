from django.conf import settings
from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage

from ayushma.utils.stream_callback import StreamingQueueCallbackHandler


class LangChainHelper:
    def __init__(
        self,
        token_queue,
        end,
        openai_api_key=settings.OPENAI_API_KEY,
        prompt_template=None,
    ):
        # 0 means more deterministic output, 1 means more random output
        llm = ChatOpenAI(
            streaming=True,
            callback_manager=AsyncCallbackManager(
                [StreamingQueueCallbackHandler(token_queue, end)]
            ),
            temperature=0.3,
            openai_api_key=openai_api_key,
        )

        template = """You are a female medical assistant called Ayushma who understands all languages and repsonds only in english and you must follow the given algorithm strictly to assist emergency nurses in ICUs. Remember you must give accurate answers otherwise it can risk the patient's life, so stick strictly to the references as explained in algorithm. Your output must be in markdown format find important terms and add bold to it (example **word**) find numbers and add italic to it(example *word*) add bullet points to a list(example -word1\n-word2):
Algorithm:
references = {reference}
/*
The references a dictionary with the key, value pairs in the following format:
<reference_id>: <text>
'text' is the content of the reference from what you can extract the information to solve the nurse's query.
*/

can_query_be_solved_by_given_references = <analyze the given "references" and current nurse's query and return true if "references" strictly contains the information to solve the current query else return false>
if "can_query_be_solved_by_given_references":
(
use_your_knowledge = <analyze "chat history with nurse" and "query" and generate an approriate result for the "query">
result = <analyze "references", chat history with nurse and nurse's current query to give the most descriptive and most accurate answer to solve the nurse's query related to medical emergencies.>
)
else:
(
result = <"Sorry I am not able to find anything related to your query in my database">

Output Format(should contain only one line'):
Ayushma: <enter_result_here> <"IMPORTANT: display reference ids in comma separated format exactly like this (don't change the format): 'References: id1, id2, id3 etc.' and don't apply any formating to references. You must display references at the end in all responses and display only relevant reference_ids from which you formed the answer">"""
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

    async def get_response(
        self, job_done, token_queue, user_msg, reference, chat_history
    ):
        chat_history.append(
            HumanMessage(
                content="@system remeber only answer the question if it can be answered with the given references"
            )
        )
        try:
            async_response = await self.chain.apredict(
                user_msg=f"Nurse: {user_msg}",
                reference=reference,
                chat_history=chat_history,
            )
            token_queue.put(job_done)
            return async_response
        except Exception as e:
            print(e)
            token_queue.put(job_done)
