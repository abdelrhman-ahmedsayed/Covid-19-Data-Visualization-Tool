"""
COVID-19 Data Visualization App — PyQt5 GUI
Port of the MATLAB MyCovid19App (Coursera Final Project).
"""

import sys
import os
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QSlider, QDateEdit, QFrame,
    QSplitter, QGroupBox, QGridLayout, QSizePolicy, QAbstractItemView,
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QLinearGradient, QBrush

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from models import DataLoader

# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
STYLESHEET = """
QMainWindow {
    background-color: #0d1117;
}
QWidget {
    color: #e6edf3;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}
QGroupBox {
    background-color: rgba(22, 27, 34, 0.95);
    border: 1px solid rgba(48, 54, 61, 0.8);
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-size: 13px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 12px;
    color: #58a6ff;
    font-size: 13px;
    font-weight: 700;
}
QListWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
    font-size: 12px;
    outline: none;
}
QListWidget::item {
    padding: 5px 8px;
    border-radius: 6px;
    margin: 1px 2px;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(88, 166, 255, 0.25), stop:1 rgba(136, 100, 255, 0.18));
    color: #79c0ff;
    border: 1px solid rgba(88, 166, 255, 0.4);
}
QListWidget::item:hover:!selected {
    background-color: rgba(88, 166, 255, 0.08);
}
QLineEdit {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: #e6edf3;
    selection-background-color: #58a6ff;
}
QLineEdit:focus {
    border: 1px solid #58a6ff;
    background-color: #0d1117;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #238636, stop:1 #2ea043);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2ea043, stop:1 #3fb950);
}
QPushButton:pressed {
    background-color: #238636;
}
QPushButton#resetBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6e40c9, stop:1 #8957e5);
}
QPushButton#resetBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8957e5, stop:1 #a371f7);
}
QPushButton#clearBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #da3633, stop:1 #f85149);
}
QPushButton#clearBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f85149, stop:1 #ff7b72);
}
QRadioButton {
    font-size: 12px;
    spacing: 6px;
    padding: 3px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #30363d;
    background-color: #161b22;
}
QRadioButton::indicator:checked {
    background-color: #58a6ff;
    border: 2px solid #58a6ff;
}
QRadioButton::indicator:hover {
    border: 2px solid #58a6ff;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #30363d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #58a6ff;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    background: #79c0ff;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #58a6ff, stop:1 #8957e5);
    border-radius: 3px;
}
QDateEdit {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    color: #e6edf3;
}
QDateEdit:focus {
    border: 1px solid #58a6ff;
}
QDateEdit::drop-down {
    border: none;
    width: 20px;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 800;
    color: #58a6ff;
    padding: 2px;
}
QLabel#subtitleLabel {
    font-size: 11px;
    color: #8b949e;
    padding: 0px;
}
QLabel#maValueLabel {
    font-size: 14px;
    font-weight: 700;
    color: #58a6ff;
    min-width: 28px;
}
"""


def parse_date(date_str: str) -> datetime:
    """Parse date strings like '1/22/20' to datetime."""
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


