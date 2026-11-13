# Bugulmekas · неоновый профиль

Profile README без внешних карточных сервисов: все панели — свои SVG-файлы
в `assets/`, они генерируются скриптом из GitHub API и обновляются Actions.

## 1. Структура

```
Bugulmekas/
├─ README.md                     # профиль (ссылается на assets/*.svg)
├─ assets/
│  ├─ header.svg                 # шапка: HUD-рамка, неон, бегущая строка
│  ├─ divider.svg                # разделитель
│  ├─ stack.svg                  # пилюли со стеком
│  ├─ stats.svg                  # репозитории / коммиты / звёзды / подписчики
│  ├─ langs.svg                  # языки по объёму кода
│  ├─ activity.svg               # heatmap активности за год
│  ├─ project-*.svg              # карточки проектов
│  └─ footer.svg                 # подвал
├─ .github/
│  ├─ scripts/cards.py           # генератор всех SVG
│  └─ workflows/
│     ├─ cards.yml               # обновляет assets раз в сутки
│     └─ snake.yml               # змейка из вкладов
└─ SETUP.md
```

## 2. Палитра

| Роль | Цвет |
| --- | --- |
| фон | `#0D1117` (совпадает с тёмной темой GitHub) |
| панель | `#0B1120` / `#0E1626` |
| рамка | `#1C2B45` |
| неон-голубой | `#00F5FF` |
| неон-фиолетовый | `#7A5CFF` |
| неон-розовый | `#FF2BD6` |
| текст | `#E7F2FF` |

Шрифт — моноширинный стек `Cascadia Code → JetBrains Mono → Consolas`.
Никаких внешних шрифтов: GitHub не подгружает их в `<img>`, поэтому стек
состоит только из системных.

## 3. Как обновляются данные

Workflow `cards` раз в сутки (04:00 UTC) запускает `cards.py`, тот пересобирает
SVG и коммитит их в `assets/`. Вручную: **Actions → cards → Run workflow**.

Локально:

```powershell
$env:GITHUB_TOKEN = (gh auth token)
py -3 .github\scripts\cards.py
```

Без `GITHUB_TOKEN` скрипт соберёт всё, кроме коммитов и heatmap (GraphQL).

## 4. Что менять

| Хочу | Где |
| --- | --- |
| Проекты (название, описание, акцент) | `PROJECTS` в `cards.py` |
| Плитки стека | `STACK` в `cards.py` |
| Цвета | константы `CYAN / VIOLET / MAGENTA / BG / PANEL / BORDER` |
| Подписи секций | `README.md`, заголовки `<samp>❯ 0X · ...</samp>` |
| Контакты | нижний блок README (бейджи shields.io) |
| Цитата | `<i>` в конце README |

После правки `cards.py` закоммитьте — workflow пересоберёт картинки сам
(в `cards.yml` указан триггер по изменению скрипта).

## 5. Важно

- Тема GitHub: **Settings → Appearance → Dark** — карточки рассчитаны на `#0D1117`.
- GitHub кэширует картинки через camo, поэтому свежие цифры могут появиться
  с задержкой до нескольких часов. Ссылки не ломаются.
- Если карточка не обновилась после пуша — Actions → cards → Run workflow,
  затем Ctrl+F5 на странице профиля.
- Змейка живёт в ветке `output`, картинки уже прописаны в README.

## 6. Полезное

- [Platane/snk](https://github.com/Platane/snk) — змейка
- [GitHub GraphQL API](https://docs.github.com/en/graphql) — календарь вкладов
- [shields.io](https://shields.io) — бейджи в блоке контактов
