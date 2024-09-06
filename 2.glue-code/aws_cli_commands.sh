aws glue create-table --database-name raw_data --table-input file://raw_schema.json

aws glue get-table --database-name raw_data --name customers
