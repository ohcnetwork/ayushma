from time import sleep

import openai
from celery import shared_task
from django.conf import settings
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

from ayushma.models.chat import Chat
from ayushma.models.testsuite import TestResult, TestRun
from ayushma.utils.language_helpers import translate_text
from ayushma.utils.openaiapi import converse, cosine_similarity, get_embedding


@shared_task
def mark_test_run_as_completed(test_run_id):
    sleep(5)

    if not settings.OPENAI_API_KEY:
        print("OpenAI API key not found. Skipping test run.")
        return

    test_run = TestRun.objects.get(id=test_run_id)
    test_suite = test_run.test_suite
    test_questions = test_suite.testquestion_set.all()

    temperature = test_suite.temperature
    topk = test_suite.topk

    chat = Chat()
    chat.title = "Test Run: " + test_run.created_at.strftime("%Y-%m-%d %H:%M:%S")
    chat.project = test_run.project
    chat.save()

    for test_question in test_questions:
        test_result = TestResult()
        test_result.test_run = test_run
        test_result.test_question = test_question
        test_result.question = test_question.question
        test_result.human_answer = test_question.human_answer

        try:
            english_text = test_question.question
            translated_text = test_question.question

            if test_question.language != "en":
                english_text = translate_text("en-IN", english_text)
                translated_text = translate_text(
                    test_question.language + "-IN", english_text
                )

            ai_response = next(
                converse(
                    english_text=english_text,
                    local_translated_text=translated_text,
                    openai_key=settings.OPENAI_API_KEY,
                    chat=chat,
                    match_number=topk,
                    stats=dict(),
                    temperature=temperature,
                    user_language=test_question.language + "-IN",
                    stream=False,
                    generate_audio=False,
                )
            )

            # Calculate cosine similarity
            openai.api_key = settings.OPENAI_API_KEY
            ai_response_embedding = get_embedding(ai_response.message)
            human_answer_embedding = get_embedding(test_question.human_answer)
            cosine_sim = cosine_similarity(
                ai_response_embedding, human_answer_embedding
            )

            # Calculate BLEU score ( https://www.nltk.org/api/nltk.translate.bleu_score.html#nltk.translate.bleu_score.SmoothingFunction.__init__ )
            reference_tokens = test_question.human_answer.split()
            candidate_tokens = ai_response.message.split()

            smoothie = SmoothingFunction().method4
            bleu_score = sentence_bleu(
                [reference_tokens], candidate_tokens, smoothing_function=smoothie
            )

            test_result.answer = ai_response.message
            test_result.cosine_sim = cosine_sim
            test_result.bleu_score = round(bleu_score, 4)

        except Exception as e:
            print("Error while running test question: ", e)
            test_result.answer = ""
            test_result.cosine_sim = 0
            test_result.bleu_score = 0

        finally:
            test_result.save()
            test_result.references.set(ai_response.reference_documents.all())
            test_result.save()
    test_run.complete = True
    test_run.save()
