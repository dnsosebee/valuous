import importlib


def import_valuous_module(name: str):
    return importlib.import_module("valuous." + name)


def exec_procedure(name: str):
    module = import_valuous_module(name)
    # do database stuff here
