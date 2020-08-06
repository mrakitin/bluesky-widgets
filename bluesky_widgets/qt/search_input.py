from qtpy.QtCore import QDateTime
from qtpy.QtWidgets import (
    QDateTimeEdit,
    QWidget,
    QPushButton,
    QFormLayout,
    QRadioButton,
    QGridLayout,
    QButtonGroup
)


class QtSearchInput(QWidget):
    """
    Qt view for SearchInput

    Parameters
    ----------
    model: SearchInput
    """

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

        self.setLayout(QFormLayout())
        # 4 Radiobuttons to quickly select default time period
        self.all_widget = QRadioButton("All")
        self.days_widget = QRadioButton("30 Days")
        self.today_widget = QRadioButton("Today")
        self.hour_widget = QRadioButton("Last Hour")
        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.all_widget)
        self.radio_button_group.addButton(self.days_widget)
        self.radio_button_group.addButton(self.today_widget)
        self.radio_button_group.addButton(self.hour_widget)
        default_period_layout = QGridLayout()
        default_period_layout.addWidget(self.all_widget, 0, 0, 1, 1)
        default_period_layout.addWidget(self.days_widget, 0, 1, 1, 1)
        default_period_layout.addWidget(self.today_widget, 1, 0, 1, 1)
        default_period_layout.addWidget(self.hour_widget, 1, 1, 1, 1)
        self.layout().addRow("When:", default_period_layout)
        when_widget = QWidget()
        when_widget.setLayout(default_period_layout)

        # "Since: <datetime picker>"
        self.since_widget = QDateTimeEdit()
        self.since_widget.setCalendarPopup(True)
        self.since_widget.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout().addRow("Since:", self.since_widget)

        # "Until: <datetime picker>"
        self.until_widget = QDateTimeEdit()
        self.until_widget.setCalendarPopup(True)
        self.until_widget.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.layout().addRow("Until:", self.until_widget)

        self.refresh_button = QPushButton("Refresh")
        self.layout().addWidget(self.refresh_button)

        # Initialize values.
        qdatetime = QDateTime()
        qdatetime.setSecsSinceEpoch(self.model.since)
        self.since_widget.setDateTime(qdatetime)
        qdatetime = QDateTime()
        qdatetime.setSecsSinceEpoch(self.model.until)
        self.until_widget.setDateTime(qdatetime)

        # Changes to the GUI update the model.
        self.since_widget.dateTimeChanged.connect(self.on_since_view_changed)
        self.until_widget.dateTimeChanged.connect(self.on_until_view_changed)
        self.refresh_button.clicked.connect(self.model.events.reload)
        # Changes to the model update the GUI.
        self.model.events.since.connect(self.on_since_model_changed)
        self.model.events.until.connect(self.on_until_model_changed)

        # connect QRadioButtons and change date dropdowns (since/until widgets) accordingly
        self.today_widget.clicked.connect(on_select_today)
        self.hour_widget.clicked.connect(on_select_lasthour)
        self.days_widget.clicked.connect(on_select_30days)
        self.all_widget.clicked.connect(on_select_all)

    def on_since_view_changed(self, qdatetime):
        # When GUI is updated
        self.model.since = qdatetime.toSecsSinceEpoch()

    def on_since_model_changed(self, event):
        # When model is updated (e.g. from console)
        qdatetime = QDateTime()
        qdatetime.setSecsSinceEpoch(event.date)
        self.since_widget.setDateTime(qdatetime)

    def on_until_view_changed(self, qdatetime):
        # When GUI is updated
        self.model.until = qdatetime.toSecsSinceEpoch()

    def on_until_model_changed(self, event):
        # When model is updated (e.g. from console)
        qdatetime = QDateTime()
        qdatetime.setSecsSinceEpoch(event.date)
        self.until_widget.setDateTime(qdatetime)

