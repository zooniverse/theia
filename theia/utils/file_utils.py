from os.path import isfile, splitext
from re import sub

class FileUtils:
    @classmethod
    def version_filename(cls, filename, version_number):
        return cls._update_version(filename, version_number)

    @classmethod
    def locate_latest_version(cls, filename, current_stage):
        while current_stage > 0:
            current_stage = current_stage - 1
            candidate = cls.version_filename(filename, current_stage)
            if isfile(candidate):
                return candidate

        return cls._unversion(filename)

    @classmethod
    def _version(cls, filename, version_number):
        return "{0}_stage_{2:0>2}{1}".format(*splitext(filename), version_number)

    @classmethod
    def _unversion(cls, filename):
        (basename, ext) = splitext(filename)
        strip = sub(r'_stage_\d{2}$', '', basename)
        return "{0}{1}".format(strip, ext)

    @classmethod
    def _update_version(cls, filename, version_number):
        return cls._version(cls._unversion(filename), version_number)
