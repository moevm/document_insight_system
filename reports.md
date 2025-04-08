# Расширение Document Insight System для обработки LaTeX документов и проектов

## 1. Описание проекта
**Цель:** Добавить возможность обрабатывать и проверять отчеты в формате LaTeX в системе анализа документов **Document Insight System (DIS)**.

---

## 2. Функциональные требования

- Валидация базового синтаксиса LaTeX
- Конвертация LaTeX-документов в промежуточный формат системы
- Извлечение метаданных (авторы, дата, версия)
- Парсинг математических формул и специальных символов
- Поддержка работа с большими файлами и многофайловыми проектами
- Обработка библиографических ссылок (BibTeX)
- Анализ структуры документа (секции, подсекции, ссылки) с использованием существующего шаблона ВКР в LaTex
- Интеграция с существующим пайплайном обработки DIS (существующие проверки документов)
- Проверка на использование системного шаблона
- Логирование процессов обработки
- Покрытие тестами

---

## 3. Сценарии использования (User Stories)

1. **Загрузка отчета LaTeX**  
  

2. **Корректная обработка**  
   

3. **Преобразование в промежуточный формат системы**  
   

4. **Проверка документа на соответствие требованиям**  
  

5. **Вывод результатов в UI**  
   
---

## Итерация 1

Артефакты первой встречи с заказчиком от [17.02](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/meetings/employer/17.02.txt)

Артефакты встреч с командой от [18.02](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/meetings/team/18.02.txt), [25.02](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/meetings/team/24.02.txt)

Презентация по результатам [первой итерации](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/presentations/1_iteration.pptx)

## Итерация 2

Созданы в формате [mermaid](https://mermaid.live/) диаграмы [Use Case](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/diagrams/use_case.md), [UML](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/diagrams/uml.md)

Артефакты встреч с командой от [14.03](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/meetings/team/14.03.txt), [21.03](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/meetings/team/21.03.txt)

Презентация по результатам [второй итерации](https://github.com/moevm/document_insight_system/blob/reports-latex/AI/presentations/2_iteration.pptx)
