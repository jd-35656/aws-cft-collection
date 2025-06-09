"""
Script that zips changed lambda folders and uploads them to S3.

Bucket name and AWS region can be passed as CLI arguments or environment variables.
AWS credentials must be configured separately via environment variables, IAM roles, or config files.
"""

import argparse
import logging
import os
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import (  # type: ignore
    BotoCoreError,
    ClientError,
    NoCredentialsError,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def list_all_folders(root_folder_name: str) -> set[str]:
    """
    Given a root folder name (like 'templates'), return the set of all first-level subfolder names inside it.
    """
    root_path = Path(root_folder_name)
    if not root_path.exists() or not root_path.is_dir():
        return set()
    return {p.name for p in root_path.iterdir() if p.is_dir()}


def zip_folder(lambda_name: str, root_folder_name: str) -> Path:
    """
    Zip the contents of a folder and return the zip file Path.
    """
    lambda_path = Path(root_folder_name) / lambda_name
    if not lambda_path.exists():
        raise FileNotFoundError(f"Lambda directory not found: {lambda_path}")

    build_dir = Path("build")
    build_dir.mkdir(parents=True, exist_ok=True)
    zip_filename = build_dir / f"{lambda_name}.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(lambda_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(lambda_path)
                zipf.write(file_path, arcname)

    return zip_filename


def upload_to_s3(
    filename: Path,
    s3_bucket: str,
    s3_prefix: str,
    aws_region: str,
) -> None:
    """
    Upload a file to S3 bucket with optional prefix.
    """
    key = f"{s3_prefix}/{filename}"
    logger.info(f"Uploading {filename} to s3://{s3_bucket}/{key}")

    try:
        s3 = boto3.client("s3", region_name=aws_region)
        s3.upload_file(str(filename), s3_bucket, key)
    except (NoCredentialsError, BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload {filename} to S3: {e}")
        raise


def main() -> None:
    """
    Main function to zip changed lambda folders, upload them to S3,
    and upload changed template files to S3.
    """
    parser = argparse.ArgumentParser(
        description="Upload changed Lambda zips and templates to S3"
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Base branch to compare changes against",
    )
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--region", default="ap-south-1", help="AWS region")
    parser.add_argument("--repository", required=True, help="Name of repository")
    args = parser.parse_args()

    changed_lambdas = list_all_folders("lambdas")
    if not changed_lambdas:
        logger.info("No lambda folders detected.")
    for lambda_name in changed_lambdas:
        try:
            zip_file = zip_folder(lambda_name, "lambdas")
            upload_to_s3(
                zip_file,
                args.bucket,
                f"{args.repository}/{args.branch}/lambdas",
                args.region,
            )
            logger.info(f"Uploaded {zip_file.name} to S3 bucket {args.bucket}.")
        except Exception as e:
            logger.error(f"Error processing lambda {lambda_name}: {e}")
            raise

    changed_templates = list_all_folders("templates")
    if not changed_templates:
        logger.info("No CloudFormation templates detected.")
    for template_folder in changed_templates:
        template_path = Path("templates") / template_folder
        if not template_path.exists():
            logger.warning(f"Template folder not found: {template_path}")
            continue
        file_path = template_path / "template.yaml"
        if not file_path.exists():
            logger.warning(f"Template file not found: {file_path}")
            continue
        try:
            upload_to_s3(
                file_path,
                args.bucket,
                f"{args.repository}/{args.branch}/cfts",
                args.region,
            )
            logger.info(f"Uploaded {file_path.name} to S3 bucket {args.bucket}.")
        except Exception as e:
            logger.error(f"Error uploading template {file_path}: {e}")
            raise


if __name__ == "__main__":
    main()
