import json
import os
from typing import Optional

from openai import OpenAI


def extract_via_llm(text: str) -> Optional[dict]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        system_prompt = (
            "Extract structured carrier packet fields from the text. "
            "The title must be the primary entity the buyer tracks (legal carrier name, "
            "vendor name, contract party, patient name etc). Never use document type or category as title. "
            "Return a JSON object with top-level keys that are field names. "
            "Normalize dates to YYYY-MM-DD where possible. "
            "If a field is not present, omit it."
        )

        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text[:12000]},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        if not content:
            return None

        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines)

        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None
