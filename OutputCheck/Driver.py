#!/usr/bin/env python
# vim: set sw=2 ts=4 softabstop=4 expandtab
"""
Output checker inspired by LLVM's FileCheck
"""
import os
import argparse
import re
import logging
import CheckFileParser
import FileChecker
import Directives
import CommentPrefixes

_logger = logging.getLogger(__name__)


def main(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check_file', type=argparse.FileType('r'), help='File containing check commands')
    parser.add_argument('-file-to-check=', type=argparse.FileType('r'), default='-', help='File to check (default %(default)s)')
    parser.add_argument('-check-prefix=', default='CHECK', help='Prefix to use from check_file')
    parser.add_argument("-l","--log-level",type=str, default="INFO", choices=['debug','info','warning','error'])
    parser.add_argument('--comment=',type=str, default="", help='Force one line comment value. Default guess from file extension of check_file')
    args = parser.parse_args(args[1:])

    logging.basicConfig(level=getattr(logging,args.log_level.upper(),None), 
                        format='%(levelname)s:%(module)s.%(funcName)s() : %(message)s')


    checkFile = args.check_file
    fileToCheck = getattr(args,'file_to_check=')
    checkDirectivePrefix = getattr(args,'check_prefix=')
    requestedLineCommentPrefix = getattr(args,'comment=')
    lineCommentPrefix = None

    try:
        if len(requestedLineCommentPrefix) == 0:
            lineCommentPrefix = CommentPrefixes.getLineCommentPrefix(checkFile.name)
        else:
            lineCommentPrefix = requestedLineCommentPrefix
            _logger.info('Assuming single line comment prefix is {prefix}'.format(prefix=lineCommentPrefix))

        _logger.debug("Line comment prefix is '{}'".format(lineCommentPrefix))
        checkFileParser = CheckFileParser.CheckFileParser(checkDirectivePrefix, lineCommentPrefix)
        FC = FileChecker.FileChecker(checkFileParser.parse(checkFile))
        FC.check(fileToCheck)
    except CheckFileParser.ParsingException as e:
        _logger.error(e)
        return 1
    except Directives.DirectiveException as e:
        _logger.error(e)
        return 1
    except CommentPrefixes.FileWithoutPrefixException as e:
        _logger.error("Check file '{file}' is missing a file extension".format(file=checkFile.name))
        _logger.info('If you know what symbols are used for one line comments then use the --comment= flag')
        return 1
    except CommentPrefixes.UnSupportedFileTypeException as e:
        _logger.error(e)
        _logger.info('If you know what symbols are used for one line comments then use the --comment= flag')
        return 1
    except KeyboardInterrupt as e:
        return 1

    return 0
