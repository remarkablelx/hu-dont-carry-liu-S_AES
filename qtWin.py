import os
import sys
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QLineEdit, QTextEdit, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from paramiko.util import bit_length

import S_AES
from S_AES import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S-AES 加密系统")
        self.setGeometry(0, 0, 1000, 600)
        center(self)

        font = QFont("Arial", 12)
        self.setFont(font)

        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.home_button = QPushButton("首页")
        self.saes_button = QPushButton("S-AES")
        self.multiple_encrypt_button = QPushButton("多重加密")
        self.cbc_button = QPushButton("CBC")
        self.middle_attack_button = QPushButton("中间相遇攻击")

        self.keygen_button = QPushButton("获取密钥")
        self.bruteforce_button = QPushButton("暴力破解")

        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 20px 40px;
                border-radius: 50px;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        self.home_button.setStyleSheet(button_style)
        self.saes_button.setStyleSheet(button_style)
        self.multiple_encrypt_button.setStyleSheet(button_style)
        self.cbc_button.setStyleSheet(button_style)

        self.keygen_button.setStyleSheet(button_style)
        self.bruteforce_button.setStyleSheet(button_style)

        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.saes_button)
        button_layout.addWidget(self.multiple_encrypt_button)
        button_layout.addWidget(self.cbc_button)

        button_layout.addWidget(self.keygen_button)
        button_layout.addWidget(self.bruteforce_button)

        self.home_button.clicked.connect(self.show_home)
        self.saes_button.clicked.connect(self.show_saes)
        self.multiple_encrypt_button.clicked.connect(self.show_multiple_encrypt)
        self.cbc_button.clicked.connect(self.show_cbc)

        self.keygen_button.clicked.connect(self.show_keygen)
        self.bruteforce_button.clicked.connect(self.show_bruteforce)

        self.stacked_widget = QStackedWidget()

        self.home_page = self.create_home_page()
        self.saes_page = self.create_saes_page()
        self.multiple_encrypt_page = self.create_multiple_encrypt_page()
        self.cbc_page = self.create_cbc_page()

        self.keygen_page = self.create_keygen_page()
        self.bruteforce_page = self.create_bruteforce_page()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.saes_page)
        self.stacked_widget.addWidget(self.multiple_encrypt_page)
        self.stacked_widget.addWidget(self.cbc_page)

        self.stacked_widget.addWidget(self.keygen_page)
        self.stacked_widget.addWidget(self.bruteforce_page)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


    def show_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)

    def show_saes(self):
        self.stacked_widget.setCurrentWidget(self.saes_page)

    def show_multiple_encrypt(self):
        self.stacked_widget.setCurrentWidget(self.multiple_encrypt_page)

    def show_cbc(self):
        self.stacked_widget.setCurrentWidget(self.cbc_page)

    def show_keygen(self):
        self.stacked_widget.setCurrentWidget(self.keygen_page)

    def show_bruteforce(self):
        self.stacked_widget.setCurrentWidget(self.bruteforce_page)

    # 创建首页
    def create_home_page(self):
        page = QWidget()
        self.setWindowIcon(QIcon(get_resource_path("img/app_icon.ico")))
        vbox = QVBoxLayout()
        label = QLabel("欢迎来到 S-AES 加密系统首页")
        label.setAlignment(Qt.AlignCenter)
        font = QFont("黑体", 30, QFont.Bold)
        label.setFont(font)
        label.setStyleSheet("color: #333;")

        vbox.addWidget(label)

        image_label = QLabel()
        pixmap = QPixmap(get_resource_path("img/logic.png"))
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        vbox.addWidget(image_label)

        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(copyright_label)

        page.setLayout(vbox)

        return page


    # 创建S-AES界面
    def create_saes_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        font = QFont("Arial", 20)

        self.combo_box1 = QComboBox()
        self.combo_box1.addItem("S-AES 二进制加解密")
        self.combo_box1.addItem("S-AES ASCII 加解密")
        self.combo_box1.setFont(font)
        self.combo_box1.setMinimumHeight(100)
        self.combo_box1.currentIndexChanged.connect(self.change_endecryption_type)

        self.change_endecryption_type(0)
        layout.addWidget(self.combo_box1)

        self.saes_label = QLabel('提示：')
        self.saes_label.setWordWrap(True)
        self.saes_label.setFont(font)
        layout.addWidget(self.saes_label)

        plaintext_label = QLabel("明文")
        plaintext_label.setFont(font)
        self.saes_plaincipher_input = QLineEdit()  # S-AES 界面的独立控件
        self.saes_plaincipher_input.setPlaceholderText("请输入明文或密文")
        self.saes_plaincipher_input.setFont(font)
        self.saes_plaincipher_input.setMinimumHeight(100)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(plaintext_label)
        hbox1.addWidget(self.saes_plaincipher_input)

        key_label = QLabel("密钥")
        key_label.setFont(font)
        self.saes_key_input = QLineEdit()  # S-AES 界面的独立控件
        self.saes_key_input.setPlaceholderText("请输入密钥")
        self.saes_key_input.setFont(font)
        self.saes_key_input.setMinimumHeight(100)
        self.saes_key_input.setEchoMode(QLineEdit.Password)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(key_label)
        hbox2.addWidget(self.saes_key_input)

        result_label = QLabel("加密或解密结果")
        result_label.setFont(font)
        self.saes_enderesult_display = QTextEdit()  # S-AES 界面的独立控件
        self.saes_enderesult_display.setReadOnly(True)
        self.saes_enderesult_display.setFont(font)
        self.saes_enderesult_display.setMinimumHeight(100)

        encrypt_button = QPushButton("加密")
        decrypt_button = QPushButton("解密")
        encrypt_button.setFont(font)
        decrypt_button.setFont(font)
        encrypt_button.setMinimumHeight(50)
        decrypt_button.setMinimumHeight(50)
        encrypt_button.setMinimumWidth(100)
        decrypt_button.setMinimumWidth(100)

        encrypt_button.clicked.connect(self.encrypt)  # 连接到S-AES加密函数
        decrypt_button.clicked.connect(self.decrypt)  # 连接到S-AES解密函数

        hbox3 = QHBoxLayout()
        hbox3.addWidget(encrypt_button)
        hbox3.addWidget(decrypt_button)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addWidget(result_label)
        layout.addWidget(self.saes_enderesult_display)
        layout.addLayout(hbox3)

        back_button = QPushButton("返回")
        back_button.setFont(font)
        back_button.setMinimumHeight(50)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 12))
        layout.addWidget(copyright_label)

        page.setLayout(layout)

        self.update_saes()

        return page


    # 创建多重加密
    def create_multiple_encrypt_page(self):
        page2 = QWidget()
        layout2 = QVBoxLayout()

        font = QFont("Arial", 20)

        self.combo_box2 = QComboBox()
        self.combo_box2.addItem("双重加解密")
        self.combo_box2.addItem("三重加解密")
        self.combo_box2.setFont(font)
        self.combo_box2.setMinimumHeight(100)
        self.combo_box2.currentIndexChanged.connect(self.change_multiple_type)

        self.change_multiple_type(0)
        layout2.addWidget(self.combo_box2)

        self.multiple_label = QLabel('提示：')
        self.multiple_label.setWordWrap(True)
        self.multiple_label.setFont(font)
        layout2.addWidget(self.multiple_label)

        plaintext_label2 = QLabel("明文")
        plaintext_label2.setFont(font)
        self.multiple_plaincipher_input = QLineEdit()  # 多重加密界面的独立控件
        self.multiple_plaincipher_input.setPlaceholderText("请输入明文或密文")
        self.multiple_plaincipher_input.setFont(font)
        self.multiple_plaincipher_input.setMinimumHeight(100)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(plaintext_label2)
        hbox1.addWidget(self.multiple_plaincipher_input)

        key_label2 = QLabel("密钥")
        key_label2.setFont(font)
        self.multiple_key_input = QLineEdit()  # 多重加密界面的独立控件
        self.multiple_key_input.setPlaceholderText("请输入密钥")
        self.multiple_key_input.setFont(font)
        self.multiple_key_input.setMinimumHeight(100)
        self.multiple_key_input.setEchoMode(QLineEdit.Password)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(key_label2)
        hbox2.addWidget(self.multiple_key_input)

        result_label2 = QLabel("加密或解密结果")
        result_label2.setFont(font)
        self.multiple_enderesult_display = QTextEdit()  # 多重加密界面的独立控件
        self.multiple_enderesult_display.setReadOnly(True)
        self.multiple_enderesult_display.setFont(font)
        self.multiple_enderesult_display.setMinimumHeight(100)

        encrypt_button2 = QPushButton("加密")
        decrypt_button2 = QPushButton("解密")
        encrypt_button2.setFont(font)
        decrypt_button2.setFont(font)
        encrypt_button2.setMinimumHeight(50)
        decrypt_button2.setMinimumHeight(50)
        encrypt_button2.setMinimumWidth(100)
        decrypt_button2.setMinimumWidth(100)

        encrypt_button2.clicked.connect(self.encrypt_multiple)
        decrypt_button2.clicked.connect(self.decrypt_multiple)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(encrypt_button2)
        hbox3.addWidget(decrypt_button2)

        layout2.addLayout(hbox1)
        layout2.addLayout(hbox2)
        layout2.addWidget(result_label2)
        layout2.addWidget(self.multiple_enderesult_display)
        layout2.addLayout(hbox3)

        back_button = QPushButton("返回")
        back_button.setFont(font)
        back_button.setMinimumHeight(50)
        back_button.clicked.connect(self.go_back)
        layout2.addWidget(back_button)

        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 12))
        layout2.addWidget(copyright_label)

        page2.setLayout(layout2)

        self.update_multiple()

        return page2

    # 创建CBC加密
    def create_cbc_page(self):
        page3 = QWidget()
        layout3 = QVBoxLayout()

        font = QFont("Arial", 20)

        # 使用下拉框实现功能的变换
        self.combo_box3 = QComboBox()
        self.combo_box3.addItem("CBC 二进制加解密")
        self.combo_box3.addItem("CBC ASCII 加解密")
        self.combo_box3.addItem("CBC Unicode 加解密")
        self.combo_box3.setFont(font)
        self.combo_box3.setMinimumHeight(100)
        self.combo_box3.currentIndexChanged.connect(self.change_cbc_type)

        # 初始设置位二进制加解密
        self.change_cbc_type(0)
        layout3.addWidget(self.combo_box3)

        self.cbc_label = QLabel('提示：')
        self.cbc_label.setWordWrap(True)
        self.cbc_label.setFont(font)
        layout3.addWidget(self.cbc_label)

        plaintext_label3 = QLabel("明文")
        plaintext_label3.setFont(font)
        self.cbc_plaincipher_input = QLineEdit()
        self.cbc_plaincipher_input.setPlaceholderText("请输入明文或密文")
        self.cbc_plaincipher_input.setFont(font)
        self.cbc_plaincipher_input.setMinimumHeight(100)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(plaintext_label3)
        hbox1.addWidget(self.cbc_plaincipher_input)

        key_label3 = QLabel("密钥")
        key_label3.setFont(font)
        self.cbc_key_input = QLineEdit()
        self.cbc_key_input.setPlaceholderText("请输入密钥")
        self.cbc_key_input.setFont(font)
        self.cbc_key_input.setMinimumHeight(100)
        self.cbc_key_input.setEchoMode(QLineEdit.Password)  # 设置为密码模式，输入内容将被隐藏

        iv_label = QLabel("初始向量")
        iv_label.setFont(font)
        self.cbc_iv_input = QLineEdit()
        self.cbc_iv_input.setPlaceholderText("请输入初始向量")
        self.cbc_iv_input.setFont(font)
        self.cbc_iv_input.setMinimumHeight(100)
        self.cbc_iv_input.setEchoMode(QLineEdit.Password)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(key_label3)
        hbox2.addWidget(self.cbc_key_input)
        hbox2.addWidget(iv_label)
        hbox2.addWidget(self.cbc_iv_input)

        result_label3 = QLabel("加密或解密结果")
        result_label3.setFont(font)
        self.cbc_enderesult_display = QTextEdit()
        self.cbc_enderesult_display.setReadOnly(True)
        self.cbc_enderesult_display.setFont(font)
        self.cbc_enderesult_display.setMinimumHeight(100)

        encrypt_button3 = QPushButton("加密")
        decrypt_button3 = QPushButton("解密")
        encrypt_button3.setFont(font)
        decrypt_button3.setFont(font)
        encrypt_button3.setMinimumHeight(50)
        decrypt_button3.setMinimumHeight(50)
        encrypt_button3.setMinimumWidth(100)
        decrypt_button3.setMinimumWidth(100)

        encrypt_button3.clicked.connect(self.encrypt_cbc)
        decrypt_button3.clicked.connect(self.decrypt_cbc)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(encrypt_button3)
        hbox3.addWidget(decrypt_button3)

        layout3.addLayout(hbox1)
        layout3.addLayout(hbox2)
        layout3.addWidget(result_label3)
        layout3.addWidget(self.cbc_enderesult_display)
        layout3.addLayout(hbox3)

        back_button = QPushButton("返回")
        back_button.setFont(font)
        back_button.setMinimumHeight(50)
        back_button.clicked.connect(self.go_back)
        layout3.addWidget(back_button)

        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 12))
        layout3.addWidget(copyright_label)

        page3.setLayout(layout3)

        self.update_cbc()

        return page3

    # 创建生成密钥和IV界面
    def create_keygen_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        font = QFont("Arial", 20)

        # 添加“密钥生成”标题
        keygen_label = QLabel('密钥生成')
        keygen_label.setFont(font)
        layout.addWidget(keygen_label)

        # 添加“请输入需要生成的密钥位数”标签和文本框
        bit_length_label = QLabel('请输入需要生成的密钥位数')
        bit_length_label.setFont(font)
        self.bit_length_input = QLineEdit()  # 输入密钥位数
        self.bit_length_input.setPlaceholderText('请输入密钥位数，如16, 32, 48...')
        self.bit_length_input.setFont(font)
        self.bit_length_input.setMinimumHeight(50)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(bit_length_label)
        hbox1.addWidget(self.bit_length_input)
        layout.addLayout(hbox1)

        # 添加密钥显示框
        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setPlaceholderText('生成的密钥会在这里显示')
        self.key_display.setFont(font)
        self.key_display.setMinimumHeight(100)
        self.key_display.setMaximumHeight(100)
        layout.addWidget(self.key_display)

        # 添加生成密钥按钮
        generate_key_button = QPushButton('生成密钥')
        generate_key_button.setFont(font)
        generate_key_button.setMinimumHeight(50)
        generate_key_button.clicked.connect(self.generate_key)  # 连接生成密钥的函数
        layout.addWidget(generate_key_button)

        # 添加初始化向量（IV）生成部分
        iv_label = QLabel('初始化向量 (IV) 生成')
        iv_label.setFont(font)
        layout.addWidget(iv_label)

        # 添加IV显示框
        self.iv_display = QLineEdit()
        self.iv_display.setReadOnly(True)
        self.iv_display.setPlaceholderText('生成的IV会在这里显示')
        self.iv_display.setFont(font)
        self.iv_display.setMinimumHeight(100)
        self.iv_display.setMaximumHeight(100)
        layout.addWidget(self.iv_display)

        # 添加生成IV按钮
        generate_iv_button = QPushButton('生成IV')
        generate_iv_button.setFont(font)
        generate_iv_button.setMinimumHeight(50)
        generate_iv_button.clicked.connect(self.generate_iv)  # 连接生成IV的函数
        layout.addWidget(generate_iv_button)

        layout.addStretch()

        # 返回按钮
        back_button = QPushButton('返回')
        back_button.setFont(font)
        back_button.setMinimumHeight(50)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        # 版权信息
        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 12))
        layout.addWidget(copyright_label)

        page.setLayout(layout)
        return page

    # 创建暴力破解界面
    def create_bruteforce_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        font = QFont("Arial", 20)

        # 也通过下拉框进行选择
        self.combo_box4 = QComboBox()
        self.combo_box4.addItem("中间相遇攻击")
        self.combo_box4.setFont(font)
        self.combo_box4.setMinimumHeight(100)
        layout.addWidget(self.combo_box4)

        self.force_label = QLabel('提示：')
        self.force_label.setWordWrap(True)
        self.force_label.setFont(font)
        layout.addWidget(self.force_label)

        plaintext_label4 = QLabel('明文列表 (每行一个)')
        plaintext_label4.setFont(font)
        self.force_plaintext_input = QTextEdit()  # 用于输入多个明文
        self.force_plaintext_input.setPlaceholderText('请输入明文，每行一个')
        self.force_plaintext_input.setFont(font)
        self.force_plaintext_input.setMinimumHeight(100)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(plaintext_label4)
        hbox1.addWidget(self.force_plaintext_input)

        ciphertext_label4 = QLabel('密文列表 (每行一个)')
        ciphertext_label4.setFont(font)
        self.force_ciphertext_input = QTextEdit()  # 用于输入多个密文
        self.force_ciphertext_input.setPlaceholderText('请输入密文，每行一个')
        self.force_ciphertext_input.setFont(font)
        self.force_ciphertext_input.setMinimumHeight(100)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(ciphertext_label4)
        hbox2.addWidget(self.force_ciphertext_input)

        result_label4 = QLabel('暴力破解结果')
        result_label4.setFont(font)
        self.force_display = QTextEdit()
        self.force_display.setReadOnly(True)
        self.force_display.setFont(font)
        self.force_display.setMinimumHeight(100)

        # 显示时间
        time_label = QLabel('破解耗时')
        time_label.setFont(font)
        self.time_display = QLabel('')

        force_button = QPushButton('暴力破解')
        back_button = QPushButton('返回')
        force_button.setFont(font)
        back_button.setFont(font)
        force_button.setMinimumHeight(50)
        back_button.setMinimumHeight(50)

        force_button.clicked.connect(self.force)
        back_button.clicked.connect(self.go_back)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(force_button)
        hbox3.addWidget(back_button)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addWidget(result_label4)
        layout.addWidget(self.force_display)
        layout.addWidget(time_label)
        layout.addWidget(self.time_display)
        layout.addLayout(hbox3)

        copyright_label = QLabel('© 小胡不带小刘')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 12))
        layout.addWidget(copyright_label)

        page.setLayout(layout)

        self.update_force()

        return page

    def update_saes(self):
        saes_text = (
            "1. 二进制加解密要求明密文为16位的01组合。\n"
            "2. 密钥要求为16位的01组合。\n"
            "3. 请确保输入格式正确。"
        )
        self.saes_label.setText(saes_text)

    def update_multiple(self):
        multiple_text = (
            "1. 多重加解密要求明密文为16位的01组合。\n"
            "2. 对于双重加解密，密钥要求为32位的01组合。\n"
            "3. 对于三重加解密，密钥要求为48位的01组合。\n"
            "4. 请确保输入格式正确。"
        )
        self.multiple_label.setText(multiple_text)

    def update_cbc(self):
        cbc_text = (
            "1. 要求明密文为16倍数位的01组合、或者是偶数倍的ASCII字符、或者是Unicode字符。\n"
            "2. 密钥要求为16位的01组合。\n"
            "3. 初始向量要求为16位的01组合。\n"
            "4. 请确保输入格式正确。"
        )
        self.cbc_label.setText(cbc_text)

    def update_hints(self):
        hint_text = (
            "1. 二进制加解密要求明密文为8位的01组合。\n"
            "2. 密钥要求为10位的01组合。\n"
            "3. 请确保输入格式正确。"
        )
        self.hint_label.setText(hint_text)

    def update_force(self):
        force_text = (
            "1. 中间相遇攻击要求明密文为16位的01组合。\n"
            "2. 请确保输入格式正确。"
        )
        self.force_label.setText(force_text)

    # 通过index确定当前选择的模式，切换对应的在S_AES定义好的函数
    def change_endecryption_type(self, index):
        if index == 0:
            self.current_encrypt = S_AES.encrypt
            self.current_decrypt = S_AES.decrypt
        elif index == 1:
            self.current_encrypt = S_AES.encrypt_ASCII
            self.current_decrypt = S_AES.decrypt_ASCII

    # 通过index确定当前选择的模式，切换对应的在S_AES定义好的函数
    def change_multiple_type(self, index):
        if index == 0:
            self.current_encrypt2 = S_AES.encrypt_double
            self.current_decrypt2 = S_AES.decrypt_double
        elif index == 1:
            self.current_encrypt2 = S_AES.encrypt_triple
            self.current_decrypt2 = S_AES.decrypt_triple


    # 通过index确定当前选择的模式，切换对应的在S_AES定义好的函数
    def change_cbc_type(self, index):
        if index == 0:
            self.current_encrypt3 = S_AES.encrypt_CBC
            self.current_decrypt3 = S_AES.decrypt_CBC
        elif index == 1:
            self.current_encrypt3 = S_AES.encrypt_CBC
            self.current_decrypt3 = S_AES.decrypt_CBC
        elif index == 2:
            self.current_encrypt3 = S_AES.encrypt_CBC
            self.current_decrypt3 = S_AES.decrypt_CBC

    # 加密接口，连接S_AES里的函数和窗口里面输入字符的读取
    def encrypt(self):
        plaintext = self.saes_plaincipher_input.text()
        key = self.saes_key_input.text()

        if self.combo_box1.currentIndex() == 0:
            if not all(c in '01' for c in plaintext):
                self.saes_enderesult_display.setText("错误：二进制明文输入只能包含 0 和 1。")
                return
            if len(plaintext) != 16:
                self.saes_enderesult_display.setText("错误：输入的二进制明文必须为 16 位。")
                return
        elif self.combo_box1.currentIndex() == 1:
            if not all(0 <= ord(c) < 256 for c in plaintext):  # 校验输入的每个字符是否为有效 ASCII
                self.saes_enderesult_display.setText("错误：请输入正确的 ASCII 字符。")
                return
            if len(plaintext) % 2 != 0:
                self.saes_enderesult_display.setText("错误：请输入偶数位的 ASCII 字符。")
                return
        if not all(c in '01' for c in key):
            self.saes_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
            return
        if len(key) != 16:
            self.saes_enderesult_display.setText("错误：密钥必须为 16 位。")
            return

        encrypted_text = self.current_encrypt(plaintext, key)
        self.saes_enderesult_display.setText(encrypted_text)

    # 解密接口，连接S_AES里的函数和窗口里面输入字符的读取
    def decrypt(self):
        ciphertext = self.saes_plaincipher_input.text()
        key = self.saes_key_input.text()

        if self.combo_box1.currentIndex() == 0:
            if not all(c in '01' for c in ciphertext):
                self.saes_enderesult_display.setText("错误：二进制密文输入只能包含 0 和 1。")
                return
            if len(ciphertext) != 16:
                self.saes_enderesult_display.setText("错误：输入的二进制密文必须为 16 位。")
                return
        elif self.combo_box1.currentIndex() == 1:
            if not all(0 <= ord(c) < 256 for c in ciphertext):  # 校验输入的每个字符是否为有效 ASCII
                self.saes_enderesult_display.setText("错误：请输入正确的 ASCII 字符。")
                return
            if len(ciphertext) % 2 != 0:
                self.saes_enderesult_display.setText("错误：请输入偶数位的 ASCII 字符。")
                return
        if not all(c in '01' for c in key):
            self.saes_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
            return
        if len(key) != 16:
            self.saes_enderesult_display.setText("错误：密钥必须为 16 位。")
            return

        decrypted_text = self.current_decrypt(ciphertext, key)
        self.saes_enderesult_display.setText(decrypted_text)

    # 加密接口，连接S_AES里的函数和窗口里面输入字符的读取
    def encrypt_multiple(self):
        plaintext = self.multiple_plaincipher_input.text()
        key = self.multiple_key_input.text()
        if not all(c in '01' for c in plaintext):
            self.multiple_enderesult_display.setText("错误：二进制明文输入只能包含 0 和 1。")
            return
        if len(plaintext) != 16:
            self.multiple_enderesult_display.setText("错误：输入的二进制明文必须为 16 位。")
            return
        if self.combo_box2.currentIndex() == 0:
            if not all(c in '01' for c in key):
                self.multiple_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
                return
            if len(key) != 32:
                self.multiple_enderesult_display.setText("错误：密钥必须为 32 位。")
                return
        elif self.combo_box2.currentIndex() == 1:
            if not all(c in '01' for c in key):
                self.multiple_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
                return
            if len(key) != 48:
                self.multiple_enderesult_display.setText("错误：密钥必须为 48 位。")
                return

        encrypted_text = self.current_encrypt2(plaintext, key)
        self.multiple_enderesult_display.setText(encrypted_text)

    # 解密接口，连接S_AES里的函数和窗口里面输入字符的读取
    def decrypt_multiple(self):
        ciphertext = self.multiple_plaincipher_input.text()
        key = self.multiple_key_input.text()
        if not all(c in '01' for c in ciphertext):
            self.multiple_enderesult_display.setText("错误：二进制密文输入只能包含 0 和 1。")
            return
        if len(ciphertext) != 16:
            self.multiple_enderesult_display.setText("错误：输入的二进制密文必须为 16 位。")
            return
        if self.combo_box2.currentIndex() == 0:
            if not all(c in '01' for c in key):
                self.multiple_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
                return
            if len(key) != 32:
                self.multiple_enderesult_display.setText("错误：密钥必须为 32 位。")
                return
        elif self.combo_box2.currentIndex() == 1:
            if not all(c in '01' for c in key):
                self.multiple_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
                return
            if len(key) != 48:
                self.multiple_enderesult_display.setText("错误：密钥必须为 48 位。")
                return

        decrypted_text = self.current_decrypt2(ciphertext, key)
        self.multiple_enderesult_display.setText(decrypted_text)

    def encrypt_cbc(self):
        plaintext = self.cbc_plaincipher_input.text()
        key = self.cbc_key_input.text()
        iv = self.cbc_iv_input.text()  # 假设有一个输入框用来输入 IV
        input_type = None
        if self.combo_box3.currentIndex() == 0:  # 二进制模式
            input_type = "binary"
            if not all(c in '01' for c in plaintext):
                self.cbc_enderesult_display.setText("错误：二进制明文输入只能包含 0 和 1。")
                return
            if len(plaintext) != 16:
                self.cbc_enderesult_display.setText("错误：输入的二进制明文必须为 16 位。")
                return
        elif self.combo_box3.currentIndex() == 1:  # ASCII 模式
            input_type = "ascii"
            if not all(0 <= ord(c) < 256 for c in plaintext):
                self.cbc_enderesult_display.setText("错误：请输入正确的 ASCII 字符。")
                return
            if len(plaintext) % 2 != 0:
                self.cbc_enderesult_display.setText("错误：请输入偶数位的 ASCII 字符。")
                return
        elif self.combo_box3.currentIndex() == 2:  # 十六进制模式
            input_type = "unicode"
        # 校验密钥
        if not all(c in '01' for c in key):
            self.cbc_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
            return
        if len(key) != 16:
            self.cbc_enderesult_display.setText("错误：密钥必须为 16 位。")
            return
        # 确保IV的长度和内容有效
        if not all(c in '01' for c in iv):
            self.cbc_enderesult_display.setText("错误：IV只能包含 0 和 1。")
            return
        if len(iv) != 16:
            self.cbc_enderesult_display.setText("错误：IV必须为 16 位。")
            return

        # 执行加密
        encrypted_text = self.current_encrypt3(plaintext, key, iv, input_type)
        self.cbc_enderesult_display.setText(encrypted_text)


    # 解密接口，连接S_AES里的函数和窗口里面输入字符的读取
    def decrypt_cbc(self):
        ciphertext = self.cbc_plaincipher_input.text()
        key = self.cbc_key_input.text()
        iv = self.cbc_iv_input.text()
        input_type = None
        if self.combo_box3.currentIndex() == 0:  # 二进制模式
            input_type = "binary"
            if not all(c in '01' for c in ciphertext):
                self.cbc_enderesult_display.setText("错误：二进制密文输入只能包含 0 和 1。")
                return
            if len(ciphertext) != 16:
                self.cbc_enderesult_display.setText("错误：输入的二进制密文必须为 16 位。")
                return
        elif self.combo_box3.currentIndex() == 1:  # ASCII 模式
            input_type = "ascii"
            if not all(0 <= ord(c) < 256 for c in ciphertext):
                self.cbc_enderesult_display.setText("错误：请输入正确的 ASCII 字符。")
                return
            if len(ciphertext) % 2 != 0:
                self.cbc_enderesult_display.setText("错误：请输入偶数位的 ASCII 字符。")
                return
        elif self.combo_box3.currentIndex() == 2:  # 十六进制模式
            input_type = "unicode"
        # 校验密钥
        if not all(c in '01' for c in key):
            self.cbc_enderesult_display.setText("错误：密钥只能包含 0 和 1。")
            return
        if len(key) != 16:
            self.cbc_enderesult_display.setText("错误：密钥必须为 16 位。")
            return
        # 确保IV的长度和内容有效
        if not all(c in '01' for c in iv):
            self.cbc_enderesult_display.setText("错误：IV只能包含 0 和 1。")
            return
        if len(iv) != 16:
            self.cbc_enderesult_display.setText("错误：IV必须为 16 位。")
            return
        decrypted_text = self.current_decrypt3(ciphertext, key, iv, input_type)
        self.cbc_enderesult_display.setText(decrypted_text)

    # 生成密钥接口，连接S_AES里的函数
    def generate_key(self):
        input = self.bit_length_input.text()
        if not input:  # 如果输入为空
            self.key_display.setText("错误：请输入密钥位数。")
            return
        key = S_AES.generate_key(input)
        self.key_display.setText(key)

    # 生成密钥接口，连接S_AES里的函数
    def generate_iv(self):
        key = S_AES.generate_iv()
        self.iv_display.setText(key)

    # 暴力破解接口，连接S_AES里的函数和窗口里面输入字符的读取
    def force(self):
        plaintext_input = self.force_plaintext_input.toPlainText()
        ciphertext_input = self.force_ciphertext_input.toPlainText()

        # 将输入转换为列表，按照行分割
        plaintext_list = plaintext_input.strip().splitlines()
        ciphertext_list = ciphertext_input.strip().splitlines()
        if len(plaintext_list) != len(ciphertext_list):
            self.force_display.setPlainText('错误：明文和密文的数量不一致。')
            return

        # 检查每个明文和密文是否符合要求
        for plaintext in plaintext_list:
            if len(plaintext) != 16 or not all(c in '01' for c in plaintext):
                self.force_display.setPlainText(f'错误：明文 {plaintext} 必须是16位的01组合。')
                return

        for ciphertext in ciphertext_list:
            if len(ciphertext) != 16 or not all(c in '01' for c in ciphertext):
                self.force_display.setPlainText(f'错误：密文 {ciphertext} 必须是16位的01组合。')
                return

        # 执行中间相遇攻击
        results, elapsed_time = S_AES.middle_attack(plaintext_list, ciphertext_list)
        if results:
            self.force_display.setPlainText('\n'.join(results))
        else:
            self.force_display.setPlainText("未找到任何密钥")
        self.time_display.setText(f"耗时: {elapsed_time:.6f} 秒")

    # 返回，显示首页
    def go_back(self):
        self.show_home()


# 为了打包函数而用
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
