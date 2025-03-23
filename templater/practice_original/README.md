# Введение

Этот скрипт использует 3 основных пакета:

- python-docx-template (https://github.com/elapouya/python-docx-template) для создания документа docx из шаблона
- Secretary (https://github.com/christopher-ramirez/secretary) для создания документа docx из шаблона
- jinja2 для управления тегами, вставленными в шаблон (используется в обоих пакетах выше)

Инструмент автоматически заполнит шаблоны документов (docx, odt) данными из таблицы (каждый столбец - это отдельное поле для вставки, каждая строка - новый документ).

### Ввод:
- CSV-файл со значениями поиска (с разделителями-запятыми и кодировкой UTF-8)
- Путь к шаблону в формате docx, odt
- Шаблон именования текстовых файлов

Пример CSV-файла:

    FirstName, LastName, Address, City, State, ZIP-code
    John, Doe, 120 jefferson st., Riverside, NJ, 08075
    Jack, McGinnis, 220 hobo Av., Phila, PA, 09119
    "John" "Da Man" "", Repici, 120 Jefferson St., Riverside, NJ, 08075
    Stephen, Tyler, "7452 Terrace" "At the Plaza" "road", SomeTown, SD, 91234
    , Blankman ,, SomeTown, SD, 00298
    "Joan" "the bone" ", Anne", Jet, "9th, at Terrace plc", Desert City, CO, 00123

Соответственно, поля для подстановки: FirstName, LastName, Address, City, State, ZIP-код.

Файл docx, odt, pptx, odp содержит указанные выше поля подстановки в виде меток следующего вида:

{{ Address }}

Шаблон именования текстовых файлов содержит комбинацию полей поиска:

{{FirstName}} {{LastName}}. Docx

### Вывод: 

В результате работы должно появиться 6 файлов, по одному на каждую строку файла CSV.

---

# Установка и использование

### Установить вручную

- Установите Python3 и pip3

На Ubuntu:

    apt-get update
    apt-get install -y python3 python3-pip

На Windows лучше использовать предоставленный установщик на главной странице.

- Установить зависимости:

    pip install -r app/requirements.txt

- Запустить скрипт:

    python app/main.py

### Установить на докер

Построить образ докера:

    docker build -t templater .

Запустить в контейнере: (*)

    docker run --rm --volume PATH_TO_DOC_DIR_ON_HOST:/data templater
    
Просто запустите образ в контейнере, смонтируйте каталог с файлом template / csv и запустите скрипт

ПРИМЕЧАНИЕ: python /app/main.py настроен как ENTRYPOINT, поэтому вам нужно просто указать параметр скрипта после команды (*)

### Usage:

    main.py [-h] [--out-dir OUTPUT_DIR] [--out-name OUTPUT_NAME]
                [--delimiter DELIMITER] [--verify-only]
                csv_path template_path

    позиционные аргументы:
    csv_path              Путь к CSV-файлу, содержащему таблицу данных
    template_path         Путь к файлу шаблона (odt, docx)

    необязательные аргументы:
    -h, --help                                  Показать это справочное сообщение и выйти
    --out-dir OUTPUT_DIR, -D OUTPUT_DIR         Путь к выходному каталогу
    --out-name OUTPUT_NAME, -o OUTPUT_NAME      Шаблон для имен выходных файлов (по умолчанию = заголовок первого столбца в csv)
    --delimiter DELIMITER, -d DELIMITER         Разделитель, используемый в файле csv (по умолчанию = ',')
    --verify-only, -v                           Проверка шаблона по CSV без создания файлов результатов

### Пример вызова скриптов на тестовых наборах

Каждый набор тестов содержит CSV-файл и 1 или более шаблонов (каждый из них представлен как в odt, так и в docx).

#### test0: 

Задача предоставила пример csv + шаблон визитной карточки

    python app/main.py tests/test0/taskEg.csv tests/test0/bizCard.docx -o "{{ FirstName }}_{{ LastName }}" -D ./output

    python app/main.py tests/test0/taskEg.csv tests/test0/bizCard.odt -o "{{ FirstName }}_{{ LastName }}" -D ./output

#### test1: 

Шаблон simple очень простой без стилей

    python app/main.py tests/test1/simple.csv tests/test1/simple.docx -o "{{ first_name }}_{{ last_name }}" -D ./output

    python app/main.py tests/test1/simple.csv tests/test1/simple.odt -o "{{ first_name }}_{{ last_name }}" -D ./output

Шаблон missing_param такой же, как приведенный выше, но специально написан с несоответствием в полях по сравнению с CSV-файлом, чтобы протестировать функцию предупреждения скрипта

    python app/main.py tests/test1/simple.csv tests/test1/missing_param.docx -o "{{ first_name }}_{{ last_name }}" -D ./output

    python app/main.py tests/test1/simple.csv tests/test1/missing_param.odt -o "{{ first_name }}_{{ last_name }}" -D ./output

#### test2:

Титульный лист лабораторной работы

    python app/main.py tests/test2/stud_teacher.csv tests/test2/title_page_temp.docx -o "{{ student_name }}_{{ lab_no }}" -D ./output

    python app/main.py tests/test2/stud_teacher.csv tests/test2/title_page_temp.odt -o "{{ student_name }}_{{ lab_no }}" -D ./output

#### test3:

Флаер с 4 полями

    python app/main.py tests/test3/flyer.csv tests/test3/flyer.docx -o "{{ event_name }}_{{ date }}" -D ./output

    python app/main.py tests/test3/flyer.csv tests/test3/flyer.odt -o "{{ event_name }}_{{ date }}" -D ./output

#### test4:

cover-letter template from office16

    python app/main.py tests/test4/info.csv tests/test4/cover_letter.docx -o "{{ name }}" -D ./output

    python app/main.py tests/test4/info.csv tests/test4/cover_letter.docx -o "{{ name }}" -D ./output