import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QScrollArea, QLabel, QFormLayout, QLineEdit, QGroupBox, QSizePolicy
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QSize, QTimer
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor

from osdag_gui.ui.components.additional_inputs_button import AdditionalInputsButton
from osdag_gui.ui.components.custom_buttons import CustomButton
import osdag_gui.resources.resources_rc
from osdag_gui.db_manager import DatabaseManager
import sqlite3

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()  # Prevent changing selection on scroll

def right_aligned_widget(widget):
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    # Remove layout.addStretch()
    layout.addWidget(widget)
    layout.setAlignment(widget, Qt.AlignVCenter)  # Optional: vertical center
    return container


def apply_dropdown_style(widget, arrow_down_path):
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    # Removed setFixedWidth to allow expansion
    if isinstance(widget, QComboBox):
        style = f"""
        QComboBox {{
            padding: 2px;
            border: 1px solid black;
            border-radius: 5px;
            background-color: white;
            color: black;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 0px;
        }}
        QComboBox::down-arrow {{
            image: url("{arrow_down_path}");
            width: 15px;
            height: 15px;
            margin-right: 5px;
        }}
        QComboBox QAbstractItemView {{
            background-color: white;
            border: 1px solid black;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            color: black;
            background-color: white;
            border: none;
            border: 1px solid white;
            border-radius: 0;
            padding: 2px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            border: 1px solid #90AF13;
            background-color: white;
            color: black;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: white;
            color: black;
            border: 1px solid #90AF13;
        }}
        QComboBox QAbstractItemView::item:selected:hover {{
            background-color: white;
            color: black;
            border: 1px solid #94b816;
        }}
        """
        widget.setStyleSheet(style)
    elif isinstance(widget, QLineEdit):
        widget.setStyleSheet("""
        QLineEdit {
            padding: 1px 7px;
            border: 1px solid #070707;
            border-radius: 6px;
            background-color: white;
            color: #000000;
            font-weight: normal;
        }
        """)

