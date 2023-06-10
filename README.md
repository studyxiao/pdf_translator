## PDF 文献翻译

本项目通过提取 PDF 文件中的文本，使用 OpenAI 进行翻译，并将翻译结果写入 txt 文件中。

- 标准pdf文件，不可以是扫描文件（图片）
- `gpt-3.5-turbo` model
- 通过 prompt 指定学术领域，实现更精准翻译。

## 基于 pypdf 提取 pdf 内容

- PdfReader
  - `pdf_header` 读取 PDF 文件的头部信息
  - `metadata` 读取 PDF 文件的元数据：Author Title Creator Producer CreationDate ModDate
  - `pages` 读取 PDF 文件的页数`len(pages)`
  - `pages[page_number]` 读取 PDF 文件的第几页
  - `page_layout` 读取 PDF 文件的页面布局, 例如：`/SinglePage` `/OneColumn` `/TwoColumnLeft` `/TwoColumnRight` `/TwoPageLeft` `/TwoPageRight`
  - `outline` 读取 PDF 文件的大纲
  - `trailer` 读取 PDF 文件的尾部信息
  - `attachments` 读取 PDF 文件的附件
- Page
  - `page_number` 页码
  - `images` 页中的图片，需要安装 Pillow
  - `rotation` 页的旋转角度
  - `rotate(angle)` 旋转页
  - `get_contents()` 读取页的内容
  - `extract_text()` 提取页的文本
- PdfWriter
  - `add_metadata(metadata: dict)` 添加元数据
  - `add_page(page)` 添加页
  - `write(output_file)` 写入文件

## OpenAI

基于特定 prompt 进行翻译，例如：

```python
messages = [
    {
        "role": "system",
        "content": "你是专业的翻译人员，并精通航空领域研究。",
    },
    {
        "role": "user",
        "content": f"按照学术文献格式，将以下文本翻译成中文，尽可能符合中文语法规则，并保留原文格式。只需返回翻译结果，不要包含其它内容：\n```{text}```",
    },
]
```

## 使用

复制 `.env.example` 为 `.env`，并修改其中的配置。

```sh
cp .env.example .env
```

安装依赖：

```sh
pip install -r requirements.txt
# or
pdm install
```

运行：

```sh
pdm run python main.py

# 修改 main.py 中main函数的参数，可以指定翻译的页码范围
```

测试每页大约需要 10 秒。

如果需要使用代理需配置 `.env` 文件中的 `PROXY`。

## TODO

- [ ] 支持 cli 参数
- [ ] 支持历史记录

## 更完善的项目或工具

- https://github.com/Raychanan/ChatGPT-for-Translation 基于机器学习的pdf内容提取和翻译
- https://github.com/immersive-translate/immersive-translate 网页翻译（支持pdf）的浏览器插件
