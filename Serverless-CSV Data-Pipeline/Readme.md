# Serverless CSV Data Pipeline with AWS

## Project Overview

This project implements a serverless data pipeline on AWS to ingest, preprocess, transform, and visualize CSV data. It demonstrates a common ETL (Extract, Transform, Load) pattern using a suite of managed AWS services, providing a scalable, cost-effective, and automated solution for data processing.

The pipeline automatically processes CSV files uploaded to an S3 bucket, cleans the data using an AWS Lambda function, catalogs and transforms the data using AWS Glue, and finally stores the refined data in another S3 bucket, ready for analysis and visualization in Amazon QuickSight.

## 🎯 Project Objectives

* **Automated Ingestion:** Accept CSV file uploads to an Amazon S3 bucket.
* **Serverless Preprocessing:** Trigger an AWS Lambda function on S3 upload to perform initial data cleaning and validation.
* **Schema Management & Transformation:** Utilize AWS Glue Crawlers to infer schema and AWS Glue ETL jobs to perform data transformations (e.g., renaming columns, filtering rows).
* **Scalable Storage:** Store raw, processed, and final transformed data in separate S3 buckets/prefixes for clarity and organization.
* **Interactive Visualization:** Build dashboards in Amazon QuickSight to analyze and present insights from the transformed data (e.g., total signups by date).
* **Security & Best Practices:** Implement secure access using IAM Roles and Policies, and follow best practices for serverless architecture.
* **Low-Cost & Reusable:** Design the pipeline to be cost-efficient by leveraging serverless components and make it adaptable for different CSV datasets.

## ⚙️ Architecture

The data flows through the following AWS services:

1.  **Amazon S3 (`csv-raw-data-<your-unique-identifier>`)**:
    * Initial storage for uploaded CSV files.
    * Triggers the Lambda function upon new object creation.
2.  **AWS Lambda (`PreprocessCSVFunction`)**:
    * Triggered by S3.
    * Reads the raw CSV.
    * Performs preprocessing (e.g., basic cleaning, filtering out invalid records).
    * Saves the processed CSV to a designated S3 bucket.
3.  **Amazon S3 (`csv-processed-data-<your-unique-identifier>/processed/`)**:
    * Stores the intermediate, preprocessed CSV files from Lambda.
4.  **AWS Glue Crawler (`processed_csv_crawler`)**:
    * Scans the `csv-processed-data` bucket.
    * Infers the schema of the processed data.
    * Creates/updates a table in the AWS Glue Data Catalog (`csv_pipeline_db`).
5.  **AWS Glue ETL Job (`TransformCSVDataJob`)**:
    * Reads data from the Glue Data Catalog table (sourced from `csv-processed-data`).
    * Performs transformations (e.g., renames columns, filters data based on business logic, selects specific fields).
    * Writes the final, transformed data to another S3 bucket.
6.  **Amazon S3 (`csv-final-data-<your-unique-identifier>/final_output/`)**:
    * Stores the fully transformed data, ready for analytics.
    * Data can be stored in formats like CSV or Parquet (recommended for analytics).
7.  **Amazon QuickSight**:
    * Connects to the data in the `csv-final-data` bucket (either directly via S3 manifest or through Athena leveraging the Glue Catalog).
    * Enables creation of interactive dashboards and visualizations.

**(Conceptual Diagram)**
`Upload (CSV)` -> `S3 (raw)` -> `Lambda` -> `S3 (processed)` -> `Glue Crawler` -> `Glue Catalog` -> `Glue Job` -> `S3 (final)` -> `QuickSight`

## 🛠️ AWS Services Used

* **Amazon S3:** For scalable object storage (raw, processed, and final data).
* **AWS Lambda:** For serverless compute to preprocess CSV files.
* **AWS Glue:**
    * **Data Catalog:** As a central metadata repository.
    * **Crawlers:** To automatically discover and catalog data schemas.
    * **ETL Jobs:** For serverless Spark-based data transformation.
* **Amazon QuickSight:** For business intelligence and data visualization.
* **AWS IAM (Identity and Access Management):** For securely managing access to AWS services and resources.
* **Amazon CloudWatch:** For logging and monitoring Lambda functions and Glue jobs.

## 📄 Data Format

The pipeline is designed to process structured tabular data in CSV format. The sample data used for development and testing has the following schema:

```csv
id,name,email,signup_date,status
1,John Doe,john@example.com,2024-11-01,active
2,Jane Smith,jane@example.com,2024-11-02,inactive
3,Alice Brown,alice@example.com,2024-11-02,active
...