"""Rotas de aprendizagem; a IA é opcional, autenticada e desacoplada por Protocol."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.models.domain import User
from app.security import get_current_user
from app.services.assistant import (
    AssistantNotConfiguredError,
    AssistantProvider,
    AssistantProviderError,
    get_assistant_provider,
)

router = APIRouter(prefix="/learning", tags=["learning"])


class AssistantRequest(BaseModel):
    """Prompt limitado em tamanho para reduzir abuso e custo do provedor."""

    prompt: str = Field(min_length=1, max_length=4000)

    @field_validator("prompt")
    @classmethod
    def prompt_must_contain_text(cls, value: str) -> str:
        """Remove espaços periféricos e recusa prompts vazios após normalização."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("O prompt não pode conter apenas espaços.")
        return normalized


class AssistantResponse(BaseModel):
    """Resposta normalizada independente do formato interno do fornecedor."""

    answer: str


@router.post("/assistant", response_model=AssistantResponse)
async def ask_assistant(
    payload: AssistantRequest,
    _current_user: Annotated[User, Depends(get_current_user)],
    provider: Annotated[AssistantProvider, Depends(get_assistant_provider)],
) -> AssistantResponse:
    """Usa async/await na porta do provider e converte falhas em erros explícitos."""

    try:
        answer = await provider.answer(payload.prompt.strip())
    except AssistantNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Assistente de IA não configurado.",
        ) from error
    except AssistantProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
    return AssistantResponse(answer=answer)
