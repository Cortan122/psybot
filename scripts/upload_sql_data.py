#!/usr/bin/env python3

import json
from datetime import date
from glob import glob
from urllib.parse import urljoin

from quizlib.database import engine, session
from quizlib.environment import ARTICLES_SITE, DATA_DIR, ECHO_SQL, QUIZ_DIR, WORDS_PER_MINUTE
from quizlib.models import Article, Quiz

engine.echo = ECHO_SQL

articles: list[Article] = session.query(Article).all()
articles_dict = {(a.category, a.title): a for a in articles}
for file in glob(f"{DATA_DIR}/articles/*/*.json"):
    with open(file) as f:
        obj = json.load(f)

        del obj["docx_url"]
        obj["date"] = date.fromisoformat(obj["date"])
        obj["reading_time"] = round(len(obj["content"].split()) / WORDS_PER_MINUTE)
        obj["article_url"] = urljoin(ARTICLES_SITE, obj.pop("url"))

        if "featured_image" in obj:
            obj["image_url"] = urljoin(ARTICLES_SITE, obj.pop("featured_image"))

        key = (obj["category"], obj["title"])
        if key in articles_dict:
            for k in obj:
                articles_dict[key].__setattr__(k, obj[k])
        else:
            session.add(Article(**obj))

session.commit()

quizzes: list[Quiz] = session.query(Quiz).all()
quizzes_dict = {(a.category, a.filename): a for a in quizzes}
for file in glob(f"{QUIZ_DIR}/*/*.json"):
    with open(file) as f:
        obj = json.load(f)

        obj.pop("scales", None)
        obj["description"] = obj.pop("desc")

        if "question" in obj:
            obj["questions"] = [obj.pop("question")]

        if "answers" in obj and isinstance(obj["answers"], dict):
            obj["answers"] = [list(obj["answers"].values())]

        key = (obj["category"], obj["filename"])
        if key in quizzes_dict:
            for k in obj:
                quizzes_dict[key].__setattr__(k, obj[k])
        else:
            session.add(Quiz(**obj))

session.commit()
