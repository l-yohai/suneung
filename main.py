import fire

from model_types import ModelType
import api_models
import gpu_inference
from utils import set_openai_key


# def main(test_file_path: str, model_type: str, prompt_type: str = "NO_INSTRUCTION"):
def main(test_file_path: str, model_type: str):
    # OpenAI API 키 설정
    set_openai_key()

    if model_type not in ModelType.list():
        # 지원하지 않는 모델 타입이 입력되었을 경우
        raise ValueError(
            f"Model type {model_type} is not supported. "
            f"Supported model types: {ModelType.list()}"
        )

    # if prompt_type not in PROMPT_DICT.keys():
    #     # 지원하지 않는 프롬프트 타입이 입력되었을 경우
    #     raise ValueError(
    #         f"Prompt type {prompt_type} is not supported. "
    #         f"Supported prompt types: {PROMPT_DICT.keys()}"
    #     )

    # 모델 타입에 따라 추론 수행
    if model_type in ModelType.api_models():
        api_models.process_model(
            model_type=model_type,
            test_file_path=test_file_path,
        )
    elif model_type in ModelType.open_source_models():
        gpu_inference.run_inference(
            model_type=model_type, test_file_path=test_file_path
        )


if __name__ == "__main__":
    fire.Fire(main)
