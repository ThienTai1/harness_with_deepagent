def get_model_config(model_name: str, provider: str):
    """Use to get model config

    Args:
        model_name str: models' name
        provider str: provider is using to call LLM model

    Returns:
        a form of string provider:model_name
    """
    return f"{provider}:{model_name}"
