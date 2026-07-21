from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    name: str = "BaseAgent"
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        ...