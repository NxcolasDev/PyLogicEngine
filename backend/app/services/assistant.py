"""Porta e adapter HTTP para IA: o domínio não depende de um provedor específico."""

from typing import Protocol
from urllib.parse import urlsplit

import httpx

from app.config import get_settings


class AssistantProvider(Protocol):
    """Contrato assíncrono que permite trocar ou substituir o provedor em testes."""

    async def answer(self, prompt: str) -> str:
        """Retorna resposta do assistente para um prompt já validado."""


class AssistantNotConfiguredError(RuntimeError):
    """Indica que endpoint e credencial do provedor não foram configurados."""


class AssistantProviderError(RuntimeError):
    """Indica falha de protocolo/serviço upstream sem expor conteúdo sensível."""


class OpenAICompatibleAssistant:
    """Adapter para endpoint chat-completions configurado no ambiente."""

    async def answer(self, prompt: str) -> str:
        """Faz chamada HTTP limitada por timeout e valida o formato da resposta."""

        settings = get_settings()
        if settings.ai_api_url is None or settings.ai_api_key is None:
            raise AssistantNotConfiguredError(
                "O assistente de IA não está configurado."
            )

        api_key = settings.ai_api_key.get_secret_value()
        if not api_key:
            raise AssistantNotConfiguredError(
                "O assistente de IA não está configurado."
            )
        parsed_url = urlsplit(settings.ai_api_url)
        if parsed_url.scheme != "https" and parsed_url.hostname not in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise AssistantNotConfiguredError(
                "AI_API_URL deve usar HTTPS fora do loopback local."
            )

        body = {
            "model": settings.ai_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é o assistente educacional do PyLogic Engine. "
                        "Explique conceitos, ofereça exemplos seguros e incentive "
                        "o aprendizado sem alegar executar código."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
                response = await client.post(
                    settings.ai_api_url,
                    json=body,
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as error:
            raise AssistantProviderError(
                "O provedor de IA excedeu o tempo limite."
            ) from error
        except httpx.HTTPStatusError as error:
            raise AssistantProviderError(
                f"O provedor de IA respondeu com HTTP {error.response.status_code}."
            ) from error
        except httpx.RequestError as error:
            raise AssistantProviderError(
                "Não foi possível conectar ao provedor de IA."
            ) from error
        except ValueError as error:
            raise AssistantProviderError(
                "O provedor de IA retornou JSON inválido."
            ) from error

        try:
            answer = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise AssistantProviderError(
                "O provedor de IA retornou formato inesperado."
            ) from error

        if not isinstance(answer, str) or not answer.strip():
            raise AssistantProviderError("O provedor de IA retornou resposta vazia.")
        return answer.strip()


def get_assistant_provider() -> AssistantProvider:
    """Dependency factory facilita injeção de adapters e mocks em testes."""

    return OpenAICompatibleAssistant()
