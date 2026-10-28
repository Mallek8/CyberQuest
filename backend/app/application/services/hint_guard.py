def contains_secret(text: str, secret_ids: list[str]) -> bool:
    lowered = text.lower()
    return any(secret.lower() in lowered for secret in secret_ids if secret)
