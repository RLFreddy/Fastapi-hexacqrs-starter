from abc import ABC, abstractmethod


class Query:
    pass


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query):
        raise NotImplementedError("Subclasses must implement handle method")
