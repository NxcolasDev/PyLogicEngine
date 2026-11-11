"""Analytics funcional: função pura e Iterable/dict type hints para contagem."""

from collections import Counter
from collections.abc import Iterable


def count_by_severity(severities: Iterable[str]) -> dict[str, int]:
    """Agrega por severidade sem mutação; type hints documentam o contrato da função."""

    return dict(Counter(severities))
