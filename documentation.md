# 📘 Templater API Documentation

---

## 🔐 Аутентификация и авторизация

### `GET /start_auth`
Запускает процесс OAuth-авторизации с Google.

**Ответ:**
```json
{ "auth_url": "https://..." }
```

---

### `GET /oauth_callback?state=...&code=...`
Завершает авторизацию Google и сохраняет токен.

- Успех: редирект на `/templates`
- Ошибка: `400`, если `state` некорректен

---

## 📂 Управление шаблонами

### `GET /templates`
Возвращает HTML-страницу со списком шаблонов.

Шаблон: `templates.jinja2`

---

### `GET /add_template`
Форма добавления шаблона.

Шаблон: `add_template.jinja2`

---

### `POST /api/add_template`
Добавляет новый шаблон.

**Тело запроса (JSON):**
```json
{
  "name": "Название",
  "description": "Описание"
}
```

**Ответ:**
```json
{
  "message": "Шаблон успешно добавлен",
  "template": { ... }
}
```

---

### `GET /edit_template/{template_id}`
HTML-форма редактирования шаблона.

Шаблон: `edit_template.jinja2`

---

### `POST /edit_template/{template_id}`
Обновляет имя и описание шаблона через форму.

Редирект на `/templates`

---

### `POST /api/update_template/{template_id}`
Обновление шаблона по API.

**Тело запроса:**
```json
{
  "name": "Новое имя",
  "description": "Новое описание"
}
```

**Ответ:**
```json
{ "message": "Шаблон успешно обновлен" }
```

---

### `POST /delete_template/{template_id}`
Удаляет один шаблон.

**Ответ:**
```json
{ "message": "Шаблон успешно удален" }
```

---

### `GET /delete_templates`
Форма массового удаления шаблонов.

Шаблон: `delete_templates.jinja2`

---

### `POST /delete_templates`
Удаляет несколько шаблонов.

**Тело запроса:**
```json
{
  "selected_templates": ["1", "2", "3"]
}
```

**Ответ:**
```json
{ "message": "Шаблоны успешно удалены" }
```

---

## 🧾 Ввод и сохранение данных шаблона

### `GET /input_template_data/{template_id}`
Форма ввода пользовательских данных.

Шаблон: `input_data_template.jinja2`

---

### `POST /api/save_template_data/{template_id}`
Сохраняет данные в шаблон.

**Тело запроса:**
```json
{
  "data": {
    "field_1": { "label": "Имя", "value": "Иван" },
    "field_2": { "label": "Фамилия", "value": "Петров" }
  }
}
```

**Ответ:**
```json
{ "message": "Данные успешно сохранены" }
```

---

### `GET /api/get_template_data_status/{template_id}`
Проверяет, есть ли сохранённые данные.

**Ответ:**
```json
{ "has_data": true }
```

---

## 📤 Экспорт шаблонов

### `POST /export_template/{template_id}`
Экспортирует шаблон как `.txt` в Google Drive.

**Тело запроса:**
```json
{ "folder_id": "GoogleDriveFolderID" }
```

**Ответ:**
```json
{
  "message": "Файл успешно экспортирован в Google Drive",
  "file_id": "..."
}
```

---

### `POST /export_archive_to_drive`
Загружает архив в Google Drive из GridFS.

**Тело запроса:**
```json
{ "file_id": "<id файла в GridFS>" }
```

**Ответ:**
```json
{
  "message": "Файл успешно загружен в Google Drive",
  "file_id": "..."
}
```

---

## 🧪 Проверка и генерация документов

### `POST /verify`
Проверяет соответствие шаблона и данных.

**Форма POST (multipart):**
- `template-id`: ID шаблона
- `data-table-id`: ID файла с данными

**Ответ:**
```json
{
  "status": "OK",
  "messages": ["Field X not defined in CSV"],
  "fields": ["имя", "фамилия", ...]
}
```

---

### `POST /render`
Генерирует документ(ы) по шаблону и данным.

**Форма POST (multipart):**
- `template-id`
- `data-table-id`
- `name-pattern` (необязательный шаблон имени)

**Ответ:**
```json
{
  "status": "OK",
  "files": {
    "имя1.docx": "<id>",
    "имя2.docx": "<id>"
  },
  "archive": "<id архива>",
  "archive_name": "шаблон.zip"
}
```

---

## 📁 Работа с файлами

### `POST /upload`
Загружает файл в GridFS.

**Форма:**
- `file`: файл
- `table-preview`: (опционально)

**Ответ:**
```json
{
  "status": "OK",
  "file_name": "filename.docx",
  "file_id": "ObjectId",
  "expire_at": "2024-10-01T12:00:00"
}
```

---

### `GET /files?file_id=<id>`
Скачивает файл из GridFS.

- Контент: `application/vnd.oasis.opendocument.text`
- Содержит заголовок `Content-Disposition: attachment`

---

## 🌍 Интерфейс и настройки

### `GET /`
Выводит CAPTCHA-проверку с выбором роли (`admin` или `user`).

Шаблон: `verify_captcha.jinja2`

---

### `GET /locale?language=ru`
Устанавливает языковую куку `_LOCALE_`.

Редирект на реферер.

---

### `GET /user_home`
Домашняя страница пользователя.

Шаблон: `user_home.jinja2`

---

### `GET /home`
Домашняя страница администратора.

Шаблон: `homepage.jinja2`

---

### `GET /dis`
Редирект на внешнюю систему DIS по переменной окружения `DIS_URL`.

---

## 🧱 Статика

Следующие пути отдают статические ресурсы:

```
/static/css
/static/js
/static/img
/ViewerJS
```

