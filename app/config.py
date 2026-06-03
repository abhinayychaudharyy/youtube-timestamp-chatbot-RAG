import os
from pathlib import Path


def load_dotenv(dotenv_path=".env"):
    path = Path(dotenv_path)
    if not path.is_file():
        return

    with path.open() as dotenv_file:
        for line in dotenv_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")