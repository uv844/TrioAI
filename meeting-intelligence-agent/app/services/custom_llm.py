
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class CustomLLM:
    """Quasar Market GPT-5 Chat client."""

    def __init__(self):
        self.api_url = os.getenv("API_URL")
        self.api_key = os.getenv("API_KEY")
        self.model = os.getenv("MODEL_NAME")

        if not all([self.api_url, self.api_key, self.model]):
            raise RuntimeError(
                "Set API_URL, API_KEY and MODEL_NAME in .env"
            )

    def generate(self, question: str, context: str) -> str:
        prompt = (
            "You are a meeting assistant. Answer only from the "
            "meeting context. If the answer is not present, say "
            "that the transcript does not provide it. "
            "Cite the relevant speaker or timestamp when available.\n\n"
            f"MEETING CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 1000
        }

        response = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key
            },
            json=payload,
            timeout=60
        )

        if not response.ok:
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            raise RuntimeError(
                f"Quasar API Error {response.status_code}: {error_data}"
            )

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected LLM response format: {data}"
            ) from exc
