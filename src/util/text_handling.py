def short_text(text: str, threshold: int = 10) -> str:
    if len(text) > threshold:
        return text[:threshold] + "..."
    else:
        return text
