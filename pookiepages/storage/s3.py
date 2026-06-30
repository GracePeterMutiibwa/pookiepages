from __future__ import annotations
import uuid
import mimetypes
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from pookiepages.storage.local import SavedFile
from pookiepages.exceptions import PookiePagesError


class S3Storage:
    def __init__(
        self,
        bucket: str,
        accessKey: str,
        secretKey: str,
        region: str = "us-east-1",
        endpointUrl: str | None = None,
        publicUrl: str = "",
    ):
        self.bucket = bucket
        self.publicUrl = publicUrl.rstrip("/")
        self._client = boto3.client(
            "s3",
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            region_name=region,
            endpoint_url=endpointUrl,
        )

    async def save(self, file_data: bytes, filename: str) -> SavedFile:
        import asyncio
        uniqueName = f"{uuid.uuid4().hex}_{filename}"
        mimeType = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.put_object(
                    Bucket=self.bucket,
                    Key=uniqueName,
                    Body=file_data,
                    ContentType=mimeType,
                ),
            )
        except ClientError as clientErr:
            errorCode = clientErr.response["Error"]["Code"]
            errorMsg = clientErr.response["Error"]["Message"]
            raise PookiePagesError(
                f"File upload to S3 bucket '{self.bucket}' failed. "
                f"S3 error {errorCode}: {errorMsg}. "
                f"Check your bucket name, credentials, and permissions."
            )
        except BotoCoreError as botoCoreErr:
            raise PookiePagesError(
                f"File upload to S3 bucket '{self.bucket}' failed. "
                f"Connection error: {botoCoreErr}. "
                f"Check your endpoint URL and network connectivity."
            )

        url = f"{self.publicUrl}/{uniqueName}" if self.publicUrl else f"https://{self.bucket}.s3.amazonaws.com/{uniqueName}"
        return SavedFile(url=url, name=uniqueName, size=len(file_data), mimeType=mimeType)


class R2Storage(S3Storage):
    def __init__(
        self,
        accountId: str,
        bucket: str,
        accessKey: str,
        secretKey: str,
        publicUrl: str = "",
    ):
        endpointUrl = f"https://{accountId}.r2.cloudflarestorage.com"
        super().__init__(
            bucket=bucket,
            accessKey=accessKey,
            secretKey=secretKey,
            region="auto",
            endpointUrl=endpointUrl,
            publicUrl=publicUrl,
        )
