from abc import ABC, abstractmethod
from anthropic import Anthropic
from evallm.config import SystemUnderTest


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


def create_provider(sut: SystemUnderTest) -> Provider:
    """Build a provider instance from system-under-test config.

    Args:
        sut: System-under-test config with provider type and settings.

    Returns:
        A Provider implementation matching sut.provider.

    Raises:
        ValueError: If sut.provider is not a supported provider.
    """
    provider = sut.provider
    if provider == "anthropic":
        return AnthropicProvider(
            model=sut.model,
            system_prompt=sut.system_prompt,
            temperature=sut.temperature,
            max_tokens=sut.max_tokens,
        )
    else:
        raise ValueError(f"{provider} is an unsupported provider")
