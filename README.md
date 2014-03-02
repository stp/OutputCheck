OutputCheck
===========

[![Build Status](https://travis-ci.org/delcypher/OutputCheck.png?branch=master)](https://travis-ci.org/delcypher/OutputCheck)

OutputCheck is a tool for checking the output of console programs
that is inspired by the FileCheck tool used by LLVM. It has its own
small language (Check Directives) for describing the expected output of 
a tool that is considerably more convenient and more powerful than GNU ``grep``.

This tool was originally written for [STP](http://github.com/stp/stp)
but it ended up being a very useful tool for other projects so it
became its own project!


Check Directives
================

Check Directives declare what output is expected from a tool. They are
written as single line comments in a file (this file is usually used
to by the tool being tested by OutputCheck).

The advantage of writing directives in this way is that the directives
can be written next to the code that generates the output that the directive
is checking for.

All directives use the regular expression syntax used by the ``re`` python
module. It is also important to note that the any spaces after the ``:``
until the first non-whitespace character are not considered part of the
regular expression.

The following directives are supported

CHECK: <regex>
--------------

This declares that that regular expression ``<regex>`` should match somewhere
on a single line. This match must occur after previously declared Check directives.

**Succesful example**

``HelloWorld.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Hello World
    printf("Hello World\n");

    // CHECK: Goodbye
    printf("Goodbye\n");
    
    return 0;
}
```

```
$ cc HelloWorld.c -o HelloWorld
$ ./HelloWorld | OutputCheck HelloWorld.c
```

This example shows a simple ``C`` program being compiled and its output being checked. There are two ``CHECK:`` declarations which effectively say...

1. At least one of the lines must match the regular expression ``Hello World``.
2. At least one line after the previous match must match regular expression ``Goodbye``.

It can be seen that the order the ``CHECK:`` directives are declared is important. If the directives were specified the other way round then the OutputCheck tool would report an error as shown below

**Failing example**

``BrokenHelloWorld.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Goodbye
    printf("Hello World\n");

    // CHECK: Hello World
    printf("Goodbye\n");
    
    return 0;
}
```

```
$ cc BrokenHelloWorld.c -o BrokenHelloWorld
$ ./BrokenHelloWorld | OutputCheck BrokenHelloWorld.c
ERROR: Could not find a match for Check Directive (BrokenHelloWorld.c:8 Pattern: 'Hello World')
```

CHECK-NEXT: <regex>
-------------------

This declares that the next line after the previous match must match the regular expression ``<regex>``. If there was no previous directive then ``CHECK-NEXT:`` matches the first line of the tool's output.

**Succesful example**

``HelloWorld2.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Hello World
    // CHECK-NEXT: Goodbye
    printf("Hello World\nGoodbye");

    return 0;
}
```

```
$ cc HelloWorld2.c -o HelloWorld2
$ ./HelloWorld2 | OutputCheck HelloWorld2.c
```

**Failing example**

``BrokenHelloWorld2.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Hello World
    
    printf("Hello World\n");
    printf("Testing...\n");
    
    // CHECK-NEXT: Goodbye
    printf("Goodbye\n");

    return 0;
}
```

```
$ cc BrokenHelloWorld2.c -o BrokenHelloWorld2
$ ./BrokenHelloWorld2 | OutputCheck BrokenHelloWorld2.c
ERROR: Could not find a match for CheckNext Directive (BrokenHelloWorld2.c:10 Pattern: 'Goodbye') expected at <stdin>:2
```

CHECK-NOT: <regex>
------------------

This declares that between the previous match (if there is none, search starts from the first line of tool's output) and the next match (if there is none the search will search to the end of the tool's output) that no line will match the regular expression ``<regex>``.

**Succesful example**

``HelloWorld3.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Hello World
    // CHECK-NOT: Testing
    // CHECK: Goodbye
    printf("Hello World\nGoodbye");

    return 0;
}
```

```
$ cc HelloWorld3.c -o HelloWorld3
$ ./HelloWorld3 | OutputCheck HelloWorld3.c
```

**Failing example**

``BrokenHelloWorld3.c``
```C
#include <stdio.h>

int main()
{
    // CHECK: Hello World
    printf("Hello World\n");
    
    // CHECK-NOT: Testing
    // CHECK: Goodbye
    printf("Testing...\n");
    printf("Goodbye\n");

    return 0;
}
```

```
$ cc BrokenHelloWorld3.c -o BrokenHelloWorld3
$ ./BrokenHelloWorld3 | OutputCheck BrokenHelloWorld3.c
```

Tests
=====

A small set of tests are present in the ``tests/`` directory. These tests are designed to be driven using ``llvm-lit`` from LLVM >=3.4 . These tests are not cross platform and will only work on systems with the ``sed`` and ``grep`` programs. It should be noted that the OutputCheck tool is implemented purely in python so the tool should work on platforms that support Python.
