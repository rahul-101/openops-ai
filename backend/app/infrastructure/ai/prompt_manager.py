from pathlib import Path


class PromptManager:
    """
    Loads and renders AI prompt templates.
    """

    def __init__(self):
        self.prompt_directory = (
            Path(__file__).parent / "prompts"
        )

    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt from the prompts directory.
        """

        prompt_path = self.prompt_directory / f"{prompt_name}.md"

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt '{prompt_name}' not found."
            )

        return prompt_path.read_text(encoding="utf-8")

    def render_prompt(
        self,
        prompt_name: str,
        **kwargs,
    ) -> str:
        """
        Render a prompt using keyword arguments.
        """

        template = self.load_prompt(prompt_name)

        return template.format(**kwargs)