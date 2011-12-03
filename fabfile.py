from fabric.api import local

def test():
    """Runs tests"""
    local("nosetests --with-progressive -w nexus/test/")

def update():
    """Updates official bitbucket repo"""
    local("hg push")

def release():
    """Releases to PyPi"""
    test()
    update()
    local("python setup.py sdist upload")


