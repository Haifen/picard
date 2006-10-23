# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""Tagger script parser and evaluator."""

import re
try:
    from re import Scanner
except ImportError:
    from sre import Scanner
from picard.component import Component, ExtensionPoint, Interface, implements
from picard.api import ITaggerScript


_re_text = r"(?:\\.|[^%$])+"
_re_text2 = r"(?:\\.|[^%$,])+"
_re_args_sep = ","
_re_name = "\w+"
_re_var = r"%" + _re_name + r"%"
_re_func_args = no_parens = r"(?:\\(|\\)|[^()])*"
for i in range(10): # 10 levels must be enough for everybody ;)
   _re_func_args = r"(\(" + _re_func_args + r"\)|" + no_parens + r")*"
_re_func = r"\$" + _re_name + r"\(" + _re_func_args + r"\)"


def func_if(context, *args):
    """If ``if`` is not empty, it returns ``then``, otherwise it returns
       ``else``."""
    if args[0]:
        return args[1]
    if len(args) == 3:
        return args[2]
    return ''

def func_if2(context, *args):
    """Returns first non empty argument."""
    for arg in args:
        if arg:
            return arg
    return args[-1]

def func_noop(context, *args):
    """Does nothing :)"""
    return "".join(args)

def func_left(context, text, length):
    """Returns first ``num`` characters from ``text``."""
    return text[:int(length)]

def func_right(context, text, length):
    """Returns last ``num`` characters from ``text``."""
    return text[-int(length):]

def func_lower(context, text):
    """Returns ``text`` in lower case."""
    return text.lower()

def func_upper(context, text):
    """Returns ``text`` in upper case."""
    return text.upper()

def func_pad(context, text, length, char):
    return char * (int(length) - len(text)) + text

def func_strip(context, text):
    return re.sub("\s+", " ", text).strip()

def func_replace(context, text, old, new):
    return text.replace(old, new)

def func_rreplace(context, text, old, new):
    return re.sub(old, new, text)

def func_rsearch(context, text, pattern):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return u""

def func_num(context, text, length):
    format = "%%0%dd" % int(length)
    return format % int(text)

def func_set(context, name, value):
    """Sets the variable ``name`` to ``value``."""
    context[name] = value
    return ""

def func_get(context, name):
    """Returns the variable ``name`` (equivalent to ``%name%``)."""
    return context.get(name, "")

def func_trim(context, text, char=None):
    """Trims all leading and trailing whitespaces from ``text``. The optional
       second parameter specifies the character to trim."""
    if char:
        return text.strip(char)
    else:
        return text.strip()

def func_add(context, x, y):
    """Add ``y`` to ``x``."""
    return str(int(x) + int(y))

def func_sub(context, x, y):
    """Substracts ``y`` from ``x``."""
    return str(int(x) - int(y))

def func_div(context, x, y):
    """Divides ``x`` by ``y``."""
    return str(int(x) / int(y))

def func_mod(context, x, y):
    """Returns the remainder of ``x`` divided by ``y``."""
    return str(int(x) % int(y))

def func_mul(context, x, y):
    """Multiplies ``x`` by ``y``."""
    return str(int(x) * int(y))

def func_or(context, x, y):
    """Returns true, if either ``x`` or ``y`` not empty."""
    if x or y:
        return "1"
    else:
        return ""

def func_and(context, x, y):
    """Returns true, if both ``x`` and ``y`` are not empty."""
    if x and y:
        return "1"
    else:
        return ""

def func_not(context, x):
    """Returns true, if ``x`` is empty."""
    if not x:
        return "1"
    else:
        return ""

def func_eq(context, x, y):
    """Returns true, if ``x`` equals ``y``."""
    if x == y:
        return "1"
    else:
        return ""

def func_ne(context, x, y):
    """Returns true, if ``x`` not equals ``y``."""
    if x != y:
        return "1"
    else:
        return ""

