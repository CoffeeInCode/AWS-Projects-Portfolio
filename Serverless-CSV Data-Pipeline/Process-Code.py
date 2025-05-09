import json
import boto3
import csv
import io
import os

s3_client = boto3.client('s3')

# Environment variables for target bucket and folder
# These should be configured in the Lambda function's environment variables for flexibility
PROCESSED_BUCKET_NAME = os.environ.get('PROCESSED_BUCKET_NAME')
PROCESSED_BUCKET_KEY_PREFIX = os.environ.get('PROCESSED_BUCKET_KEY_PREFIX', 'processed/') # Default to 'processed/' prefix

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    if not PROCESSED_BUCKET_NAME:
        print("Error: PROCESSED_BUCKET_NAME environment variable not set.")
        return {'statusCode': 500, 'body': json.dumps('Configuration error: PROCESSED_BUCKET_NAME not set')}

    try:
        # Get the bucket and key (filename) from the S3 event
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']

        print(f"Source Bucket: {source_bucket}")
        print(f"Source Key: {source_key}")

        # Ensure the file is a CSV
        if not source_key.lower().endswith('.csv'):
            print(f"File {source_key} is not a CSV. Skipping processing.")
            return {'statusCode': 200, 'body': json.dumps('File is not a CSV. Skipped.')}

        # Get the CSV file object from S3
        response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
        csv_file_content = response['Body'].read().decode('utf-8')

        print("Successfully read CSV from S3.")

        # --- Preprocessing Logic ---
        # Example: Remove rows where 'email' is missing or 'status' is 'pending'
        # You can customize this part heavily.

        reader = csv.DictReader(io.StringIO(csv_file_content))
        processed_rows = []
        headers = reader.fieldnames # Preserve original headers or define new ones

        if not headers:
            print("CSV has no headers or is empty.")
            return {'statusCode': 400, 'body': json.dumps('CSV has no headers or is empty.')}

        for row in reader:
            # Basic validation: check if 'email' exists and is not empty
            if row.get('email') and row['email'].strip():
                # Filter out rows with status 'pending'
                if row.get('status', '').lower() != 'pending':
                    processed_rows.append(row)
            else:
                print(f"Skipping row due to missing email: {row.get('id', 'N/A')}")

        print(f"Original rows: {len(list(csv.DictReader(io.StringIO(csv_file_content))))}, Processed rows: {len(processed_rows)}")

        if not processed_rows:
            print("No data left after preprocessing. Nothing to write.")
            return {'statusCode': 200, 'body': json.dumps('No data after preprocessing.')}

        # Convert processed data back to CSV format
        output_stream = io.StringIO()
        writer = csv.DictWriter(output_stream, fieldnames=headers) # Use original headers for consistency
        writer.writeheader()
        writer.writerows(processed_rows)
        processed_csv_content = output_stream.getvalue()
        output_stream.close()

        # --- End Preprocessing Logic ---

        # Define the destination key (filename) in the processed bucket
        # Example: processed/original_filename.csv
        destination_key = f"{PROCESSED_BUCKET_KEY_PREFIX}{os.path.basename(source_key)}"

        print(f"Writing processed data to: Bucket - {PROCESSED_BUCKET_NAME}, Key - {destination_key}")

        # Upload the processed CSV to the processed data S3 bucket
        s3_client.put_object(
            Bucket=PROCESSED_BUCKET_NAME,
            Key=destination_key,
            Body=processed_csv_content,
            ContentType='text/csv'
        )

        print("Successfully processed and uploaded to processed bucket.")
        return {
            'statusCode': 200,
            'body': json.dumps(f'File {source_key} processed successfully and uploaded to {PROCESSED_BUCKET_NAME}/{destination_key}')
        }

    except Exception as e:
        print(f"Error processing file {source_key} from bucket {source_bucket}: {e}")
        # Consider sending error details to CloudWatch Logs or another monitoring service
        # For production, you might want to move the failed file to a 'dead-letter' S3 prefix
        raise e # Raise exception to allow Lambda to handle retries if configured