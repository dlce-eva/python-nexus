import string
import statistics
import collections

SAFE_CHARACTERS = string.ascii_letters + string.digits + '-_'


class Checker(object):

    EMPTY_STATES = ('?', '-', '0')

    def __init__(self, nex):
        self.errors, self.messages = [], []
        self.check(nex)

    @property
    def has_errors(self):
        return len(self.errors) > 0

    def check(self, nex):  # pragma: no cover
        raise NotImplementedError("Should be subclassed")

    def log(self, message):
        self.messages.append(message)

    def status(self):  # pragma: no cover
        print("%s\t%d errors" % (self.__class__.__name__.ljust(50), len(self.errors)))
        for i, e in enumerate(self.messages, 1):
            print("\t%3d. %s" % (i, e))
        for i, e in enumerate(self.errors, 1):
            print("\t%3d. %s" % (i, e))


class DuplicateLabelChecker(Checker):
    """
    Checks for Duplicate Character Labels
    """
    def check(self, nex):
        labels = collections.Counter(nex.data.charlabels.values())
        for label in labels:
            if labels[label] > 1:
                self.errors.append("Duplicate Label (n=%d): %s" % (labels[label], label))
        return not self.has_errors


class PotentiallyUnsafeTaxaLabelsChecker(Checker):
    """
    Checks for Potentially Unsafe Taxa Labels (non-Latin 1 characters etc)
    """
    def check(self, nex):
        for taxon in nex.data.taxa:
            bad = [char for char in taxon if char not in SAFE_CHARACTERS]
            if len(bad):
                self.errors.append(
                    "Potentially Unsafe Taxon Label: %s: %s" % (taxon, " ".join(bad)))
        return not self.has_errors


class LabelChecker(Checker):
    """
    Checks that the number of character labels (if present) is correct
    """
    def check(self, nex):
        nlabels = len(nex.data.charlabels)
        if nlabels == 0:
            return not self.has_errors
        if nlabels != nex.data.nchar:
            self.errors.append(
                "Incorrect number of character labels (expected %d, got %d)" % (
                    nex.data.nchar, nlabels))
        return not self.has_errors


class UnusualStateChecker(Checker):
    """
    Checks for unusual states.

    Returns errors if there are states with counts of less than `THRESHOLD`.
    """
    THRESHOLD = 0.001  # anything less than this is flagged

    def check(self, nex):
        states = collections.Counter()
        for s in nex.data.matrix.values():
            states.update(s)
        total = sum(states.values())
        for s, n in states.most_common():
            if n <= total * self.THRESHOLD:
                self.errors.append("Unusual State Found: %s (n=%d)" % (s, n))
        return not self.has_errors


class EmptyCharacterChecker(Checker):
    """
    Checks for Empty Characters (i.e. sites with nothing other than the values in
    `EMPTY_STATES`. By default: ('?', '-', '0')
    """
    MIN_COUNT = 0

    def check(self, nex):
        tally = collections.Counter()
        for taxon in nex.data.matrix:
            tally.update([
                i for i, c in enumerate(nex.data.matrix[taxon], 0)
                if c not in self.EMPTY_STATES
            ])

        for i in range(0, nex.data.nchar):
            n = tally.get(i, 0)
            if n == self.MIN_COUNT:
                if 'ascert' in nex.data.charlabels.get(i, '').lower():  # ignore
                    self.log("Character %d is an ascertainment character" % i)
                else:
                    self.errors.append("Character %d has count %d" % (i, self.MIN_COUNT))
        return not self.has_errors


class SingletonCharacterChecker(EmptyCharacterChecker):
    MIN_COUNT = 1


class LowStateCountChecker(Checker):
    """
    Checks for taxa with low character states.

    Returns errors if there are taxa with counts of less than 3 standard
    deviations
    """
    THRESHOLD = 3  # 3 x the standard deviation

    def check(self, nex):
        counts = {}
        for taxon in nex.data.matrix:
            counts[taxon] = len([
                c for c in nex.data.matrix[taxon] if c not in self.EMPTY_STATES])

        med = statistics.median(counts.values())
        sd = statistics.stdev(counts.values())
        sd_threshold = med - (self.THRESHOLD * sd)

        for taxon in sorted(counts):
            if counts[taxon] <= sd_threshold:
                self.errors.append(
                    "Taxon %s has a low state count (%d, median = %0.2f - %0.2f)" % (
                        taxon, counts[taxon], med, sd_threshold))
        return not self.has_errors


class BEASTAscertainmentChecker(Checker):
    """
    Checks that the ascertainment correction for BEAST is correct
    """
    def check(self, nex):
        # do we have character labels? -- find characters identified as _asc
        ascert = [c for c in nex.data.charlabels if 'ascert' in nex.data.charlabels[c]]
        # are they empty?
        for a in ascert:
            states = [nex.data.matrix[t][a] for t in nex.data.matrix]
            states = collections.Counter([s for s in states if s not in self.EMPTY_STATES])
            if len(states):
                self.errors.append(
                    "Character %d - %s should be an ascertainment character but has data (%r)" % (
                        a, nex.data.charlabels[a], states))

        # if we have more than one then we should have assumptions block
        if len(ascert) > 1:
            if 'assumptions' not in [k.lower() for k in nex.blocks.keys()]:
                self.errors.append("Missing assumptions block")
        return not self.has_errors


# TODO check assumptions block

CHECKERS = {
    'base': [
        LabelChecker,
        DuplicateLabelChecker,
        PotentiallyUnsafeTaxaLabelsChecker,
        LowStateCountChecker,
        EmptyCharacterChecker,
    ],
    'ascertainment': [
        BEASTAscertainmentChecker,
    ],
    'extra': [
        UnusualStateChecker,
        SingletonCharacterChecker,
    ],
}
