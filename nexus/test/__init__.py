import unittest

def nexus_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('.')
    return suite
