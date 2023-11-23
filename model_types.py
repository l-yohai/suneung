class ModelType:
    API_MODELS = ["gpt-4-1106-preview", "gpt-3.5-turbo-1106"]
    OPEN_SOURCE_MODELS = [
        "01-ai/Yi-34B",
        "upstage/SOLAR-0-70b-16bit",
        "Riiid/sheep-duck-llama-2-70b-v1.1",
        "EleutherAI/polyglot-ko-12.8b",
    ]

    @staticmethod
    def list():
        return ModelType.API_MODELS + ModelType.OPEN_SOURCE_MODELS

    @staticmethod
    def api_models():
        return ModelType.API_MODELS

    @staticmethod
    def open_source_models():
        return ModelType.OPEN_SOURCE_MODELS
