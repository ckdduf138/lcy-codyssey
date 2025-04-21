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
        self.init_ui()

    # 아이폰 계산기와 최대한 유사하게 계산기 UI를 만든다. 출력 형태 및 버튼의 배치는 동일하게 해야한다.
    # 색상이나 버튼의 모양까지 동일할 필요는 없다. 
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

        for button_info in buttons:
            label = button_info[0]
            row = button_info[1]
            col = button_info[2]
            rowspan = button_info[3] if len(button_info) > 3 else 1
            colspan = button_info[4] if len(button_info) > 4 else 1

            button = QPushButton(label)
            button.setFont(QFont('Helvetica', 20, QFont.Bold))

            if label in ['÷', '×', '−', '+', '=']:
                color = '#FF9500'
                text_color = 'white'
            elif label in ['C', '+/-', '%']:
                color = '#A5A5A5'
                text_color = 'black'
            else:
                color = '#333333'
                text_color = 'white'

            if label == '0':
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: {text_color};
                        font-size: 20px;
                        border: none;
                        border-radius: 35px;
                        min-width: 140px;
                        min-height: 70px;
                        text-align: left;
                        padding-left: 25px;
                    }}
                ''')
            else:
                button.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: {text_color};
                        font-size: 20px;
                        border: none;
                        min-width: 70px;
                        min-height: 70px;
                        border-radius: 35px;
                    }}
                ''')

            # 각각의 버튼을 누를 때 마다 숫자가 입력 될 수 있게 이벤트를 처리한다. 
            button.clicked.connect(lambda _, text=label: self.on_click(text))
            layout.addWidget(button, row, col, rowspan, colspan)

    def format_result(self, result, digits=6, max_len=10):
        try:
            float_result = round(float(result), digits)
            result = str(float_result)
            if len(result) > max_len:
                result = result[:max_len] + '...'
            return result
        except:
            return 'Error'

    def on_click(self, text):
        if text == 'C':
            self.expression = ''
            self.display.setText('')
        elif text == '=': # 4칙 연산이 가능하도록 코드를 추가한다. 
            try:
                expr = self.expression.replace('×', '*').replace('÷', '/').replace('−', '-')
                raw_result = str(eval(expr))
                result = self.format_result(raw_result)
                self.display.setText(result)
                self.expression = result
            except Exception:
                self.display.setText('Error')
                self.expression = ''
        elif text == '+/-':
            if self.expression.startswith('-'):
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.display.setText(self.expression)
        else:
            self.expression += text
            self.display.setText(self.expression)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())




# 1. Python으로 UI를 만들 수 있는 PyQT 라이브러리를 설치한다. 
# pip install PyQt5
