"""Segurança com funções tipadas e injeção de dependências FastAPI para JWT/Argon2."""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.domain import User

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _jwt_secret() -> str:
    """Valida o segredo externo antes de assinar ou verificar tokens."""

    configured_secret = get_settings().jwt_secret_key
    if configured_secret is None or len(configured_secret.get_secret_value()) < 32:
        raise RuntimeError("JWT_SECRET_KEY deve conter pelo menos 32 caracteres.")
    return configured_secret.get_secret_value()


def hash_password(password: str) -> str:
    """Aplica Argon2; type hints deixam explícitos entrada e saída sem expor a senha."""

    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Compara senha e hash tipados sem persistir nem registrar a senha em texto."""

    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    """Monta JWT tipado com expiração UTC; a função encapsula assinatura segura."""

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=get_settings().jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires_at}, _jwt_secret(), algorithm=ALGORITHM
    )


def _unauthorized() -> HTTPException:
    """Padroniza resposta de autenticação inválida sem revelar detalhes do token."""

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Valida JWT e resolve o usuário; Annotated/Depends aplicam injeção tipada."""

    try:
        payload: dict[str, Any] = jwt.decode(
            token, _jwt_secret(), algorithms=[ALGORITHM]
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise _unauthorized()
        user_id = int(subject)
    except (JWTError, ValueError) as error:
        raise _unauthorized() from error

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _unauthorized()
    return user
