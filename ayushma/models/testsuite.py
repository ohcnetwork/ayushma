from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    CASCADE,
    CharField,
    FloatField,
    ForeignKey,
    IntegerField,
    TextField,
)

from ayushma.models import Project
from ayushma.models.document import Document
from ayushma.models.enums import FeedBackRating, ModelType, StatusChoices
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
    documents = models.ManyToManyField(Document, blank=True)
    language = models.CharField(max_length=10, blank=False, default="en")


class TestRun(BaseModel):
    test_suite = ForeignKey(TestSuite, on_delete=CASCADE)
    project = ForeignKey(Project, on_delete=CASCADE)
    status = IntegerField(choices=StatusChoices.choices, default=StatusChoices.RUNNING)
    references = models.BooleanField(default=True)
    models = ArrayField(models.IntegerField(choices=ModelType.choices), default=list)


class TestResult(BaseModel):
    test_run = ForeignKey(TestRun, on_delete=CASCADE)
    test_question = ForeignKey(TestQuestion, on_delete=CASCADE)
    question = TextField()
    human_answer = TextField()
    answer = TextField()
    cosine_sim = FloatField()
    bleu_score = FloatField()
    references = models.ManyToManyField(Document, blank=True)
    model = models.IntegerField(choices=ModelType.choices, blank=True, null=True)


class Feedback(BaseModel):
    user = ForeignKey(User, on_delete=CASCADE)
    test_result = ForeignKey(TestResult, on_delete=CASCADE)
    rating = IntegerField(choices=FeedBackRating.choices)
    notes = TextField()
