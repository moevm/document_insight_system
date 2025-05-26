# app/main/reports/latex/tokenizer.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

# Типы токенов для классификации элементов LaTeX
class TokenType(Enum):
    COMMAND = auto()        # Команда вида \command
    ENVIRONMENT = auto()    # Окружение \begin{env}...\end{env}
    ARG_OPEN = auto()       # Открывающая фигурная скобка {
    ARG_CLOSE = auto()      # Закрывающая фигурная скобка }
    TEXT = auto()           # Обычный текст
    SPECIAL_CHAR = auto()   # Специальные символы (~, ^, _ и др.)
    COMMENT = auto()        # Комментарий, начинающийся с %
    BRACE_OPEN = auto()     # Открывающая скобка {
    BRACE_CLOSE = auto()    # Закрывающая скобка }
    BRACKET_OPEN = auto()   # Открывающая квадратная скобка [
    BRACKET_CLOSE = auto()  # Закрывающая квадратная скобка ]
    ESCAPE = auto()         # Экранированный символ (\$, \% и т.д.)

# Структура для хранения информации о токене
@dataclass
class Token:
    type: TokenType  # Тип токена из перечисления
    value: str       # Значение токена (текст команды, содержимое и т.д.)
    position: int    # Позиция в исходном тексте

class LatexTokenizer:
    def __init__(self):
        # Инициализация состояния токенизатора
        self.state = self.State.DEFAULT  # Текущее состояние автомата
        self.tokens: List[Token] = []  # Список накопленных токенов
        self.buffer: str = ''       # Буфер для накопления символов
        self.position: int = 0      # Текущая позиция в тексте
        self.env_stack: List[str] = []  # Стек для отслеживания окружений

    # Состояния конечного автомата
    class State(Enum):
        DEFAULT = auto()      # Обычный режим обработки
        COMMAND = auto()      # Обработка команды (после \)
        ARGUMENT = auto()     # Обработка аргументов команд {}
        ENVIRONMENT = auto() # Обработка окружений \begin/\end
        ESCAPE = auto()       # Обработка экранированных символов
        COMMENT = auto()     # Обработка комментариев

    def tokenize(self, content: str) -> List[Token]:
        """Основной метод токенизации. Возвращает список токенов."""
        self.reset()  # Сброс состояния перед обработкой нового содержимого
        content = self._clean_content(content)  # Нормализация переносов строк
        
        # Главный цикл обработки символов
        while self.position < len(content):
            char = content[self.position]
            
            # Выбор обработчика в зависимости от текущего состояния
            if self.state == self.State.DEFAULT:
                self._handle_default(char)
            elif self.state == self.State.COMMAND:
                self._handle_command(char)
            elif self.state == self.State.ARGUMENT:
                self._handle_argument(char)
            elif self.state == self.State.ENVIRONMENT:
                self._handle_environment(char)
            elif self.state == self.State.ESCAPE:
                self._handle_escape(char)
            elif self.state == self.State.COMMENT:
                self._handle_comment(char)
            
            self.position += 1  # Переход к следующему символу
        
        self._flush_buffer()  # Обработка остатков в буфере
        return self.tokens

    def _clean_content(self, content: str) -> str:
        """Нормализация переносов строк для единообразия обработки."""
        return content.replace('\r\n', '\n').replace('\r', '\n')

    def _handle_default(self, char: str):
        """Обработка символов в обычном состоянии."""
        if char == '\\':
            # Начало команды или экранирования
            self._flush_buffer()  # Сброс предыдущего текста
            self.state = self.State.COMMAND
            self.buffer = char  # Начало накопления команды
        elif char == '%':
            # Начало комментария
            self._flush_buffer()
            self.state = self.State.COMMENT
        elif char in '{[(':
            # Обработка открывающих скобок
            self._flush_buffer()
            token_type = {
                '{': TokenType.BRACE_OPEN,
                '[': TokenType.BRACKET_OPEN,
                '(': TokenType.BRACE_OPEN  # Обрабатываем ( как обычную скобку
            }[char]
            self.tokens.append(Token(token_type, char, self.position))
        elif char in '}])':
            # Обработка закрывающих скобок
            self._flush_buffer()
            token_type = {
                '}': TokenType.BRACE_CLOSE,
                ']': TokenType.BRACKET_CLOSE,
                ')': TokenType.BRACE_CLOSE
            }[char]
            self.tokens.append(Token(token_type, char, self.position))
        elif char == '~':
            # Специальный символ неразрывного пробела
            self._flush_buffer()
            self.tokens.append(Token(TokenType.SPECIAL_CHAR, '~', self.position))
        else:
            # Накопление обычного текста
            self.buffer += char

    def _handle_command(self, char: str):
        """Обработка команд LaTeX после обратного слеша."""
        if char.isalpha():
            # Продолжение имени команды
            self.buffer += char
        else:
            # Конец имени команды
            cmd = self.buffer[1:]  # Убираем начальный \
            if cmd in ['begin', 'end']:
                # Обработка окружений \begin и \end
                self.tokens.append(Token(
                    TokenType.COMMAND, cmd, self.position - len(cmd) - 1
                ))
                self.state = self.State.ENVIRONMENT
            else:
                # Обычная команда
                self.tokens.append(Token(
                    TokenType.COMMAND, cmd, self.position - len(cmd) - 1
                ))
                self._flush_buffer()
                self.state = self.State.DEFAULT
                # Возврат позиции для повторной обработки символа
                self.position -= 1

    def _handle_environment(self, char: str):
        """Обработка окружений после \begin или \end."""
        if char == '{':
            # Начало имени окружения
            self.buffer = ''
            self.state = self.State.ARGUMENT
        else:
            # Некорректный синтаксис, возврат в обычное состояние
            self.state = self.State.DEFAULT
            self.position -= 1

    def _handle_argument(self, char: str):
        """Обработка аргументов в фигурных скобках."""
        if char == '}':
            # Конец аргумента
            token_type = TokenType.ENVIRONMENT if self.env_stack else TokenType.TEXT
            self.tokens.append(Token(
                token_type,
                self.buffer,
                self.position - len(self.buffer) - 1
            ))
            self.buffer = ''
            self.state = self.State.DEFAULT
        else:
            # Накопление содержимого аргумента
            self.buffer += char

    def _handle_escape(self, char: str):
        """Обработка экранированных символов."""
        self.tokens.append(Token(TokenType.ESCAPE, char, self.position))
        self.state = self.State.DEFAULT

    def _handle_comment(self, char: str):
        """Обработка комментариев."""
        if char == '\n':
            # Конец комментария
            self.tokens.append(Token(TokenType.COMMENT, self.buffer, self.position))
            self.buffer = ''
            self.state = self.State.DEFAULT
        else:
            # Накопление текста комментария
            self.buffer += char

    def _flush_buffer(self):
        """Сброс буфера в токены типа TEXT."""
        if self.buffer:
            self.tokens.append(Token(TokenType.TEXT, self.buffer, self.position))
            self.buffer = ''

    def reset(self):
        """Сброс состояния токенизатора перед новым использованием."""
        self.state = self.State.DEFAULT
        self.tokens = []
        self.buffer = ''
        self.position = 0
        self.env_stack = [] 

    # if __name__ == "__main__":
    #     # Пример LaTeX-документа для тестирования
    #     latex_content = r"""
    #     \documentclass{article}
    #     \begin{document}
    #     Hello \textbf{world}! % Пример комментария
    #     Экранирование: \$\%\&
    #     \end{document}
    #     """

    #     tokenizer = LatexTokenizer()
    #     tokens = tokenizer.tokenize(latex_content)

    #     # Вывод результатов токенизации
    #     print("{:<15} | {:<20} | {}".format("Тип", "Значение", "Позиция"))
    #     print("-" * 45)
    #     for token in tokens:
    #         print("{:<15} | {:<20} | {}".format(
    #             token.type.name, 
    #             token.value.replace('\n', '\\n'), 
    #             token.position
    #         ))