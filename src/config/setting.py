from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODEL_NAME: str = Field(...)
    PROVIDER: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class MobileModelConfig(BaseSettings):
    MOBILE_BASE_URL: str = Field(...)
    MOBILE_MODEL_NAME: str = Field(...)
    MOBILE_PROVIDER: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
mobile_model_config = MobileModelConfig()


if __name__ == "__main__":
    # print(settings.MODEL_NAME)
    # print(settings.PROVIDER)
    print(mobile_model_config.MOBILE_BASE_URL)
    print(mobile_model_config.MOBILE_MODEL_NAME)
    print(mobile_model_config.MOBILE_PROVIDER)
