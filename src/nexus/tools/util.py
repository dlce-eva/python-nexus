import pathlib
import functools

from nexus import NexusWriter, NexusReader


def get_nexus_reader(thing):
    if isinstance(thing, str):
        return NexusReader.from_string(thing)
    if isinstance(thing, pathlib.Path):
        return NexusReader.from_file(thing)
    if isinstance(thing, NexusWriter):
        return NexusReader.from_string(thing.write())
    assert isinstance(thing, NexusReader)
    return thing


def with_nexus_reader(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        return func(get_nexus_reader(args[0]), *args[1:], **kwargs)
    return _