def func_lt(context, x, y):
    """Returns true, if ``x`` is lower than ``y``."""
    if x < y:
        return "1"
    else:
        return ""

def func_lte(context, x, y):
    """Returns true, if ``x`` is lower than or equals ``y``."""
    if x <= y:
        return "1"
    else:
        return ""

def func_gt(context, x, y):
    """Returns true, if ``x`` is greater than ``y``."""
    if x > y:
        return "1"
    else:
        return ""

def func_gte(context, x, y):
    """Returns true, if ``x`` is greater than or equals ``y``."""
    if x >= y:
        return "1"
    else:
        return ""

class TagzError(Exception):
    pass


class TagzParseError(TagzError):
    pass


class TagzUnknownFunction(TagzError):
    pass


class ITagzFunctionProvider(Interface):
    pass


class TagzBuiltins(Component):

    implements(ITagzFunctionProvider)

    _functions = {
        "noop": func_noop,
        "if": func_if,
        "if2": func_if2,
        "eq": func_eq,
        "ne": func_ne,
        "lt": func_lt,
        "lte": func_lte,
        "gt": func_gt,
        "gte": func_gte,

        "left": func_left,
        "right": func_right,
        "lower": func_lower,
        "upper": func_upper,
        "pad": func_pad,
        "strip": func_strip,
        "replace": func_replace,
        "rreplace": func_rreplace,
        "rsearch": func_rsearch,
        "num": func_num,

        "set": func_set,
        "get": func_get,

        "add": func_add,
        "sub": func_sub,
        "div": func_div,
        "mod": func_mod,
        "mul": func_mul,

        "or": func_or,
        "and": func_and,
        "not": func_not,
    }

    def get_functions(self):
        return self._functions


class TagzParser(object):
    """Tagger script implementation similar to Foobar2000's titleformat."""

    def __init__(self, context, functions):
        self.context = context
        self.functions = functions

    def evaluate(self, text):
        """Parse and evaluate the script from ``text``."""
        scanner = Scanner([(_re_text, self.s_text),
                           (_re_var, self.s_variable),
                           (_re_func, self.s_func)])
        res = scanner.scan(text)
        if res[1]:
            raise TagzParseError()
        return "".join(res[0])

    def s_text(self, scanner, string):
        string = string.replace("\\(", "(")
        string = string.replace("\\)", ")")
        string = string.replace("\\\\", "\\")
        return string

    def s_variable(self, scanner, string):
        try:
            return self.context[string[1:-1].lower()]
        except KeyError:
            return ""

    def s_args_sep(self, scanner, string):
        return "\0"

    def s_func(self, scanner, string):
        args_begin = string.find("(")
        name = string[1:args_begin]
        args = string[args_begin+1:-1]

        scanner = Scanner([(_re_args_sep, self.s_args_sep),
                           (_re_text2, self.s_text),
                           (_re_var, self.s_variable),
                           (_re_func, self.s_func)])
        results, error = scanner.scan(args)
        if error:
            raise TagzParseError(string.rfind(error))

        args = []
        if results:
            if results[0] == "\0":
                results.insert(0, "")
            if results[-1] == "\0":
                results.append("")
        while results:
            j = 1
            for res in results:
                if res == "\0":
                    break
                j += 1
            args.append("".join(results[:j-1]))
            results = results[j:]

        try:
            return self.functions[name](self.context, *args)
        except KeyError:
            raise TagzUnknownFunction, "Unknown function $%s" % name


class Tagz(Component):

    implements(ITaggerScript)

    function_providers = ExtensionPoint(ITagzFunctionProvider)

    def __init__(self):
        self.functions = {}
        for prov in self.function_providers:
            self.functions.update(prov.get_functions())

    def evaluate_script(self, text, context={}):
        """Parse and evaluate the script from ``text``."""
        parser = TagzParser(context, self.functions)
        return parser.evaluate(text)


