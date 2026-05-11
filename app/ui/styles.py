def build_stylesheet(primary: str) -> str:
    return f"""
    QWidget {{
        font-family: Segoe UI;
        font-size: 10pt;
        color: #0f172a;
        background: #f8fafc;
    }}
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {{
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 7px;
    }}
    QPushButton {{
        background: {primary};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: #1d4ed8; }}
    QPushButton[secondary="true"] {{
        background: #e2e8f0;
        color: #0f172a;
    }}
    QPushButton[danger="true"] {{
        background: #dc2626;
        color: white;
    }}
    QTableWidget {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: #e2e8f0;
        selection-background-color: #dbeafe;
    }}
    QHeaderView::section {{
        background: #e2e8f0;
        color: #0f172a;
        padding: 7px;
        border: none;
        font-weight: 700;
    }}
    QListWidget {{
        background: #0f172a;
        color: #cbd5e1;
        border: none;
        font-size: 11pt;
    }}
    QListWidget::item {{
        padding: 12px 14px;
        border-left: 4px solid transparent;
    }}
    QListWidget::item:selected {{
        background: #1e293b;
        color: white;
        border-left: 4px solid {primary};
    }}
    QLabel[metric="true"] {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        font-size: 12pt;
        font-weight: 700;
    }}
    """
