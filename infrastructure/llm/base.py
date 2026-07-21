from abc import ABC, abstractmethod
from typing import Optional


class LLMService(ABC):
    """大模型服务统一接口（Unified LLM Interface）"""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        response_format: Optional[dict] = None,
    ) -> str:...
