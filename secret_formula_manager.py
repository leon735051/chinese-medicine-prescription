from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

class SecretFormulaManager:
    def __init__(self, db_manager, ui):
        self.db = db_manager
        self.ui = ui
        # 初始載入所有秘方資料
        self.load_all_secret_formulas()
    
    def load_all_secret_formulas(self):
        """載入所有秘方到列表"""
        try:
            self.ui.secretTableWidget.setRowCount(0)
            # 從獨立的 secret_formulas 表格查詢
            secrets = self.db.execute_query("SELECT * FROM secret_formulas ORDER BY id")
            
            if secrets:
                for row, secret in enumerate(secrets):
                    self.ui.secretTableWidget.insertRow(row)
                    self.ui.secretTableWidget.setItem(row, 0, QTableWidgetItem(str(secret['id'])))
                    self.ui.secretTableWidget.setItem(row, 1, QTableWidgetItem(secret['name'] or ""))
                    self.ui.secretTableWidget.setItem(row, 2, QTableWidgetItem(secret['origin_text'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"無法載入秘方列表: {e}")
    
    def clear_secret_formula(self):
        """清除秘方欄位"""
        self.ui.secretIdLineEdit.clear()
        self.ui.secretNameLineEdit.clear()
        self.ui.secretSourceLineEdit.clear()
        self.ui.secretCompositionTextEdit.clear()
        self.ui.secretEffectTextEdit.clear()
        self.ui.secretIndicationTextEdit.clear()
        self.ui.secretApplicationTextEdit.clear()
        
        # 新增：清除注意事項欄位
        if hasattr(self.ui, 'secretWarningsTextEdit'):
            self.ui.secretWarningsTextEdit.clear()
        
        # 品號欄位設為可編輯
        self.ui.secretIdLineEdit.setReadOnly(False)
    
    def search_secret_formula(self):
        """搜尋秘方"""
        secret_name = self.ui.secretNameLineEdit.text().strip()
        if not secret_name:
            # 如果搜尋欄位為空，載入所有秘方
            self.load_all_secret_formulas()
            return
        
        try:
            # 同時搜尋品號和名稱
            query = "SELECT * FROM secret_formulas WHERE id LIKE %s OR name LIKE %s ORDER BY id"
            secrets = self.db.execute_query(query, (f'%{secret_name}%', f'%{secret_name}%'))
            
            self.ui.secretTableWidget.setRowCount(0)
            if secrets:
                for row, secret in enumerate(secrets):
                    self.ui.secretTableWidget.insertRow(row)
                    self.ui.secretTableWidget.setItem(row, 0, QTableWidgetItem(str(secret['id'])))
                    self.ui.secretTableWidget.setItem(row, 1, QTableWidgetItem(secret['name'] or ""))
                    self.ui.secretTableWidget.setItem(row, 2, QTableWidgetItem(secret['origin_text'] or ""))
            
            if len(secrets) == 0:
                QMessageBox.information(self.ui, "查詢結果", "沒有找到符合的秘方")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"搜尋秘方時發生錯誤: {e}")
    
    def select_secret_formula(self, item):
        """選擇秘方並載入詳細資料"""
        row = item.row()
        secret_id = self.ui.secretTableWidget.item(row, 0).text()
        
        try:
            # 從 secret_formulas 表格查詢
            query = "SELECT * FROM secret_formulas WHERE id = %s"
            secrets = self.db.execute_query(query, (secret_id,))
            
            if secrets:
                secret = secrets[0]
                self.ui.secretIdLineEdit.setText(str(secret['id']))
                self.ui.secretNameLineEdit.setText(secret['name'] or "")
                self.ui.secretSourceLineEdit.setText(secret['origin_text'] or "")
                self.ui.secretCompositionTextEdit.setPlainText(secret['composition'] or "")
                self.ui.secretEffectTextEdit.setPlainText(secret['effect'] or "")
                self.ui.secretIndicationTextEdit.setPlainText(secret['indication'] or "")
                self.ui.secretApplicationTextEdit.setPlainText(secret['application'] or "")
                
                # 新增：載入注意事項資料
                if hasattr(self.ui, 'secretWarningsTextEdit'):
                    self.ui.secretWarningsTextEdit.setPlainText(secret.get('warnings_side_effects', '') or "")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"載入秘方資料時發生錯誤: {e}")
    
    def save_secret_formula(self):
        """儲存秘方資料"""
        secret_id = self.ui.secretIdLineEdit.text().strip()
        name = self.ui.secretNameLineEdit.text().strip()
        
        if not secret_id:
            QMessageBox.warning(self.ui, "警告", "品號不能為空")
            return
        
        if not name:
            QMessageBox.warning(self.ui, "警告", "秘方名稱不能為空")
            return
        
        source = self.ui.secretSourceLineEdit.text().strip()
        composition = self.ui.secretCompositionTextEdit.toPlainText().strip()
        effect = self.ui.secretEffectTextEdit.toPlainText().strip()
        indication = self.ui.secretIndicationTextEdit.toPlainText().strip()
        application = self.ui.secretApplicationTextEdit.toPlainText().strip()
        
        # 新增：獲取注意事項資料
        warnings = ""
        if hasattr(self.ui, 'secretWarningsTextEdit'):
            warnings = self.ui.secretWarningsTextEdit.toPlainText().strip()
        
        try:
            # 檢查品號是否已存在
            existing_secret = self.db.execute_query("SELECT id FROM secret_formulas WHERE id = %s", (secret_id,))
            
            if existing_secret:
                # 更新現有秘方
                query = """
                UPDATE secret_formulas SET 
                    name = %s, origin_text = %s, composition = %s, 
                    effect = %s, indication = %s, application = %s, warnings_side_effects = %s
                WHERE id = %s
                """
                values = (name, source, composition, effect, indication, application, warnings, secret_id)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "秘方資料已成功更新")
                    self.load_all_secret_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "更新秘方失敗")
            else:
                # 新增秘方
                query = """
                INSERT INTO secret_formulas (id, name, origin_text, composition, effect, indication, application, warnings_side_effects) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (secret_id, name, source, composition, effect, indication, application, warnings)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "新秘方資料已成功新增")
                    self.load_all_secret_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "新增秘方失敗")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"儲存秘方資料時發生錯誤: {e}")
    
    def delete_secret_formula(self):
        """刪除秘方資料"""
        secret_id = self.ui.secretIdLineEdit.text().strip()
        
        if not secret_id:
            QMessageBox.warning(self.ui, "警告", "請先選擇要刪除的秘方")
            return
        
        reply = QMessageBox.question(self.ui, "確認刪除", 
                                     f"確定要刪除品號為 {secret_id} 的秘方資料嗎？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # 從 secret_formulas 表格刪除
                if self.db.execute_insert_update_delete("DELETE FROM secret_formulas WHERE id = %s", (secret_id,)):
                    QMessageBox.information(self.ui, "成功", "秘方資料已成功刪除")
                    self.clear_secret_formula()
                    self.load_all_secret_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "刪除秘方失敗")
            
            except Exception as e:
                QMessageBox.critical(self.ui, "資料庫錯誤", f"刪除秘方資料時發生錯誤: {e}")