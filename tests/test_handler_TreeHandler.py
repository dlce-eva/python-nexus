"""Tests for TreeHandler"""
import pytest

from nexus.reader import NexusReader
from nexus.exceptions import NexusFormatException
from nexus.handlers.tree import TreeHandler, Tree


def test_Tree():
    t = Tree('tree name = (A,B)C;')
    assert t == Tree.from_newick(t.newick_tree, name=t.name, rooted=t.rooted)


def test_block_find(trees):
    # did we get a tree block?
    assert 'trees' in trees.blocks


def test_treecount(trees):
    # did we find 3 trees?
    assert len(trees.blocks['trees'].trees) == 3
    assert trees.blocks['trees'].ntrees == 3
    assert len(trees.trees.trees) == 3
    assert trees.trees.ntrees == 3


def test_taxa(trees):
    expected = [
        'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
        'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
    ]
    assert len(trees.trees.taxa) == len(expected) == trees.trees.ntaxa
    for taxon in expected:
        assert taxon in trees.trees.taxa


def test_iterable(trees):
    assert list(trees.blocks['trees'])
    assert list(trees.trees)


def test_write(trees, examples):
    written = trees.trees.write()
    expected = examples.joinpath('example.trees').read_text(encoding='utf8')
    # remove leading header which isn't generated by .write()
    expected = expected.lstrip("#NEXUS\n\n")
    assert expected == written


def test_write_produces_end(trees):
    assert "end;" in trees.trees.write()
    assert len([_ for _ in trees.trees[0].newick_tree.walk()]) == 25


def test_block_findt(trees_translated):
    # did we get a tree block?
    assert 'trees' in trees_translated.blocks


def test_treecountt(trees_translated):
    # did we find 3 trees?
    assert len(trees_translated.blocks['trees'].trees) == 3
    assert trees_translated.blocks['trees'].ntrees == 3
    assert len(trees_translated.trees.trees) == 3
    assert trees_translated.trees.ntrees == 3


def test_iterablet(trees_translated):
    assert list(trees_translated.blocks['trees'])
    assert list(trees_translated.trees)


def test_taxat(trees_translated):
    expected = [
        'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
        'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
    ]
    assert len(trees_translated.trees.taxa) == len(expected)
    for taxon in expected:
        assert taxon in trees_translated.trees.taxa


def test_was_translated_flag_set(trees_translated):
    assert trees_translated.trees.was_translated


def test_parsing_sets_translators(trees_translated):
    assert len(trees_translated.trees.translators) == 13


def test_been_detranslated_flag_set(trees_translated):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    assert trees_translated.trees._been_detranslated


def test_writet(trees_translated, examples):
    assert not trees_translated.trees._been_detranslated
    written = trees_translated.trees.write()
    expected = examples.joinpath('example-translated.trees').read_text(encoding='utf8')
    # remove leading header which isn't generated by .write()
    expected = expected.lstrip("#NEXUS\n\n")
    # remove tabs since we reformat things a bit
    expected = expected.replace("\t", "").strip()
    written = written.replace("\t", "").strip()
    # handle the workaround for the beast bug
    expected = expected.replace("12 David;", "12 David\n;")
    assert expected == written, "%s\n----\n%s" % (expected, written)


def test_no_error_on_multiple_translate(trees_translated):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    assert trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()  # should not cause an error


def test_detranslate(trees_translated, examples):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    # should NOW be the same as tree 0 in example.trees
    other_tree_file = NexusReader(str(examples / 'example.trees'))
    assert other_tree_file.trees[0] == trees_translated.trees[0]


