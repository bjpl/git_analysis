import sys
import os
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QListWidget, QListWidgetItem, QMessageBox,
    QInputDialog, QStatusBar, QAction, QDialog, QTextEdit, QFormLayout, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt

# Setup global logging to a file.
logging.basicConfig(
    level=logging.INFO,
    filename="inventory_app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =============================================================================
# DetailedItemDialog: A dialog to add/edit detailed inventory items.
# =============================================================================
class DetailedItemDialog(QDialog):
    def __init__(self, fields, initial_data=None, parent=None):
        """
        fields: list of field names (strings).
        initial_data: optional dictionary with pre-filled values.
        """
        super().__init__(parent)
        self.setWindowTitle("Detailed Item Entry")
        self.resize(400, 300)
        self.fields = fields
        self.data = {}
        self.inputs = {}  # To store QLineEdit widgets keyed by field name.
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Create a QLineEdit for each field.
        for field in fields:
            line_edit = QLineEdit()
            if initial_data and field in initial_data:
                line_edit.setText(str(initial_data[field]))
            form_layout.addRow(QLabel(field + ":"), line_edit)
            self.inputs[field] = line_edit
        
        layout.addLayout(form_layout)
        
        # Buttons: OK and Cancel.
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def accept(self):
        # Build the data dictionary from all inputs.
        for field, widget in self.inputs.items():
            self.data[field] = widget.text().strip()
        super().accept()
    
    def get_data(self):
        return self.data

# =============================================================================
# HistoryDialog: Parses the log file for history entries for a given category.
# =============================================================================
class HistoryDialog(QDialog):
    def __init__(self, category_name, log_filename="inventory_app.log", parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.log_filename = log_filename
        self.setWindowTitle(f"History for {category_name}")
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        # Buttons: Refresh and Close.
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_history)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.load_history()
    
    def load_history(self):
        history_entries = []
        try:
            if os.path.exists(self.log_filename):
                with open(self.log_filename, "r", encoding="utf-8") as f:
                    for line in f:
                        # Look for log entries that mention the category in square brackets.
                        if f"[{self.category_name}]" in line:
                            history_entries.append(line.strip())
        except Exception as e:
            history_entries.append(f"Error reading log file: {e}")
        if history_entries:
            self.history_text.setPlainText("\n".join(history_entries))
        else:
            self.history_text.setPlainText("No history found for this category.")

# =============================================================================
# InventoryTab: A generic inventory management tab.
#
# This class can work in two modes:
#   - Simple mode: each item is a text string.
#   - Detailed mode: each item is a dictionary of values, and the UI uses a
#     custom dialog (DetailedItemDialog) for add/edit.
#
# Parameters:
#   category_name: Name of the category.
#   filename: File to load/save the inventory.
#   detailed: (bool) Whether to use detailed mode.
#   fields: (list of strings) Field names for detailed mode. (Ignored in simple mode.)
#   display_field: (optional) Which field to use as the summary text. If None,
#                  the first field in 'fields' is used.
# =============================================================================
class InventoryTab(QWidget):
    def __init__(self, category_name, filename, detailed=False, fields=None, display_field=None, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.filename = filename
        self.detailed = detailed
        self.fields = fields if detailed and fields else []
        self.display_field = display_field if display_field else (self.fields[0] if self.fields else None)
        
        # Main layout: list widget and a row of buttons.
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_item)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_item)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_item)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_inventory)
        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(self.show_history)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.history_button)
        self.layout.addLayout(button_layout)
        
        self.setLayout(self.layout)
        self.load_inventory()
    
    def record_history(self, action, item_text):
        """Log the action with a timestamp and the category name."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"{timestamp} - {action}: {item_text}"
        logging.info("[%s] %s", self.category_name, entry)
    
    def add_item(self):
        """Add a new item using either simple or detailed input."""
        if self.detailed:
            dialog = DetailedItemDialog(self.fields, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                # Use the display_field value (or first field) as the summary.
                summary = data.get(self.display_field, "Item")
                item = QListWidgetItem(summary)
                item.setData(Qt.UserRole, data)
                self.list_widget.addItem(item)
                self.record_history("Added", f"{data}")
        else:
            text, ok = QInputDialog.getText(self, f"Add {self.category_name} Item", "Item:")
            if ok and text.strip():
                item_text = text.strip()
                self.list_widget.addItem(item_text)
                self.record_history("Added", item_text)
    
    def remove_item(self):
        """Remove the selected item."""
        selected_row = self.list_widget.currentRow()
        if selected_row >= 0:
            if self.detailed:
                item = self.list_widget.item(selected_row)
                data = item.data(Qt.UserRole)
                self.record_history("Removed", f"{data}")
            else:
                item_text = self.list_widget.item(selected_row).text()
                self.record_history("Removed", item_text)
            self.list_widget.takeItem(selected_row)
    
    def edit_item(self):
        """Edit the selected item."""
        current_item = self.list_widget.currentItem()
        if current_item:
            if self.detailed:
                data = current_item.data(Qt.UserRole)
                dialog = DetailedItemDialog(self.fields, initial_data=data, parent=self)
                if dialog.exec_() == QDialog.Accepted:
                    new_data = dialog.get_data()
                    summary = new_data.get(self.display_field, "Item")
                    current_item.setText(summary)
                    current_item.setData(Qt.UserRole, new_data)
                    self.record_history("Edited", f"from {data} to {new_data}")
            else:
                original_text = current_item.text()
                text, ok = QInputDialog.getText(
                    self, f"Edit {self.category_name} Item", "Item:", text=original_text
                )
                if ok and text.strip():
                    new_text = text.strip()
                    current_item.setText(new_text)
                    self.record_history("Edited", f"from '{original_text}' to '{new_text}'")
    
    def load_inventory(self):
        """Load inventory items from the associated file."""
        self.list_widget.clear()
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            if self.detailed:
                                # Each line is a JSON object.
                                data = json.loads(line)
                                summary = data.get(self.display_field, "Item")
                                item = QListWidgetItem(summary)
                                item.setData(Qt.UserRole, data)
                                self.list_widget.addItem(item)
                            else:
                                self.list_widget.addItem(line)
                logging.info("Loaded %d item(s) for %s from %s.",
                             self.list_widget.count(), self.category_name, self.filename)
            except Exception as e:
                QMessageBox.warning(self, "Load Error",
                                    f"Could not load inventory for {self.category_name}:\n{e}")
    
    def save_inventory(self):
        """Save the current inventory list to the associated file."""
        items = []
        for i in range(self.list_widget.count()):
            if self.detailed:
                # Retrieve the full dictionary stored in the item.
                data = self.list_widget.item(i).data(Qt.UserRole)
                items.append(data)
            else:
                item_text = self.list_widget.item(i).text().strip()
                if item_text:
                    items.append(item_text)
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                if self.detailed:
                    for item in items:
                        f.write(json.dumps(item) + "\n")
                else:
                    for item in items:
                        f.write(item + "\n")
            self.record_history("Saved", f"{len(items)} item(s)")
            QMessageBox.information(self, "Save Successful",
                                    f"{self.category_name} inventory saved to {self.filename}.")
        except Exception as e:
            logging.error("Error saving inventory for %s: %s", self.category_name, e)
            QMessageBox.critical(self, "Save Error",
                                 f"Could not save inventory for {self.category_name}:\n{e}")
    
    def show_history(self):
        """Open the history dialog, parsing the log file for this category."""
        dialog = HistoryDialog(self.category_name, parent=self)
        dialog.exec_()

# =============================================================================
# BathroomProductsTab: A specialized tab for Bathroom Products with nested sub-tabs.
# =============================================================================
class BathroomProductsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        
        # For demonstration, using simple mode for these sub-categories.
        self.shower_tab = InventoryTab("Shower Products", "bathroom_shower.txt")
        self.dental_tab = InventoryTab("Dental Products", "bathroom_dental.txt")
        self.skincare_tab = InventoryTab("Skincare Products", "bathroom_skincare.txt")
        
        self.tab_widget.addTab(self.shower_tab, "Shower")
        self.tab_widget.addTab(self.dental_tab, "Dental")
        self.tab_widget.addTab(self.skincare_tab, "Skincare")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def save_all(self):
        """Save all sub-tab inventories."""
        self.shower_tab.save_inventory()
        self.dental_tab.save_inventory()
        self.skincare_tab.save_inventory()

# =============================================================================
# MainWindow: The main window that holds a tab for each inventory category.
#
# Here, we set up some categories in simple mode and others in detailed mode.
# For example, "Clothing", "Books", and "Art and Craft Supplies" are set up
# as detailed categories with their own field definitions.
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        self.inventory_tabs = []
        
        # Define some categories in simple mode.
        simple_categories = [
            ("Cleaning Tools/Resources", "cleaning_tools.txt"),
            ("Bedding and Towels", "bedding_towels.txt")
        ]
        for cat_name, filename in simple_categories:
            tab = InventoryTab(cat_name, filename, detailed=False)
            self.tab_widget.addTab(tab, cat_name)
            self.inventory_tabs.append(tab)
        
        # Define detailed categories with extra fields.
        # Example: Clothing
        clothing_fields = ["Name", "Size", "Color", "Brand", "Notes"]
        tab = InventoryTab("Clothing", "clothing.jsonl", detailed=True, fields=clothing_fields, display_field="Name")
        self.tab_widget.addTab(tab, "Clothing")
        self.inventory_tabs.append(tab)
        
        # Example: Books
        book_fields = ["Title", "Author", "ISBN", "Genre", "Notes"]
        tab = InventoryTab("Books", "books.jsonl", detailed=True, fields=book_fields, display_field="Title")
        self.tab_widget.addTab(tab, "Books")
        self.inventory_tabs.append(tab)
        
        # Example: Art and Craft Supplies
        art_fields = ["Item", "Type", "Brand", "Quantity", "Notes"]
        tab = InventoryTab("Art and Craft Supplies", "art_craft_supplies.jsonl", detailed=True, fields=art_fields, display_field="Item")
        self.tab_widget.addTab(tab, "Art and Craft Supplies")
        self.inventory_tabs.append(tab)
        
        # Bathroom Products as a specialized tab (using simple mode for now).
        self.bathroom_tab = BathroomProductsTab()
        self.tab_widget.addTab(self.bathroom_tab, "Bathroom Products")
        self.inventory_tabs.append(self.bathroom_tab)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.create_menu()
        self.apply_styles()
    
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        
        save_all_action = QAction("Save All Inventories", self)
        save_all_action.triggered.connect(self.save_all)
        file_menu.addAction(save_all_action)
    
    def save_all(self):
        """Save inventories for all tabs."""
        for tab in self.inventory_tabs:
            if isinstance(tab, BathroomProductsTab):
                tab.save_all()
            else:
                tab.save_inventory()
        self.status_bar.showMessage("All inventories saved.", 3000)
    
    def apply_styles(self):
        """Apply a simple stylesheet for a clean look."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9f9f9;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 2px solid #007ACC;
            }
            QPushButton {
                background-color: #007ACC;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005F9E;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: #f7f7f7;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
