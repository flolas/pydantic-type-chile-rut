# pydantic-type-chile-rut

[![CI](https://github.com/flolas/pydantic-type-chile-rut/actions/workflows/ci.yml/badge.svg)](https://github.com/flolas/pydantic-type-chile-rut/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pydantic-type-chile-rut.svg)](https://badge.fury.io/py/pydantic-type-chile-rut)
[![PyPI Downloads](https://static.pepy.tech/badge/pydantic-type-chile-rut)](https://pepy.tech/projects/pydantic-type-chile-rut)
[![Python versions](https://img.shields.io/pypi/pyversions/pydantic-type-chile-rut.svg)](https://pypi.org/project/pydantic-type-chile-rut/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Pydantic custom type for Chilean RUT (Rol Único Tributario) validation and formatting.

## Features

- ✅ **Comprehensive validation**: Validates RUT format, length, and check digit
- 🔧 **Flexible input**: Accepts RUTs with or without dots and hyphens
- 📝 **Multiple formats**: Provides both compact and formatted output
- 🏷️ **Type-safe**: Full Pydantic v2 integration with proper type hints
- 🧪 **Well-tested**: Comprehensive test suite with 100% coverage
- 🚀 **High performance**: Efficient validation using Pydantic's core schema

## Installation

```bash
pip install pydantic-type-chile-rut
```

Or using uv:

```bash
uv add pydantic-type-chile-rut
```

## Quick Start

```python
from pydantic import BaseModel
from pydantic_type_chile_rut import RutNumber

class Person(BaseModel):
    name: str
    rut: RutNumber

# Create a person with a valid RUT
person = Person(name="Juan Pérez", rut="12.345.678-5")

print(person.rut)           # "12345678-5" (compact format)
print(person.rut.formatted) # "12.345.678-5" (with dots)
print(person.rut.number)    # 12345678 (numeric part)
print(person.rut.dv)        # "5" (check digit)
```

## RUT Format Support

The library accepts RUTs in various formats:

```python
from pydantic_type_chile_rut import RutNumber

# All these inputs are equivalent and valid:
valid_formats = [
    "12.345.678-5",    # Standard format with dots and hyphen
    "12345678-5",      # Without dots
    "123456785",       # Without dots or hyphen
    "12.345.678-5",    # With spaces (trimmed automatically)
]

# Case insensitive check digits:
rut_with_k = RutNumber.model_validate("15.345.678-k")  # -> "15345678-K"
```

## RutNumber Properties

The `RutNumber` class provides several useful properties and methods:

```python
from pydantic_type_chile_rut import RutNumber

rut = RutNumber(12345678, "5")

# Properties
print(rut.number)     # 12345678 (int)
print(rut.dv)         # "5" (str)
print(str(rut))       # "12345678-5" (compact format)

# Formatting methods
print(rut.formatted)   # "12.345.678-5" (property)
print(rut.with_dots()) # "12.345.678-5" (method)

# Representation
print(repr(rut))      # "RutNumber(number=12345678, dv='5')"
```

## Validation Examples

### Valid RUTs

```python
from pydantic import BaseModel
from pydantic_type_chile_rut import RutNumber

class TestModel(BaseModel):
    rut: RutNumber

# These will all validate successfully:
valid_ruts = [
    "12.345.678-5",      # Standard format
    "15.345.678-K",      # With K check digit
    "1-9",               # Short RUT
    "0-0",               # Zero RUT (special case)
    "123456785",         # Without punctuation
    "00001234-3",        # With leading zeros (normalized)
]

for rut_str in valid_ruts:
    model = TestModel(rut=rut_str)
    print(f"{rut_str} -> {model.rut}")
```

### Invalid RUTs

```python
from pydantic import ValidationError

invalid_ruts = [
    "12345678-4",        # Wrong check digit
    "ABC",               # Not numeric
    "12.345.678-",       # Missing check digit
    "",                  # Empty string
    "123.456.789-0",     # Too long (> 9 digits)
    "12345678-X",        # Invalid check digit character
]

for rut_str in invalid_ruts:
    try:
        TestModel(rut=rut_str)
    except ValidationError as e:
        print(f"{rut_str} -> {e.errors()[0]['msg']}")
```

## Integration with Pydantic Models

### Basic Usage

```python
from pydantic import BaseModel
from typing import Optional
from pydantic_type_chile_rut import RutNumber

class Employee(BaseModel):
    id: int
    name: str
    rut: RutNumber
    supervisor_rut: Optional[RutNumber] = None

employee = Employee(
    id=1,
    name="María González",
    rut="18.765.432-1",
    supervisor_rut="12.345.678-5"
)

# Serialization
employee_dict = employee.model_dump()
print(employee_dict)
# {
#     'id': 1,
#     'name': 'María González',
#     'rut': '18765432-1',
#     'supervisor_rut': '12345678-5'
# }
```

### JSON Schema Generation

```python
from pydantic import BaseModel
from pydantic_type_chile_rut import RutNumber

class Person(BaseModel):
    rut: RutNumber

# Generate JSON schema
schema = Person.model_json_schema()
print(schema)
```

### Using with TypeAdapter

```python
from pydantic import TypeAdapter
from pydantic_type_chile_rut import RutNumber

adapter = TypeAdapter(RutNumber)

# Validate single RUT
rut = adapter.validate_python("12.345.678-5")
print(f"Valid RUT: {rut.formatted}")

# Validate list of RUTs
ruts_adapter = TypeAdapter(list[RutNumber])
ruts = ruts_adapter.validate_python([
    "12.345.678-5",
    "15.345.678-K",
    "1-9"
])
```

## Advanced Usage

### Custom Validation

```python
from pydantic import BaseModel, field_validator
from pydantic_type_chile_rut import RutNumber

class BusinessEntity(BaseModel):
    business_rut: RutNumber
    legal_rep_rut: RutNumber

    @field_validator('business_rut')
    @classmethod
    def validate_business_rut(cls, v):
        # Business RUTs in Chile typically have 8-9 digits
        if v.number < 50000000:
            raise ValueError('Business RUT seems too low')
        return v

entity = BusinessEntity(
    business_rut="96.511.760-1",
    legal_rep_rut="12.345.678-5"
)
```

### Working with Databases

```python
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from pydantic_type_chile_rut import RutNumber

# SQLAlchemy model
class PersonDB:
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    rut = Column(String(12))  # Store as "12345678-5"
    name = Column(String(100))

# Pydantic model for API
class PersonAPI(BaseModel):
    id: int
    rut: RutNumber
    name: str

    @classmethod
    def from_db(cls, db_person):
        return cls(
            id=db_person.id,
            rut=db_person.rut,  # Automatically validates
            name=db_person.name
        )
```

## Check Digit Algorithm

The library implements the standard Chilean RUT check digit algorithm (modulo 11):

1. Multiply each digit by weights [2, 3, 4, 5, 6, 7] from right to left, cycling
2. Sum all products
3. Calculate `11 - (sum % 11)`
4. If result is 11, use "0"; if 10, use "K"; otherwise use the number

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and packaging.

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/flolas/pydantic-type-chile-rut.git
cd pydantic-type-chile-rut

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/pydantic_type_chile_rut --cov-report=html

# Run linting and formatting
uv run pre-commit run --all-files
```

### Project Structure

```
pydantic-type-chile-rut/
├── src/
│   └── pydantic_type_chile_rut/
│       ├── __init__.py
│       └── rut.py
├── tests/
│   ├── __init__.py
│   └── test_rut.py
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── pyproject.toml
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Guidelines

- Add tests for any new features
- Ensure all tests pass
- Follow the existing code style
- Update documentation as needed

## Testing

Run the full test suite:

```bash
uv run pytest tests/ -v
```

Run with coverage:

```bash
uv run pytest tests/ --cov=src/pydantic_type_chile_rut --cov-report=term-missing
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/flolas/pydantic-type-chile-rut/issues) on GitHub.

## Related Projects

- [pydantic](https://github.com/pydantic/pydantic) - Data validation using Python type hints
- [python-rut](https://github.com/YerkoPalma/python-rut) - Another RUT validation library
- [django-rut](https://github.com/YerkoPalma/django-rut) - RUT field for Django

## Acknowledgments

- Thanks to the Pydantic team for creating an excellent validation library
- Inspired by various Chilean RUT validation implementations
