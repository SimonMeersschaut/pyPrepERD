from abc import ABC, abstractmethod


class Process(ABC):
    """Each instance of this superclass represents an object that
    handles operations on data. More specifically, each subclass will define
    an operation (such as reading an input file, converting it to another format etc.).
    Each instance of such a subclass will hold information about its task and will have a function
    which, when called, executes its operation."""

    
    @abstractmethod
    def run(*args):
        """
        @pre
        @post
        @result
        """

        ...