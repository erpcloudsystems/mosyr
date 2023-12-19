from abc import ABC, abstractmethod


class Factory(ABC):

    @staticmethod
    @abstractmethod
    def create(*args, **kwargs):
        pass


class DAO(ABC):
    @staticmethod
    @abstractmethod
    def create(*args, **kwargs):
        pass
