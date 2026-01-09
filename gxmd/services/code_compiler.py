from typing import Callable

from selectolax.parser import HTMLParser


class CodeCompiler:
    @classmethod
    def compile_code(cls, code: str, purpose="manga_info") -> Callable:
        # Safely compile and return callable
        func = compile(code, '<scraper>', 'exec')

        # Use a clean dict for globals to prevent cross-contamination
        # and module pollution.
        isolated_globals = {
            "__builtins__": __builtins__,
        }
        local_ns = {
            "node": HTMLParser
        }

        exec(func, isolated_globals, local_ns)
        function_name = f"parse_{purpose}"
        scraper_func = local_ns.get(function_name)

        return scraper_func