from fabric.api import local

project = 'nexus'

def test():
    """Runs tests"""
    local("nosetests")

def lint():
    """Runs pyflakes"""
    local("pyflakes %s" % project)
    
def py2to3():
    """Runs 2to3"""
    local("2to3 %s" % project)

def update():
    """Updates official bitbucket repo"""
    local("hg push")

def release():
    """Releases to PyPi"""
    test()
    update()
    local("python setup.py sdist upload")


