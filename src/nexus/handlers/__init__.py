import re

COMMENT_PATTERN = re.compile(r"""(\[.*?\])""")
QUOTED_PATTERN = re.compile(r"""^["'](.*)["']$""")
WHITESPACE_PATTERN = re.compile(r"""\s+""")
MESQUITE_TITLE_PATTERN = re.compile(r"""^TITLE\s+(.*);$""", re.IGNORECASE)
MESQUITE_LINK_PATTERN = re.compile(
    r"""^LINK\s+(.*?)\s+=\s+(.*);$""", re.IGNORECASE
)
BEGIN_PATTERN = re.compile(r"""begin (\w+)(\s*|\[.*\]);""", re.IGNORECASE)
END_PATTERN = re.compile(r"""end\s*;""", re.IGNORECASE)


class GenericHandler(object):
    """
    Handlers are objects to store specialised blocks found in nexus files.

    Nexus Block->Handler mapping is initialised in Nexus.handlers

    Handlers have (at least) the following attributes:

        1. parse(self, data) - the function for parsing the block
        2. write(self, data) - a function for returning the block to a text
            representation (used to regenerate a nexus file).
        3. block - a list of raw strings in this block
    """
    def __init__(self, data=None):
        """Initialise datastore in <block> under <keyname>"""
        self.block = data or []
        self.comments = []

        # save comments
        for line in self.block:
            if line.strip().startswith("[") and line.strip().endswith("]"):
                self.comments.append(line)

    def write(self):
        """
        Generates a string containing a generic nexus block for this data.

        :return: String
        """
        return "\n".join(self.block)

    @staticmethod
    def remove_comments(line):
        """
        Removes comments from lines

        >>> g = GenericHandler()
        >>> g.remove_comments("Hello [world]")
        'Hello '
        >>> g.remove_comments("He[bite]ll[me]o")
        'Hello'

        :param line: string
        :type line: string

        :return: Returns a cleaned string.
        """
        return COMMENT_PATTERN.sub('', line)

    @staticmethod
    def is_mesquite_attribute(line):
        """
        Returns True if the line is a mesquite attribute

        :return: Boolean
        """
        if MESQUITE_TITLE_PATTERN.match(line):
            return True
        elif MESQUITE_LINK_PATTERN.match(line):
            return True
        return False
