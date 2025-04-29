import os
import secrets
import uuid


def generate_safe_uuid():
    """Generate a universally unique identifier (UUID) suitable for use in a multiprocess-safe manner.

    This function generates a UUID that is safe for use in a multiprocess environment across different operating systems.
    It handles platform differences in random byte generation to ensure cryptographic security and uniqueness.

    Returns:
        str: A universally unique identifier (UUID) as a string.
    Raises:
        NotImplementedError: If the platform is not supported.
    """
    if os.name == "posix":
        unique_id = uuid.UUID(bytes=os.urandom(16), version=4)
    elif os.name == "nt":
        # Generate random bytes using secrets on windows as urandom doesn't exist
        random_bytes = secrets.token_bytes(16)
        unique_id = uuid.UUID(bytes=random_bytes, version=4)
    else:
        raise NotImplementedError("Unsupported platform")

    return str(unique_id)
