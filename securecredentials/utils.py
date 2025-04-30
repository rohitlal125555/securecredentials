import sys
import ctypes


class ANSITerminal:
    """
    A class to handle ANSI escape sequences for colored terminal output.
    """

    # Foreground colors
    FG_CODES = {
        "red": 31,
        "yellow": 33,
        "green": 32,
        "aqua": 36,
    }

    # Additional text styles
    STYLE_CODES = {
        "bold": 1,
        "underline": 4,
    }

    RESET_CODE = 0

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
    def is_interactive_terminal(cls):
        """Return True if stdout is an interactive terminal (not a file or redirected)."""
        return sys.stdout.isatty()

    @classmethod
    def decorate(cls, text: str, color: str = None, style: str = None) -> str:
        """
        Wrap text with ANSI codes.
        :param text: Text for ANSI formatting
        :param color: one of FG_COLORS keys
        :param style: one of STYLES keys
        """
        if not cls.is_interactive_terminal():
            # If not an interactive terminal, return the text without ANSI codes
            print('Not interactive terminal')
            return text
        else:
            cls._enable_ansi_support()

            ansi_formatting = []
            if style and style.lower() in cls.STYLE_CODES:
                ansi_formatting.append(str(cls.STYLE_CODES[style.lower()]))
            if color and color.lower() in cls.FG_CODES:
                ansi_formatting.append(str(cls.FG_CODES[color.lower()]))

            if ansi_formatting:
                start = f"\033[{';'.join(ansi_formatting)}m"
                end = f"\033[{cls.RESET_CODE}m"
                return f"{start}{text}{end}"
            else:
                return text
