from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.ingestion import load_knowledge_base
from src.knowledge_base import parse_knowledge_base
from src.llm_integration import LLMRequestError, OpenAITextGenerator
from src.prompt_engineering import PromptInputBundle, assemble_prompt


class _FakeResponsesAPI:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[dict] = []

    def create(self, **kwargs):  # noqa: ANN001
        self.calls.append(kwargs)
        return self.response


class _FakeOpenAIClient:
    def __init__(self, response: object) -> None:
        self.responses = _FakeResponsesAPI(response)


class _FakeResponse:
    def __init__(self, output_text: str, response_id: str = "resp_test") -> None:
        self.output_text = output_text
        self.id = response_id


class LLMIntegrationTests(unittest.TestCase):
    def test_generate_uses_prompt_assembly_and_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "primary").mkdir()
            (root / "secondary").mkdir()
            (root / "primary" / "manifesto.md").write_text("Brand manifesto", encoding="utf-8")

            parsed = parse_knowledge_base(load_knowledge_base(root))
            assembly = assemble_prompt(
                parsed,
                PromptInputBundle(tone="warm"),
                "launch_copy",
            )

            fake_client = _FakeOpenAIClient(_FakeResponse("Generated launch copy"))
            generator = OpenAITextGenerator(client=fake_client, model="gpt-test")

            result = generator.generate(assembly)

            self.assertEqual(result.model, "gpt-test")
            self.assertEqual(result.text, "Generated launch copy")
            self.assertEqual(result.response_id, "resp_test")
            self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-test")
            self.assertEqual(fake_client.responses.calls[0]["input"], assembly.prompt_text)

    def test_generate_allows_model_override(self) -> None:
        fake_client = _FakeOpenAIClient(_FakeResponse("Generated text"))
        generator = OpenAITextGenerator(client=fake_client, model="gpt-default")

        assembly = type(
            "Assembly",
            (),
            {"prompt_text": "Prompt text"},
        )()

        result = generator.generate(assembly, model="gpt-override")

        self.assertEqual(result.model, "gpt-override")
        self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-override")

    def test_generate_rejects_empty_prompt_text(self) -> None:
        fake_client = _FakeOpenAIClient(_FakeResponse("Generated text"))
        generator = OpenAITextGenerator(client=fake_client)
        assembly = type(
            "Assembly",
            (),
            {"prompt_text": "   "},
        )()

        with self.assertRaises(LLMRequestError):
            generator.generate(assembly)


if __name__ == "__main__":
    unittest.main()
