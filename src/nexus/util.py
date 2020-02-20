import pathlib


class FileWriterMixin(object):
    def write_to_file(self, filename_, encoding='utf8', **kw):
        """
        Writes the nexus to a file.

        :return: `pathlib.Path` instance of the written file.
        """
        res = pathlib.Path(filename_)
        res.write_text(self.write(**kw), encoding=encoding)
        return res
