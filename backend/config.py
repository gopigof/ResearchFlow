from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, extra="ignore"):
    # Snowflake DB
    SNOWFLAKE_DB_USER: str
    SNOWFLAKE_DB_PASSWORD: str
    SNOWFLAKE_DB_ACCOUNT: str
    SNOWFLAKE_DB_ROLE: str
    SNOWFLAKE_DB_WAREHOUSE: str = "COMPUTE_WH"  # Default warehouse, change if needed
    SNOWFLAKE_DB_DATABASE: str = "MY_DATABASE"  # Default database, change if needed
    SNOWFLAKE_DB_SCHEMA: str = "PUBLIC"  # Default schema, change if needed
    SNOWFLAKE_CONN_STRING: str | None = None

    # Milvus Cloud (for vector store)
    MILVUS_CLOUD_USER: str
    MILVUS_CLOUD_PASSWORD: str
    MILVUS_API_KEY: str
    MILVUS_CLOUD_URI: str
    MILVUS_DOCUMENTS_COLLECTION: str = "DocumentsIndex"
    MILVUS_REPORTS_COLLECTION: str = "Reports"

    # JWT Authentication
    JWT_ACCESS_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 3  # 3 hours
    JWT_REFRESH_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 24 * 1  # 1 day
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str

    # Fast API config
    APP_TITLE: str = "QA & Summarization Interface"
    APP_VERSION: str = "0.1"

    # AWS S3 Bucket
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str

    # Logging Config
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_MAX_BYTES: int = 2000000  # Default to 2MB
    LOG_BACKUP_COUNT: int = 10

    # Nvidia API KEY
    NVIDIA_API_KEY: str

    # #Open
    # OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def validator(cls, values: "Settings") -> "Settings":
        # Construct Snowflake connection string
        values.SNOWFLAKE_CONN_STRING = (
            f"snowflake://{values.SNOWFLAKE_DB_USER}:{values.SNOWFLAKE_DB_PASSWORD}@{values.SNOWFLAKE_DB_ACCOUNT}/"
            f"{values.SNOWFLAKE_DB_DATABASE}/{values.SNOWFLAKE_DB_SCHEMA}?warehouse={values.SNOWFLAKE_DB_WAREHOUSE}"
        )
        return values


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
