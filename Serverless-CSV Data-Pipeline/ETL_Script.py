import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3 # For direct S3 operations if needed, though Glue handles most.

# Initialize contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job arguments (if any are passed, not used in this basic script)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job.init(args['JOB_NAME'], args)

# Define Database and Table names from the Glue Data Catalog
database_name = "YOUR_DATABASE_NAME" # e.g., "csv_pipeline_db"
source_table_name = "YOUR_TABLE_NAME_FROM_CRAWLER" # e.g., "processed" or "processed_csv_processed_data_..."

# Define the S3 path for the final output
# It's good practice to include a trailing slash for a "folder"
final_output_s3_path = "s3://csv-final-data-<your-unique-identifier>/final_output/" # e.g., "s3://csv-final-data-johndoe-20250507/final_output/"

# Read data from Glue Data Catalog (sourced from csv-processed-data)
# This creates a DynamicFrame
input_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
    database=database_name,
    table_name=source_table_name,
    transformation_ctx="input_dynamic_frame_ctx" # Context for bookmarking
)

print(f"Schema of input_dynamic_frame:")
input_dynamic_frame.printSchema()
print(f"Count of records in input_dynamic_frame: {input_dynamic_frame.count()}")

if input_dynamic_frame.count() == 0:
    print("No data in the source table. Exiting job.")
    job.commit()
    sys.exit(0) # Exit gracefully

# --- Transformation Logic ---
# Example 1: Rename a column
# From 'signup_date' to 'registration_date'
transformed_dynamic_frame = RenameField.apply(
    frame=input_dynamic_frame,
    old_name="`signup_date`", # Backticks needed if there are special characters or spaces, or just good practice
    new_name="`registration_date`",
    transformation_ctx="rename_field_ctx"
)
print("Schema after renaming 'signup_date':")
transformed_dynamic_frame.printSchema()

# Example 2: Filter rows
# Keep only rows where 'status' is 'active'
# Note: You might have already filtered in Lambda. This is an example of further transformation.
# If status column might not exist (e.g. due to schema evolution), add checks.
# For robust filtering, ensure the 'status' column exists or handle potential errors.
# One way is to convert to DataFrame for easier column checks or use Filter.apply with a custom function.

# Simple filter assuming 'status' column exists:
if 'status' in [field.name for field in transformed_dynamic_frame.schema()]:
    filtered_dynamic_frame = Filter.apply(
        frame=transformed_dynamic_frame,
        f=lambda x: x["status"] == "active",
        transformation_ctx="filter_status_ctx"
    )
    print(f"Count after filtering for 'active' status: {filtered_dynamic_frame.count()}")
else:
    print("Column 'status' not found, skipping filter by status.")
    filtered_dynamic_frame = transformed_dynamic_frame # Pass through if column doesn't exist

# Example 3: Select specific columns for the final output
# Let's say we only want id, name, email, registration_date
# Note: If you filtered by status, 'status' column might still be there.
# The SelectFields transform will only keep specified fields.
final_selected_dynamic_frame = SelectFields.apply(
    frame=filtered_dynamic_frame,
    paths=["`id`", "`name`", "`email`", "`registration_date`"], # Use the new name 'registration_date'
    transformation_ctx="select_fields_ctx"
)
print("Schema after SelectFields:")
final_selected_dynamic_frame.printSchema()
print(f"Count after SelectFields: {final_selected_dynamic_frame.count()}")

# --- End Transformation Logic ---

if final_selected_dynamic_frame.count() == 0:
    print("No data left after transformations. Exiting job.")
    job.commit()
    sys.exit(0) # Exit gracefully

# Write the transformed data to the final S3 bucket
# Output format can be CSV, Parquet (recommended for analytics), JSON, etc.
# For Parquet (better for QuickSight performance with Athena):
# glueContext.write_dynamic_frame.from_options(
#     frame=final_selected_dynamic_frame,
#     connection_type="s3",
#     connection_options={"path": final_output_s3_path, "partitionKeys": []}, # No partitioning in this example
#     format="parquet",
#     transformation_ctx="write_parquet_ctx"
# )

# For CSV output (as requested initially):
glueContext.write_dynamic_frame.from_options(
    frame=final_selected_dynamic_frame,
    connection_type="s3",
    connection_options={"path": final_output_s3_path}, # CSVs will be written here
    format="csv",
    format_options={"quoteChar": -1, "writeHeader": True}, # writeHeader ensures CSV has headers
    transformation_ctx="write_csv_ctx"
)

print(f"Successfully transformed data and wrote to {final_output_s3_path}")

# Commit the job bookmark
job.commit()