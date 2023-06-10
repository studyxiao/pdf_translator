import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import openai
from pypdf import PdfReader
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from config import OPENAI_API_KEY, PDF_PATH, PROXY, THREAD_NUM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def translate(text: str):
    if text.strip() == "":
        return ""
    openai.api_key = OPENAI_API_KEY
    if PROXY:
        openai.proxy = PROXY

    messages = [
        {
            "role": "system",
            "content": "你是专业的翻译人员。",
        },
        {
            "role": "user",
            "content": f"""将以下文本按照物流配送领域翻译成中文，尽可能符合正式语气，并保留原文格式，\
            结果仅返回翻译内容，不包括其它内容：
            {text}""",
        },
    ]
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        t_text = completion["choices"][0].get("message").get("content").encode("utf8").decode()  # type: ignore
        return t_text
    except Exception as e:
        logging.warning(f"Translate error: {e}，retrying...")
        raise


def extract_pdf_text_to_paragraph(
    pdf_path,
    start_page: int = 0,
    end_page: int = -1,
) -> list[str]:
    """提取 pdf 文本到段落"""
    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")
    pdf = PdfReader(pdf_path)
    all_pages = ""
    start_page = start_page if start_page >= 0 else 0
    if end_page < 0 or end_page > len(pdf.pages):
        end_page = len(pdf.pages)
    for page in pdf.pages[start_page:end_page]:
        page_text = page.extract_text()
        # 剔除页码，每页文本最后可能是如 "\n1" 的页码
        regex = r"\n\d+$"
        page_text = re.sub(regex, "\n", page_text)
        all_pages += page_text
    # 整合段落，将形如 "a\nb" 合并为 "ab"
    regex = r"[a-zA-Z\-\,)]\n[a-z\(]"
    paragraphs = re.sub(regex, lambda match: match.group().replace("\n", " "), all_pages).split("\n")
    return paragraphs


def main(pdf_path: Path, start_page: int = 0, end_page: int = -1) -> list[str]:
    paragraphs = extract_pdf_text_to_paragraph(pdf_path, start_page, end_page)
    logging.info(f"Paragraphs length: {len(paragraphs)}")
    tasks = []
    translated_paragraphs = [""] * len(paragraphs)
    with ThreadPoolExecutor(max_workers=int(THREAD_NUM)) as executor:
        for index, paragraph in enumerate(paragraphs):
            future = executor.submit(translate, paragraph)
            tasks.append((index, future))
        for future in as_completed((task[1] for task in tasks)):
            for index, task in tasks:
                if task == future:
                    try:
                        result = future.result()
                        translated_paragraphs[index] = result
                    except Exception as exc:
                        logging.error(f"{future} generated an exception: {exc}")
    return translated_paragraphs


def write_to_txt(text: list[str], writer: Path):
    if not writer.parent.exists():
        writer.parent.mkdir(parents=True)
    writer.write_text("\n".join(text), encoding="utf-8")


if __name__ == "__main__":
    # 判断并读取 PDF_PATH
    if not PDF_PATH:
        raise ValueError("PDF_PATH is not set")
    pdf_path = Path(PDF_PATH)
    if pdf_path.suffix != ".pdf" or not pdf_path.exists():
        raise ValueError(f"PDF_PATH is not a pdf file: {pdf_path}")

    start = time.perf_counter()

    # 可以指定页码，比如第1-2页，不指定默认全部
    result = main(pdf_path, 0, 2)
    # result = main(pdf_path)

    end = time.perf_counter()
    logging.info(f"Time elapsed: {(end - start):.2f} seconds")

    # 写入 txt
    write_to_txt(result, Path("./result/a.txt"))
