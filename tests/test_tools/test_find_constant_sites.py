from nexus.tools import find_constant_sites


def test_find_constant_sites_1(nex):
    assert not find_constant_sites(nex)


def test_find_constant_sites_2(nex2):
    const = find_constant_sites(nex2)
    assert len(const) == 4
    assert 0 in const
    assert 1 in const
    assert 2 in const
    assert 3 in const
