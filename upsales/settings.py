"""
Settings management using Pydantic v2.

Provides type-safe configuration from environment variables with validation
using the same validators as models. This is the recommended way to configure
the Upsales SDK.

Example:
    >>> from upsales.settings import UpsalesSettings
    >>>
    >>> # Load from .env file with validation
    >>> settings = UpsalesSettings()
    >>> print(settings.upsales_token[:10])
    >>>
    >>> # Use with client
    >>> upsales = Upsales(
    ...     token=settings.upsales_token,
    ...     max_concurrent=settings.upsales_max_concurrent
    ... )
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from upsales.validators import EmailStr


class UpsalesSettings(BaseSettings):
    """
    Upsales SDK configuration from environment variables.

    Automatically loads from .env file with type validation and field validation.
    Reuses the same Pydantic v2 validators as models for consistency.

    All settings are loaded from environment variables with the UPSALES_ prefix.

    Environment Variables:
        UPSALES_TOKEN: API authentication token (required).
        UPSALES_EMAIL: Email for fallback authentication (optional).
        UPSALES_PASSWORD: Password for fallback authentication (optional).
        UPSALES_ENABLE_FALLBACK_AUTH: Enable automatic token refresh (default: false).
        UPSALES_BASE_URL: API base URL (default: https://power.upsales.com/api/v2).
        UPSALES_MAX_CONCURRENT: Maximum concurrent requests 1-200 (default: 50).

    Example:
        >>> # .env file:
        >>> # UPSALES_TOKEN=your_token_here
        >>> # UPSALES_MAX_CONCURRENT=100
        >>>
        >>> settings = UpsalesSettings()
        >>> settings.upsales_token
        'your_token_here'
        >>> settings.upsales_max_concurrent
        100

    Example with Validation:
        >>> # .env file:
        >>> # UPSALES_MAX_CONCURRENT=999  # Too high!
        >>>
        >>> settings = UpsalesSettings()
        Traceback (most recent call last):
        ...
        ValidationError: upsales_max_concurrent must be <= 200

    Example with Upsales Client:
        >>> settings = UpsalesSettings()
        >>> async with Upsales(
        ...     token=settings.upsales_token,
        ...     max_concurrent=settings.upsales_max_concurrent
        ... ) as upsales:
        ...     user = await upsales.users.get(1)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # Required - API Token
    upsales_token: str = Field(description="Upsales API authentication token (required)")

    # Optional - Fallback Authentication
    upsales_email: EmailStr | None = Field(
        None, description="Email for fallback authentication (token refresh)"
    )

    upsales_password: str | None = Field(None, description="Password for fallback authentication")

    upsales_enable_fallback_auth: bool = Field(
        False, description="Enable automatic token refresh on expiration"
    )

    # API Configuration
    upsales_base_url: str = Field(
        default="https://power.upsales.com/api/v2", description="Upsales API base URL"
    )

    upsales_max_concurrent: int = Field(
        50, ge=1, le=200, description="Maximum concurrent requests (1-200, API limit is 200/10sec)"
    )

    @field_validator("upsales_max_concurrent")
    @classmethod
    def validate_max_concurrent_reasonable(cls, v: int) -> int:
        """
        Validate max_concurrent is reasonable for API rate limits.

        Upsales API allows 200 requests per 10 seconds. Setting max_concurrent
        too high could trigger rate limits.

        Args:
            v: Max concurrent value.

        Returns:
            Validated value.

        Raises:
            ValueError: If value is unreasonably high.
        """
        if v > 200:
            raise ValueError(
                f"upsales_max_concurrent ({v}) exceeds API rate limit (200 req/10sec). "
                "Use value <= 200 to avoid rate limit errors."
            )
        if v > 100:
            # Warning in docstring - consider if this is too aggressive
            pass  # Allow but could add warning log
        return v


def load_settings(env_file: str = ".env") -> UpsalesSettings:
    """
    Load and validate Upsales settings from environment.

    Convenience function that loads settings from specified .env file
    and validates all configuration.

    Args:
        env_file: Path to .env file (default: ".env").

    Returns:
        Validated UpsalesSettings instance.

    Raises:
        ValidationError: If required settings missing or invalid.

    Example:
        >>> settings = load_settings()
        >>> settings.upsales_token
        'your_token_here'

        >>> # Load from different env file
        >>> prod_settings = load_settings(".env.production")

        >>> # Handle validation errors
        >>> try:
        ...     settings = load_settings()
        ... except ValidationError as e:
        ...     print(f"Invalid configuration: {e}")
    """
    # Load settings with custom env_file by temporarily updating config
    # Pydantic settings will load from env_file in model_config
    original_env_file = UpsalesSettings.model_config.get("env_file")
    try:
        UpsalesSettings.model_config["env_file"] = env_file
        return UpsalesSettings()
    finally:
        # Restore original
        if original_env_file:
            UpsalesSettings.model_config["env_file"] = original_env_file
