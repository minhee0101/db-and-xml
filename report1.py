import csv
import json
import xml.etree.ElementTree as ET
import sys,datetime,pymysql
from PyQt5.QtWidgets import *


class DB_Utils:

    # SQL 질의문(sql과 params)을 전달받아 실행하는 메소드
    def queryExecutor(self, sql, params):
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:     # dictionary based cursor
                cursor.execute(sql, params)                             # dynamic SQL
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            cursor.close()
            conn.close()

class DB_Queries:
    # 검색문을 각각 하나의 메소드로 정의

    #주문 선택(mainwindw 초기)
    def selectorders(self):
        sql = "select o.orderNo, o.orderDate, o.requiredDate, o.shippedDate, o.status, c.name as customer, o.comments from orders o INNER JOIN customers c on o.customerId = c.customerId"
        params = ()
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql,params=params)
        return rows
    #새로운 주문 선택
    def neworders(self,lastclick,value,contry):
        if value == 'ALL':
            sql = "select o.orderNo, o.orderDate, o.requiredDate, o.shippedDate, o.status, c.name as customer, o.comments from orders o INNER JOIN customers c on o.customerId = c.customerId ORDER BY o.orderNo ASC"
            params = ()
            util = DB_Utils()
            rows = util.queryExecutor(sql=sql, params=params)
            return rows
        if lastclick == 0:
            sql = "select o.orderNo, o.orderDate, o.requiredDate, o.shippedDate, o.status, c.name as customer, o.comments from orders o INNER JOIN customers c on o.customerId = c.customerId WHERE c.name = %s ORDER BY o.orderNo ASC"
        if lastclick == 1:
            sql = "select o.orderNo, o.orderDate, o.requiredDate, o.shippedDate, o.status, c.name as customer, o.comments from orders o INNER JOIN customers c on o.customerId = c.customerId WHERE c.country = %s ORDER BY o.orderNo ASC"
        if lastclick == 2:
            sql = "select o.orderNo, o.orderDate, o.requiredDate, o.shippedDate, o.status, c.name as customer, o.comments from orders o INNER JOIN customers c on o.customerId = c.customerId WHERE c.city = %s ORDER BY o.orderNo ASC"
        params = value
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql,params=params)
        return rows

    #subwindow 초기화면
    def subwindowselectorders(self,orderNo_):
        sql = "select o.orderLineNo, o.productCode, p.name as productName, o.quantity, o.priceEach, o.quantity*o.priceEach as 상품주문액 from orderdetails o INNER JOIN products p on o.productCode = p.productCode WHERE o.orderNo = %s ORDER BY o.orderLineNo ASC"
        params = (orderNo_)
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql, params=params)
        return rows

    #이름콤보박스 종류
    def addnamecombo(self):
        sql = "SELECT NAME FROM CUSTOMERS ORDER BY NAME ASC"
        params = ()
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql, params=params)
        return rows
    #국가콤보박스종류
    def addcountrycombo(self):
        sql = "SELECT COUNTRY FROM CUSTOMERS ORDER BY COUNTRY ASC"
        params = ()
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql, params=params)
        return rows
    #도시콤보박스종류
    def addcitycombo(self,contry):
        if contry != 'ALL':
            sql = "SELECT CITY FROM CUSTOMERS WHERE COUNTRY = %s ORDER BY CITY ASC"
            params = contry
            util = DB_Utils()
            rows = util.queryExecutor(sql=sql, params=params)
            return rows

        sql = "SELECT CITY FROM CUSTOMERS ORDER BY CITY ASC"
        params = ()
        util = DB_Utils()
        rows = util.queryExecutor(sql=sql, params=params)
        return rows

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.positionvalue = None
        self.lastclicked = None
        self.nowcontry = 'ALL'
        self.setupUI1()
        #self.lastclicked

    #초기화면
    def search(self):
        orders = self.query.selectorders()

        self.tablewidget1_1.clearContents()
        self.tablewidget1_1.setRowCount(len(orders))
        self.tablewidget1_1.setColumnCount(len(orders[0]))
        columnNames = list(orders[0].keys())
        self.tablewidget1_1.setHorizontalHeaderLabels(columnNames)
        self.tablewidget1_1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label1_5.setText(str(len(orders))) #order cnt update

        if len(orders):
            for rowIDX, order in enumerate(orders):
                for columnIDX, (k,v) in enumerate(order.items()):
                    if v == None:  # 파이썬이 DB의 널값을 None으로 변환함.
                        continue  # QTableWidgetItem 객체를 생성하지 않음
                    elif isinstance(v, datetime.date):  # QTableWidgetItem 객체 생성
                        item = QTableWidgetItem(v.strftime('%Y-%m-%d'))
                    else:
                        item = QTableWidgetItem(str(v))

                    self.tablewidget1_1.setItem(rowIDX, columnIDX, item)

        self.tablewidget1_1.resizeColumnsToContents()
        self.tablewidget1_1.resizeRowsToContents()

    #기능_초기화버튼 클릭
    def clearbtn_clicked(self):
        self.lastclicked = 0
        self.positionvalue = 'ALL'
        self.nowcontry = 'ALL'

        self.combo1_1.setCurrentIndex(0)
        self.combo1_2.setCurrentIndex(0)
        self.combo1_3.setCurrentIndex(0)

        orders = self.query.neworders(self.lastclicked, self.positionvalue)

        self.tablewidget1_1.clearContents()
        self.tablewidget1_1.setRowCount(len(orders))
        self.tablewidget1_1.setColumnCount(len(orders[0]))
        columnNames = list(orders[0].keys())
        self.tablewidget1_1.setHorizontalHeaderLabels(columnNames)
        self.tablewidget1_1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label1_5.setText(str(len(orders)))  # order cnt update

        if len(orders):
            for rowIDX, order in enumerate(orders):
                for columnIDX, (k, v) in enumerate(order.items()):
                    if v == None:  # 파이썬이 DB의 널값을 None으로 변환함.
                        continue  # QTableWidgetItem 객체를 생성하지 않음
                    elif isinstance(v, datetime.date):  # QTableWidgetItem 객체 생성
                        item = QTableWidgetItem(v.strftime('%Y-%m-%d'))
                    else:
                        item = QTableWidgetItem(str(v))

                    self.tablewidget1_1.setItem(rowIDX, columnIDX, item)

        self.tablewidget1_1.resizeColumnsToContents()
        self.tablewidget1_1.resizeRowsToContents()

    #기능_검색버튼 클릭
    def searchbtn_clicked(self):
        orders = self.query.neworders(self.lastclicked,self.positionvalue,self.nowcontry)
        self.tablewidget1_1.clearContents()
        self.tablewidget1_1.setRowCount(len(orders))

        if len(orders) != 0:
            self.tablewidget1_1.setColumnCount(len(orders[0]))
            columnNames = list(orders[0].keys())
            self.tablewidget1_1.setHorizontalHeaderLabels(columnNames)
            self.tablewidget1_1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.label1_5.setText(str(len(orders)))  # order cnt update

        if len(orders):
            for rowIDX, order in enumerate(orders):
                for columnIDX, (k, v) in enumerate(order.items()):
                    if v == None:  # 파이썬이 DB의 널값을 None으로 변환함.
                        continue  # QTableWidgetItem 객체를 생성하지 않음
                    elif isinstance(v, datetime.date):  # QTableWidgetItem 객체 생성
                        item = QTableWidgetItem(v.strftime('%Y-%m-%d'))
                    else:
                        item = QTableWidgetItem(str(v))

                    self.tablewidget1_1.setItem(rowIDX, columnIDX, item)

        self.tablewidget1_1.resizeColumnsToContents()
        self.tablewidget1_1.resizeRowsToContents()

    #마지막클릭확인
    def customer_clicked(self):
        self.lastclicked = 0
        self.positionvalue = self.combo1_1.currentText()
        #print(self.lastclicked)
    def country_clicked(self):
        self.lastclicked = 1
        self.positionvalue = self.combo1_2.currentText()
        self.nowcontry = self.combo1_2.currentText()
        #print(self.nowcontry)
        self.combo_city(self.nowcontry)
        #print(self.lastclicked)
    def city_clicked(self):
        self.lastclicked = 2
        self.positionvalue = self.combo1_3.currentText()
        #print(self.lastclicked)

    #콤보박스넣기
    def combo_name(self):
        combo_name = self.query.addnamecombo()
        combo_name_item = [row['NAME']for row in combo_name]
        combo_name_item.insert(0,'ALL')
        #print(combo_name_item)
        self.combo1_1.addItems(combo_name_item)
    def combo_country(self):
        combo_country = self.query.addcountrycombo()
        combo_country_item = [row['COUNTRY']for row in combo_country]
        combo_country_item.insert(0,'ALL')
        #print(combo_country_item)
        self.combo1_2.addItems(combo_country_item)

    def combo_city(self,nowcontry):
        if nowcontry == 'ALL':
            self.combo1_3.clear()
            combo_city = self.query.addcitycombo(nowcontry)
            combo_city_item = [row['CITY']for row in combo_city]
            combo_city_item.insert(0,'ALL')
            #print(combo_city_item)
            self.combo1_3.addItems(combo_city_item)
        if nowcontry != 'ALL':
            self.combo1_3.clear()
            combo_city = self.query.addcitycombo(nowcontry)
            combo_city_item = [row['CITY'] for row in combo_city]
            combo_city_item.insert(0, ' ')
            #print(combo_city_item)
            self.combo1_3.addItems(combo_city_item)

    #주문더블클릭
    def tablewidget1_1_duble_click(self):
        row = self.tablewidget1_1.currentIndex().row()
        #print(row)
        ordersample = self.tablewidget1_1.item(row,0).text()
        #print(ordersample)
        dialogue = Subwindow(ordersample)
        dialogue.exec_()

    def setupUI1(self):
        self.query = DB_Queries()
        # 윈도우 설정
        self.setWindowTitle("주문검색")
        self.setGeometry(0, 0, 300, 300)

        # 위젯 생성 (위젯에 move()와 resize()를 사용하지 않음.)
        self.btn1_1 = QPushButton("검색")
        self.btn1_1.clicked.connect(self.searchbtn_clicked)
        self.btn1_2 = QPushButton("초기화")
        self.btn1_2.clicked.connect(self.clearbtn_clicked)

        self.label1_0 = QLabel("주문검색")
        self.label1_1 = QLabel("고객: ")
        self.label1_2 = QLabel("국가: ")
        self.label1_3 = QLabel("도시: ")
        self.label1_4 = QLabel("검색된 주문의 개수: ")
        self.label1_5 = QLabel()  #주문갯수
        self.label_empty = QLabel()

        self.combo1_1 = QComboBox()  #고객
        self.combo1_1.activated.connect(self.customer_clicked)
        self.combo1_2 = QComboBox()  #국가
        self.combo1_2.activated.connect(self.country_clicked)
        self.combo1_3 = QComboBox()  #도시
        self.combo1_3.activated.connect(self.city_clicked)

        self.tablewidget1_1 = QTableWidget(self)
        self.tablewidget1_1.doubleClicked.connect(self.tablewidget1_1_duble_click)

        #기능구현
        #self.btn1_2.clickedconnect(self.clearbtn_clicked) #초기화 버튼

        # 레이아웃의 생성, 위젯 연결
        layout1 = QVBoxLayout()   #전체
        layout1_1 = QGridLayout()   #고객줄
        layout1_2 = QGridLayout()   #검색된줄
        layout1_3 = QVBoxLayout()   #1_1+1_2
        layout1_4 = QVBoxLayout()    #버튼들
        layout1_5 = QHBoxLayout()   # 1_3+1_4
        layout_empty = QVBoxLayout()  #예쁜 UI를 위한 빈공간

        layout1_1.addWidget(self.label1_1,0,0) #고객
        layout1_1.addWidget(self.combo1_1,0,1) #고객콤보박스
        layout1_1.addWidget(self.label1_2,0,2) #국가
        layout1_1.addWidget(self.combo1_2,0,3) #국가콤보박스
        layout1_1.addWidget(self.label1_3,0,4) #도시
        layout1_1.addWidget(self.combo1_3,0,5) #도시콤보박스
        #layout1.addWidget(self.btn1,0,6)

        layout1_2.addWidget(self.label1_4,0,0)
        layout1_2.addWidget(self.label1_5,0, 1)
        #layout2.addWidget(self.btn2, 0, 2)

        layout1_3.addLayout(layout1_1)
        layout1_3.addLayout(layout1_2)

        layout1_4.addWidget(self.btn1_1)
        layout1_4.addWidget(self.btn1_2)
        #layout4.addStretch()

        layout_empty.addWidget(self.label_empty)

        layout1_5.addLayout(layout1_3)
        layout1_5.addLayout(layout_empty)
        layout1_5.addLayout(layout1_4)

        layout1.addWidget(self.label1_0)
        layout1.addLayout(layout1_5)
        #layout.addLayout(layout2)
        layout1.addWidget(self.tablewidget1_1) #table widget

        #layout.addWidget(self.btnQuit)
        #--------------------------------------------------------

        #기능함수들
        self.search()
        self.combo_name()
        self.combo_city(self.nowcontry)
        self.combo_country()

        # 레이아웃 설정
        self.setLayout(layout1)

