from abc import ABC, abstractmethod


class BaseModuleApp(ABC):
    def __init__(self, reqData):
        self.reqData = reqData

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def schedule(self):
        pass

    @abstractmethod
    def get_name(self):
        pass
