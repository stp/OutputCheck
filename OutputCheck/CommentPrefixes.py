"""
This module defines the mapping of file type to the symbol
used for one-line comments.
"""
import re

extensionToCommentSymbolMap = {
    'sh':'#',
    'cvc':'%',
    'c':'//',
    'cpp':'//',
    'cxx':'//',
    'py':'#',
    'smt':';',
    'smt2':';',
}

class FileWithoutSuffixException(Exception):
    pass

class UnSupportedFileTypeException(Exception):
    def  __init__(self, suffix):
        super(self.__class__,self).__init__()
        self.suffix = suffix
    
    def __str__(self):
        return 'The file extension "{ext}" is not supported.'.format(ext=self.suffix)

def getLineCommentPrefix(fileName):
    m = re.search(r'\.(.+)$',fileName)
    if not m:
        raise FileWithoutSuffixException()
    else:
        suffix = m.group(1)

    try:
        return extensionToCommentSymbolMap[suffix]
    except KeyError as e:
        raise UnSupportedFileTypeException(suffix)

