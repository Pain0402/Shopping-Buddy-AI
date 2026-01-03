import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
import uuid
import io
from app.core.config import settings

class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Tạo bucket nếu chưa tồn tại (Dành cho môi trường Dev/MinIO)"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                print(f"Could not create bucket: {e}")

    async def upload_file(self, file: UploadFile) -> str:
        """
        Upload file lên S3 và trả về File Key (Path).
        """
        # 1. Tạo tên file unique để tránh trùng lặp
        file_extension = file.filename.split(".")[-1]
        file_key = f"{uuid.uuid4()}.{file_extension}"
        
        try:
            # 2. Upload
            # Lưu ý: upload_fileobj là hàm sync, nhưng boto3 xử lý I/O khá tốt.
            # Trong production scale lớn, có thể dùng aioboto3, nhưng boto3 là đủ cho giai đoạn này.
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_key,
                ExtraArgs={"ContentType": file.content_type}
            )
            return file_key
        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"S3 Upload Failed: {str(e)}")

    def get_presigned_url(self, file_key: str, expiration=3600) -> str:
        """
        Tạo URL tạm thời để xem ảnh (Bảo mật: URL này chỉ sống 1 tiếng)
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError:
            return ""
    def download_file_as_bytes(self, file_key: str) -> bytes:
        """
        Tải file từ S3 và trả về dạng bytes (để nạp vào AI Model)
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            raise e