def test_detranslate_without_translators(nex):
    """
    Test that running detranslate when there's no translate block doesn't
    break the trees
    """
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        tree = (A,(B,C));
    end;
    """)
    assert nex.trees.translators == {1: 'A', 2: 'B', 3: 'C'}
    assert nex.trees._been_detranslated
    nex.trees.detranslate()
    assert nex.trees.trees[0] == 'tree = (A,(B,C));'


def test_treelabel():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree TREEONE = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree TREEONE = (0,1,2);']


def test_no_treelabel():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree = (0,1,2);']


def test_rooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree [&] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree [&] = (0,1,2);']
    assert nex.trees.trees[0].rooted is None  # we only recognize [&R]!


def test_unrooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree [&U] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree [&U] = (0,1,2);']
    assert nex.trees.trees[0].rooted is False


def test_labelled_unrooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree unrooted [U] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree unrooted [U] = (0,1,2);']


def test_ok_starting_with_zero():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree tree = (0,1,2)
    end;
    """)
    assert len(nex.trees.translators) == 3
    assert '0' in nex.trees.translators
    assert '1' in nex.trees.translators
    assert '2' in nex.trees.translators


def test_ok_starting_with_one():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            1 Tom,
            2 Simon,
            3 Fred;
            tree tree = (1,2,3)
    end;
    """)
    assert len(nex.trees.translators) == 3
    assert '1' in nex.trees.translators
    assert '2' in nex.trees.translators
    assert '3' in nex.trees.translators


def test_error_on_duplicate_taxa_id():
    with pytest.raises(NexusFormatException):
        NexusReader.from_string("""
        #NEXUS
    
        begin trees;
            translate
                0 Tom,
                1 Simon,
                1 Tom;
                tree tree = (0,1,2)
        end;
        """)


def test_error_on_duplicate_taxa():
    with pytest.raises(NexusFormatException):
        NexusReader.from_string("""
        #NEXUS
    
        begin trees;
            translate
                0 Tom,
                1 Simon,
                2 Tom;
                tree tree = (0,1,2)
        end;
        """)


def test_read_BEAST_format(trees_beast):
    assert trees_beast.trees[0].name == 'STATE_201000'
    assert len([_ for _ in trees_beast.trees[0].newick_tree.walk()]) == 75
    trees_beast.trees.detranslate()
    assert 'F38' in set(n.name for n in trees_beast.trees[0].newick_tree.walk())


def test_block_find_BEAST(trees_beast):
    # did we get a tree block?
    assert 'trees' in trees_beast.blocks


def test_taxa_BEAST(trees_beast):
    expected = [
        "R1", "B2", "S3", "T4", "A5", "E6", "U7", "T8", "T9", "F10", "U11",
        "T12", "N13", "F14", "K15", "N16", "I17", "L18", "S19", "T20",
        "V21", "R22", "M23", "H24", "M25", "M26", "M27", "R28", "T29",
        "M30", "P31", "T32", "R33", "P34", "R35", "W36", "F37", "F38"
    ]
    assert len(trees_beast.trees.taxa) == len(expected)
    for taxon in expected:
        assert taxon in trees_beast.trees.taxa


def test_treecount_BEAST(trees_beast):
    assert len(trees_beast.blocks['trees'].trees) == 1
    assert trees_beast.blocks['trees'].ntrees == 1
    assert len(trees_beast.trees.trees) == 1
    assert trees_beast.trees.ntrees == 1


def test_flag_set_BEAST(trees_beast):
    assert trees_beast.trees.was_translated


def test_parsing_sets_translators_BEAST(trees_beast):
    assert len(trees_beast.trees.translators) == 38


def test_detranslate_BEAST_format_extended(trees_beast):
    trees_beast.trees.detranslate()
    for index, taxon in trees_beast.trees.translators.items():
        # check if the taxon name is present in the tree...
        assert taxon in trees_beast.trees[0], \
            "Expecting taxon %s in tree description" % taxon
    assert trees_beast.trees._been_detranslated


@pytest.fixture
def findall():
    th = TreeHandler()
    return th._findall_chunks


def test_tree(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': 'Chris',
            'comment': None,
            'branch': None,
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': 'Bruce',
            'comment': None,
            'branch': None,
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': 'Tom',
            'comment': None,
            'branch': None,
            'end': ')'
        },
    }
    found = findall("tree a = ((Chris,Bruce),Tom);")
    assert len(found) == 3
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_digits(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': None,
            'branch': None,
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': None,
            'branch': None,
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': None,
            'branch': None,
            'end': ')'
        },
    }
    found = findall("tree a = ((1,2),3);")
    assert len(found) == len(expected)
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_with_branchlengths(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': None,
            'branch': '0.1',
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': None,
            'branch': '0.2',
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': None,
            'branch': '0.3',
            'end': ')'
        },
    }
    found = findall("tree a = ((1:0.1,2:0.2):0.9,3:0.3):0.9;")
    assert len(found) == len(expected)
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_complex(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': '[&var=1]',
            'branch': '0.1',
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': '[&var=2]',
            'branch': '0.2',
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': '[&var=4]',
            'branch': '0.3',
            'end': ')'
        },
    }
    found = findall(
        "tree a = ((1:[&var=1]0.1,2:[&var=2]0.2):[&var=3]0.9,3:[&var=4]0.3):[&var=5]0.9;"
    )
    assert len(found) == len(expected)
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_beast(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': '[&height=2.3452879110403307E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=258.70043556210754,length_95%_HPD={125.0945446246701,400.9482857259336},length_median=248.74247485637466,length_range={87.67414535194837,569.5185478509179}]',
            'comment2': '[&rate=1.0490840741428833]',
            'branch': '248.74247485637466',
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '8',
            'comment': '[&height=2.3452879110403307E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=258.70043556210754,length_95%_HPD={125.0945446246701,400.9482857259336},length_median=248.74247485637466,length_range={87.67414535194837,569.5185478509179}]',
            'comment2': '[&rate=0.5685693841839251]',
            'branch': '248.74247485637466',
            'end': ')'
        },
        2: {
            'start': '(',
            'taxon': '2',
            'comment': '[&height=2.349830841618617E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=228.10859461916877,length_95%_HPD={131.22075419530938,356.5786515170671},length_median=222.10500215033449,length_range={77.89722838644559,459.08340510231324}]',
            'comment2': '[&rate=1.212285030570299]',
            'branch': '225.26384804987163',
            'end': ','
        },
    }
    found = findall("""tree TREE1 = (((((1[&height=2.3452879110403307E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=258.70043556210754,length_95%_HPD={125.0945446246701,400.9482857259336},length_median=248.74247485637466,length_range={87.67414535194837,569.5185478509179}]:[&rate=1.0490840741428833]248.74247485637466,8[&height=2.3452879110403307E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=258.70043556210754,length_95%_HPD={125.0945446246701,400.9482857259336},length_median=248.74247485637466,length_range={87.67414535194837,569.5185478509179}]:[&rate=0.5685693841839251]248.74247485637466)[&height=258.70043556210777,height_95%_HPD={125.09454462467033,400.94828572593383},height_median=248.74247485637488,height_range={87.6741453519486,569.5185478509181},length=290.168171002562,length_95%_HPD={104.52601887523406,509.30103866387697},length_median=278.84468430173035,length_range={43.32725532041934,701.3959413910843},posterior=1.0]:[&rate=0.8984829210873586]269.91864982346624,((2[&height=2.349830841618617E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=228.10859461916877,length_95%_HPD={131.22075419530938,356.5786515170671},length_median=222.10500215033449,length_range={77.89722838644559,459.08340510231324}]:[&rate=1.212285030570299]225.26384804987163,(5[&height=2.2987228726128955E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,9.094947017729282E-13},length=154.99053758134195,length_95%_HPD={71.07202704642134,254.02798333744158},length_median=148.5994591519618,length_range={40.663248568802146,360.98015436563946}]:[&rate=1.3913960645678562]146.9812596385919,11[&height=2.286229813522608E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,9.094947017729282E-13},length=159.31026847208952,length_95%_HPD={71.07202704642134,266.7061022958778},length_median=150.9796070714549,length_range={40.663248568802146,391.8925493279751}]:[&rate=0.9304290024380776]146.9812596385919)[&height=153.11858682647878,height_95%_HPD={70.1071182878378,247.61369584888666},height_median=146.98125963859212,height_range={40.663248568802146,360.9801543656399},length=78.77236008715263,length_95%_HPD={17.917450065465914,155.22776333332945},length_median=71.59151005409262,length_range={5.8454208223879505,331.22353191699494},posterior=0.929070929070929]:[&rate=0.6372148460963499]78.28258841127973)[&height=232.52844039863925,height_95%_HPD={139.76383444345765,357.8723140898412},height_median=225.26384804987185,height_range={77.89722838644582,459.08340510231346},length=107.48718697982387,length_95%_HPD={30.871901584928537,205.22879205708728},length_median=99.15495552903059,length_range={13.634227648258843,383.1637039486467},posterior=0.999000999000999]:[&rate=0.7968654134343461]105.981629529261,15[&height=2.3657310986426193E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=339.9758221718785,length_95%_HPD={204.9515053278742,496.1523832482874},length_median=331.23067147294125,length_range={137.29595433157874,672.6023748769472}]:[&rate=1.3310316896338557]331.2454775791326)[&height=340.00940619428206,height_95%_HPD={204.95150532787432,496.1523832482876},height_median=331.24547757913285,height_range={137.29595433157897,672.6023748769475},length=194.50831195215406,length_95%_HPD={63.58873253110528,325.2377695831469},length_median=187.20598843933556,length_range={45.2576784424532,670.7599881486103},posterior=1.0]:[&rate=1.1563168353663102]187.41564710070827)[&height=529.2946623066919,height_95%_HPD={332.0853556299478,771.3711127105082},height_median=518.6611246798411,height_range={271.2632610518173,1121.9402235516059},length=114.12288973446404,length_95%_HPD={32.47670492944752,218.60228617968608},length_median=105.82996360571929,length_range={16.09827073241047,410.67627767558895},posterior=0.8201798201798202]:[&rate=1.6578172332564658]111.1111165249655,(((3[&height=2.3895814841786225E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=173.68582542966865,length_95%_HPD={85.87916259002316,272.88599650284254},length_median=167.52208873786753,length_range={59.5779355538732,373.04257882904676}]:[&rate=0.7567578662495598]167.5220887378673,(9[&height=2.38049562302205E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,9.094947017729282E-13},length=98.94998768716802,length_95%_HPD={38.853757983202286,175.251197040041},length_median=93.59409165099669,length_range={22.543458717158728,290.32111094967354}]:[&rate=1.4792249885207513]93.59409165099669,10[&height=2.38049562302205E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,9.094947017729282E-13},length=98.94998768716802,length_95%_HPD={38.853757983202286,175.251197040041},length_median=93.59409165099669,length_range={22.543458717158728,290.32111094967354}]:[&rate=1.2842331341962436]93.59409165099669)[&height=98.94998768716822,height_95%_HPD={38.8537579832024,175.251197040041},height_median=93.59409165099692,height_range={22.543458717158956,290.32111094967377},length=74.73583774250073,length_95%_HPD={22.81398174440426,138.46060937334505},length_median=69.41476306630375,length_range={7.179109136220745,214.2400015221051},posterior=1.0]:[&rate=1.3310316896338557]73.92799708687062)[&height=173.6858254296689,height_95%_HPD={85.87916259002338,272.8859965028428},height_median=167.52208873786753,height_range={59.57793555387343,373.042578829047},length=176.0045067179382,length_95%_HPD={57.62545503606634,301.7622713657802},length_median=166.41157997814616,length_range={46.303669149082225,432.2341594138278},posterior=1.0]:[&rate=1.2455557655099214]142.2773987740664,4[&height=2.4316035920277715E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=311.23288109451113,length_95%_HPD={175.456209957257,471.36624091868225},length_median=303.48235247228536,length_range={111.02713374990992,680.8184231048691}]:[&rate=1.088218207187109]309.7994875119337)[&height=320.5093917390516,height_95%_HPD={180.29443303424728,464.03074813193234},height_median=309.79948751193393,height_range={143.57932153708384,680.8184231048693},length=70.62732552968313,length_95%_HPD={12.480993266270616,151.8283837992817},length_median=62.660796047871145,length_range={0.076410640793938,265.6232291478491},posterior=0.4875124875124875]:[&rate=1.0490840741428833]66.70997737407896,(13[&height=2.3952601474014804E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=112.35332662226135,length_95%_HPD={38.03794967900262,198.20876868970595},length_median=106.329746319082,length_range={26.71081209056854,368.64254601223865}]:[&rate=1.0490840741428833]106.32974631908178,19[&height=2.3952601474014804E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=112.35332662226135,length_95%_HPD={38.03794967900262,198.20876868970595},length_median=106.329746319082,length_range={26.71081209056854,368.64254601223865}]:[&rate=0.832684006377655]106.32974631908178)[&height=112.35332662226158,height_95%_HPD={38.03794967900285,198.20876868970618},height_median=106.329746319082,height_range={26.710812090568766,368.6425460122389},length=231.82435900722984,length_95%_HPD={91.59595306872973,377.3581753238161},length_median=222.5953672923083,length_range={60.293686737246276,575.4779205485341},posterior=1.0]:[&rate=0.7775268188857386]270.1797185669309)[&height=385.6089339232876,height_95%_HPD={216.19279816128665,549.9155188267073},height_median=376.5094648860129,height_range={139.5420619797378,731.2026338505391},length=242.09273220746576,length_95%_HPD={104.94965086497768,401.6033511631731},length_median=232.24267507441175,length_range={50.13569296241599,656.4719777949385},posterior=1.0]:[&rate=0.832684006377655]253.26277631879373)[&height=642.8872409419835,height_95%_HPD={414.9048901999846,942.8378628754554},height_median=629.7722412048066,height_range={335.1832964153999,1176.3087869965289},length=286.48917746100517,length_95%_HPD={93.16893089699317,501.21222202917056},length_median=268.6067419102857,length_range={93.16893089699317,974.569599340233},posterior=1.0]:[&rate=1.1319829805577242]276.88386465540634,17[&height=2.3850385536003363E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,4.547473508864641E-13},length=929.3764184029874,length_95%_HPD={543.8382135352783,1305.9352427660904},length_median=906.6561058602127,length_range={486.0917410289215,1894.208904715308}]:[&rate=0.5685693841839251]906.6561058602127)[&height=929.3764184029878,height_95%_HPD={543.8382135352786,1305.9352427660906},height_median=906.656105860213,height_range={486.0917410289217,1894.2089047153083},length=344.1806879221153,length_95%_HPD={20.693371148009305,709.67821338241},length_median=320.90002929197874,length_range={0.8686008759475499,1261.7527037979075},posterior=1.0]:[&rate=1.2842331341962436]328.54484901401304,((6[&height=2.391852949467766E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=229.97465979992901,length_95%_HPD={109.75469030067734,346.0165478038964},length_median=228.7298866582346,length_range={84.05655132669335,486.751397593304}]:[&rate=0.8824188210038937]228.7298866582346,18[&height=2.391852949467766E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=229.97465979992901,length_95%_HPD={109.75469030067734,346.0165478038964},length_median=228.7298866582346,length_range={84.05655132669335,486.751397593304}]:[&rate=1.3310316896338557]228.7298866582346)[&height=229.97465979992933,height_95%_HPD={109.75469030067757,346.0165478038964},height_median=228.72988665823482,height_range={84.05655132669358,486.7513975933042},length=218.9786379369377,length_95%_HPD={92.80790627153647,333.8673919809794},length_median=218.50103321712413,length_range={60.84039835385272,431.76178495371596},posterior=1.0]:[&rate=0.7081605424897239]226.48203128195087,((7[&height=2.4225177308711986E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=247.49644764784986,length_95%_HPD={146.47012075413204,353.2160935687174},length_median=246.69336490527394,length_range={93.21758260613706,461.84143334286046}]:[&rate=0.8661719838694598]246.69336490527394,12[&height=2.4259249288049136E-13,height_95%_HPD={0.0,4.547473508864641E-13},height_median=2.2737367544323206E-13,height_range={0.0,6.821210263296962E-13},length=253.3538242296732,length_95%_HPD={141.1892039510575,362.86514703623504},length_median=250.35988330441273,length_range={93.21758260613706,487.70217519402036}]:[&rate=0.7567578662495598]246.69336490527394)[&height=247.2078688722885,height_95%_HPD={148.08095112892056,352.43565395917585},height_median=246.69336490527417,height_range={93.21758260613728,461.8414333428609},length=119.82285120047494,length_95%_HPD={37.06416391275661,218.29981597542155},length_median=114.99408555763193,length_range={20.34960868172891,310.55851619269606},posterior=0.9440559440559441]:[&rate=1.030757305880866]121.17781720251173,(14[&height=9.653727478858504E-15,height_95%_HPD={0.0,0.0},height_median=0.0,height_range={0.0,4.547473508864641E-13},length=221.8751096003859,length_95%_HPD={123.37850366703844,330.03234470825714},length_median=220.5581145217834,length_range={82.17779399808546,417.1234406231214}]:[&rate=1.212285030570299]218.36257839253528,16[&height=9.653727478858504E-15,height_95%_HPD={0.0,0.0},height_median=0.0,height_range={0.0,4.547473508864641E-13},length=218.41389612204873,length_95%_HPD={120.76296958365106,316.2979249218963},length_median=217.42851427791834,length_range={82.17779399808546,349.61641425985}]:[&rate=0.8496358084660076]218.36257839253528)[&height=218.96834342443523,height_95%_HPD={128.99444166760463,324.44238569049276},height_median=218.36257839253528,height_range={82.17779399808546,349.61641425985},length=145.3605128936476,length_95%_HPD={52.97596353429776,241.7257424706154},length_median=140.40379056728892,length_range={27.887531387445392,323.5392821638645},posterior=0.97002997002997]:[&rate=1.1319829805577242]149.50860371525062)[&height=366.34537566475643,height_95%_HPD={258.6271888080021,466.5388763228782},height_median=367.8711821077859,height_range={204.16216546982878,550.6732282795645},length=86.84086796929844,length_95%_HPD={25.931106266377412,160.3641380533661},length_median=80.69820227693492,length_range={12.616639270858457,259.10079521308853},posterior=0.9600399600399601]:[&rate=0.6372148460963499]87.34073583239979)[&height=453.0654837711674,height_95%_HPD={349.78834726216394,541.4813285829149},height_median=455.2119179401857,height_range={274.468974726194,609.0390253633507},length=820.4916225539342,length_95%_HPD={376.8373139927555,1326.9028441870373},length_median=777.8309130511332,length_range={281.2176089978106,1948.8837290447304},posterior=1.0]:[&rate=0.832684006377655]779.9890369340403)[&height=1273.5571063251045,height_95%_HPD={769.6522881467952,1812.34194950441},height_median=1235.200954874226,height_range={619.7568429516483,2474.618943662244},length=0.0,posterior=1.0]:0.0;""")
    assert len(found) == 19  # 19 taxa
    for c in found:
        print(c)
        print("")
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]



def test_no_change():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((Chris,Bruce),Tom);"
    newtree = "tree a = ((Chris,Bruce),Tom);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly NOT translate a simple tree"


def test_no_change_branchlengths():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly NOT translate a tree with branchlengths"


def test_change():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0,1),2);"
    newtree = "tree a = ((Chris,Bruce),Tom);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a simple tree"


def test_change_branchlengths():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0:0.1,1:0.2):0.3,2:0.4);"
    newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a tree with branchlengths"


def test_change_comment():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0[x],1[y]),2[z]);"
    newtree = "tree a = ((Chris[x],Bruce[y]),Tom[z]);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a tree with branchlengths"


def test_BEAST_format():
    translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
    oldtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
    newtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a BEAST tree"


def test_leading_BEAST_format():
    translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
    oldtree = "tree STATE_0 [&lnP=-8411959.874895355,posterior=-8411959.874895355] = [&R] ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
    newtree = "tree STATE_0 [&lnP=-8411959.874895355,posterior=-8411959.874895355] = [&R] ((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a BEAST tree"


def test_preamble():
    translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
    oldtree = "tree STATE_0=((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
    newtree = "tree STATE_0=((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a BEAST tree"


def test_invalid_preamble():
    with pytest.raises(ValueError):
        TreeHandler()._detranslate_tree(
            'tree STATE_0 [abcde=1234 = ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);', {})
