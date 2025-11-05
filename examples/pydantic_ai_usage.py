"""Example integration with PydanticAI (https://ai.pydantic.dev/).

PydanticAI retries tool calls automatically when schema validation fails.  This
example shows how the ``RutNumber`` type can participate in those validation
cycles without introducing any runtime dependency on LLM tooling.
"""

from __future__ import annotations

from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent

from pydantic_type_chile_rut import RutNumber


class Person(BaseModel):
    name: str
    rut: RutNumber


agent = Agent(
    model="openai:gpt-4o-mini",
    result_type=Person,
)

prompt = "Inventa una persona con un RUT válido."

try:
    # PydanticAI retries generation until ``Person`` validates or the internal
    # ``max_attempts`` limit is hit.  An invalid RUT will raise ``ValidationError``
    # inside the agent, triggering a fresh LLM call.
    result = agent.run(prompt, max_attempts=3)
except ValidationError as exc:
    print("Could not obtain a valid RUT after several attempts:")
    print(exc)
else:
    print(result.model_dump())
