from typing import TypedDict

from src.util import DictMan


class Person(TypedDict):
    name: str
    age: int

person = Person({"name": "John", "age": 30})

md = DictMan(person)
md.include(["name"])
md.exclude(["age"])

cleaned = md.clean()
print(cleaned)
