import re
from pygments import highlight
from pygments.lexers import PythonLexer, CSharpLexer, JavaLexer, GDScriptLexer, JsonLexer, CssLexer, XmlLexer
from pygments.formatters import TerminalFormatter
from colorama import Fore

class SyntaxHighlighter:
    """A class to handle syntax highlighting for various programming languages."""

    # Mapping of language names to their respective Pygments lexers
    LANGUAGE_LEXER_MAP = {
        'python': PythonLexer,
        'csharp': CSharpLexer,
        'java': JavaLexer,
        'gdscript': GDScriptLexer,
        'json': JsonLexer,
        'css': CssLexer,
        'xml': XmlLexer,
    }

    def __init__(self):
        pass

    def highlight_code(self, text: str) -> str:
        # Regex to find code blocks with specified language
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', text, re.DOTALL)
        for lang, code in code_blocks:
            lexer = self.LANGUAGE_LEXER_MAP.get(lang.lower(), PythonLexer) if lang else PythonLexer  # Default to PythonLexer
            # Highlight the code using Pygments
            highlighted_code = highlight(code.strip(), lexer(), TerminalFormatter())
            text = text.replace(f'```{lang if lang else ""}\n{code}```', f'\n{Fore.CYAN}{highlighted_code}{Fore.RESET}\n')
        return text
