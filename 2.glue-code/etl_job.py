import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Parse job arguments
args = getResolvedOptions(sys.argv, [
  'JOB_NAME',
  'source_database',
  'source_table',
  'target_path',
  'target_database',
  'target_table'
])

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Initialize Glue job
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Extract data from AWS Glue Data Catalog
dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
  database=args['source_database'], 
  table_name=args['source_table'], 
  transformation_ctx="dynamic_frame"
)

# Add current timestamp to the data
dynamic_frame_with_timestamp = dynamic_frame.gs_now(colName="loadtime")

# Define the output sink
sink = glueContext.getSink(
  path=args['target_path'], 
  connection_type="s3", 
  updateBehavior="UPDATE_IN_DATABASE", 
  partitionKeys=["loadtime"], 
  enableUpdateCatalog=True, 
  transformation_ctx="sink"
)

# Set catalog information and format for the output
sink.setCatalogInfo(catalogDatabase=args['target_database'], catalogTableName=args['target_table'])
sink.setFormat("glueparquet", compression="snappy")

# Write the transformed data to the sink
sink.writeFrame(dynamic_frame_with_timestamp)

# Commit the job
job.commit()