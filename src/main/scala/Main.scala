import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.log4j._
import org.apache.spark.sql.types.{IntegerType, StringType, StructField, StructType}

class SetUpVidSpark(val spark: SparkSession, val path: String) {
  def initDataset(): Unit = {
    val df: DataFrame = spark.read
      .format("csv")
      .option("header", "true")
      .load(path)

    df.createOrReplaceTempView("data")

    val ids: Seq[Int] = df.select("id")
      .distinct()
      .collect()
      .map(r => r.getString(0).toInt)
      .toList

    val vidTextSchema = List(
      StructField("id", IntegerType, nullable = false),
      StructField("text", StringType, nullable = false)
    )

    val vidText = Seq[Row]()

    for (id <- ids) {
      val msg = df.filter("id = %d".format(id))
        .select("msg")
        .collect()
        .map(r => r.getString(0))
        .toList
        .mkString(" ")

      vidText :+ Row(id, msg)
    }

    val vidTextDf = spark.createDataFrame(
      spark.sparkContext.parallelize(vidText),
      StructType(vidTextSchema)
    )

    // TODO: Generate topics for vidTextDf
  }

  def process(): Unit = {
    println("Setting up VidSpark...")
    initDataset()
  }
}

object Main {
  Logger.getLogger("org").setLevel(Level.ERROR)

  def main(args: Array[String]): Unit = {
    println("Initialising spark...")
    val spark = SparkSession
      .builder()
      .appName("VidSpark")
      .master("local")
      .getOrCreate()

    println("Initialised!")

    new SetUpVidSpark(spark, "data/alv.csv")
      .process()

    println("Closing spark...")
    spark.stop()
  }
}