class MplCanvas(FigureCanvas):
    """Matplotlib canvas styled for dark mode."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.patch.set_facecolor('#0d1117')
        self.ax = self.fig.add_subplot(111)
        self._style_axes()
        super().__init__(self.fig)
        self.setMinimumHeight(350)

    def _style_axes(self):
        ax = self.ax
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#8b949e', which='both', labelsize=9)
        ax.xaxis.label.set_color('#8b949e')
        ax.yaxis.label.set_color('#8b949e')
        ax.title.set_color('#e6edf3')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.grid(True, alpha=0.15, color='#8b949e', linestyle='--')


class Covid19App(QMainWindow):
    """Main application window."""

    # Plot colors
    CASES_COLOR = '#58a6ff'
    DEATHS_COLOR = '#f85149'
    CASES_FILL = (88, 166, 255, 30)
    DEATHS_FILL = (248, 81, 73, 30)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("COVID-19 Data Visualization")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        # Load data
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covid_data.json")
        self.data = DataLoader(json_path)
        self.all_dates = [parse_date(d) for d in self.data.dates]

        # State
        self.current_country = None
        self.current_state = None

        self._build_ui()
        self._connect_signals()
        self._reset_all()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # ---- Left Sidebar ----
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Title
        title_label = QLabel("🦠 COVID-19 Viewer")
        title_label.setObjectName("titleLabel")
        left_layout.addWidget(title_label)

        subtitle_label = QLabel("Pandemic Data Visualization Tool")
        subtitle_label.setObjectName("subtitleLabel")
        left_layout.addWidget(subtitle_label)

        left_layout.addSpacing(6)

        # Search
        search_group = QGroupBox("Search")
        search_lay = QVBoxLayout(search_group)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Type to search countries...")
        search_lay.addWidget(self.search_edit)
        left_layout.addWidget(search_group)

        # Country list
        country_group = QGroupBox("Countries")
        country_lay = QVBoxLayout(country_group)
        self.country_list = QListWidget()
        self.country_list.setSelectionMode(QAbstractItemView.SingleSelection)
        country_lay.addWidget(self.country_list)
        left_layout.addWidget(country_group, stretch=3)

        # State list
        state_group = QGroupBox("States / Regions")
        state_lay = QVBoxLayout(state_group)
        self.state_list = QListWidget()
        self.state_list.setSelectionMode(QAbstractItemView.SingleSelection)
        state_lay.addWidget(self.state_list)
        left_layout.addWidget(state_group, stretch=2)

        main_layout.addWidget(left_panel)

        # ---- Center: Chart ----
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(4)

        self.canvas = MplCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("""
            QToolBar { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 2px; }
            QToolButton { color: #8b949e; padding: 4px; }
            QToolButton:hover { background: rgba(88,166,255,0.12); border-radius: 4px; }
        """)

        center_layout.addWidget(self.toolbar)
        center_layout.addWidget(self.canvas, stretch=1)
        main_layout.addWidget(center_panel, stretch=1)

        # ---- Right Sidebar: Controls ----
        right_panel = QWidget()
        right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Data type
        data_group = QGroupBox("Data Type")
        data_lay = QVBoxLayout(data_group)
        self.data_type_group = QButtonGroup(self)
        self.rb_cases = QRadioButton("📊  Cases")
        self.rb_deaths = QRadioButton("💀  Deaths")
        self.rb_both = QRadioButton("📊💀  Both")
        self.rb_cases.setChecked(True)
        self.data_type_group.addButton(self.rb_cases, 0)
        self.data_type_group.addButton(self.rb_deaths, 1)
        self.data_type_group.addButton(self.rb_both, 2)
        data_lay.addWidget(self.rb_cases)
        data_lay.addWidget(self.rb_deaths)
        data_lay.addWidget(self.rb_both)
        right_layout.addWidget(data_group)

        # Display mode
        mode_group = QGroupBox("Display Mode")
        mode_lay = QVBoxLayout(mode_group)
        self.mode_group = QButtonGroup(self)
        self.rb_cumulative = QRadioButton("Cumulative")
        self.rb_daily = QRadioButton("Daily")
        self.rb_cumulative.setChecked(True)
        self.mode_group.addButton(self.rb_cumulative, 0)
        self.mode_group.addButton(self.rb_daily, 1)
        mode_lay.addWidget(self.rb_cumulative)
        mode_lay.addWidget(self.rb_daily)
        right_layout.addWidget(mode_group)

        # Moving average
        ma_group = QGroupBox("Moving Average")
        ma_lay = QVBoxLayout(ma_group)
        ma_top = QHBoxLayout()
        ma_label = QLabel("Window:")
        self.ma_value_label = QLabel("1")
        self.ma_value_label.setObjectName("maValueLabel")
        ma_top.addWidget(ma_label)
        ma_top.addStretch()
        ma_top.addWidget(self.ma_value_label)
        ma_top.addWidget(QLabel("days"))
        ma_lay.addLayout(ma_top)
        self.ma_slider = QSlider(Qt.Horizontal)
        self.ma_slider.setMinimum(1)
        self.ma_slider.setMaximum(15)
        self.ma_slider.setValue(1)
        self.ma_slider.setTickPosition(QSlider.TicksBelow)
        self.ma_slider.setTickInterval(1)
        ma_lay.addWidget(self.ma_slider)
        right_layout.addWidget(ma_group)

        # Date range
        date_group = QGroupBox("Date Range")
        date_lay = QGridLayout(date_group)
        date_lay.addWidget(QLabel("From:"), 0, 0)
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("MM/dd/yyyy")
        date_lay.addWidget(self.date_start, 0, 1)
        date_lay.addWidget(QLabel("To:"), 1, 0)
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("MM/dd/yyyy")
        date_lay.addWidget(self.date_end, 1, 1)
        right_layout.addWidget(date_group)

        right_layout.addStretch()

        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.clear_btn = QPushButton("🗑  Clear Search")
        self.clear_btn.setObjectName("clearBtn")
        btn_layout.addWidget(self.clear_btn)

        self.reset_btn = QPushButton("🔄  Reset All")
        self.reset_btn.setObjectName("resetBtn")
        btn_layout.addWidget(self.reset_btn)

        right_layout.addLayout(btn_layout)
        main_layout.addWidget(right_panel)

    # ------------------------------------------------------------------
    # Signal Connections
    # ------------------------------------------------------------------
    def _connect_signals(self):
        self.country_list.currentItemChanged.connect(self._on_country_changed)
        self.state_list.currentItemChanged.connect(self._on_state_changed)
        self.search_edit.textChanged.connect(self._on_search)
        self.data_type_group.buttonClicked.connect(self._update_plot)
        self.mode_group.buttonClicked.connect(self._update_plot)
        self.ma_slider.valueChanged.connect(self._on_ma_changed)
        self.date_start.dateChanged.connect(self._update_plot)
        self.date_end.dateChanged.connect(self._update_plot)
        self.clear_btn.clicked.connect(self._clear_search)
        self.reset_btn.clicked.connect(self._reset_all)

    # ------------------------------------------------------------------
    # Data Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _moving_average(data: np.ndarray, window: int) -> np.ndarray:
        if window <= 1:
            return data.copy()
        kernel = np.ones(window) / window
        # Use 'same' mode and handle edges
        result = np.convolve(data, kernel, mode='same')
        return result

    def _get_date_indices(self):
        """Return (start_idx, end_idx) based on date pickers."""
        d_start = self.date_start.date().toPyDate()
        d_end = self.date_end.date().toPyDate()
        start_dt = datetime(d_start.year, d_start.month, d_start.day)
        end_dt = datetime(d_end.year, d_end.month, d_end.day)

        start_idx = 0
        end_idx = len(self.all_dates) - 1

        for i, d in enumerate(self.all_dates):
            if d >= start_dt:
                start_idx = i
                break
        for i in range(len(self.all_dates) - 1, -1, -1):
            if self.all_dates[i] <= end_dt:
                end_idx = i
                break

        return start_idx, end_idx + 1  # end exclusive

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _populate_country_list(self, names=None):
        self.country_list.blockSignals(True)
        self.country_list.clear()
        names = names or self.data.country_names
        for name in names:
            self.country_list.addItem(name)
        self.country_list.blockSignals(False)

    def _on_country_changed(self, current, previous):
        if current is None:
            return
        name = current.text()
        country = self.data.get_country(name)
        if country is None:
            return
        self.current_country = country
        self.current_state = None

        # Populate states
        self.state_list.blockSignals(True)
        self.state_list.clear()
        if country.number_of_states > 0:
            self.state_list.addItem("(All / Country Total)")
            for sn in country.list_of_state_names:
                self.state_list.addItem(sn)
            self.state_list.setCurrentRow(0)
        self.state_list.blockSignals(False)

        self._update_plot()

    def _on_state_changed(self, current, previous):
        if current is None or self.current_country is None:
            return
        text = current.text()
        if text == "(All / Country Total)":
            self.current_state = None
        else:
            for s in self.current_country.list_of_states:
                if s.name == text:
                    self.current_state = s
                    break
        self._update_plot()

    def _on_search(self, text):
        if not text.strip():
            self._populate_country_list()
            return
        matches = self.data.search_countries(text)
        self._populate_country_list(matches)

    def _on_ma_changed(self, value):
        self.ma_value_label.setText(str(value))
        self._update_plot()

    def _clear_search(self):
        self.search_edit.clear()
        self._populate_country_list()

    def _reset_all(self):
        self.search_edit.clear()
        self._populate_country_list()
        self.rb_cases.setChecked(True)
        self.rb_cumulative.setChecked(True)
        self.ma_slider.setValue(1)
        self.ma_value_label.setText("1")

        # Set date range
        if self.all_dates:
            first = self.all_dates[0]
            last = self.all_dates[-1]
            self.date_start.setDateRange(
                QDate(first.year, first.month, first.day),
                QDate(last.year, last.month, last.day)
            )
            self.date_end.setDateRange(
                QDate(first.year, first.month, first.day),
                QDate(last.year, last.month, last.day)
            )
            self.date_start.setDate(QDate(first.year, first.month, first.day))
            self.date_end.setDate(QDate(last.year, last.month, last.day))

        # Select first country
        if self.country_list.count() > 0:
            self.country_list.setCurrentRow(0)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def _update_plot(self, *args):
        source = self.current_state if self.current_state else self.current_country
        if source is None:
            return

        ax = self.canvas.ax
        ax.clear()
        self.canvas._style_axes()

        # Determine data
        is_cumulative = self.rb_cumulative.isChecked()
        show_cases = self.rb_cases.isChecked() or self.rb_both.isChecked()
        show_deaths = self.rb_deaths.isChecked() or self.rb_both.isChecked()
        ma_window = self.ma_slider.value()

        start_idx, end_idx = self._get_date_indices()
        dates = self.all_dates[start_idx:end_idx]

        if len(dates) == 0:
            self.canvas.draw()
            return

        if is_cumulative:
            cases_data = source.cumulative_cases[start_idx:end_idx]
            deaths_data = source.cumulative_deaths[start_idx:end_idx]
            mode_label = "Cumulative"
        else:
            cases_data = source.daily_cases[start_idx:end_idx]
            deaths_data = source.daily_deaths[start_idx:end_idx]
            mode_label = "Daily"

        # Apply moving average
        if ma_window > 1:
            cases_data = self._moving_average(cases_data, ma_window)
            deaths_data = self._moving_average(deaths_data, ma_window)
            ma_label = f" ({ma_window}-day avg)"
        else:
            ma_label = ""

        # Plot
        if show_cases:
            ax.plot(dates, cases_data, color=self.CASES_COLOR, linewidth=1.8,
                    label=f"Cases{ma_label}", zorder=3)
            ax.fill_between(dates, cases_data, alpha=0.08, color=self.CASES_COLOR, zorder=2)

        if show_deaths:
            ax.plot(dates, deaths_data, color=self.DEATHS_COLOR, linewidth=1.8,
                    label=f"Deaths{ma_label}", zorder=3)
            ax.fill_between(dates, deaths_data, alpha=0.08, color=self.DEATHS_COLOR, zorder=2)

        # Title
        entity_name = source.name if hasattr(source, 'name') else "Unknown"
        ax.set_title(f"{entity_name} — {mode_label} COVID-19 Data",
                     fontsize=15, fontweight='bold', color='#e6edf3', pad=14)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Count", fontsize=10)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        self.canvas.fig.autofmt_xdate(rotation=30)

        # Y-axis formatting with comma separator
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))

        if show_cases or show_deaths:
            ax.legend(loc='upper left', fontsize=10, fancybox=True,
                      framealpha=0.3, edgecolor='#30363d',
                      facecolor='#161b22', labelcolor='#e6edf3')

        self.canvas.fig.tight_layout()
        self.canvas.draw()


# ======================================================================
# Entry point
# ======================================================================
def main():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0d1117"))
    palette.setColor(QPalette.WindowText, QColor("#e6edf3"))
    palette.setColor(QPalette.Base, QColor("#161b22"))
    palette.setColor(QPalette.AlternateBase, QColor("#1c2128"))
    palette.setColor(QPalette.ToolTipBase, QColor("#161b22"))
    palette.setColor(QPalette.ToolTipText, QColor("#e6edf3"))
    palette.setColor(QPalette.Text, QColor("#e6edf3"))
    palette.setColor(QPalette.Button, QColor("#21262d"))
    palette.setColor(QPalette.ButtonText, QColor("#e6edf3"))
    palette.setColor(QPalette.BrightText, QColor("#58a6ff"))
    palette.setColor(QPalette.Link, QColor("#58a6ff"))
    palette.setColor(QPalette.Highlight, QColor("#388bfd"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = Covid19App()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
