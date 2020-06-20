import java.io.File

import org.apache.spark.sql.SparkSession

import scala.util.control.Breaks
import org.apache.log4j._
import SrtParser._

class ReadSRT(val spark: SparkSession) {
  case class Transcript(id: Int, startTime: String, endTime: String, message: String)

  def parseFile(path: String): Unit = {
    println("Parsing -> %s".format(path))

    SrtParser.parse(path)
  }

  def readFiles(path: String): Unit = {
    val loop = new Breaks

    loop.breakable {
      for (file <- new File(path).listFiles.sortBy(_.getName)) {
        parseFile(file.getPath)
        loop.break()
      }
    }
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

    import spark.implicits._

    new ReadSRT(spark)
      .readFiles("/home/mahen/ScalaProjects/vidspark/src/main/data/alv_srt")

    println("Closing spark...")
    spark.close()
  }
}
