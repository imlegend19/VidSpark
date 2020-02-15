from pyspark.sql import SQLContext
from pyspark import SparkContext

if __name__ == '__main__':
    sc = SparkContext()
    sc.setLogLevel("WARN")

    sql_context = SQLContext(sc)

    data = sql_context.read.text("Hello")

    data.printSchema()
    data.select("time")
