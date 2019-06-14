from .abstract_operation import AbstractOperation

class NoOp(AbstractOperation):
    def apply(self, filenames):
        print("NOOP")  # pragma:nocover