def create_connecting_members_group(apply_style_func, arrow_path):
    db_manager = DatabaseManager()
    # It's assumed the DatabaseManager has a connection object, typically called 'conn'
    conn = db_manager.conn 
    # This line is crucial to get dictionary-like results
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Columns")
    rows = cursor.fetchall()
    column_sections = [row['Designation'] for row in rows]

    cursor.execute("SELECT * FROM Beams")
    beam = cursor.fetchall()
    primary_beams = [row['Designation'] for row in beam]
    secondary_beams = [row['Designation'] for row in beam]

    cursor.execute("SELECT * FROM Material")
    Mat = cursor.fetchall()
    materials = [row['Grade'] for row in Mat]
    
    # The rest of your function remains exactly the same...
    connectivity_configs = {
        "Column Flange-Beam Web": {
            "image": ":/images/colF2.png",
            "fields": [
                {"label": "Column Section *", "items": column_sections},
                {"label": "Primary Beam *", "items": primary_beams},
                {"label": "Material *", "items": materials}
            ]
        },
        "Column Web-Beam Web": {
            "image": ":/images/colW1.png",
            "fields": [
                {"label": "Column Section *", "items": column_sections},
                {"label": "Primary Beam *", "items": primary_beams},
                {"label": "Material *", "items": materials}
            ]
        },
        "Beam-Beam": {
            "image": ":/images/fin_beam_beam.png",
            "fields": [
                {"label": "Primary Beam *", "items": primary_beams},
                {"label": "Secondary Beam *", "items": secondary_beams},
                {"label": "Material *", "items": materials}
            ]
        }
    }


    group = QGroupBox("Connecting Members")
    group.setStyleSheet("""
        QGroupBox {
            border: 1px solid #90AF13;
            border-radius: 4px;
            margin-top: 0.8em;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: content;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 4px;
            margin-top: -15px;
            background-color: white;
        }
    """)
    layout = QVBoxLayout(group)
    layout.setSpacing(5)
    layout.setContentsMargins(4, 4, 4, 4)

    conn_form = QFormLayout()
    conn_form.setHorizontalSpacing(20)
    conn_form.setVerticalSpacing(10)
    conn_form.setContentsMargins(10, 5, 10, 5)
    conn_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    conn_form.setAlignment(Qt.AlignmentFlag.AlignRight)  # Align fields to the right

    connectivity_cb = NoScrollComboBox()
    connectivity_cb.addItems(list(connectivity_configs.keys()))
    apply_style_func(connectivity_cb, arrow_path)
    conn_form.addRow("Connectivity *", right_aligned_widget(connectivity_cb))
    layout.addLayout(conn_form)

    details_widget = QWidget()
    details_layout = QVBoxLayout(details_widget)
    details_layout.setContentsMargins(0, 0, 0, 0)
    details_layout.setSpacing(0)

    all_comboboxes = [connectivity_cb]
    connectivity_widgets = {}

    for conn_type, config in connectivity_configs.items():
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.setContentsMargins(5, 5, 5, 5)
        widget_layout.setSpacing(5)

        img_label = QLabel()
        img_path = config["image"]
        img_label.setPixmap(QPixmap(img_path).scaledToWidth(90, Qt.SmoothTransformation))
        img_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)
        form.setContentsMargins(10, 5, 10, 5)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setAlignment(Qt.AlignmentFlag.AlignRight)  # Align fields to the right

        form.addRow("", img_label)

        for field in config["fields"]:
            cb = NoScrollComboBox()
            cb.addItems(field["items"])
            apply_style_func(cb, arrow_path)
            form.addRow(field["label"], right_aligned_widget(cb))
            all_comboboxes.append(cb)

        widget_layout.addLayout(form)
        details_layout.addWidget(widget)
        connectivity_widgets[conn_type] = widget

    def switch_view(text):
        for conn_type, widget in connectivity_widgets.items():
            widget.setVisible(conn_type == text)

    connectivity_cb.currentTextChanged.connect(switch_view)
    switch_view(connectivity_cb.currentText())

    layout.addWidget(details_widget)
    return group

def create_group_box(title, fields, apply_style_func, arrow_path, horizontal_spacing=5):
    group = QGroupBox(title)
    group.setStyleSheet("""
        QGroupBox {
            border: 1px solid #90AF13;
            border-radius: 4px;
            margin-top: 0.8em;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: content;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 4px;
            margin-top: -15px;
            background-color: white;
        }
    """)
    form_layout = QFormLayout()
    form_layout.setHorizontalSpacing(horizontal_spacing)
    form_layout.setVerticalSpacing(10)
    form_layout.setContentsMargins(10, 10, 10, 10)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    # Data class already pads labels
    all_widgets = []
    for field in fields:
        label = field["label"]
        if "items" in field:
            widget = NoScrollComboBox()
            widget.addItems(field["items"])
        else:
            widget = QLineEdit()
            if "placeholder" in field:
                widget.setPlaceholderText(field["placeholder"])
        apply_style_func(widget, arrow_path)
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace;")
        form_layout.addRow(label_widget, right_aligned_widget(widget))
        all_widgets.append(widget)
    group.setLayout(form_layout)
    return group, all_widgets

