import os
import base64
from collections import defaultdict

from dotenv import load_dotenv
from datasets import Dataset
import openai
import pandas as pd


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def make_prompt(
    instruction: str,
    paragraph: str,
    question_plus: str,
    question: str,
    choices: list,
    model_type: str,
    test_file_path: str,
):
    prompt_messages = []
    content_text_key = (
        "text"
        # if question_plus != "" and is_picture_extention(question_plus)
        if "gpt-4-vision" in model_type
        else "content"
    )

    prompt = ""
    if instruction != "":
        prompt_messages.append(
            {"role": "system", content_text_key: f"{instruction}\n\n"}
        )
        prompt += f"{instruction}\n\n"

    if paragraph:
        prompt_messages.append(
            {
                "role": "user",
                content_text_key: f"지문: {paragraph}\n\n"
                if "국어" in test_file_path
                else f"Paragraph: {paragraph}\n\n",
            }
        )

        prompt += (
            f"지문: {paragraph}\n\n"
            if "국어" in test_file_path
            else f"Paragraph: {paragraph}\n\n"
        )

    if question_plus != "":
        if is_picture_extention(question_plus):
            base64_image = encode_image(question_plus)
            if "gpt-4-vision" in model_type:
                prompt_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"<보기>: "
                                if "국어" in test_file_path
                                else f"<Example>: ",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                )
            else:
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Please explain this image.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=1024,
                )
                caption_text = response.choices[0].message.content
                prompt_messages.append(
                    {
                        "role": "user",
                        "content": f"<보기>: {caption_text}"
                        if "국어" in test_file_path
                        else f"<Example>: {caption_text}",
                    }
                )

                prompt += (
                    f"<보기>: {caption_text}\n\n"
                    if "국어" in test_file_path
                    else f"<Example>: {caption_text}\n\n"
                )
        else:
            prompt_messages.append(
                {
                    "role": "user",
                    content_text_key: f"<보기>: {question_plus}\n\n"
                    if "국어" in test_file_path
                    else f"<Example>: {question_plus}\n\n",
                }
            )

            prompt += (
                f"<보기>: {question_plus}\n\n"
                if "국어" in test_file_path
                else f"<Example>: {question_plus}\n\n"
            )

    prompt += (
        f"질문: {question}\n\n" if "국어" in test_file_path else f"Question: {question}\n\n"
    )

    if choices:
        prompt += "선택지:\n" if "국어" in test_file_path else "Choices:\n"
        for i, choice in enumerate(choices):
            prompt += (
                f"{i+1}번: {choice}\n"
                if "국어" in test_file_path
                else f"{i+1}: {choice}\n"
            )

        prompt += (
            "1번, 2번, 3번, 4번, 5번 중에 하나를 정답으로 고르세요."
            if "국어" in test_file_path
            else "Choose one of 1, 2, 3, 4, 5 as the answer."
        )

    prompt += "\n정답: " if "국어" in test_file_path else "\nAnswer: "

    prompt_messages.append({"role": "user", content_text_key: prompt})

    # return prompt_messages
    return [{"role": "user", content_text_key: prompt}]


def is_picture_extention(text: str):
    return text.split(".")[-1] in ["png", "jpg", "jpeg"]


# def preprocess_df(df: pd.DataFrame, prompt_type: str):
def preprocess(df: pd.DataFrame, model_type: str, test_file_path: str):
    preprocessed = defaultdict(list)

    # prompt_dict = PROMPT_DICT[prompt_type]

    for _, row in df.iterrows():
        """
        row_keys: ["id", "instruction", "paragraph", "problems"]
        """
        instruction = row.get("instruction", "")
        paragraph = row.get("paragraph", "")

        for problem in row["problems"]:
            _id = problem["id"]
            question = problem["question"]
            question_plus = problem.get("question_plus", "")
            choices = problem.get("choices", "")
            answer = problem["answer"]
            score = problem["score"]

            prompt = make_prompt(
                instruction=instruction,
                paragraph=paragraph,
                question_plus=question_plus,
                question=question,
                choices=choices,
                model_type=model_type,
                test_file_path=test_file_path,
            )
            preprocessed["id"].append(_id)
            preprocessed["messages"].append(prompt)
            preprocessed["answer"].append(answer)
            preprocessed["score"].append(score)

    return preprocessed


def load_dataset(model_type: str, test_file_path: str):
    # 데이터셋 로드
    preprocessed_data_path = test_file_path.replace(".json", "_preprocessed.json")
    if preprocessed_data_path.split("/")[-1] in os.listdir("data"):
        dataset_df = pd.read_json(preprocessed_data_path)
        dataset = Dataset.from_pandas(dataset_df)
        return dataset

    df = pd.read_json(test_file_path)

    preprocessed_data = preprocess(
        df=df, model_type=model_type, test_file_path=test_file_path
    )

    preprocessed_df = pd.DataFrame(data=preprocessed_data)
    preprocessed_df.to_json(
        test_file_path.replace(".json", "_preprocessed.json"),
        orient="records",
        indent=4,
        force_ascii=False,
    )
    dataset = Dataset.from_pandas(preprocessed_df)

    return dataset


def set_openai_key():
    # OpenAI API 키 설정
    load_dotenv()
    openai.api_key = os.environ["OPENAI_API_KEY"]
