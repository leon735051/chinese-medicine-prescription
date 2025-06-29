import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QHeaderView
from PyQt5.QtGui import QFont

from database_manager import DatabaseManager
from customer_manager import CustomerManager
from formula_manager import FormulaManager
from herb_manager import HerbManager
from secret_formula_manager import SecretFormulaManager

class CustomerManagementApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(CustomerManagementApp, self).__init__()
        
        # 載入UI檔案
        uic.loadUi('customer_management.ui', self)
        
        # 設置整體字體大小
        self.setup_global_font()
        
        # 初始化資料庫管理器
        self.db_manager = DatabaseManager()
        if not self.db_manager.connect():
            QMessageBox.critical(self, "資料庫連接錯誤", "無法連接到MySQL資料庫")
            sys.exit(1)
        
        # 初始化各個管理器
        self.customer_manager = CustomerManager(self.db_manager, self)
        self.formula_manager = FormulaManager(self.db_manager, self)
        self.herb_manager = HerbManager(self.db_manager, self)
        self.secret_formula_manager = SecretFormulaManager(self.db_manager, self)
        
        # 設定當前日期
        self.customer_manager.update_current_date()
        
        # 設置表格的自適應寬度
        self.setup_table_headers()
        
        # 綁定客戶管理按鈕事件
        self.newButton.clicked.connect(self.customer_manager.new_customer)
        self.deleteButton.clicked.connect(self.customer_manager.delete_customer)
        self.saveButton.clicked.connect(self.customer_manager.save_customer)
        self.fetchButton.clicked.connect(self.customer_manager.open_prescription_form)  # 抓藥按鈕
        self.searchButton.clicked.connect(self.search_customers)
        self.printButton.clicked.connect(self.print_prescription)
        self.deleteRecordButton.clicked.connect(self.customer_manager.delete_record)
        
        # 綁定方劑相關按鈕事件
        self.clearFormulaButton.clicked.connect(self.formula_manager.clear_formula)
        self.searchFormulaButton.clicked.connect(self.formula_manager.search_formula)
        self.saveFormulaButton.clicked.connect(self.formula_manager.save_formula)
        self.deleteFormulaButton.clicked.connect(self.formula_manager.delete_formula)
        
        # 綁定單味藥相關按鈕事件
        self.clearHerbButton.clicked.connect(self.herb_manager.clear_herb)
        self.searchHerbButton.clicked.connect(self.herb_manager.search_herb)
        self.saveHerbButton.clicked.connect(self.herb_manager.save_herb)
        self.deleteHerbButton.clicked.connect(self.herb_manager.delete_herb)
        
        # 綁定秘方相關按鈕事件
        if hasattr(self, 'clearSecretButton'):
            self.clearSecretButton.clicked.connect(self.secret_formula_manager.clear_secret_formula)
        if hasattr(self, 'searchSecretButton'):
            self.searchSecretButton.clicked.connect(self.secret_formula_manager.search_secret_formula)
        if hasattr(self, 'saveSecretButton'):
            self.saveSecretButton.clicked.connect(self.secret_formula_manager.save_secret_formula)
        if hasattr(self, 'deleteSecretButton'):
            self.deleteSecretButton.clicked.connect(self.secret_formula_manager.delete_secret_formula)
        
        # 綁定表格選擇事件
        self.formulaTableWidget.itemClicked.connect(self.formula_manager.select_formula)
        self.herbsTableWidget.itemClicked.connect(self.herb_manager.select_herb)
        if hasattr(self, 'secretTableWidget'):
            self.secretTableWidget.itemClicked.connect(self.secret_formula_manager.select_secret_formula)
        
        # 綁定客戶列表選擇事件
        self.clientListWidget.itemClicked.connect(self.customer_manager.select_customer)
        
        # 初始載入客戶列表
        self.customer_manager.load_all_customers()
        
        # 設定TabWidget當前頁
        self.tabWidget.setCurrentIndex(1)  # 客戶資料索引，從0開始
        
        # 隱藏身分證號碼欄位
        self.labelIdNumber.setVisible(False)
        self.idNumberLineEdit.setVisible(False)
        
        # 設置編號和建檔日期欄位為唯讀
        self.idLineEdit.setReadOnly(True)
        self.yearSpinBox.setReadOnly(True)
        self.monthSpinBox.setReadOnly(True)
        self.daySpinBox.setReadOnly(True)
    
        # 修改搜尋相關的綁定
        self.searchButton.clicked.connect(self.search_customers)
        # 綁定查詢類型改變事件
        self.searchTypeComboBox.currentTextChanged.connect(self.update_search_placeholder)
        # 設定初始提示文字
        self.update_search_placeholder()
        
        self.recordsTableWidget.verticalHeader().setVisible(False)
    
    def setup_global_font(self):
        """設置全局字體大小"""
        # 創建全局字體
        global_font = QFont()
        global_font.setPointSize(10)  # 設置全局字體大小為10點
        global_font.setFamily("Microsoft JhengHei UI")  # 設置字體為微軟正黑體
        
        # 應用到整個應用程式
        self.setFont(global_font)
        
        # 設置較大字體給表格
        table_font = QFont()
        table_font.setPointSize(11)
        table_font.setFamily("Microsoft JhengHei UI")
        
        # 應用到所有表格
        if hasattr(self, 'recordsTableWidget'):
            self.recordsTableWidget.setFont(table_font)
        if hasattr(self, 'prescriptionTableWidget'):
            self.prescriptionTableWidget.setFont(table_font)
        if hasattr(self, 'clientListWidget'):
            self.clientListWidget.setFont(table_font)
        if hasattr(self, 'formulaTableWidget'):
            self.formulaTableWidget.setFont(table_font)
        if hasattr(self, 'herbsTableWidget'):
            self.herbsTableWidget.setFont(table_font)
        if hasattr(self, 'secretTableWidget'):
            self.secretTableWidget.setFont(table_font)
    
    def setup_table_headers(self):
        """設置所有表格表頭的自適應寬度"""
        # 設置記錄表格的列寬自適應
        header = self.recordsTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 次數
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 日期時間
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 價錢
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # 主述
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # 判斷
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 成效
        
        # 設置處方表格的列寬自適應
        prescription_header = self.prescriptionTableWidget.horizontalHeader()
        prescription_header.setSectionResizeMode(0, QHeaderView.Stretch)           # 方劑名
        prescription_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 組成
        prescription_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 數量
        prescription_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 單位
        
        # 設置方劑表格的列寬自適應
        formula_header = self.formulaTableWidget.horizontalHeader()
        formula_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
        formula_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 方名
        formula_header.setSectionResizeMode(2, QHeaderView.Stretch)           # 出典
        
        # 設置單味藥表格的列寬自適應
        herbs_header = self.herbsTableWidget.horizontalHeader()
        herbs_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
        herbs_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 藥名
        herbs_header.setSectionResizeMode(2, QHeaderView.Stretch)           # 出典
        
        # 設置秘方表格的列寬自適應
        if hasattr(self, 'secretTableWidget'):
            secret_header = self.secretTableWidget.horizontalHeader()
            secret_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 品號
            secret_header.setSectionResizeMode(1, QHeaderView.Stretch)           # 秘方
            secret_header.setSectionResizeMode(2, QHeaderView.Stretch)           # 出典
    
    def search_customers(self):
        """搜尋客戶的包裝函數"""
        search_text = self.searchEdit.text().strip()
        self.customer_manager.search_customers(search_text)
        
    # 新增：當查詢類型改變時，清空搜尋框並提示用戶
    def update_search_placeholder(self):
        """根據查詢類型更新搜尋框提示文字"""
        search_type = self.searchTypeComboBox.currentText()
        
        if search_type == "姓名查詢":
            self.searchEdit.setPlaceholderText("請輸入姓名")
        elif search_type == "生日查詢":
            self.searchEdit.setPlaceholderText("請輸入：年份(民國年) 或 月/日 或 月份")
        elif search_type == "電話查詢":
            self.searchEdit.setPlaceholderText("請輸入電話號碼")
        elif search_type == "手機查詢":
            self.searchEdit.setPlaceholderText("請輸入手機號碼")
        
        # 清空搜尋框
        self.searchEdit.clear()
    def print_prescription(self):
        """列印處方"""
        customer_id = self.idLineEdit.text().strip()
        if not customer_id or customer_id == "(自動編號)":
            QMessageBox.warning(self, "警告", "請先選擇客戶")
            return
        
        QMessageBox.information(self, "列印功能", "此功能尚未實現，將根據實際需求建置列印功能")
    
    def closeEvent(self, event):
        """程式關閉時關閉資料庫連接"""
        self.db_manager.disconnect()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # 設置全局應用程式字體
    global_font = QFont()
    global_font.setPointSize(10)
    global_font.setFamily("Microsoft JhengHei UI")
    app.setFont(global_font)
    
    window = CustomerManagementApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()