"""Example integration with Instructor (https://python.useinstructor.com/).

This script shows how to combine Instructor's automatic retry behaviour with the
``RutNumber`` Pydantic type.  When the language model produces an invalid RUT,
Instructor will transparently ask it to try again until validation succeeds or
``max_retries`` is exhausted.

You need to set the ``OPENAI_API_KEY`` environment variable before running the
script.  The example keeps the repository LLM-agnostic: we only demonstrate how
one *could* wire things together in an application.
"""

from __future__ import annotations

import instructor
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from pydantic_type_chile_rut import RutNumber


# Wrap the OpenAI client so Instructor can handle validation failures.
client = instructor.from_openai(OpenAI(), mode=instructor.Mode.TOOLS)


class Person(BaseModel):
    name: str
    rut: RutNumber


messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that invents Chilean identities.",
    },
    {
        "role": "user",
        "content": "Inventa una persona con un RUT válido.",
    },
]

try:
    # Instructor will keep retrying (up to ``max_retries``) until the response is
    # parsed into ``Person``.  If the model returns an invalid RUT, the validator
    # raises ``ValidationError`` and Instructor asks the LLM to try again.
    person = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Person,
        messages=messages,
        max_retries=3,
    )
except ValidationError as exc:
    print("Could not obtain a valid RUT after several attempts:")
    print(exc)
else:
    print(person.model_dump())