class Data:
    def __init__(self):
        self.connectivity_configs = {
            "Connectivity *": {
                "Column Flange-Beam Web": {
                    "image": ":/images/colF2.png",
                    "fields": [
                        {"label": "Column Section *", "items": ["HB150", "HB200", "HB250", "HB300"]},
                        {"label": "Primary Beam *", "items": ["JB150", "JB175", "JB200", "JB225"]},
                        {"label": "Material *", "items": ["E 165 (Fe 290)", "E250", "E300", "E350"]}
                    ]
                },
                "Column Web-Beam Web": {
                    "image": ":/images/colW1.png",
                    "fields": [
                        {"label": "Column Section *", "items": ["HB150", "HB200", "HB250", "HB300"]},
                        {"label": "Primary Beam *", "items": ["JB150", "JB175", "JB200", "JB225"]},
                        {"label": "Material *", "items": ["E 165 (Fe 290)", "E250", "E300", "E350"]}
                    ]
                },
                "Beam-Beam": {
                    "image": ":/images/fin_beam_beam.png",
                    "fields": [
                        {"label": "Primary Beam *", "items": ["JB150", "JB175", "JB200", "JB225"]},
                        {"label": "Secondary Beam *", "items": ["JB150", "JB175", "JB200", "JB225"]},
                        {"label": "Material *", "items": ["E 165 (Fe 290)", "E250", "E300", "E350"]}
                    ]
                }
            }
        }
        self.group_configs = {
            "Factored Loads": {
                "fields": [
                    {"label": "Shear Force (kN)", "placeholder": "ex. 10 kN"},
                    {"label": "Axial Force (kN)", "placeholder": "ex. 10 kN"}
                ]
            },
            "Bolt": {
                "fields": [
                    {"label": "Diameter (mm) *", "items": ["All", "Customized"]},
                    {"label": "Type *", "items": ["Bearing Bolt", "Friction Grip Bolt"]},
                    {"label": "Property Class *(mm)", "items": ["All", "Customized"]}
                ]
            },
            "Plate": {
                "fields": [
                    {"label": "Thickness (mm) *", "items": ["All", "Customized"]}
                ]
            }
        }
        self.make_label_size_equal()

    def make_label_size_equal(self):
        # Collect all label strings from connectivity_configs and group_configs
        labels = []
        for label in self.connectivity_configs.keys():
            labels.append(label)
            label_dict = self.connectivity_configs[label]
            for config in label_dict.values():
                for field in config['fields']:
                    labels.append(field['label'])
        for config in self.group_configs.values():
            for field in config['fields']:
                labels.append(field['label'])
        # Find max length
        max_len = max(len(label) for label in labels)
        # Pad all labels to max_len
        for label in self.connectivity_configs.keys():
            for config in label_dict.values():
                for field in config['fields']:
                    field['label'] = field['label'].ljust(max_len)

        label = list(self.connectivity_configs.keys())[0]
        self.connectivity_configs[label.ljust(max_len)] = self.connectivity_configs[label]
        del self.connectivity_configs[label]

        for config in self.group_configs.values():
            for field in config['fields']:
                field['label'] = field['label'].ljust(max_len)

