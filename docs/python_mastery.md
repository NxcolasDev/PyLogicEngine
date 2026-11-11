# Python: do básico ao avançado

Os exemplos são independentes e usam apenas a biblioteca padrão.

## Básico: valores, condições e loops

```python
name = "PyLogic"
attempts = 0

while attempts < 3:
    if name:
        print(f"Bem-vinda(o), {name}")
    attempts += 1

for severity in ("INFO", "WARN", "ERROR"):
    print(severity)
```

`for` percorre iteráveis; `while` repete enquanto a condição é verdadeira.
Use `break`/`continue` com parcimônia e evite loops sem condição de saída.

## Coleções e comprehensions

```python
scores = [10, 20, 30, 40]
doubled = [score * 2 for score in scores]
errors = {code for code in ("E1", "W1", "E1") if code.startswith("E")}
counts = {severity: 0 for severity in ("INFO", "ERROR")}
```

List comprehensions expressam transformações curtas; para lógica extensa,
prefira um loop nomeado para legibilidade. `set` remove duplicatas e `dict`
associa chave a valor.

## Fatiamento (slicing)

```python
scores = [10, 20, 30, 40, 50]
first_three = scores[:3]      # [10, 20, 30]
last_two = scores[-2:]        # [40, 50]
every_other = scores[::2]     # [10, 30, 50]
reversed_scores = scores[::-1]
```

O formato é `sequencia[inicio:fim:passo]`; o limite `fim` não é incluído.
Fatiar uma lista cria outra lista (cópia rasa), não uma view.

## Funções e type hints

```python
def rolling_average(values: list[float], window: int) -> list[float]:
    if window <= 0 or window > len(values):
        return []
    return [
        sum(values[start : start + window]) / window
        for start in range(len(values) - window + 1)
    ]
```

Anotações documentam o contrato e ajudam ferramentas estáticas, mas não
validam entrada em runtime por si só. Valide valores na fronteira da aplicação.
Prefira tipos específicos a `Any` e defina comportamento para entradas inválidas.

## Decoradores

Um decorador recebe uma função e devolve uma função envoltória, preservando
metadados com `functools.wraps`:

```python
from functools import wraps
from time import perf_counter
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def timed(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {perf_counter() - started:.4f}s")
    return wrapper
```

Decoradores são usados por frameworks para registrar rotas e por ferramentas
para instrumentação. Evite efeitos colaterais inesperados e não registre
segredos/argumentos sensíveis.

## POO e dataclasses

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Lesson:
    title: str
    level: int

class Course:
    def __init__(self, lessons: tuple[Lesson, ...]) -> None:
        self._lessons = lessons

    def titles(self) -> list[str]:
        return [lesson.title for lesson in self._lessons]
```

Classes encapsulam estado e comportamento relacionados. `dataclass` reduz
código repetitivo para objetos de dados. `frozen=True` evita reatribuição dos
campos; não significa imutabilidade profunda dos objetos internos. Use
composição antes de herança quando relações de subtipo não forem necessárias.

## Generators e context managers

```python
def chunks(items: list[str], size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]

with open("events.txt", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

Generators produzem valores sob demanda e reduzem memória em grandes fluxos.
`with` garante liberação de recursos (arquivo, conexão, lock) mesmo com erro.

## Async/await

```python
import asyncio

async def fetch_lesson() -> str:
    await asyncio.sleep(0.01)  # Simula I/O assíncrono
    return "Event loop liberado durante a espera"

async def main() -> None:
    lesson = await fetch_lesson()
    print(lesson)

asyncio.run(main())
```

`await` é apropriado para operações I/O realmente assíncronas. Não execute
chamadas de rede síncronas ou cálculos CPU-intensivos no event loop; use
bibliotecas async, threadpool para I/O bloqueante, ou workers separados para
CPU.

## Práticas de engenharia

- Use ambientes virtuais, dependências declaradas e versões compatíveis.
- Separe domínio puro, adaptadores, handlers e infraestrutura.
- Teste casos de sucesso, limites, erros e autorização.
- Prefira exceções específicas; não esconda erros com `except Exception`.
- Faça logging estruturado sem credenciais, tokens ou dados pessoais.
- Use formatter, linter, testes e type checker no pipeline de CI.
