# CURRENTLY NOT IN USE

# This will eventually become an actual db
from pydantic import BaseModel


class Person(BaseModel):
    name: str


class Procedure(BaseModel):
    module_name: str
    name: str
    code: str


class State(BaseModel):
    procedures: list = []
    traces: list = []
    memories: list = []
    messages: list = []
