"""
math_tools.py - Individual Math Operation Tools
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class TwoNumberInput(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")

class OneNumberInput(BaseModel):
    number: float = Field(description="The number")

class AddTool(BaseTool):
    name: str = "add"
    description: str = "Add two numbers: a + b"
    args_schema: Type[BaseModel] = TwoNumberInput
    def _run(self, a: float, b: float) -> str:
        result = a + b
        print(f"🔧 ADD: {a} + {b} = {result}")
        return str(result)

class SubtractTool(BaseTool):
    name: str = "subtract"
    description: str = "Subtract: a - b"
    args_schema: Type[BaseModel] = TwoNumberInput
    def _run(self, a: float, b: float) -> str:
        result = a - b
        print(f"🔧 SUBTRACT: {a} - {b} = {result}")
        return str(result)

class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "Multiply two numbers: a × b"
    args_schema: Type[BaseModel] = TwoNumberInput
    def _run(self, a: float, b: float) -> str:
        result = a * b
        print(f"🔧 MULTIPLY: {a} × {b} = {result}")
        return str(result)

class DivideTool(BaseTool):
    name: str = "divide"
    description: str = "Divide: a ÷ b"
    args_schema: Type[BaseModel] = TwoNumberInput
    def _run(self, a: float, b: float) -> str:
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        print(f"🔧 DIVIDE: {a} ÷ {b} = {result}")
        return str(result)

class PowerTool(BaseTool):
    name: str = "power"
    description: str = "Power: a ^ b"
    args_schema: Type[BaseModel] = TwoNumberInput
    def _run(self, a: float, b: float) -> str:
        result = a ** b
        print(f"🔧 POWER: {a} ^ {b} = {result}")
        return str(result)

class SqrtTool(BaseTool):
    name: str = "sqrt"
    description: str = "Square root of number"
    args_schema: Type[BaseModel] = OneNumberInput
    def _run(self, number: float) -> str:
        if number < 0:
            return "Error: Negative number"
        result = number ** 0.5
        print(f"🔧 SQRT: √{number} = {result}")
        return str(result)

# Test the tools manually
if __name__ == "__main__":
    print("🧪 Testing Individual Tools:")
    add = AddTool()
    print(f"5 + 3 = {add._run(5, 3)}")
    multiply = MultiplyTool()
    print(f"4 × 7 = {multiply._run(4, 7)}")
    sqrt = SqrtTool()
    print(f"√16 = {sqrt._run(16)}")