import itertools
from typing import Iterator, List


class SpinnerAnimation:
    """Animated spinner with multiple styles."""

    STYLES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "line": ["-", "\\", "|", "/"],
        "dots_bounce": ["⠁", "⠂", "⠄", "⠂"],
        "box": ["◰", "◳", "◲", "◱"],
        "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
        "circle": ["◴", "◷", "◶", "◵"],
        "earth": ["🌍", "🌎", "🌏"],
        "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    }

    def __init__(self, style: str = "dots"):
        if style not in self.STYLES:
            style = "dots"
        self.frames = self.STYLES[style]
        self.cycle = itertools.cycle(self.frames)

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        return next(self.cycle)


class ASCIIAnimation:
    """ASCII art animations for different modules."""

    DOCKER_WHALE = [
        """
          ##         .
    ## ## ##        ==
 ## ## ## ## ##    ===
        """,
        """
          ##         .
    ## ## ##        ==
 ## ## ## ## ##    ===
   ~~~~    ~~~~
        """,
        """
          ##         .
    ## ## ##        ==
 ## ## ## ## ##    ===
   ~~~~    ~~~~
  ~~~~~~~~~~~~~~
        """,
    ]

    PYTHON_SNAKE = [
        "🐍         ",
        " 🐍        ",
        "  🐍       ",
        "   🐍      ",
        "    🐍     ",
    ]

    @classmethod
    def get_animation(cls, module: str) -> List[str]:
        """Get animation frames for module."""
        animations = {
            "docker": cls.DOCKER_WHALE,
            "python": cls.PYTHON_SNAKE,
        }
        return animations.get(module, ["⏳"])
