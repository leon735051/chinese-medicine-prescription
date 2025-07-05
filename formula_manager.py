from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

class FormulaManager:
    def __init__(self, db_manager, ui):
        self.db = db_manager
        self.ui = ui
        # 初始載入所有方劑資料
        self.load_all_formulas()
    
    def load_all_formulas(self):
        """載入所有方劑到列表"""
        try:
            self.ui.formulaTableWidget.setRowCount(0)
            formulas = self.db.execute_query("SELECT * FROM formulas ORDER BY id")
            
            if formulas:
                for row, formula in enumerate(formulas):
                    self.ui.formulaTableWidget.insertRow(row)
                    self.ui.formulaTableWidget.setItem(row, 0, QTableWidgetItem(str(formula['id'])))
                    self.ui.formulaTableWidget.setItem(row, 1, QTableWidgetItem(formula['name'] or ""))
                    self.ui.formulaTableWidget.setItem(row, 2, QTableWidgetItem(formula['origin_text'] or ""))
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"無法載入方劑列表: {e}")
    
    def clear_formula(self):
        """清除方劑欄位"""
        self.ui.formulaIdLineEdit.clear()
        self.ui.formulaNameLineEdit.clear()
        self.ui.formulaSourceLineEdit.clear()
        self.ui.formulaCompositionTextEdit.clear()
        self.ui.formulaEffectTextEdit.clear()
        self.ui.formulaIndicationTextEdit.clear()
        self.ui.formulaApplicationTextEdit.clear()
    
    def search_formula(self):
        """搜尋方劑"""
        formula_name = self.ui.formulaNameLineEdit.text().strip()
        if not formula_name:
            # 如果搜尋欄位為空，載入所有方劑
            self.load_all_formulas()
            return
        
        try:
            query = "SELECT * FROM formulas WHERE name LIKE %s"
            formulas = self.db.execute_query(query, (f'%{formula_name}%',))
            
            self.ui.formulaTableWidget.setRowCount(0)
            if formulas:
                for row, formula in enumerate(formulas):
                    self.ui.formulaTableWidget.insertRow(row)
                    self.ui.formulaTableWidget.setItem(row, 0, QTableWidgetItem(str(formula['id'])))
                    self.ui.formulaTableWidget.setItem(row, 1, QTableWidgetItem(formula['name'] or ""))
                    self.ui.formulaTableWidget.setItem(row, 2, QTableWidgetItem(formula['origin_text'] or ""))
            
            if len(formulas) == 0:
                QMessageBox.information(self.ui, "查詢結果", "沒有找到符合的方劑")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"搜尋方劑時發生錯誤: {e}")
    
    def select_formula(self, item):
        """選擇方劑並載入詳細資料"""
        row = item.row()
        formula_id = self.ui.formulaTableWidget.item(row, 0).text()
        
        try:
            query = "SELECT * FROM formulas WHERE id = %s"
            formulas = self.db.execute_query(query, (formula_id,))
            
            if formulas:
                formula = formulas[0]
                self.ui.formulaIdLineEdit.setText(str(formula['id']))
                self.ui.formulaNameLineEdit.setText(formula['name'] or "")
                self.ui.formulaSourceLineEdit.setText(formula['origin_text'] or "")
                self.ui.formulaCompositionTextEdit.setPlainText(formula['composition'] or "")
                self.ui.formulaEffectTextEdit.setPlainText(formula['effect'] or "")
                self.ui.formulaIndicationTextEdit.setPlainText(formula['indication'] or "")
                self.ui.formulaApplicationTextEdit.setPlainText(formula['application'] or "")
                # 新增：載入注意事項資料
                if hasattr(self.ui, 'formulaWarningsTextEdit'):
                    self.ui.formulaWarningsTextEdit.setPlainText(formula.get('warnings_side_effects', '') or "")
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"載入方劑資料時發生錯誤: {e}")
    
    def save_formula(self):
        """儲存方劑資料"""
        formula_id = self.ui.formulaIdLineEdit.text().strip()
        name = self.ui.formulaNameLineEdit.text().strip()
        
        if not formula_id:
            QMessageBox.warning(self.ui, "警告", "品號不能為空")
            return
        
        if not name:
            QMessageBox.warning(self.ui, "警告", "方劑名稱不能為空")
            return
        
        source = self.ui.formulaSourceLineEdit.text().strip()
        composition = self.ui.formulaCompositionTextEdit.toPlainText().strip()
        effect = self.ui.formulaEffectTextEdit.toPlainText().strip()
        indication = self.ui.formulaIndicationTextEdit.toPlainText().strip()
        application = self.ui.formulaApplicationTextEdit.toPlainText().strip()
        # 新增：獲取注意事項資料
        warnings = ""
        if hasattr(self.ui, 'formulaWarningsTextEdit'):
            warnings = self.ui.formulaWarningsTextEdit.toPlainText().strip()
        try:
            # 檢查品號是否已存在（但排除當前正在編輯的記錄）
            existing_formula = self.db.execute_query("SELECT id FROM formulas WHERE id = %s", (formula_id,))
            
            if existing_formula:
                # 更新現有方劑
                query = """
                UPDATE formulas SET 
                    name = %s, origin_text = %s, composition = %s, 
                    effect = %s, indication = %s, application = %s, warnings_side_effects = %s
                WHERE id = %s
                """
                values = (name, source, composition, effect, indication, application, warnings, formula_id)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "方劑資料已成功更新")
                    self.load_all_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "更新方劑失敗")
            else:
                # 新增方劑
                query = """
                INSERT INTO formulas (id, name, origin_text, composition, effect, indication, application, warnings_side_effects) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (formula_id, name, source, composition, effect, indication, application, warnings)
                
                if self.db.execute_insert_update_delete(query, values):
                    QMessageBox.information(self.ui, "成功", "新方劑資料已成功新增")
                    self.load_all_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "新增方劑失敗")
        
        except Exception as e:
            QMessageBox.critical(self.ui, "資料庫錯誤", f"儲存方劑資料時發生錯誤: {e}")
    
    def delete_formula(self):
        """刪除方劑資料"""
        formula_id = self.ui.formulaIdLineEdit.text().strip()
        
        if not formula_id:
            QMessageBox.warning(self.ui, "警告", "請先選擇要刪除的方劑")
            return
        
        reply = QMessageBox.question(self.ui, "確認刪除", 
                                     f"確定要刪除品號為 {formula_id} 的方劑資料嗎？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if self.db.execute_insert_update_delete("DELETE FROM formulas WHERE id = %s", (formula_id,)):
                    QMessageBox.information(self.ui, "成功", "方劑資料已成功刪除")
                    self.clear_formula()
                    self.load_all_formulas()  # 重新載入列表
                else:
                    QMessageBox.critical(self.ui, "錯誤", "刪除方劑失敗")
            
            except Exception as e:
                QMessageBox.critical(self.ui, "資料庫錯誤", f"刪除方劑資料時發生錯誤: {e}")