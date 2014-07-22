import sys


def has_colors(stream):
    """
    Determine if the terminal supports ansi colors.
    """
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        return False

has_colors = has_colors(sys.stdout)

# BEGIN PRETTY
# pretty - A miniature library that provides a Python print and stdout
# wrapper that makes colored terminal text easier to use (eg. without
# having to mess around with ANSI escape sequences). This code is public
# domain - there is no license except that you must leave this header.
#
# Copyright (C) 2008 Brian Nez <thedude at bri1 dot com>
#
# http://nezzen.net/2008/06/23/colored-text-in-python-using-ansi-escape-sequences/

codeCodes = {
    'black': '0;30', 'bright gray': '0;37',
    'blue': '0;34', 'white': '1;37',
    'green': '0;32', 'bright blue': '1;34',
    'cyan': '0;36', 'bright green': '1;32',
    'red': '0;31', 'bright cyan': '1;36',
    'purple': '0;35', 'bright red': '1;31',
    'yellow': '0;33', 'bright purple': '1;35',
    'dark gray': '1;30', 'bright yellow': '1;33',
    # EDITING PRETTY TO SUPPORT BRIGHT WHITE
    'normal': '0', 'bright normal': '1'
    # END EDITING PRETTY
}


def stringc(text, color):
    """
    Return a string with terminal colors.
    """
    if has_colors:
        text = str(text)

        return "\033["+codeCodes[color]+"m"+text+"\033[0m"
    else:
        return text
# END PRETTY
