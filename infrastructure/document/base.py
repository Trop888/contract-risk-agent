from abc import ABC,abstractmethod

class DocumentParser(ABC):
    @abstractmethod
    def parse(self,file_path:str)->str:
        ...