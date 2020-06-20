name := "vidspark"

version := "0.1"

scalaVersion := "2.11.12"

libraryDependencies ++= Seq(
  "org.apache.spark" % "spark-core_2.11" % "2.4.5",
  "org.apache.spark" % "spark-sql_2.11" % "2.4.5",
  "org.apache.spark" % "spark-mllib_2.11" % "2.4.5"
)
