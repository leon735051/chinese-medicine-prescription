
import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QHeaderView
from PyQt5.QtCore import Qt, QDate, QTimer

class PrescriptionManager(QDialog):
    def __init__(self, db_manager, customer_id, customer_name, parent=None):
        super(PrescriptionManager, self).__init__(parent)
        
        # 載入UI檔案
        uic.loadUi('prescription_form.ui', self)
        
        # 保存資料庫管理器和客戶資料
        self.db = db_manager
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.parent_window = parent
        self.current_selected_item_id = None  # 當前選中的項目ID
        self.current_selected_item_type = None  # 當前選中的項目類型 (formula/herb/secret)
        
        # 設定視窗標題
        self.setWindowTitle(f"中藥處方好幫手 - 開立處方 ({customer_name})")
        
        # 初始化UI
        self.init_ui()
        
        # 綁定事件
        self.bind_events()
        
        # 載入初始資料
        self.load_initial_data()
        
        # 設定計時器更新時間
        self.setup_timer()
        
        # 設置表格的自適應寬度
        self.setup_table_headers()
    
    def setup_timer(self):
        """設定計時器每秒更新當前時間"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_datetime)
        self.timer.start(1000)  # 每秒更新一次
        self.update_current_datetime()  # 立即更新一次
    
    def update_current_datetime(self):
        """更新當前日期時間"""
        current_datetime = datetime.datetime.now()
        datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        self.currentDateTimeLineEdit.setText(datetime_str)
    
    def calculate_age(self, birthday):
        """計算年齡"""
        if not birthday:
            return ""
        
        try:
            today = datetime.date.today()
            age = today.year - birthday.year
            
            # 檢查是否還沒到生日
            if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day):
                age -= 1
                
            return str(age)
        except:
            return ""
    
    def load_customer_data(self):
        """載入客戶詳細資料"""
        try:
            query = """
            SELECT name, birthday 
            FROM customers 
            WHERE id = %s
            """
            result = self.db.execute_query(query, (self.customer_id,))
            
            if result:
                customer = result[0]
                self.customer_name = customer['name']
                
                # 計算年齡
                age = self.calculate_age(customer['birthday'])
                self.patientAgeLineEdit.setText(age)
                
                # 計算抓藥次數（歷史記錄數量）
                count_query = "SELECT COUNT(*) as count FROM records WHERE customer_id = %s"
                count_result = self.db.execute_query(count_query, (self.customer_id,))
                prescription_count = count_result[0]['count'] + 1 if count_result else 1  # +1是因為即將新增一筆
                self.prescriptionCountLineEdit.setText(str(prescription_count))
                
        except Exception as e:
            print(f"載入客戶資料時發生錯誤: {e}")
    
    def setup_table_headers(self):
        """設置所有表格表頭的自適應寬度"""
        # 設置處方表格的列寬自適應
        prescription_header = self.prescriptionTableWidget.horizontalHeader()
        prescription_header.setSectionResizeMode(0, QHeaderView.Stretch)           # 方劑名/藥材名
        prescription_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 組成
        prescription_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 數量
        prescription_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 單位
        
        # 設置方劑選擇表格
        formula_header = self.formulaListTableWidget.horizontalHeader()
        formula_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
        formula_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 品名
        
        # 設置單味藥選擇表格
        herb_header = self.herbListTableWidget.horizontalHeader()
        herb_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
        herb_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 品名
        
        # 設置秘方選擇表格
        if hasattr(self, 'secretListTableWidget'):
            secret_header = self.secretListTableWidget.horizontalHeader()
            secret_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
            secret_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 品名
        
        # 設置歷史記錄表格
        history_header = self.historyPrescriptionsTableWidget.horizontalHeader()
        history_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 日期時間
        history_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 主訴
        history_header.setSectionResizeMode(2, QHeaderView.Stretch)           # 判斷
        history_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 狀態
        
        # 設置歷史藥單詳細內容表格
        if hasattr(self, 'historyDetailTableWidget'):
            detail_header = self.historyDetailTableWidget.horizontalHeader()
            detail_header.setSectionResizeMode(0, QHeaderView.Stretch)           # 方劑名/藥材名
            detail_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 組成
            detail_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 數量
            detail_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 單位
    
    def init_ui(self):
        """初始化UI設定"""
        # 設定病患資料
        self.patientIdLineEdit.setText(str(self.customer_id))
        self.patientNameLineEdit.setText(self.customer_name)
        
        # 載入客戶詳細資料（包含年齡和抓藥次數）
        self.load_customer_data()
        
        # 設定資訊類型選單的預設值
        if hasattr(self, 'infoTypeComboBox'):
            self.infoTypeComboBox.setCurrentIndex(3)  # 預設選擇"主治"
    
    def bind_events(self):
        """綁定事件處理器"""
        # 處方相關按鈕
        self.clearPrescriptionButton.clicked.connect(self.clear_prescription)
        self.deletePrescriptionItemButton.clicked.connect(self.delete_prescription_item)
        self.storePrescriptionButton.clicked.connect(self.store_prescription)
        self.printPrescriptionButton.clicked.connect(self.print_prescription)
        
        # 搜尋按鈕
        self.formulaSearchButton.clicked.connect(self.search_formula)
        self.herbSearchButton.clicked.connect(self.search_herb)
        if hasattr(self, 'secretSearchButton'):
            self.secretSearchButton.clicked.connect(self.search_secret_formula)
        
        # 搜尋輸入框按下Enter鍵
        self.formulaSearchLineEdit.returnPressed.connect(self.search_formula)
        self.herbSearchLineEdit.returnPressed.connect(self.search_herb)
        if hasattr(self, 'secretSearchLineEdit'):
            self.secretSearchLineEdit.returnPressed.connect(self.search_secret_formula)
        
        # 加入處方按鈕
        self.addToPrescriptionButton.clicked.connect(self.add_to_prescription)
        if hasattr(self, 'addToPowderButton'):
            self.addToPowderButton.clicked.connect(self.add_to_powder)
        
        # 歷史記錄按鈕
        self.loadHistoryButton.clicked.connect(self.load_history_prescriptions)
        self.copyHistoryButton.clicked.connect(self.copy_history_prescription)
        
        # 雙擊藥材列表加入處方
        self.formulaListTableWidget.itemDoubleClicked.connect(self.add_formula_to_prescription)
        self.herbListTableWidget.itemDoubleClicked.connect(self.add_herb_to_prescription)
        if hasattr(self, 'secretListTableWidget'):
            self.secretListTableWidget.itemDoubleClicked.connect(self.add_secret_to_prescription)
        
        # 表格選擇事件 - 顯示詳細資訊
        self.formulaListTableWidget.itemClicked.connect(self.show_formula_info)
        self.herbListTableWidget.itemClicked.connect(self.show_herb_info)
        if hasattr(self, 'secretListTableWidget'):
            self.secretListTableWidget.itemClicked.connect(self.show_secret_info)
        
        # 歷史記錄選擇事件
        self.historyPrescriptionsTableWidget.itemClicked.connect(self.show_history_prescription_detail)
        
        # 處方表格編輯
        self.prescriptionTableWidget.itemChanged.connect(self.prescription_item_changed)
        
        # 資訊類型選單變更事件
        if hasattr(self, 'infoTypeComboBox'):
            self.infoTypeComboBox.currentTextChanged.connect(self.update_selected_info)
    
    def load_initial_data(self):
        """載入初始資料"""
        # 載入所有方劑
        self.load_all_formulas()
        # 載入所有單味藥
        self.load_all_herbs()
        # 載入所有秘方
        self.load_all_secret_formulas()
        # 載入病患歷史記錄
        self.load_history_prescriptions()
    
    def load_all_formulas(self):
        """載入所有方劑到列表"""
        try:
            self.formulaListTableWidget.setRowCount(0)
            formulas = self.db.execute_query("SELECT id, name FROM formulas WHERE id NOT LIKE 'S%' ORDER BY id")
            
            if formulas:
                for row, formula in enumerate(formulas):
                    self.formulaListTableWidget.insertRow(row)
                    self.formulaListTableWidget.setItem(row, 0, QTableWidgetItem(str(formula['id'])))
                    self.formulaListTableWidget.setItem(row, 1, QTableWidgetItem(formula['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"無法載入方劑列表: {e}")
    
    def load_all_herbs(self):
        """載入所有單味藥到列表"""
        try:
            self.herbListTableWidget.setRowCount(0)
            herbs = self.db.execute_query("SELECT id, name FROM medicines ORDER BY id")
            
            if herbs:
                for row, herb in enumerate(herbs):
                    self.herbListTableWidget.insertRow(row)
                    self.herbListTableWidget.setItem(row, 0, QTableWidgetItem(str(herb['id'])))
                    self.herbListTableWidget.setItem(row, 1, QTableWidgetItem(herb['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"無法載入藥材列表: {e}")
    
    def load_all_secret_formulas(self):
        """載入所有秘方到列表"""
        if not hasattr(self, 'secretListTableWidget'):
            return
        
        try:
            self.secretListTableWidget.setRowCount(0)
            # 查詢獨立的 secret_formulas 表格
            secrets = self.db.execute_query("SELECT id, name FROM secret_formulas ORDER BY id")
            
            if secrets:
                for row, secret in enumerate(secrets):
                    self.secretListTableWidget.insertRow(row)
                    self.secretListTableWidget.setItem(row, 0, QTableWidgetItem(str(secret['id'])))
                    self.secretListTableWidget.setItem(row, 1, QTableWidgetItem(secret['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"無法載入秘方列表: {e}")
    
    def load_history_prescriptions(self):
        """載入病患歷史處方記錄"""
        try:
            self.historyPrescriptionsTableWidget.setRowCount(0)
            query = """
            SELECT DISTINCT r.record_date, r.id as record_id, r.description, r.judgment
            FROM records r
            WHERE r.customer_id = %s
            ORDER BY r.record_date DESC
            LIMIT 20
            """
            records = self.db.execute_query(query, (self.customer_id,))
            
            if records:
                for row, record in enumerate(records):
                    self.historyPrescriptionsTableWidget.insertRow(row)
                    
                    # 日期格式化 - 加上時間
                    if record['record_date']:
                        if hasattr(record['record_date'], 'strftime'):
                            # 如果是 datetime 對象
                            date_str = record['record_date'].strftime('%Y-%m-%d %H:%M')
                        else:
                            # 如果是 date 對象，補上時間
                            date_str = f"{record['record_date']} 00:00"
                    else:
                        date_str = ""
                    
                    self.historyPrescriptionsTableWidget.setItem(row, 0, QTableWidgetItem(date_str))
                    self.historyPrescriptionsTableWidget.setItem(row, 1, QTableWidgetItem(record['description'] or ""))
                    self.historyPrescriptionsTableWidget.setItem(row, 2, QTableWidgetItem(record['judgment'] or ""))
                    self.historyPrescriptionsTableWidget.setItem(row, 3, QTableWidgetItem(""))  # 空的狀態欄
                    
                    # 在第一個項目中隱藏地儲存record_id，供後續使用
                    item = self.historyPrescriptionsTableWidget.item(row, 0)
                    item.setData(Qt.UserRole, record['record_id'])
        
        except Exception as e:
            print(f"載入歷史處方時發生錯誤: {e}")
    
    def show_history_prescription_detail(self, item):
        """顯示選中歷史處方的詳細內容"""
        if not hasattr(self, 'historyDetailTableWidget'):
            return
            
        row = item.row()
        # 從UserRole中獲取record_id
        date_item = self.historyPrescriptionsTableWidget.item(row, 0)
        record_id = date_item.data(Qt.UserRole)
        
        try:
            # 清空詳細內容表格
            self.historyDetailTableWidget.setRowCount(0)
            
            # 直接根據 record_id 查詢該記錄的處方明細
            query = """
            SELECT prescription_name, composition, quantity, unit
            FROM prescriptions
            WHERE record_id = %s
            ORDER BY id
            """
            prescriptions = self.db.execute_query(query, (record_id,))
            
            if prescriptions:
                for detail_row, prescription in enumerate(prescriptions):
                    self.historyDetailTableWidget.insertRow(detail_row)
                    
                    self.historyDetailTableWidget.setItem(detail_row, 0, QTableWidgetItem(prescription['prescription_name'] or ""))
                    self.historyDetailTableWidget.setItem(detail_row, 1, QTableWidgetItem(prescription['composition'] or ""))
                    self.historyDetailTableWidget.setItem(detail_row, 2, QTableWidgetItem(str(prescription['quantity'] or "")))
                    self.historyDetailTableWidget.setItem(detail_row, 3, QTableWidgetItem(prescription['unit'] or ""))
            else:
                # 如果沒有找到處方，顯示提示訊息
                self.historyDetailTableWidget.insertRow(0)
                self.historyDetailTableWidget.setItem(0, 0, QTableWidgetItem("此記錄無處方明細"))
                self.historyDetailTableWidget.setItem(0, 1, QTableWidgetItem(""))
                self.historyDetailTableWidget.setItem(0, 2, QTableWidgetItem(""))
                self.historyDetailTableWidget.setItem(0, 3, QTableWidgetItem(""))
        
        except Exception as e:
            print(f"載入歷史處方詳細內容時發生錯誤: {e}")
    
    def copy_history_prescription(self):
        """引用歷史藥單"""
        if not hasattr(self, 'historyDetailTableWidget'):
            QMessageBox.warning(self, "警告", "請先選擇歷史處方記錄查看詳細內容")
            return
            
        # 檢查是否有選中的歷史處方詳細內容
        if self.historyDetailTableWidget.rowCount() == 0:
            QMessageBox.warning(self, "警告", "請先選擇歷史處方記錄查看詳細內容")
            return
        
        # 檢查是否是"此記錄無處方明細"的提示行
        first_item = self.historyDetailTableWidget.item(0, 0)
        if first_item and first_item.text() == "此記錄無處方明細":
            QMessageBox.warning(self, "警告", "選中的記錄沒有處方明細可以引用")
            return
        
        # 將歷史處方詳細內容複製到當前處方
        for row in range(self.historyDetailTableWidget.rowCount()):
            prescription_name = self.historyDetailTableWidget.item(row, 0).text()
            composition = self.historyDetailTableWidget.item(row, 1).text()
            quantity = self.historyDetailTableWidget.item(row, 2).text()
            unit = self.historyDetailTableWidget.item(row, 3).text()
            
            # 加入到當前處方
            if prescription_name:  # 確保有有效的處方名稱
                self.add_item_to_prescription(f"HIST_{row}", prescription_name, composition, 
                                            int(quantity) if quantity.isdigit() else 1, unit)
        
        QMessageBox.information(self, "成功", "歷史藥單已加入當前處方")
    
    def show_formula_info(self, item):
        """顯示方劑詳細資訊"""
        row = item.row()
        formula_id = self.formulaListTableWidget.item(row, 0).text()
        
        self.current_selected_item_id = formula_id
        self.current_selected_item_type = "formula"
        self.update_selected_info()
    
    def show_herb_info(self, item):
        """顯示單味藥詳細資訊"""
        row = item.row()
        herb_id = self.herbListTableWidget.item(row, 0).text()
        
        self.current_selected_item_id = herb_id
        self.current_selected_item_type = "herb"
        self.update_selected_info()
    
    def show_secret_info(self, item):
        """顯示秘方詳細資訊"""
        if not hasattr(self, 'secretListTableWidget'):
            return
            
        row = item.row()
        secret_id = self.secretListTableWidget.item(row, 0).text()
        
        self.current_selected_item_id = secret_id
        self.current_selected_item_type = "secret"
        self.update_selected_info()
    
    def update_selected_info(self):
        """根據選中的資訊類型更新顯示內容"""
        if not hasattr(self, 'infoTypeComboBox') or not hasattr(self, 'selectedInfoTextEdit'):
            return
            
        if not self.current_selected_item_id or not self.current_selected_item_type:
            self.selectedInfoTextEdit.clear()
            return
        
        info_type = self.infoTypeComboBox.currentText()
        
        try:
            if self.current_selected_item_type == "formula":
                # 方劑
                query = "SELECT origin_text, composition, effect, indication, application, warnings_side_effects FROM formulas WHERE id = %s"
                result = self.db.execute_query(query, (self.current_selected_item_id,))
            elif self.current_selected_item_type == "secret":
                # 秘方
                query = "SELECT origin_text, composition, effect, indication, application, warnings_side_effects FROM secret_formulas WHERE id = %s"
                result = self.db.execute_query(query, (self.current_selected_item_id,))
            elif self.current_selected_item_type == "herb":
                # 單味藥
                query = "SELECT origin_text, nature_flavor as composition, effect, indication, application, warnings_side_effects FROM medicines WHERE id = %s"
                result = self.db.execute_query(query, (self.current_selected_item_id,))
            else:
                return
            
            if result:
                data = result[0]
                
                if info_type == "出典":
                    content = data['origin_text'] or ""
                elif info_type == "組成":
                    content = data['composition'] or ""
                elif info_type == "功能":
                    content = data['effect'] or ""
                elif info_type == "主治":
                    content = data['indication'] or ""
                elif info_type == "應用":
                    content = data['application'] or ""
                elif info_type == "注意事項":
                    content = data.get('warnings_side_effects', '') or ""
                else:
                    content = ""
                
                self.selectedInfoTextEdit.setPlainText(content)
            else:
                self.selectedInfoTextEdit.clear()
        
        except Exception as e:
            print(f"載入詳細資訊時發生錯誤: {e}")
            self.selectedInfoTextEdit.clear()
    
    def search_formula(self):
        """搜尋方劑"""
        search_text = self.formulaSearchLineEdit.text().strip()
        
        if not search_text:
            self.load_all_formulas()
            return
        
        try:
            # 同時搜尋品號和名稱，排除秘方（S開頭）
            query = "SELECT id, name FROM formulas WHERE (id LIKE %s OR name LIKE %s) AND id NOT LIKE 'S%' ORDER BY id"
            formulas = self.db.execute_query(query, (f'%{search_text}%', f'%{search_text}%'))
            
            self.formulaListTableWidget.setRowCount(0)
            if formulas:
                for row, formula in enumerate(formulas):
                    self.formulaListTableWidget.insertRow(row)
                    self.formulaListTableWidget.setItem(row, 0, QTableWidgetItem(str(formula['id'])))
                    self.formulaListTableWidget.setItem(row, 1, QTableWidgetItem(formula['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"搜尋方劑時發生錯誤: {e}")
    
    def search_herb(self):
        """搜尋單味藥"""
        search_text = self.herbSearchLineEdit.text().strip()
        
        if not search_text:
            self.load_all_herbs()
            return
        
        try:
            # 同時搜尋品號和名稱
            query = "SELECT id, name FROM medicines WHERE id LIKE %s OR name LIKE %s ORDER BY id"
            herbs = self.db.execute_query(query, (f'%{search_text}%', f'%{search_text}%'))
            
            self.herbListTableWidget.setRowCount(0)
            if herbs:
                for row, herb in enumerate(herbs):
                    self.herbListTableWidget.insertRow(row)
                    self.herbListTableWidget.setItem(row, 0, QTableWidgetItem(str(herb['id'])))
                    self.herbListTableWidget.setItem(row, 1, QTableWidgetItem(herb['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"搜尋藥材時發生錯誤: {e}")
    
    def search_secret_formula(self):
        """搜尋秘方"""
        if not hasattr(self, 'secretSearchLineEdit') or not hasattr(self, 'secretListTableWidget'):
            return
            
        search_text = self.secretSearchLineEdit.text().strip()
        
        if not search_text:
            self.load_all_secret_formulas()
            return
        
        try:
            # 同時搜尋品號和名稱
            query = "SELECT id, name FROM secret_formulas WHERE id LIKE %s OR name LIKE %s ORDER BY id"
            secrets = self.db.execute_query(query, (f'%{search_text}%', f'%{search_text}%'))
            
            self.secretListTableWidget.setRowCount(0)
            if secrets:
                for row, secret in enumerate(secrets):
                    self.secretListTableWidget.insertRow(row)
                    self.secretListTableWidget.setItem(row, 0, QTableWidgetItem(str(secret['id'])))
                    self.secretListTableWidget.setItem(row, 1, QTableWidgetItem(secret['name'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"搜尋秘方時發生錯誤: {e}")
    
    def add_formula_to_prescription(self, item):
        """雙擊方劑加入處方"""
        row = item.row()
        formula_id = self.formulaListTableWidget.item(row, 0).text()
        formula_name = self.formulaListTableWidget.item(row, 1).text()
        
        # 查詢方劑組成
        try:
            query = "SELECT composition FROM formulas WHERE id = %s"
            result = self.db.execute_query(query, (formula_id,))
            composition = result[0]['composition'] if result else ""
            
            # 加入處方（使用固定單位"包"）
            self.add_item_to_prescription(formula_id, formula_name, composition, 
                                        self.quantitySpinBox.value(), "包")
        
        except Exception as e:
            QMessageBox.critical(self, "資料庫錯誤", f"加入方劑時發生錯誤: {e}")
    
    def add_herb_to_prescription(self, item):
        """雙擊單味藥加入處方"""
        row = item.row()
        herb_id = self.herbListTableWidget.item(row, 0).text()
        herb_name = self.herbListTableWidget.item(row, 1).text()
        
        # 加入處方（使用固定單位"錢"）
        self.add_item_to_prescription(herb_id, herb_name, "", 
                                    self.quantitySpinBox.value(), "錢")
    
    def add_secret_to_prescription(self, item):
            """雙擊秘方加入處方"""
            if not hasattr(self, 'secretListTableWidget'):
                return
                
            row = item.row()
            secret_id = self.secretListTableWidget.item(row, 0).text()
            secret_name = self.secretListTableWidget.item(row, 1).text()
            
            # 查詢秘方組成
            try:
                query = "SELECT composition FROM secret_formulas WHERE id = %s"
                result = self.db.execute_query(query, (secret_id,))
                composition = result[0]['composition'] if result else ""
                
                # 加入處方（使用固定單位"包"）
                self.add_item_to_prescription(secret_id, secret_name, composition, 
                                            self.quantitySpinBox.value(), "包")
            
            except Exception as e:
                QMessageBox.critical(self, "資料庫錯誤", f"加入秘方時發生錯誤: {e}")
    
    def add_to_prescription(self):
        """加入選中的藥材到處方"""
        current_tab = self.medicineTabWidget.currentIndex()
        
        if current_tab == 0:  # 方劑頁籤
            current_item = self.formulaListTableWidget.currentItem()
            if current_item:
                self.add_formula_to_prescription(current_item)
        elif current_tab == 1:  # 單味藥頁籤
            current_item = self.herbListTableWidget.currentItem()
            if current_item:
                self.add_herb_to_prescription(current_item)
        elif current_tab == 2 and hasattr(self, 'secretListTableWidget'):  # 秘方頁籤
            current_item = self.secretListTableWidget.currentItem()
            if current_item:
                self.add_secret_to_prescription(current_item)
    
    def add_to_powder(self):
        """加入到粉劑丸錠（待實現）"""
        QMessageBox.information(self, "功能提示", "粉劑丸錠功能將在後續版本中實現")
    
    def add_item_to_prescription(self, item_id, name, composition, quantity, unit):
        """加入項目到處方表格"""
        # 檢查是否已存在（根據名稱比較）
        for row in range(self.prescriptionTableWidget.rowCount()):
            if self.prescriptionTableWidget.item(row, 0).text() == name:
                # 如果已存在，更新數量
                current_qty = int(self.prescriptionTableWidget.item(row, 2).text())
                self.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(current_qty + quantity)))
                return
        
        # 新增一行
        row = self.prescriptionTableWidget.rowCount()
        self.prescriptionTableWidget.insertRow(row)
        
        # 設定項目資料
        self.prescriptionTableWidget.setItem(row, 0, QTableWidgetItem(name))
        self.prescriptionTableWidget.setItem(row, 1, QTableWidgetItem(composition))
        self.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(quantity)))
        self.prescriptionTableWidget.setItem(row, 3, QTableWidgetItem(unit))
        
        # 更新總價
        self.update_total_price()
    
    def prescription_item_changed(self, item):
        """處方項目變更時更新總價"""
        if item.column() == 2:  # 數量欄位
            self.update_total_price()
    
    def update_total_price(self):
        """更新總價（這裡先用簡單的計算）"""
        # 這裡可以根據實際需求計算總價
        # 暫時先顯示項目數量
        total_items = self.prescriptionTableWidget.rowCount()
        self.priceLineEdit.setText(f"{total_items * 100}")  # 假設每項100元
    
    def clear_prescription(self):
        """清除處方"""
        reply = QMessageBox.question(self, "確認清除", 
                                   "確定要清除目前的處方內容嗎？",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.prescriptionTableWidget.setRowCount(0)
            self.priceLineEdit.clear()
            if hasattr(self, 'chiefComplaintTextEdit'):
                self.chiefComplaintTextEdit.clear()
            if hasattr(self, 'diagnosisTextEdit'):
                self.diagnosisTextEdit.clear()
            if hasattr(self, 'selectedInfoTextEdit'):
                self.selectedInfoTextEdit.clear()
    
    def delete_prescription_item(self):
        """刪除選中的處方項目"""
        current_row = self.prescriptionTableWidget.currentRow()
        
        if current_row >= 0:
            self.prescriptionTableWidget.removeRow(current_row)
            self.update_total_price()
        else:
            QMessageBox.warning(self, "警告", "請先選擇要刪除的項目")
    
    def store_prescription(self):
        """儲存處方"""
        if self.prescriptionTableWidget.rowCount() == 0:
            QMessageBox.warning(self, "警告", "處方內容不能為空")
            return
        
        try:
            # 確保沒有進行中的事務
            try:
                self.db.connection.rollback()
            except:
                pass
            
            # 獲取處方日期時間（使用當前時間）
            prescription_datetime = datetime.datetime.now()
            
            # 獲取診療記錄
            chief_complaint = ""
            diagnosis = ""
            
            if hasattr(self, 'chiefComplaintTextEdit'):
                chief_complaint = self.chiefComplaintTextEdit.toPlainText().strip()
            if hasattr(self, 'diagnosisTextEdit'):
                diagnosis = self.diagnosisTextEdit.toPlainText().strip()
            
            price = self.priceLineEdit.text().strip()
            
            # 開始新的事務
            self.db.connection.start_transaction()
            
            # 插入記錄
            record_query = """
            INSERT INTO records (customer_id, record_date, price, description, judgment)
            VALUES (%s, %s, %s, %s, %s)
            """
            record_values = (self.customer_id, prescription_datetime, price or 0, 
                           chief_complaint, diagnosis)
            
            if not self.db.execute_insert_update_delete(record_query, record_values):
                self.db.connection.rollback()
                QMessageBox.critical(self, "錯誤", "儲存記錄失敗")
                return
            
            # 獲取記錄ID
            record_id = self.db.get_last_insert_id()
            
            # 插入處方明細
            for row in range(self.prescriptionTableWidget.rowCount()):
                name = self.prescriptionTableWidget.item(row, 0).text()
                composition = self.prescriptionTableWidget.item(row, 1).text()
                quantity = self.prescriptionTableWidget.item(row, 2).text()
                unit = self.prescriptionTableWidget.item(row, 3).text()
                
                prescription_query = """
                INSERT INTO prescriptions (customer_id, record_id, prescription_name, composition, quantity, unit)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                prescription_values = (self.customer_id, record_id, name, composition, quantity, unit)
                
                if not self.db.execute_insert_update_delete(prescription_query, prescription_values):
                    self.db.connection.rollback()
                    QMessageBox.critical(self, "錯誤", "儲存處方明細失敗")
                    return
            
            # 提交事務
            self.db.connection.commit()
            
            QMessageBox.information(self, "成功", "處方已成功儲存")
            
            # 更新父視窗的記錄
            if self.parent_window:
                self.parent_window.customer_manager.load_customer_records(self.customer_id)
            
            # 重新載入歷史記錄
            self.load_history_prescriptions()
            
            # 更新抓藥次數
            self.load_customer_data()
            
            # 詢問是否繼續開立處方
            reply = QMessageBox.question(self, "繼續開立處方", 
                                       "是否要繼續為此客戶開立新處方？",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 清除處方內容但保留客戶資料
                self.clear_prescription()
            else:
                # 關閉視窗
                self.accept()
        
        except Exception as e:
            try:
                self.db.connection.rollback()
            except:
                pass
            QMessageBox.critical(self, "資料庫錯誤", f"儲存處方時發生錯誤: {e}")
    
    def print_prescription(self):
        """列印處方"""
        if self.prescriptionTableWidget.rowCount() == 0:
            QMessageBox.warning(self, "警告", "處方內容不能為空")
            return
        
        # 這裡可以實現列印功能
        QMessageBox.information(self, "列印功能", "此功能將根據實際需求建置列印功能")
    
    def keyPressEvent(self, event):
        """處理鍵盤事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """關閉視窗時停止計時器"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)