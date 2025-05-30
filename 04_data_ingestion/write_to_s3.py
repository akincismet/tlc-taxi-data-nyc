import os, logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# ─── Upload every file under a local directory to S3 ──────────────────────
def upload_to_s3(
    local_dir: str | Path,
    bucket: str,
    s3_prefix: str = "",
    *,
    s3_endpoint: str | None = None,
    aws_access_key: str | None = None,
    aws_secret_key: str | None = None,
    region: str | None = None,
):
    """
    Walk *local_dir* recursively and copy each file to
    s3://<bucket>/<s3_prefix>/<relative_path>.

    Example
    -------
    >>> upload_to_s3(
    ...     local_dir='data/year=2023/month=1/day=15',
    ...     bucket='bronze',
    ...     s3_prefix='data/year=2023/month=1/day=15',
    ...     s3_endpoint='http://localhost:30900',
    ...     aws_access_key='minioadmin',
    ...     aws_secret_key='minioadmin123'
    ... )
    """
    log = logging.getLogger("upload_to_s3")

    session_kwargs = dict(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region,
    )
    # strip Nones (avoids boto3 warnings)
    session_kwargs = {k: v for k, v in session_kwargs.items() if v is not None}

    s3 = boto3.client("s3", endpoint_url=s3_endpoint, **session_kwargs)

    # create bucket if it doesn't exist (best-effort)
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchBucket"):
            log.info("Bucket %s not found - creating it.", bucket)
            s3.create_bucket(Bucket=bucket)
        else:
            raise

    local_dir = Path(local_dir).expanduser().resolve()
    for root, _, files in os.walk(local_dir):
        for fname in files:
            local_path = Path(root) / fname
            rel_path   = local_path.relative_to(local_dir)
            key        = str(Path(s3_prefix) / rel_path).replace("\\", "/")  # win→unix

            log.info("↑ %s → s3://%s/%s", local_path, bucket, key)
            s3.upload_file(str(local_path), bucket, key)
    log.info("✓ Upload completed for %s", local_dir)
    return f"s3://{bucket}/{s3_prefix}".rstrip("/")
