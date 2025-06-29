from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

class HerbManager:
    def __init__(self, db_manager, ui):
        self.db = db_manager
        self.ui = ui
        # 初始載入所有藥材資料
        self.load_all_herbs()
    
    def load_all_herbs(self):
        """載入所有藥材到列表"""
        try:
            self.ui.herbsTableWidget.setRowCount(0)
            herbs = self.db.execute_query("SELECT * FROM medicines ORDER BY id")
            
            if herbs:
                for row, herb in enumerate(herbs):
                    self.ui.herbsTableWidget.insertRow(row)
                    self.ui.herbsTableWidget.setItem(row, 0, QTableWidgetItem(str(herb['id'])))
                    self.ui.herbsTableWidget.setItem(row, 1, QTableWidgetItem(herb['name'] or ""))
                    self.ui.herbsTableWidget.setItem(row, 2, QTableWidgetItem(herb['origin_text'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"無法載入藥材列表: {e}")
    
    def clear_herb(self):
        """清除單味藥欄位"""
        self.ui.herbIdLineEdit.clear()
        self.ui.herbNameLineEdit.clear()
        self.ui.herbSourceLineEdit.clear()
        self.ui.herbNatureFlavorTextEdit.clear()
        self.ui.herbEffectTextEdit.clear()
        self.ui.herbIndicationTextEdit.clear()
        self.ui.herbApplicationTextEdit.clear()
        
        # 新增：清除注意事項欄位
        if hasattr(self.ui, 'herbWarningsTextEdit'):
            self.ui.herbWarningsTextEdit.clear()
        
        # 品號欄位設為可編輯
        self.ui.herbIdLineEdit.setReadOnly(False)
    
    def search_herb(self):
        """搜尋單味藥"""
        herb_name = self.ui.herbNameLineEdit.text().strip()
        if not herb_name:
            # 如果搜尋欄位為空，載入所有藥材
            self.load_all_herbs()
            return
        
        try:
            query = "SELECT * FROM medicines WHERE name LIKE %s"
            herbs = self.db.execute_query(query, (f'%{herb_name}%',))
            
            self.ui.herbsTableWidget.setRowCount(0)
            if herbs:
                for row, herb in enumerate(herbs):
                    self.ui.herbsTableWidget.insertRow(row)
                    self.ui.herbsTableWidget.setItem(row, 0, QTableWidgetItem(str(herb['id'])))
                    self.ui.herbsTableWidget.setItem(row, 1, QTableWidgetItem(herb['name'] or ""))
                    self.ui.herbsTableWidget.setItem(row, 2, QTableWidgetItem(herb['origin_text'] or ""))
            
            if len(herbs) == 0:
                QMessageBox.information(self.ui, "查詢結果", "沒有找到符合的藥材")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"搜尋藥材時發生錯誤: {e}")
    
    def select_herb(self, item):
        """選擇單味藥並載入詳細資料"""
        row = item.row()
        herb_id = self.ui.herbsTableWidget.item(row, 0).text()
        
        try:
            query = "SELECT * FROM medicines WHERE id = %s"
            herbs = self.db.execute_query(query, (herb_id,))
            
            if herbs:
                herb = herbs[0]
                self.ui.herbIdLineEdit.setText(str(herb['id']))
                self.ui.herbNameLineEdit.setText(herb['name'] or "")
                self.ui.herbSourceLineEdit.setText(herb['origin_text'] or "")
                self.ui.herbNatureFlavorTextEdit.setPlainText(herb['nature_flavor'] or "")
                self.ui.herbEffectTextEdit.setPlainText(herb['effect'] or "")
                self.ui.herbIndicationTextEdit.setPlainText(herb['indication'] or "")
                self.ui.herbApplicationTextEdit.setPlainText(herb['application'] or "")
                
                # 新增：載入注意事項資料
                if hasattr(self.ui, 'herbWarningsTextEdit'):
                    self.ui.herbWarningsTextEdit.setPlainText(herb.get('warnings_side_effects', '') or "")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"載入藥材資料時發生錯誤: {e}")
    
    def save_herb(self):
        """儲存單味藥資料"""
        herb_id = self.ui.herbIdLineEdit.text().strip()
        name = self.ui.herbNameLineEdit.text().strip()
        
        if not herb_id:
            QMessageBox.warning(self.ui, "警告", "品號不能為空")
            return
            
        if not name:
            QMessageBox.warning(self.ui, "警告", "藥材名稱不能為空")
            return
        
        source = self.ui.herbSourceLineEdit.text().strip()
        nature_flavor = self.ui.herbNatureFlavorTextEdit.toPlainText().strip()
        effect = self.ui.herbEffectTextEdit.toPlainText().strip()
        indication = self.ui.herbIndicationTextEdit.toPlainText().strip()
        application = self.ui.herbApplicationTextEdit.toPlainText().strip()
        
        # 新增：獲取注意事項資料
        warnings = ""
        if hasattr(self.ui, 'herbWarningsTextEdit'):
            warnings = self.ui.herbWarningsTextEdit.toPlainText().strip()
        
        try:
            # 檢查品號是否已存在
            existing_herb = self.db.execute_query("SELECT id FROM medicines WHERE id = %s", (herb_id,))
            
            if existing_herb:
                # 更新現有藥材
                query = """
                UPDATE medicines SET 
                    name = %s, origin_text = %s, nature_flavor = %s, 
                    effect = %s, indication = %s, application = %s, warnings_side_effects = %s
                WHERE id = %s
                """
                values = (name, source, nature_flavor, effect, indication, application, warnings, herb_id)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "藥材資料已成功更新")
                    self.load_all_herbs()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "更新藥材失敗")
            else:
                # 新增藥材
                query = """
                INSERT INTO medicines (id, name, origin_text, nature_flavor, effect, indication, application, warnings_side_effects) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (herb_id, name, source, nature_flavor, effect, indication, application, warnings)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "新藥材資料已成功新增")
                    self.load_all_herbs()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "新增藥材失敗")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"儲存藥材資料時發生錯誤: {e}")
    
    def delete_herb(self):
        """刪除單味藥資料"""
        herb_id = self.ui.herbIdLineEdit.text().strip()
        
        if not herb_id:
            QMessageBox.warning(self.ui, "警告", "請先選擇要刪除的藥材")
            return
        
        reply = QMessageBox.question(self.ui, "確認刪除", 
                                     f"確定要刪除品號為 {herb_id} 的藥材資料嗎？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.execute_insert_update_delete("DELETE FROM medicines WHERE id = %s", (herb_id,)):
                    QMessageBox.information(self.ui, "成功", "藥材資料已成功刪除")
                    self.clear_herb()
                    self.load_all_herbs()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "刪除藥材失敗")
            
            except Exception as e:
                QMessageBox.critical(self.ui, "資料庫錯誤", f"刪除藥材資料時發生錯誤: {e}")