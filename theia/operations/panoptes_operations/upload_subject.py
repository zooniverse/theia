from .utils import PanoptesUtils

class UploadSubject:
    @classmethod
    def apply(self, filename, bundle):
        stage = bundle.current_stage
