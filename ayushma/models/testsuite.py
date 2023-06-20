from django.db import models
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    FloatField,
    ForeignKey,
    IntegerField,
    TextField,
)

from ayushma.models import Project
from ayushma.models.enums import FeedBackRating
from ayushma.models.users import User
from utils.models.base import BaseModel


class TestSuite(BaseModel):
    name = CharField(max_length=255)
    temperature = FloatField()
    topk = IntegerField()


class TestQuestion(BaseModel):
    test_suite = ForeignKey(TestSuite, on_delete=CASCADE)
    question = TextField()
    human_answer = TextField()
    language = models.CharField(max_length=10, blank=False, default="en")


class TestRun(BaseModel):
    test_suite = ForeignKey(TestSuite, on_delete=CASCADE)
    project = ForeignKey(Project, on_delete=CASCADE)
    complete = BooleanField(default=False)


class TestResult(BaseModel):
    test_run = ForeignKey(TestRun, on_delete=CASCADE)
    test_question = ForeignKey(TestQuestion, on_delete=CASCADE)
    question = TextField()
    human_answer = TextField()
    answer = TextField()
    cosine_sim = FloatField()
    bleu_score = FloatField()


class Feedback(BaseModel):
    user = ForeignKey(User, on_delete=CASCADE)
    test_result = ForeignKey(TestResult, on_delete=CASCADE)
    rating = IntegerField(choices=FeedBackRating.choices)
    notes = TextField()
