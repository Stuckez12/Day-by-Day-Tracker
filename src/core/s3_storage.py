from typing import TYPE_CHECKING, BinaryIO

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from src.enums import ObjectType
from src.schemas import FileObjectUploaded
from src.settings import app_config


if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


class ObjectStorage:
    def __init__(self):
        self.client: "S3Client" = boto3.client(
            "s3",
            endpoint_url=app_config.S3_HTTP_ADDRESS,
            aws_access_key_id=app_config.S3_ACCESS_KEY,
            aws_secret_access_key=app_config.S3_SECRET_KEY,
            region_name=app_config.S3_REGION,
        )

    def _raise_client_http_exception(self, status_code: int, detail: str):
        raise HTTPException(status_code=status_code, detail=f"Client Error: {detail}")

    def create_bucket(self, bucket_name: ObjectType, error_if_exists: bool = True):
        if self.bucket_exists(bucket_name):
            if error_if_exists:
                raise ValueError("Bucket already exists")

            return

        self.client.create_bucket(Bucket=bucket_name.value)

    def bucket_exists(self, bucket_name: ObjectType) -> bool:
        try:
            self.client.head_bucket(Bucket=bucket_name.value)

            return True

        except ClientError as e:
            status_code = int(e.response["Error"]["Code"])  # type: ignore
            detail = str(e.response["Error"]["Message"])  # type: ignore

            if status_code == 404:
                return False

            self._raise_client_http_exception(status_code=status_code, detail=detail)

    def upload_file(
        self, file: BinaryIO, file_type: ObjectType, file_dir: str
    ) -> FileObjectUploaded:
        if file_dir[-1] == "/":
            raise IndexError("Invalid file directory provided")

        self.create_bucket(file_type, error_if_exists=False)

        self.client.upload_fileobj(
            Fileobj=file,
            Bucket=file_type.value,
            Key=file_dir,
        )

        return FileObjectUploaded(
            message="File successfully uploaded",
            bucket=file_type,
            filename=file_dir.split("/")[-1],
        )

    def download_file(self, file_type: ObjectType, file_dir: str):
        self.create_bucket(file_type, error_if_exists=False)

        file_object = self.client.get_object(
            Bucket=file_type.value,
            Key=file_dir,
        )

        return file_object

    def delete_file(self):
        pass
