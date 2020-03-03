import glob
import os.path
from re import sub
import tarfile


class FileUtils:
    @classmethod
    def version_filename(cls, filename, version_number, new_extension=None):
        return cls._version(cls._unversion(filename, new_extension=new_extension), version_number)

    @classmethod
    def locate_latest_version(cls, filename, current_stage):
        while current_stage > 0:
            current_stage = current_stage - 1
            candidate = cls.version_filename(filename, current_stage)
            matches = [filename for filename in glob.glob(os.path.splitext(candidate)[0] + '.*') if os.path.isfile(filename)]
            if matches and matches[0]:
                return matches[0]

        return cls._unversion(filename)

    @classmethod
    def untar(cls, source, target):
        # extract the file
        with tarfile.open(source, 'r') as archive:
            # make the temp directory if it doesn't already exist
            if not os.path.isdir(target):
                os.mkdir(target)
            archive.extractall(target)

    @classmethod
    def absolutize(cls, *, bundle=None, work_dir=None, input_dir=None, filename, new_extension=None):
        return os.path.join(os.path.abspath(work_dir or bundle.local_path), input_dir or '', filename)

    @classmethod
    def _version(cls, filename, version_number, new_extension=None):
        return "{0}_stage_{2:0>2}{1}".format(*os.path.splitext(filename), version_number)

    @classmethod
    def _unversion(cls, filename, new_extension=None):
        (basename, ext) = os.path.splitext(filename)
        strip = sub(r'_stage_\d{2}$', '', basename)
        return "{0}{1}".format(strip, ext)
