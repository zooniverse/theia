from .abstract_operation import AbstractOperation


class NoOp(AbstractOperation):
    def apply(self, filenames):
        self.establish_output_directory()
        print("NOOP")  # pragma:nocover
