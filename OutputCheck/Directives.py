import collections
import logging
from . import CheckFileParser
import re

_logger = logging.getLogger(__name__)

class DirectiveException(Exception):
    def __init__(self, directive):
        self.directive = directive

    def __str__(self):
        return self.directive.getErrorMessage()

class Directive(object):
    def __init__(self, pattern, sourceLocation):
        if not isinstance(pattern,str):
            raise Exception('Arg must be a string')

        if not isinstance(sourceLocation, CheckFileParser.FileLocation):
            raise Exception('sourceLocation must be a FileLocation')

        try:
            self.regex = re.compile(pattern)
        except Exception as e:
            raise CheckFileParser.ParsingException("Failed to parse regular expression at {location} : {reason}".format(
                                                   location=sourceLocation, reason=str(e)))

        self.sourceLocation = sourceLocation
        self.matchLocation = None
        self.failed = False

    def __str__(self):
        s = self.getName() + ' Directive ('
        s += "{file}:{line} Pattern: '{Regex}')".format(file=self.sourceLocation.fileName, line=self.sourceLocation.lineNumber, Regex=self.regex.pattern)
        return s

    def getName(self):
        return self.__class__.__name__

    def getErrorMessage(self):
        raise NotImplementedError()

    def match(self, subsetLines, subsetOffset, fileName):
        """
            Search through lines for match.
            What is returned is defined by implementations
        """
        raise NotImplementedError()


class Check(Directive):
    @staticmethod
    def directiveToken():
        return ':'

    def match(self, subsetLines, offsetOfSubset, fileName):
        """
            Search through lines for match.
            Raise an Exception if fail to match
            If match is succesful return the position the match was found
        """

        for (offset,l) in enumerate(subsetLines):
            m = self.regex.search(l)
            if m != None:
                truePosition = offset + offsetOfSubset
                _logger.debug('Found match on line {}'.format(str(truePosition+ 1)))
                _logger.debug('Line is {}'.format(l))
                self.matchLocation = CheckFileParser.FileLocation(fileName, truePosition +1) 
                return truePosition

        # No Match found
        self.failed = True
        raise DirectiveException(self)

    def getErrorMessage(self):
        return 'Could not find a match for {}'.format(str(self))

    @staticmethod
    def validate(directiveList):
        """
            No special validation is needed here.
        """
        pass

class CheckNext(Directive):
    @staticmethod
    def directiveToken():
        return '-NEXT:'

    def __init__(self, pattern, sourceLocation):
        super(CheckNext,self).__init__(pattern, sourceLocation)
        self.expectedMatchLocation = None

    def match(self, line, positionOfLine, fileName):
        self.expectedMatchLocation = CheckFileParser.FileLocation(fileName, positionOfLine)

        m = self.regex.search(line)
        if m == None:
            self.failed = True
            raise DirectiveException(self)
        else:
            self.matchLocation = self.expectedMatchLocation
            _logger.debug('Found match for {pattern} at {location}'.format(pattern=self.regex.pattern, location=self.matchLocation))

    def getErrorMessage(self):
        return 'Could not find a match for {directive} expected at {location}'.format(directive=str(self), location=self.expectedMatchLocation)

    @staticmethod
    def validate(directiveList):
        """
            We should enforce that every CHECK-NEXT directive in the list (apart from if it
            is the first directive) should have a CHECK or CHECK-NEXT before it.

            * CHECK-NEXT is the first directive
            * CHECK-NEXT either has a CHECK or a CHECK-NEXT before it

        """
        for (index,directive) in enumerate(directiveList):
            if isinstance(directive, CheckNext):
                if index > 0:
                    before = directiveList[index -1]
                    if not (isinstance(before, CheckNext) or isinstance(before, Check)):
                        raise CheckFileParser.ParsingException("{directive} must have a CHECK{check} or CHECK{checkNext} directive before it instead of a {bad}".format(
                                                                directive=directive,
                                                                check=Check.directiveToken(),
                                                                checkNext=CheckNext.directiveToken(),
                                                                bad=before)
                                                              )

class CheckNot(Directive):
    RegexLocationTuple = collections.namedtuple('RegexLocationTuple',['Regex','SourceLocation'])
    def __init__(self, pattern, sourceLocation):
        if not isinstance(pattern,str):
            raise Exception('pattern must be a string')

        self.regex = [ self.RegexLocationTuple(Regex=re.compile(pattern), SourceLocation=sourceLocation) ]
        self.matchLocation = None

    @staticmethod
    def directiveToken():
        return '-NOT:'

    def addPattern(self, pattern, sourceLocation):
        if not isinstance(pattern,str):
            raise Exception('pattern must be a string')

        self.regex.append( self.RegexLocationTuple(Regex=re.compile(pattern), SourceLocation=sourceLocation) )

    def match(self, subsetLines, offsetOfSubset, fileName):
        """
            Search through lines for match.
            Raise an Exception if a match 
        """
        for (offset,l) in enumerate(subsetLines):
            for t in self.regex:
                m = t.Regex.search(l)
                if m != None:
                    truePosition = offset + offsetOfSubset
                    _logger.debug('Found match on line {}'.format(str(truePosition+ 1)))
                    _logger.debug('Line is {}'.format(l))
                    self.failed = True
                    self.matchLocation = CheckFileParser.FileLocation(fileName, truePosition +1)
                    raise DirectiveException(self)

    def __str__(self):
        s = self.getName() + ' Directive ('
        for (index,p) in enumerate(self.regex):
            s += "{file}:{line} : Pattern: '{pattern}'".format(file=p.SourceLocation.fileName, line=p.SourceLocation.lineNumber, pattern=p.Regex.pattern)

            if index < (len(self.regex) -1):
                # Comma for all but last in list
                s+= ', '

            s += ")"

        return s

    def getErrorMessage(self):
        return 'Found a match for ' + str(self) + ' in {location}'.format(location=str(self.matchLocation))

    @staticmethod
    def validate(directiveList):
        """
            We should enforce for every CHECK-NOT directive that the next directive (if it exists) is
            a CHECK directive
        """
        last = len(directiveList) -1
        for (index,directive) in enumerate(directiveList):
            if isinstance(directive, CheckNot):
                if index < last:
                    after = directiveList[index +1]
                    if not isinstance(after, Check):
                        raise CheckFileParser.ParsingException("{directive} must have a CHECK{check} directive after it instead of a {bad}".format(
                                                                directive=directive,
                                                                check=Check.directiveToken(),
                                                                bad=after)
                                                               )
