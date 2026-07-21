import os
from typing import Optional
from openai import OpenAI
from .base import LLMService
class DeepseekLLMService(LLMService):
    def __init__(self):
        api_key=os.getenv("DEEPSEEK_API_KEY")
        base_url=os.getenv("DEEPSEEK_BASE_URL","https://api.deepseek.com")
        self.model=os.getenv("DEEPSEEK_MODEL","deepseek-chat")

        if not api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY，请检查.env文件")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self,messages:list[dict],temperature:float=0.2,response_format:Optional[dict]=None,)->str:
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            params["response_format"] = response_format

        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
