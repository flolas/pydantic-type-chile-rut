"""Example integration with LangChain structured output.

LangChain's structured output helpers retry model calls when parsing into a
Pydantic schema fails.  This script demonstrates how the ``RutNumber`` type can
participate in those retries without adding LangChain as a dependency of the
package.  Set the ``OPENAI_API_KEY`` environment variable before running it.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from pydantic_type_chile_rut import RutNumber


class Person(BaseModel):
    name: str
    rut: RutNumber


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that invents Chilean identities."),
        ("human", "Inventa una persona con un RUT válido."),
    ]
)

# ``with_structured_output`` creates a Runnable that keeps retrying until the
# response can be parsed into ``Person`` or ``max_retries`` is exhausted.
structured_llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(
    Person,
    max_retries=3,
)

chain = prompt | structured_llm

try:
    result = chain.invoke({})
except Exception as exc:  # pragma: no cover - demo script
    print("Could not obtain a valid RUT after several attempts:")
    print(exc)
else:
    print(result.model_dump())
