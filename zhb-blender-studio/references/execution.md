# Запуск помощников

Найди Blender в окружении пользователя; не предполагай определённую ОС или путь
установки. Путь скилла определяй по его собственной папке. Помощники используют
встроенный Python Blender (`bpy`) и стандартную библиотеку. Установка через pip не нужна.

Примеры фонового запуска. Подставь реальные пути и кавычки для используемой оболочки:

```text
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- report --json /path/to/report.json
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- prepare --width 1920 --height 1080 --fps 30 --save /path/to/prepared.blend
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- proxies --max-px 1024 --save /path/to/proxy-work.blend
blender --background proxy-work.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- restore-proxies --save /path/to/restored.blend
blender --background project.blend --python-exit-code 1 --python /path/to/zhb-blender-studio/scripts/studio.py -- collect --output /path/to/new-delivery --extra box3d_cache
```

Команды выводят маркер `STUDIO_JSON ` и JSON после него. Параметр `--json`
команды `report` дополнительно записывает новый файл отчёта и не перезаписывает
существующий. Команды изменения сохраняют только в новый путь `--save`;
исходник и существующие файлы отклоняются. Родительская папка должна существовать.
Команда `collect` создаёт свою новую папку результата.

Запуск в открытой сессии через доступный инструмент выполнения Python в Blender:

```python
import sys
sys.path.insert(0, "/path/to/zhb-blender-studio/scripts")
import studio
print(studio.report())
```

Функции `report`, `prepare`, `make_proxies`, `restore_proxies` можно импортировать.
Функции изменения работают с данными в памяти; сохранением управляет вызывающая
сторона. Не запускай сборку в пользовательском интерфейсе Blender: она требует
фонового процесса.

`--factory-startup` используй только для независимых тестов на пустых проектах.
Рабочей сцене может быть нужен существующий профиль для геометрических нод
и симуляций. `--python-exit-code 1` позволяет отразить исключение кодом ошибки процесса.

Не составляй текст команды из недоверенных имён. Передавай аргументы списком
в API запуска процессов. Справка `--help` должна идти после разделителя Blender `--`.
Имена команд, ключи JSON и идентификаторы API сохранены для совместимости;
текстовые сообщения помощника переведены на русский.
