## Краулер для веб-страниц

Данный скрипт помогает обойти сайт и сохранить список ссылок в текстовый файл.

Для разворачивания проекта нужен Python3.9 и Poetry.

```bash
pip install poetry
poetry install
poetry run crawler.py --target-url=https://example.com
```