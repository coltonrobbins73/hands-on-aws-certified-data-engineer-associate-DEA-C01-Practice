import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import current_timestamp

# Initialize contexts and session
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_database', 'source_table', 'target_path', 'target_database', 'target_table'])

source_database = args['source_database']
source_table = args['source_table']
target_path = args['target_path']
target_database = args['target_database']
target_table = args['target_table']

# Read from Glue Catalog
dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
  database=source_database,
  table_name=source_table
)

# Convert to DataFrame to add loadtime
df = dynamic_frame.toDF()
df = df.withColumn("loadtime", current_timestamp())

# Write to S3 in Parquet format, partitioned by loadtime
df.write.partitionBy("loadtime").mode("append").parquet(target_path)

# Create or update table in Glue Catalog
glueContext.write_dynamic_frame.from_options(
  frame=DynamicFrame.fromDF(df, glueContext, "nested"),
  connection_type="s3",
  connection_options={"path": target_path},
  format="parquet",
  transformation_ctx="datasink",
  format_options={"partitionKeys": ["loadtime"]},
  database=target_database,
  table_name=target_table
)

job.commit()