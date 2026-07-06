from pathlib import Path

from manim import Scene, Text, Write, config


class Hello(Scene):
    def construct(self):
        self.play(Write(Text("Hello, Manim!")))


if __name__ == "__main__":
    # Dump output into the repo-level media/ folder, regardless of where this is run from.
    config.media_dir = str(Path(__file__).resolve().parent.parent / "media")
    config.quality = "high_quality"  # low_quality | medium_quality | high_quality
    Hello().render()
