from nexus.tools import new_nexus_without_sites


def test_remove_sites_list(nex):
    nexus = new_nexus_without_sites(nex, [1])
    assert len(nexus.data) == 1


def test_remove_sites_set(nex):
    nexus = new_nexus_without_sites(nex, set([1]))
    assert len(nexus.data) == 1
