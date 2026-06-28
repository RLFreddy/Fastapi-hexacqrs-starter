from abc import ABC, abstractmethod


class Command:
    pass


class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command):
        raise NotImplementedError("Subclasses must implement handle method")
