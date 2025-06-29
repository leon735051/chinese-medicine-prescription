import datetime
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CustomerManager:
    def __init__(self, db_manager, ui):
        self.db = db_manager
        self.ui = ui
        
    def setup_table_headers(self):
        """設置表格表頭的自適應寬度"""
        # 設置記錄表格的列寬自適應
        header = self.ui.recordsTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 次數
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 日期時間
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 價錢
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # 主述
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # 判斷
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 成效
        
        # 設置處方表格的列寬自適應
        prescription_header = self.ui.prescriptionTableWidget.horizontalHeader()
        prescription_header.setSectionResizeMode(0, QHeaderView.Stretch)           # 方劑名
        prescription_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 組成
        prescription_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 數量
        prescription_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 單位
        
        # 設置字體大小
        self.setup_font_sizes()
        
    def setup_font_sizes(self):
        """設置整體字體大小"""
        # 創建較大的字體
        larger_font = QFont()
        larger_font.setPointSize(11)  # 增加字體大小到11點
        
        # 應用到記錄表格
        self.ui.recordsTableWidget.setFont(larger_font)
        
        # 應用到處方表格
        self.ui.prescriptionTableWidget.setFont(larger_font)
        
        # 應用到客戶列表
        self.ui.clientListWidget.setFont(larger_font)
        
        # 應用到其他主要輸入欄位
        input_font = QFont()
        input_font.setPointSize(10)
        
        self.ui.nameLineEdit.setFont(input_font)
        self.ui.occupationLineEdit.setFont(input_font)
        self.ui.phoneLineEdit.setFont(input_font)
        self.ui.mobileLineEdit.setFont(input_font)
        self.ui.addressLineEdit.setFont(input_font)
        
    def load_all_customers(self):
        """載入所有客戶到列表"""
        try:
            self.ui.clientListWidget.clear()
            customers = self.db.execute_query("SELECT id, name FROM customers ORDER BY id")
            
            if customers:
                for customer in customers:
                    self.ui.clientListWidget.addItem(f"{customer['id']}.{customer['name']}")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"無法載入客戶列表: {e}")
    
    def search_customers(self, search_text):
        """根據選擇的條件搜尋客戶"""
        if not search_text:
            self.load_all_customers()
            return
        
        try:
            self.ui.clientListWidget.clear()
            
            # 獲取查詢類型
            search_type = self.ui.searchTypeComboBox.currentText()
            
            if search_type == "姓名查詢":
                # 搜尋姓名中任何位置的字串
                query = "SELECT id, name FROM customers WHERE name LIKE %s ORDER BY id"
                search_param = f'%{search_text}%'
                
            elif search_type == "生日查詢":
                # 生日查詢 - 可以輸入年份、月份或日期
                try:
                    # 嘗試解析輸入的日期格式
                    if len(search_text) == 4 and search_text.isdigit():
                        # 輸入年份（民國年）
                        western_year = int(search_text) + 1911
                        query = "SELECT id, name FROM customers WHERE YEAR(birthday) = %s ORDER BY id"
                        search_param = western_year
                    elif '/' in search_text:
                        # 輸入月/日格式
                        parts = search_text.split('/')
                        if len(parts) == 2:
                            month, day = parts
                            query = "SELECT id, name FROM customers WHERE MONTH(birthday) = %s AND DAY(birthday) = %s ORDER BY id"
                            search_param = (int(month), int(day))
                        else:
                            QMessageBox.warning(self.ui, "輸入格式錯誤", "生日查詢格式：年份(民國年) 或 月/日")
                            return
                    else:
                        # 嘗試解析為月份
                        month = int(search_text)
                        query = "SELECT id, name FROM customers WHERE MONTH(birthday) = %s ORDER BY id"
                        search_param = month
                except ValueError:
                    QMessageBox.warning(self.ui, "輸入格式錯誤", "生日查詢格式：年份(民國年) 或 月/日 或 月份")
                    return
                    
            elif search_type == "電話查詢":
                query = "SELECT id, name FROM customers WHERE phone LIKE %s ORDER BY id"
                search_param = f'%{search_text}%'
                
            elif search_type == "手機查詢":
                query = "SELECT id, name FROM customers WHERE mobile LIKE %s ORDER BY id"
                search_param = f'%{search_text}%'
            
            else:
                # 預設為姓名查詢
                query = "SELECT id, name FROM customers WHERE name LIKE %s ORDER BY id"
                search_param = f'%{search_text}%'
            
            # 執行查詢
            if isinstance(search_param, tuple):
                customers = self.db.execute_query(query, search_param)
            else:
                customers = self.db.execute_query(query, (search_param,))
            
            if customers:
                for customer in customers:
                    self.ui.clientListWidget.addItem(f"{customer['id']}.{customer['name']}")
            
            if self.ui.clientListWidget.count() == 0:
                QMessageBox.information(self.ui, "查詢結果", f"沒有找到符合{search_type}條件的客戶")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"搜尋客戶時發生錯誤: {e}")
    
    def new_customer(self):
        """準備新增客戶"""
        # 清空所有輸入欄位
        self.ui.idLineEdit.clear()
        self.ui.nameLineEdit.clear()
        self.ui.birthYearSpinBox.setValue(0)
        self.ui.birthMonthSpinBox.setValue(0)
        self.ui.birthDaySpinBox.setValue(0)
        self.ui.maleRadioButton.setChecked(True)
        self.ui.occupationLineEdit.clear()
        self.ui.phoneLineEdit.clear()
        self.ui.mobileLineEdit.clear()
        self.ui.addressLineEdit.clear()
        
        # 更新為當前日期
        self.update_current_date()
        
        # ID欄位設為唯讀，顯示"自動編號"
        self.ui.idLineEdit.setReadOnly(True)
        self.ui.idLineEdit.setText("(自動編號)")
        
        # 清空記錄表格
        self.ui.recordsTableWidget.setRowCount(0)
        self.ui.prescriptionTableWidget.setRowCount(0)
    
    def update_current_date(self):
        """更新當前日期到建檔日期欄位"""
        current_date = datetime.date.today()
        ROC_year = current_date.year - 1911  # 轉換為民國年
        self.ui.yearSpinBox.setValue(ROC_year)
        self.ui.monthSpinBox.setValue(current_date.month)
        self.ui.daySpinBox.setValue(current_date.day)
    
    def save_customer(self):
        """儲存客戶資料"""
        # 獲取輸入值
        name = self.ui.nameLineEdit.text().strip()
        
        # 基本驗證
        if not name:
            QMessageBox.warning(self.ui, "警告", "客戶姓名不能為空")
            return
        
        # 獲取其他資料
        gender = "男" if self.ui.maleRadioButton.isChecked() else "女"
        
        # 獲取生日（民國年）
        birth_year = self.ui.birthYearSpinBox.value()
        birth_month = self.ui.birthMonthSpinBox.value()
        birth_day = self.ui.birthDaySpinBox.value()
        
        # 生日可能為空，如果有值就轉換為西元年日期
        birthday = None
        if birth_year > 0 and birth_month > 0 and birth_day > 0:
            try:
                western_year = birth_year + 1911
                birthday = datetime.date(western_year, birth_month, birth_day)
            except ValueError:
                QMessageBox.warning(self.ui, "警告", "生日日期無效")
                return
        
        # 獲取系統當前日期時間作為建檔日期時間
        create_date = datetime.datetime.now()
        
        # 其他欄位
        occupation = self.ui.occupationLineEdit.text().strip()
        phone = self.ui.phoneLineEdit.text().strip()
        mobile = self.ui.mobileLineEdit.text().strip()
        address = self.ui.addressLineEdit.text().strip()
        
        try:
            # 檢查是新增還是更新
            customer_id = self.ui.idLineEdit.text().strip()
            
            if customer_id == "(自動編號)" or not customer_id or not customer_id.isdigit():
                # 新增客戶
                query = """
                INSERT INTO customers (
                    name, birthday, gender, occupation, 
                    phone, mobile, address, create_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, birthday, gender, occupation, phone, mobile, address, create_date)
                
                if self.db.execute_insert_update_delete(query, values):
                    customer_id = self.db.get_last_insert_id()
                    self.ui.idLineEdit.setText(str(customer_id))
                    QMessageBox.information(self.ui, "成功", "新客戶資料已成功新增")
                else:
                    QMessageBox.critical(self.ui, "錯誤", "新增客戶失敗")
                    return
            else:
                # 更新現有客戶
                query = """
                UPDATE customers SET 
                    name = %s, birthday = %s, gender = %s, occupation = %s,
                    phone = %s, mobile = %s, address = %s, update_date = %s
                WHERE id = %s
                """
                values = (name, birthday, gender, occupation, phone, mobile, address, create_date, customer_id)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "客戶資料已成功更新")
                else:
                    QMessageBox.critical(self.ui, "錯誤", "更新客戶失敗")
                    return
            
            # 重新載入客戶列表
            self.load_all_customers()
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"儲存客戶資料時發生錯誤: {e}")
    
    def delete_customer(self):
        """刪除客戶資料"""
        customer_id = self.ui.idLineEdit.text().strip()
        
        if not customer_id or customer_id == "(自動編號)":
            QMessageBox.warning(self.ui, "警告", "請先選擇要刪除的客戶")
            return
        
        # 確認刪除
        reply = QMessageBox.question(self.ui, "確認刪除", 
                                     f"確定要刪除ID為 {customer_id} 的客戶資料嗎？\n此操作將一併刪除該客戶的所有記錄！",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        try:
            if self.db.execute_insert_update_delete("DELETE FROM customers WHERE id = %s", (customer_id,)):
                QMessageBox.information(self.ui, "成功", "客戶資料已成功刪除")
                self.new_customer()
                self.load_all_customers()
            else:
                QMessageBox.critical(self.ui, "錯誤", "刪除客戶失敗")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"刪除客戶資料時發生錯誤: {e}")
    
    def fetch_customer(self):
        """根據客戶編號查詢客戶資料"""
        customer_id = self.ui.idLineEdit.text().strip()
        
        if not customer_id or customer_id == "(自動編號)":
            QMessageBox.warning(self.ui, "警告", "請輸入客戶編號")
            return
        
        try:
            query = """
            SELECT id, name, birthday, gender, occupation, 
                   phone, mobile, address, create_date 
            FROM customers WHERE id = %s
            """
            customers = self.db.execute_query(query, (customer_id,))
            
            if not customers:
                QMessageBox.warning(self.ui, "未找到", f"找不到ID為 {customer_id} 的客戶")
                return
            
            customer = customers[0]
            
            # 填充表單
            self.ui.idLineEdit.setText(str(customer['id']))
            self.ui.nameLineEdit.setText(customer['name'])
            
            # 設定性別
            if customer['gender'] == '男':
                self.ui.maleRadioButton.setChecked(True)
            else:
                self.ui.femaleRadioButton.setChecked(True)
            
            # 設定生日（如有）
            if customer['birthday']:
                roc_year = customer['birthday'].year - 1911
                self.ui.birthYearSpinBox.setValue(roc_year)
                self.ui.birthMonthSpinBox.setValue(customer['birthday'].month)
                self.ui.birthDaySpinBox.setValue(customer['birthday'].day)
            else:
                self.ui.birthYearSpinBox.setValue(0)
                self.ui.birthMonthSpinBox.setValue(0)
                self.ui.birthDaySpinBox.setValue(0)
            
            # 設定建檔日期
            if customer['create_date']:
                roc_year = customer['create_date'].year - 1911
                self.ui.yearSpinBox.setValue(roc_year)
                self.ui.monthSpinBox.setValue(customer['create_date'].month)
                self.ui.daySpinBox.setValue(customer['create_date'].day)
            
            # 設定其他資料
            self.ui.occupationLineEdit.setText(customer['occupation'] or '')
            self.ui.phoneLineEdit.setText(customer['phone'] or '')
            self.ui.mobileLineEdit.setText(customer['mobile'] or '')
            self.ui.addressLineEdit.setText(customer['address'] or '')
            
            # 載入客戶記錄
            self.load_customer_records(customer_id)
            
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"查詢客戶資料時發生錯誤: {e}")
    
    def load_customer_records(self, customer_id):
        """載入客戶的記錄資料"""
        try:
            # 清空表格
            self.ui.recordsTableWidget.setRowCount(0)
            
            # 查詢客戶記錄
            query = """
            SELECT id, record_date, times, price, description, judgment, result 
            FROM records 
            WHERE customer_id = %s 
            ORDER BY record_date DESC
            """
            records = self.db.execute_query(query, (customer_id,))
            
            if records:
                # 填充記錄表格
                for row, record in enumerate(records):
                    self.ui.recordsTableWidget.insertRow(row)
                    
                    # 計算倒序次數：總記錄數 - 當前索引
                    reverse_count = len(records) - row
                    self.ui.recordsTableWidget.setItem(row, 0, QTableWidgetItem(str(reverse_count)))
                    
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
                    
                    # 調整欄位索引（移除編號欄位）
                    self.ui.recordsTableWidget.setItem(row, 1, QTableWidgetItem(date_str))
                    self.ui.recordsTableWidget.setItem(row, 2, QTableWidgetItem(str(record['price'] or "")))
                    self.ui.recordsTableWidget.setItem(row, 3, QTableWidgetItem(record['description'] or ""))
                    self.ui.recordsTableWidget.setItem(row, 4, QTableWidgetItem(record['judgment'] or ""))
                    self.ui.recordsTableWidget.setItem(row, 5, QTableWidgetItem(record['result'] or ""))
                    
                    # 在第一個項目中隱藏地儲存record_id，供後續使用
                    item = self.ui.recordsTableWidget.item(row, 1)
                    item.setData(256, record['id'])  # 使用Qt.UserRole = 256
            
            # 綁定記錄選擇事件（如果還沒綁定）
            try:
                self.ui.recordsTableWidget.itemClicked.disconnect()
            except:
                pass
            self.ui.recordsTableWidget.itemClicked.connect(self.select_record)
            
            # 載入所有處方資料（初始顯示）
            self.load_all_prescriptions(customer_id)
            
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"載入客戶記錄時發生錯誤: {e}")
    
    def load_all_prescriptions(self, customer_id):
        """載入客戶的所有處方資料（初始顯示）"""
        try:
            # 清空表格
            self.ui.prescriptionTableWidget.setRowCount(0)
            
            # 查詢客戶所有處方，加入記錄日期資訊
            query = """
            SELECT p.prescription_name, p.composition, p.quantity, p.unit, r.record_date
            FROM prescriptions p
            LEFT JOIN records r ON p.record_id = r.id
            WHERE p.customer_id = %s 
            ORDER BY r.record_date DESC, p.id
            """
            prescriptions = self.db.execute_query(query, (customer_id,))
            
            if prescriptions:
                # 填充處方表格
                for row, prescription in enumerate(prescriptions):
                    self.ui.prescriptionTableWidget.insertRow(row)
                    
                    # 格式化顯示：加入日期資訊
                    record_date = prescription['record_date']
                    if record_date:
                        if hasattr(record_date, 'strftime'):
                            date_str = record_date.strftime('%m/%d %H:%M')
                        else:
                            date_str = f"{record_date} 00:00"
                        prescription_name_with_date = f"[{date_str}] {prescription['prescription_name'] or ''}"
                    else:
                        prescription_name_with_date = prescription['prescription_name'] or ""
                    
                    # 調整欄位索引（移除編號欄位）
                    self.ui.prescriptionTableWidget.setItem(row, 0, QTableWidgetItem(prescription_name_with_date))
                    self.ui.prescriptionTableWidget.setItem(row, 1, QTableWidgetItem(prescription['composition'] or ""))
                    self.ui.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(prescription['quantity'] or "")))
                    self.ui.prescriptionTableWidget.setItem(row, 3, QTableWidgetItem(prescription['unit'] or ""))
            
        except Exception as e:
            # 如果新的查詢失敗（可能是舊資料），嘗試舊的查詢方式
            try:
                query = """
                SELECT prescription_name, composition, quantity, unit 
                FROM prescriptions 
                WHERE customer_id = %s 
                ORDER BY id
                """
                prescriptions = self.db.execute_query(query, (customer_id,))
                
                if prescriptions:
                    # 填充處方表格
                    for row, prescription in enumerate(prescriptions):
                        self.ui.prescriptionTableWidget.insertRow(row)
                        
                        # 調整欄位索引（移除編號欄位）
                        self.ui.prescriptionTableWidget.setItem(row, 0, QTableWidgetItem(prescription['prescription_name'] or ""))
                        self.ui.prescriptionTableWidget.setItem(row, 1, QTableWidgetItem(prescription['composition'] or ""))
                        self.ui.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(prescription['quantity'] or "")))
                        self.ui.prescriptionTableWidget.setItem(row, 3, QTableWidgetItem(prescription['unit'] or ""))
            except Exception as e2:
                print(f"載入處方資料時發生錯誤: {e2}")
    
    def select_record(self, item):
        """選擇記錄時載入對應的處方明細"""
        row = item.row()
        # 從UserRole中獲取record_id
        date_item = self.ui.recordsTableWidget.item(row, 1)
        record_id = date_item.data(256)  # 使用Qt.UserRole = 256
        
        # 載入該記錄的處方明細
        self.load_prescriptions_by_record(record_id)
    
    def load_prescriptions_by_record(self, record_id):
        """根據記錄ID載入對應的處方明細"""
        try:
            # 清空表格
            self.ui.prescriptionTableWidget.setRowCount(0)
            
            # 查詢特定記錄的處方
            query = """
            SELECT p.prescription_name, p.composition, p.quantity, p.unit, r.record_date
            FROM prescriptions p
            LEFT JOIN records r ON p.record_id = r.id
            WHERE p.record_id = %s
            ORDER BY p.id
            """
            prescriptions = self.db.execute_query(query, (record_id,))
            
            if prescriptions:
                # 填充處方表格
                for row, prescription in enumerate(prescriptions):
                    self.ui.prescriptionTableWidget.insertRow(row)
                    
                    # 格式化顯示：加入日期資訊
                    record_date = prescription['record_date']
                    if record_date:
                        if hasattr(record_date, 'strftime'):
                            date_str = record_date.strftime('%m/%d %H:%M')
                        else:
                            date_str = f"{record_date} 00:00"
                        prescription_name_with_date = f"[{date_str}] {prescription['prescription_name'] or ''}"
                    else:
                        prescription_name_with_date = prescription['prescription_name'] or ""
                    
                    # 調整欄位索引（移除編號欄位）
                    self.ui.prescriptionTableWidget.setItem(row, 0, QTableWidgetItem(prescription_name_with_date))
                    self.ui.prescriptionTableWidget.setItem(row, 1, QTableWidgetItem(prescription['composition'] or ""))
                    self.ui.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(prescription['quantity'] or "")))
                    self.ui.prescriptionTableWidget.setItem(row, 3, QTableWidgetItem(prescription['unit'] or ""))
            else:
                # 如果沒有找到處方，顯示提示
                self.ui.prescriptionTableWidget.insertRow(0)
                self.ui.prescriptionTableWidget.setItem(0, 0, QTableWidgetItem("此記錄無處方明細"))
                self.ui.prescriptionTableWidget.setItem(0, 1, QTableWidgetItem(""))
                self.ui.prescriptionTableWidget.setItem(0, 2, QTableWidgetItem(""))
                self.ui.prescriptionTableWidget.setItem(0, 3, QTableWidgetItem(""))
            
        except Exception as e:
            # 如果查詢失敗，嘗試舊的查詢方式
            try:
                customer_id = self.ui.idLineEdit.text().strip()
                query = """
                SELECT p.prescription_name, p.composition, p.quantity, p.unit
                FROM prescriptions p
                JOIN records r ON p.customer_id = r.customer_id
                WHERE r.id = %s AND p.customer_id = %s
                AND DATE(r.record_date) = (
                    SELECT DATE(record_date) FROM records WHERE id = %s
                )
                ORDER BY p.id
                """
                prescriptions = self.db.execute_query(query, (record_id, customer_id, record_id))
                
                if prescriptions:
                    for row, prescription in enumerate(prescriptions):
                        self.ui.prescriptionTableWidget.insertRow(row)
                        
                        # 調整欄位索引（移除編號欄位）
                        self.ui.prescriptionTableWidget.setItem(row, 0, QTableWidgetItem(prescription['prescription_name'] or ""))
                        self.ui.prescriptionTableWidget.setItem(row, 1, QTableWidgetItem(prescription['composition'] or ""))
                        self.ui.prescriptionTableWidget.setItem(row, 2, QTableWidgetItem(str(prescription['quantity'] or "")))
                        self.ui.prescriptionTableWidget.setItem(row, 3, QTableWidgetItem(prescription['unit'] or ""))
            except Exception as e2:
                print(f"載入記錄處方明細時發生錯誤: {e2}")

    def delete_record(self):
        """刪除選定的記錄及其相關處方"""
        # 獲取當前選中行
        selected_rows = self.ui.recordsTableWidget.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self.ui, "警告", "請先選擇要刪除的記錄")
            return
        
        # 獲取記錄ID
        row = selected_rows[0].row()
        date_item = self.ui.recordsTableWidget.item(row, 1)
        record_id = date_item.data(256)  # 使用Qt.UserRole = 256
        customer_id = self.ui.idLineEdit.text().strip()
        
        # 確認刪除
        reply = QMessageBox.question(self.ui, "確認刪除", 
                                     f"確定要刪除此記錄嗎？\n這將同時刪除相關的處方明細！",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        try:
            # 直接刪除記錄，相關處方會因為外鍵約束自動刪除（ON DELETE CASCADE）
            if self.db.execute_insert_update_delete("DELETE FROM records WHERE id = %s", (record_id,)):
                QMessageBox.information(self.ui, "成功", "記錄及相關處方已成功刪除")
                
                # 重新載入記錄和處方
                if customer_id and customer_id != "(自動編號)":
                    self.load_customer_records(customer_id)
            else:
                QMessageBox.critical(self.ui, "錯誤", "刪除記錄失敗")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"刪除記錄時發生錯誤: {e}")
    
    def select_customer(self, item):
        """從列表中選擇客戶並載入其資料"""
        # 解析列表項文字，格式為: "ID.姓名"
        item_text = item.text()
        parts = item_text.split('.')
        
        if len(parts) < 2:
            return
        
        customer_id = parts[0].strip()
        self.ui.idLineEdit.setText(customer_id)
        
        # 載入選擇的客戶資料
        self.fetch_customer()
    
    def open_prescription_form(self):
        """開啟處方開立視窗"""
        customer_id = self.ui.idLineEdit.text().strip()
        customer_name = self.ui.nameLineEdit.text().strip()
        
        if not customer_id or customer_id == "(自動編號)":
            QMessageBox.warning(self.ui, "警告", "請先選擇客戶")
            return
        
        if not customer_name:
            QMessageBox.warning(self.ui, "警告", "客戶姓名不能為空")
            return
        
        try:
            # 匯入處方管理器
            from prescription_manager import PrescriptionManager
            
            # 建立處方開立視窗
            prescription_window = PrescriptionManager(
                self.db, 
                customer_id, 
                customer_name,
                self.ui
            )
            
            # 顯示視窗
            prescription_window.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.ui, "錯誤", f"無法開啟處方視窗: {e}")