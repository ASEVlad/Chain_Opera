import os
import random
from loguru import logger
from openai import OpenAI
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_llm_clients(api_file_path: str, base_url: str | None, llm_name: str, llm_model: str) -> None:
    with open(api_file_path, "r", encoding="utf-8") as f:
        api_list = f.read().splitlines()

    for api in api_list:
        new_llm_client = OpenAI(
            api_key=api,
            base_url=base_url,
        )

        llm_clients.append(
            {
                "name": llm_name,
                "client": new_llm_client,
                "model": llm_model
            }
        )

        logger.info(f"Created new {llm_name} LLM client.")

llm_clients = list()
# setup_llm_clients(
#     os.path.abspath(os.path.join(BASE_DIR, "..", "data", "llm_api", "openai_api.txt")),
#     None,
#     "OPENAI",
#     "o4-mini-2025-04-16"
# )
setup_llm_clients(
    os.path.abspath(os.path.join(BASE_DIR, "..", "data", "llm_api", "hyperbolic_api.txt")),
    "https://api.hyperbolic.xyz/v1",
    "HYPERBOLIC",
    "meta-llama/Llama-3.3-70B-Instruct"
)
setup_llm_clients(
    os.path.abspath(os.path.join(BASE_DIR, "..", "data", "llm_api", "nous_api.txt")),
    "https://inference-api.nousresearch.com/v1",
    "NOUS",
    "Hermes-3-Llama-3.1-405B"
)

topics_file_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "topics.txt"))
with open(topics_file_path, "r", encoding="utf-8") as f:
    topics = f.read().splitlines()


def fetch_random_llm_response(messages):
    random_llm_client = random.choice(llm_clients)
    # logger.info(f"{random_llm_client['name']} was chosen as random LLM for response.")
    return fetch_llm_response(random_llm_client['client'], messages, random_llm_client['model'])

def fetch_llm_response(client: OpenAI, messages, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating response from OpenAI: {e}")
        raise

def generate_test_prompt():
    random_topic = random.choice(topics)
    # logger.info(f"{random_topic} was chosen as random topic for response.")
    messages = [
    {
        "role": "system",
        "content": (
            "You are an expert in testing different language models with broad knowledge in every possible field"
            "Your task is to test two different LLMs and determine which one is better by asking them different questions. "
            "You are using only high quality prompts that are clear, specific, well-structured"
            "You always provide relevant background or examples"
            "You always provide your goal"
            "You always set boundaries (e.g., word count, tone, style or other)"
            "You must ONLY respond with plain prompt with no additional information with no brackets or additional symbol"
        )
    },
    {
        "role": "user",
        "content": (
            f"Generate a high quality prompt that will test LLM. As a topic take anything related to {random_topic}"
            "Provide only the text of the prompt without any additional words, brackets or anything else."
            "Goal: The text you will generate will be directly copy pasted to llm model to test it."
        )
    }
    ]
    return fetch_random_llm_response(messages)
