import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('계산기')
        self.setFixedSize(360, 500)
        self.expression = ''
        self.result_displayed = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet('background-color: #1C1C1C;')

        layout = QGridLayout()
        layout.setSpacing(8)
        self.setLayout(layout)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFont(QFont('Courier', 32))
        self.display.setStyleSheet('color: white; background-color: black; border: none; padding: 20px;')
        layout.addWidget(self.display, 0, 0, 1, 4)

        buttons = [
            ('C', 1, 0), ('+/-', 1, 1), ('%', 1, 2), ('÷', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('×', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('−', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('0', 5, 0, 1, 2), ('.', 5, 2), ('=', 5, 3)
        ]

        for btn in buttons:
            label, row, col = btn[0], btn[1], btn[2]
            rowspan = btn[3] if len(btn) > 3 else 1
            colspan = btn[4] if len(btn) > 4 else 1
            button = QPushButton(label)
            button.setFont(QFont('Helvetica', 20, QFont.Bold))

            if label in ['÷', '×', '−', '+', '=']:
                color, text_color = '#FF9500', 'white'
            elif label in ['C', '+/-', '%']:
                color, text_color = '#A5A5A5', 'black'
            else:
                color, text_color = '#333333', 'white'

            style = f'''
                QPushButton {{
                    background-color: {color};
                    color: {text_color};
                    font-size: 20px;
                    border: none;
                    border-radius: 35px;
                    min-width: {140 if label == '0' else 70}px;
                    min-height: 70px;
                    text-align: {'left' if label == '0' else 'center'};
                    padding-left: {'25px' if label == '0' else '0'};
                }}
            '''
            button.setStyleSheet(style)
            button.clicked.connect(lambda _, t=label: self.on_click(t))
            layout.addWidget(button, row, col, rowspan, colspan)

    def update_display(self, text):
        # 자동 폰트 크기 조정
        font_size = 32
        if len(text) > 12:
            font_size = 24
        elif len(text) > 18:
            font_size = 18
        self.display.setFont(QFont('Courier', font_size))
        self.display.setText(text)

    def reset(self):
        self.expression = ''
        self.update_display('')

    def add(self, value):
        self.expression += value
        self.update_display(self.expression)

    def subtract(self, value):
        self.expression += value
        self.update_display(self.expression)

    def multiply(self, value):
        self.expression += value
        self.update_display(self.expression)

    def divide(self, value):
        self.expression += value
        self.update_display(self.expression)

    def negative_positive(self):
        if self.expression.startswith('-'):
            self.expression = self.expression[1:]
        elif self.expression and self.expression[0].isdigit():
            self.expression = '-' + self.expression
        self.update_display(self.expression)

    def percent(self):
        try:
            result = str(eval(self.expression) / 100)
            self.expression = result
            self.update_display(self.format_result(result))
        except Exception:
            self.update_display('Error')
            self.expression = ''

    def equal(self):
        try:
            expr = self.expression.replace('×', '*').replace('÷', '/').replace('−', '-')
            if '/0' in expr:
                raise ZeroDivisionError
            result = str(eval(expr))
            formatted = self.format_result(result)
            self.expression = formatted
            self.update_display(formatted)
        except ZeroDivisionError:
            self.update_display('Error')
            self.expression = ''
        except Exception:
            self.update_display('Error')
            self.expression = ''

    def format_result(self, result):
        try:
            number = round(float(result), 6)
            formatted = str(number)
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
            return formatted
        except Exception:
            return 'Error'

    def on_click(self, text):
        if self.result_displayed and text.isdigit():
            self.expression = ''
            self.result_displayed = False

        if text == 'C':
            self.reset()
        elif text == '=':
            self.equal()
            self.result_displayed = True
        elif text == '+/-':
            self.negative_positive()
        elif text == '%':
            self.percent()
        elif text in ['+', '−', '×', '÷']:
            if not self.expression.endswith(('+', '−', '×', '÷')):
                self.expression += text
                self.update_display(self.expression)
        elif text == '.':
            parts = self.expression.split('+')[-1].split('−')[-1].split('×')[-1].split('÷')[-1]
            if '.' not in parts:
                self.expression += '.'
                self.update_display(self.expression)
        else:  # 숫자
            self.expression += text
            self.update_display(self.expression)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
