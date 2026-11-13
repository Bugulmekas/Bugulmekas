# Профиль Bugulmek (github.com/Bugulmekas) — как опубликовать

Готовый Profile README в неоновом стиле: тёмный фон `#0D1117`, акценты
голубой `#00F5FF`, фиолетовый `#7A00FF`, розовый `#FF00E4`.

## 1. Что внутри

```
Bugulmekas/
├─ README.md                      # сам профиль
├─ SETUP.md                       # эта инструкция
└─ .github/workflows/snake.yml    # генератор «змейки» из вкладов
```

## 2. Публикация (имя репозитория = имя аккаунта)

GitHub показывает README на странице профиля только если репозиторий называется
точно так же, как логин аккаунта — то есть `Bugulmekas`, и README лежит в корне.

### Вариант А — через сайт (проще)

1. Создайте **публичный** репозиторий `Bugulmekas` без README и лицензии.
2. Add file → Upload files → перетащите `README.md` и папку `.github`
   (путь `.github/workflows/snake.yml` должен сохраниться).
3. Commit changes — профиль https://github.com/Bugulmekas обновится через минуту.

### Вариант Б — через git

```bash
cd F:\Bugulmekas
git init -b main
git add .
git commit -m "chore: neon profile readme"
git remote add origin https://github.com/Bugulmekas/Bugulmekas.git
git push -u origin main
```

## 3. Змейка

1. После пуша: **Actions → snake → Run workflow**.
2. Через минуту появится ветка `output` с SVG-файлами.
3. В README картинка уже подключена, отображаться начнёт автоматически.
4. Дальше обновляется сама каждый день в 03:00 UTC.

Пока workflow не запущен, на месте змейки будет пусто/битая картинка — это нормально.

## 4. Чек-лист после публикации

- [ ] Репозиторий называется `Bugulmekas` и он публичный.
- [ ] У репозиториев заполнены **Description** (репозиторий → ⚙️ → Description) —
      их показывают карточки в блоке «Проекты».
- [ ] В блоке «Проекты» указаны `zapret-gui`, `Lavka_helper`, `LoveApp`.
      Если переименуете репозиторий — поправьте `repo=` в ссылке карточки.
- [ ] Тема GitHub: **Settings → Appearance → Dark** (палитра рассчитана на тёмный фон).
- [ ] По желанию: **Settings → Profile → Bio / Location / Website** — профиль выглядит
      законченным, когда заполнены и они.

## 5. Что легко поменять

| Хочу | Где править |
| --- | --- |
| Цвета | `color=0:00F5FF,50:7A00FF,100:FF00E4` (голубой → фиолетовый → розовый) |
| Текст шапки | `text=Bugulmek`, `desc=...` у capsule-render |
| Бегущая строка | `lines=...` у readme-typing-svg (текст в URL-кодировке) |
| Набор технологий | блок «Стек», шаблон `https://img.shields.io/badge/Имя-0D1117?style=for-the-badge&logo=...` |
| Проекты | блок «Проекты», параметры `username=` и `repo=` |
| Подпись | цитата в блоке «Контакты» |

## 6. Сервисы, которые рисуют карточки

- capsule-render — шапка и волны: https://github.com/kyechan99/capsule-render
- readme-typing-svg — бегущая строка: https://github.com/DenverCoder1/readme-typing-svg
- streak-stats — серия коммитов: https://github.com/DenverCoder1/github-readme-streak-stats
- profile-summary-cards — статистика, сводка и языки: https://github.com/vn7n24fzkq/github-profile-summary-cards
- Platane/snk — змейка: https://github.com/Platane/snk

Блок «Проекты» сделан без внешних генераторов карточек — только `shields.io`
(язык и звёзды) и обычные ссылки, поэтому он не зависит от лимитов Vercel.

## 7. Если картинка не грузится

Карточки статистики рисуют публичные сервисы на Vercel, у них общий лимит
запросов. `github-readme-stats` мы специально не используем — он чаще всех
уходит в `503 Maximum retries exceeded`.

Если какая-то карточка всё же не отрисовалась — обновите страницу через минуту,
обычно проходит само. Для полной стабильности можно развернуть свои копии
[profile-summary-cards](https://github.com/vn7n24fzkq/github-profile-summary-cards#deploy-to-vercel)
и [streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats#deploy-your-own-instance)
и заменить домены в ссылках.