class InputDock(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setStyleSheet("background: transparent;")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_container = QWidget()
        self.original_width = int(self.width())
        self.setMinimumWidth(100)
        self.data = Data()  # <-- Create Data instance here
        self.build_left_panel()
        self.main_layout.addWidget(self.left_container)

        self.toggle_strip = QWidget()
        self.toggle_strip.setStyleSheet("background-color: #94b816;")
        self.toggle_strip.setFixedWidth(6)
        toggle_layout = QVBoxLayout(self.toggle_strip)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        toggle_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.toggle_btn = QPushButton("❮")
        self.toggle_btn.setFixedSize(6, 60)
        self.toggle_btn.setToolTip("Hide panel")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c8408;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #5e7407;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_input_dock)
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_btn)
        toggle_layout.addStretch()
        self.main_layout.addWidget(self.toggle_strip)

        self.right_spacer = QWidget()
        self.main_layout.addWidget(self.right_spacer)

    def get_menu_data(self):
        # Returns the menu data dicts from the Data instance
        return {
            'connectivity_configs': self.data.connectivity_configs,
            'group_configs': self.data.group_configs
        }

    def build_left_panel(self):
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # --- Main Content Panel (to be scrolled horizontally and vertically) ---
        self.left_panel = QWidget()
        self.left_panel.setStyleSheet("background-color: white;")
        panel_layout = QVBoxLayout(self.left_panel)
        panel_layout.setContentsMargins(5, 5, 5, 5)
        panel_layout.setSpacing(0)

        # --- Top Bar (fixed inside scroll area) ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        input_dock_btn = QPushButton("Input Dock")
        input_dock_btn.setStyleSheet(
            "background-color: #90AF13; color: white; border-radius: 5px; padding: 4px 16px; font-weight: bold;"
        )
        input_dock_btn.setFixedHeight(28)
        top_bar.addWidget(input_dock_btn)
        additional_inputs_btn = AdditionalInputsButton()
        additional_inputs_btn.setToolTip("Additional Inputs")
        top_bar.addWidget(additional_inputs_btn)
        top_bar.addStretch()
        panel_layout.addLayout(top_bar)

        # Vertical scroll area for group boxes (vertical only)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #EFEFEC;
                background-color: transparent;
                padding: 3px;
            }
            QScrollBar:vertical {
                background: #E0E0E0;
                width: 8px;
                margin: 0px 0px 0px 3px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #A0A0A0;
                min-height: 30px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #707070;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # --- Main Content (group boxes) ---
        arrow_path = ":/images/down_arrow.png"
        menu_data = self.get_menu_data()
        connecting_members_group = create_connecting_members_group(apply_dropdown_style, arrow_path)

        group_container = QWidget()
        group_container_layout = QVBoxLayout(group_container)
        group_container_layout.addWidget(connecting_members_group)
        group_configs = menu_data['group_configs']
        all_comboboxes = []
        for title, config in group_configs.items():
            group, widgets = create_group_box(
                title=title,
                fields=config["fields"],
                apply_style_func=apply_dropdown_style,
                arrow_path=arrow_path
            )
            group_container_layout.addWidget(group)
            all_comboboxes.extend(widgets)

        group_container_layout.addStretch()

        scroll_area.setWidget(group_container)
        panel_layout.addWidget(scroll_area)

        # --- Bottom Design Button (fixed inside scroll area) ---
        btn_button_layout = QHBoxLayout()
        btn_button_layout.setContentsMargins(0, 20, 0, 0)
        btn_button_layout.addStretch(1)

        svg_clickable_btn = CustomButton("Design")
        svg_clickable_btn.clicked.connect(lambda: print("design clicked"))
        # svg_clickable_btn.clicked.connect(lambda: print("design clicked"))


        btn_button_layout.addWidget(svg_clickable_btn, 2)
        btn_button_layout.addStretch(1)
        panel_layout.addLayout(btn_button_layout)

        # --- Horizontal scroll area for all right content ---
        h_scroll_area = QScrollArea()
        h_scroll_area.setWidgetResizable(True)
        h_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        h_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        h_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                background: #E0E0E0;
                height: 8px;
                margin: 3px 0px 0px 0px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #A0A0A0;
                min-width: 30px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #707070;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        h_scroll_area.setWidget(self.left_panel)

        left_layout.addWidget(h_scroll_area)

    def toggle_input_dock(self):
        parent = self.parent
        if hasattr(parent, 'toggle_animate'):
            is_collapsing = self.width() > 0
            parent.toggle_animate(show=not is_collapsing, dock='input')
        
        self.toggle_btn.setText("❯" if is_collapsing else "❮")
        self.toggle_btn.setToolTip("Show panel" if is_collapsing else "Hide panel")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() == 0 and hasattr(self.parent, 'update_docking_icons'):
            self.parent.update_docking_icons(False, self.parent.log_dock_active, self.parent.output_dock_active)
        elif self.width() > 0 and hasattr(self.parent, 'update_docking_icons'):
            self.parent.update_docking_icons(True, self.parent.log_dock_active, self.parent.output_dock_active)

#----------------Standalone-Test-Code--------------------------------

# class MyMainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setStyleSheet("border: none")

#         self.central_widget = QWidget()
#         self.central_widget.setObjectName("central_widget")
#         self.setCentralWidget(self.central_widget)

#         self.main_h_layout = QHBoxLayout(self.central_widget)
#         self.main_h_layout.addWidget(InputDock(),15)

#         self.main_h_layout.addStretch(40)

#         self.setWindowState(Qt.WindowMaximized)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MyMainWindow()
#     window.show()
#     sys.exit(app.exec()) 