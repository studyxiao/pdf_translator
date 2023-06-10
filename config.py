import os

import dotenv

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THREAD_NUM = os.getenv("THREAD_NUM", 10)
PROXY = os.getenv("PROXY", None)
PDF_PATH = os.getenv("PDF_PATH", None)
