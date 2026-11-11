"""Catálogo puro de trilhas: dataclasses imutáveis e enums sem dependências externas."""

from dataclasses import dataclass
from enum import StrEnum


class LearningTrack(StrEnum):
    """Áreas de estudo disponíveis no catálogo educacional."""

    PYTHON = "python"
    CLOUD = "cloud"
    DATABASES = "databases"
    TERRAFORM = "terraform"
    DEVOPS = "devops"


@dataclass(frozen=True, slots=True)
class Lesson:
    """Lição imutável, identificada por trilha e nível progressivo."""

    track: LearningTrack
    level: int
    title: str
    objectives: tuple[str, ...]


CURRICULUM: tuple[Lesson, ...] = (
    Lesson(
        LearningTrack.PYTHON,
        1,
        "Fundamentos e tipos",
        ("variáveis", "condições", "loops"),
    ),
    Lesson(
        LearningTrack.PYTHON,
        2,
        "Coleções e funções",
        ("listas", "dicionários", "funções"),
    ),
    Lesson(
        LearningTrack.PYTHON, 3, "Engenharia Python", ("type hints", "POO", "testes")
    ),
    Lesson(
        LearningTrack.CLOUD,
        1,
        "Fundamentos de cloud",
        ("IAM", "regiões", "responsabilidade"),
    ),
    Lesson(
        LearningTrack.CLOUD, 2, "Serviços serverless", ("filas", "funções", "eventos")
    ),
    Lesson(
        LearningTrack.DATABASES,
        1,
        "Modelagem relacional",
        ("SQL", "joins", "constraints"),
    ),
    Lesson(
        LearningTrack.DATABASES,
        2,
        "Bancos de documentos",
        ("NoSQL", "agregação", "índices"),
    ),
    Lesson(
        LearningTrack.TERRAFORM,
        1,
        "Infraestrutura como código",
        ("providers", "state", "plan"),
    ),
    Lesson(
        LearningTrack.TERRAFORM,
        2,
        "Módulos reutilizáveis",
        ("inputs", "outputs", "composição"),
    ),
    Lesson(LearningTrack.DEVOPS, 1, "Entrega contínua", ("Git", "CI", "automação")),
    Lesson(
        LearningTrack.DEVOPS, 2, "Operação confiável", ("logs", "métricas", "alertas")
    ),
)


def lessons_for_track(track: LearningTrack) -> tuple[Lesson, ...]:
    """Retorna lições ordenadas por nível, sem modificar o catálogo global."""

    return tuple(
        sorted(
            (lesson for lesson in CURRICULUM if lesson.track is track),
            key=lambda lesson: lesson.level,
        )
    )
