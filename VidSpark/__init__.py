from __future__ import absolute_import, unicode_literals

import os
from pathlib import Path
import multiprocessing as mp

from elasticsearch import Elasticsearch
from .celery import app as celery_app

__all__ = ('celery_app',)

from pyspark.sql import SparkSession

ROOT = Path(os.path.abspath(os.curdir))

jars = []
for jar in os.listdir(os.path.join(ROOT, "jars")):
    jars.append(os.path.join(ROOT, f"jars/{jar}"))

EXTRA_JARS = ",".join(jars)
DATABASE = os.path.join(ROOT, "db.sqlite3")

print("Initialising Spark...")
spark = SparkSession \
    .builder \
    .appName("VidSpark") \
    .master("local[2]") \
    .config("spark.jars", EXTRA_JARS) \
    .getOrCreate()

spark.conf.set("es.index.auto.create", "true")
print("Initialised!")

print("Starting Elasticsearch...")
es = Elasticsearch()
print("Elasticsearch is running!")

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

THREADS = min(32, mp.cpu_count() + 4)
