import scala.io.{BufferedSource, Source}

object SrtParser {
  val lineIndex = "^\\d*$"
  val lineTimestamp = "^\\d{2}:\\d{2}:\\d{2},\\d{3} --> \\d{2}:\\d{2}:\\d{2},\\d{3}$"

  def parse(path: String): Unit = {
    var subTitle = new Array[Any](4)

    val bufferedSource: BufferedSource = Source.fromFile(path)

    for (line <- bufferedSource.getLines()) {
      val temp = line.trim()
      if (temp == "") {
        println("%s | %s | %s | %s".format(subTitle(0), subTitle(1), subTitle(2), subTitle(3)))
        subTitle = new Array[Any](4)
      } else if (temp.matches(lineIndex)) {
        subTitle(0) = temp
      } else if (temp.matches(lineTimestamp)) {
        subTitle(1) = temp.split("-->")(0).trim()
        subTitle(2) = temp.split("-->")(1).trim()
      } else {
        subTitle(3) = temp
      }
    }

    bufferedSource.close()
  }
}
