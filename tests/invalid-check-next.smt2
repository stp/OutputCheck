; RUN: sed 's/^;[ ]*CHECK.\+$//g' %s | not %OutputCheck %s 2> %t
; RUN: grep 'ParsingException: CheckNot Directive' %t
; RUN: grep 'must have a CHECK: directive after it instead of a CheckNext Directive' %t
; CHECK-NOT: foo
; CHECK-NEXT: bar
humdrum
bar
