: <<'END_COMMENT'
This is a list of cli commands for easy reference
END_COMMENT

# make a table from json and check that it exists
aws glue create-table --database-name raw_data --table-input file://raw_schema.json
aws glue get-table --database-name raw_data --name customers

# make a crawler from json, start it, and then check it's status
aws glue create-crawler --cli-input-json file://mk_emp_crawler.json
aws glue start-crawler --name "employees"
aws glue get-crawler --name "employees"

# make etl job and run it
aws glue create-job --cli-input-json file://customer_etl_job.json
aws glue start-job-run --job-name "customer_etl_job"
aws glue get-job-runs --job-name "customer_etl_job"