class Subwindow(QDialog):
    def __init__(self,orderNo):
        super().__init__()
        self.lastclikcktype = 0
        #print('goodggod')
        self.orderNo_ = orderNo
        self.setupUI2()

    #초기화면
    def orderdetails(self):
        details = self.query.subwindowselectorders(self.orderNo_)

        self.tablewidget2_1.clearContents()
        self.tablewidget2_1.setRowCount(len(details))
        self.tablewidget2_1.setColumnCount(len(details[0]))
        columnNames = list(details[0].keys())
        self.tablewidget2_1.setHorizontalHeaderLabels(columnNames)
        self.tablewidget2_1.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #요기 주문번호 어케 받아오지???
        self.label2_2.setText(str(self.orderNo_)) #주문번호 Update
        self.label2_4.setText(str(len(details))) #상품개수 update  #??이거 마증ㅁ??
        #print(details)
        self.allmoney = 0
        for i in range(len(details)) :
            #print(self.allmoney)
            self.allmoney += details[i]['상품주문액']
        self.label2_6.setText(str(self.allmoney)) #주문액 Update

        if len(details):
            for rowIDX, order in enumerate(details):
                for columnIDX, (k,v) in enumerate(order.items()):
                    if v == None:  # 파이썬이 DB의 널값을 None으로 변환함.
                        continue  # QTableWidgetItem 객체를 생성하지 않음
                    elif isinstance(v, datetime.date):  # QTableWidgetItem 객체 생성
                        item = QTableWidgetItem(v.strftime('%Y-%m-%d'))
                    else:
                        item = QTableWidgetItem(str(v))

                    self.tablewidget2_1.setItem(rowIDX, columnIDX, item)

        self.tablewidget2_1.resizeColumnsToContents()
        self.tablewidget2_1.resizeRowsToContents()

    def setupUI2(self):
        self.query = DB_Queries()
        # 윈도우 설정
        self.setWindowTitle("주문상세내역")
        self.setGeometry(0, 0, 300, 300)

        # 위젯 생성 (위젯에 move()와 resize()를 사용하지 않음.)
        self.label2_0 = QLabel("주문검색")
        self.label2_1 = QLabel("주문번호")
        self.label2_2 = QLabel()  #주문번호
        self.label2_3 = QLabel("상품개수")
        self.label2_4 = QLabel()  #상품개수
        self.label2_5 = QLabel("주문액")
        self.label2_6 = QLabel()  #주문액
        self.label2_7 = QLabel("파일출력")

        self.tablewidget2_1 = QTableWidget()

        self.radioBtn2_1 = QRadioButton("CSV")
        self.radioBtn2_1.setChecked(True)
        self.radioBtn2_1.clicked.connect(self.radiobtn2_1_clicked)
        self.radioBtn2_2 = QRadioButton("JSON")
        self.radioBtn2_2.clicked.connect(self.radiobtn2_2_clicked)
        self.radioBtn2_3 = QRadioButton("XML")
        self.radioBtn2_3.clicked.connect(self.radiobtn2_3_clicked)

        self.btn2_1 = QPushButton("저장")
        self.btn2_1.clicked.connect(self.save_clicked)

        # 레이아웃의 생성, 위젯 연결
        layout2 = QVBoxLayout()  # 전체
        layout2_1 = QHBoxLayout() # 주문번호줄
        layout2_2 = QHBoxLayout() # csv,json,xml 선택줄

        layout2_1.addWidget(self.label2_1)
        layout2_1.addWidget(self.label2_2)
        layout2_1.addWidget(self.label2_3)
        layout2_1.addWidget(self.label2_4)
        layout2_1.addWidget(self.label2_5)
        layout2_1.addWidget(self.label2_6)

        layout2_2.addWidget(self.radioBtn2_1)
        layout2_2.addWidget(self.radioBtn2_2)
        layout2_2.addWidget(self.radioBtn2_3)

        layout2.addWidget(self.label2_0)
        layout2.addLayout(layout2_1)
        layout2.addWidget(self.tablewidget2_1)
        layout2.addWidget(self.label2_7)
        layout2.addLayout(layout2_2)
        layout2.addWidget(self.btn2_1)

        #합수들
        self.orderdetails()
        self.save_clicked()

        # 레이아웃 설정
        self.setLayout(layout2)

        ########################################
    def radiobtn2_1_clicked(self):
        self.lastclikcktype =0
        #print(self.lastclikcktype)
    def radiobtn2_2_clicked(self):
        self.lastclikcktype =1
        #print(self.lastclikcktype)
    def radiobtn2_3_clicked(self):
        self.lastclikcktype =2
        #print(self.lastclikcktype)

    def save_clicked(self):
        # DB 검색문 실행
        query = DB_Queries()
        rows = query.subwindowselectorders(self.orderNo_)  # rows는 딕셔너리의 리스트
        # print(rows)
        # print()

        if self.lastclikcktype == 0:
        # CSV 화일을 쓰기 모드로 생성
            with open('{0}.csv'.format(self.orderNo_), 'w', encoding='utf-8', newline='') as f:
                wr = csv.writer(f)

                # 테이블 헤더를 출력
                columnNames = list(rows[0].keys())
                #print(columnNames)
                # print()
                wr.writerow(columnNames)

                # 테이블 내용을 출력
                for row in rows:  # row는 딕셔너리
                    player = list(row.values())  # player는 리스트
                    #print(player)
                    wr.writerow(player)
                    # 날짜 변환 기능을 csv 패키지에서 제공함.

        if self.lastclikcktype == 1:
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, datetime.date):
                        row[k] = v.strftime('%Y-%m-%d')  # 키가 k인 item의 값 v를 수정
                        #print(row[k])
                    if not isinstance(v, str):
                        row[k] = str(v)  # 키가 k인 item의 값 v를 수정
                        #print(row[k])
                #print(row)
            #print()

            newDict = dict(details=rows)  # key: playerGK, value: players
            #print(newDict)

            # JSON 화일에 쓰기
            # dump()에 의해 모든 작은 따옴표('')는 큰 따옴표("")로 변환됨
            with open('{0}.json'.format(self.orderNo_), 'w', encoding='utf-8') as f:
                json.dump(newDict, f, ensure_ascii=False)  # dump to JSON file

            with open('{0}_indent.json'.format(self.orderNo_), 'w', encoding='utf-8') as f:
                json.dump(newDict, f, indent=4, ensure_ascii=False)

        if self.lastclikcktype == 2:
            # 애트리뷰트 BIRTH_DATE의 값을 MySQL datetime 타입에서 스트링으로 변환함. (CSV에서는 패키지가 변환하였음.)
            for row in rows:
                for k, v in row.items():
                    if isinstance(v, datetime.date):
                        row[k] = v.strftime('%Y-%m-%d')  # 키가 k인 item의 값 v를 수정
                    if not isinstance(v, str):
                        row[k] = str(v)  # 키가 k인 item의 값 v를 수정

            newDict = dict(details=rows)
            #print(newDict)

            # XDM 트리 생성
            tableName = list(newDict.keys())[0]  # 'playerGK'
            tableRows = list(newDict.values())[0]  # 딕셔너리의 리스트

            rootElement = ET.Element('Table')
            rootElement.attrib['name'] = tableName

            for row in tableRows:
                rowElement = ET.Element('Row')
                rootElement.append(rowElement)

                for columnName in list(row.keys()):
                    if row[columnName] is None:  # NICKNAME, JOIN_YYYY, NATION 처리
                        rowElement.attrib[columnName] = ''
                    elif type(row[columnName]) == int:  # BACK_NO, HEIGHT, WEIGHT 처리
                        rowElement.attrib[columnName] = str(row[columnName])
                    else:
                        rowElement.attrib[columnName] = row[columnName]

            # XDM 트리를 화일에 출력
            ET.ElementTree(rootElement).write('{0}.xml'.format(self.orderNo_), encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()