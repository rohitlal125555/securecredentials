import sys
import ctypes


class ANSITerminal:
    """
    A class to handle ANSI escape sequences for colored terminal output.
    """

    # Foreground colors
    _fg_codes = {
        "red": 31,
        "yellow": 33,
        "green": 32,
        "aqua": 36,
    }

    # Additional text styles
    _style_codes = {
        "bold": 1,
        "underline": 4,
    }

    _reset_code = 0

    @classmethod
    def _enable_ansi_support(cls):
        """Enable ANSI escape sequence processing on Windows 10+."""
        if sys.platform == "win32":
            try:
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(handle, mode)
            except (AttributeError, OSError, ctypes.ArgumentError):
                pass
            except Exception as e:
                # Handle any other exceptions that may occur
                print(f"[ANSITerminal] unexpected error enabling ANSI support: {e!r}", file=sys.stderr)

    @classmethod
    def _is_interactive_terminal(cls):
        """Return True if stdout is an interactive terminal (not a file or redirected)."""
        return sys.stdout.isatty()

    @classmethod
    def decorate(cls, text: str, color: str = None, style: str = None) -> str:
        """
        Decorate the given text with ANSI escape sequences for color and style.

        :param text: text for ANSI formatting
        :param color: fg codes for formatting
        :param style: style codes for formatting
        :return: ANSI formatted text if in an interactive terminal, else the original text
        """
        if not cls._is_interactive_terminal():
            # If not an interactive terminal, return the text without ANSI codes
            print('Not interactive terminal')
            return text
        else:
            cls._enable_ansi_support()

            ansi_formatting = []
            if style and style.lower() in cls._style_codes:
                ansi_formatting.append(str(cls._style_codes[style.lower()]))
            if color and color.lower() in cls._fg_codes:
                ansi_formatting.append(str(cls._fg_codes[color.lower()]))

            if ansi_formatting:
                start = f"\033[{';'.join(ansi_formatting)}m"
                end = f"\033[{cls._reset_code}m"
                return f"{start}{text}{end}"
            else:
                return text