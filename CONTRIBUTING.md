# Проверки и вклад

Новые сценарии начинаются с воспроизводимого кейса. Не добавляйте в общий
скилл личные пути, клиентские сцены, обязательный лук и частные правила проекта.
Используйте `zhb-blender-studio/references/cases.md`.

Проверка структуры, Python-синтаксиса и локальных ссылок (обычный Python 3.12+):

```text
python tools/check_package.py
python tools/package.py
```

Интеграционные проверки запускать на пустом изолированном профиле Blender.
Переменные `BLENDER_USER_CONFIG`, `BLENDER_USER_SCRIPTS`,
`BLENDER_USER_EXTENSIONS` должны указывать на отдельные тестовые каталоги.
Тест создаёт временные данные и не открывает производственные сцены.

```text
blender --background --factory-startup --python-exit-code 1 --python tests/test_blender.py
```

Для проверки ZIP извлеките его в новый каталог и запустите тот же тест,
указав `STUDIO_HELPER_PATH` на извлечённый `scripts/studio.py`.
Структурный CI не заменяет запуск Blender и визуальные проверки.

Постер: `python tools/build_poster.py` (нужен Pillow и установленный шрифт с
кириллицей; `--font` и `--bold-font` задают пути). SVG и PNG строятся из одного
макета. Самому скиллу Pillow не нужен. Шрифты в репозиторий не включены.
