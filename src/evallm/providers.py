from abc import ABC, abstractmethod
from anthropic import Anthropic


class Provider(ABC):
    @abstractmethod
    def generate(self, input: str) -> str: ...


class AnthropicProvider(Provider):
    def __init__(
        self,
        model: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ):
        self.client = Anthropic()
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, input: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": input}],
        )
        return response.content[0].text
