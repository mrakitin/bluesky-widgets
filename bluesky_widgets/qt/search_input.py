import contextlib
from datetime import datetime, timedelta
from qtpy.QtCore import QDateTime
from qtpy.QtWidgets import (
    QButtonGroup,
    QDateTimeEdit,
    QWidget,
    QPushButton,
    QFormLayout,
    QRadioButton,
    QGridLayout,
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
        # Radiobuttons to quickly select default time period
        self.all_widget = QRadioButton("All")
        self.year_widget = QRadioButton("1 Year")
        self.month_widget = QRadioButton("30 Days")
        self.week_widget = QRadioButton("1 Week")
        self.today_widget = QRadioButton("24h")
        self.hour_widget = QRadioButton("1 Hour")
        self.radio_button_group = QButtonGroup()
        self.radio_button_group.addButton(self.all_widget)
        self.radio_button_group.addButton(self.year_widget)
        self.radio_button_group.addButton(self.month_widget)
        self.radio_button_group.addButton(self.week_widget)
        self.radio_button_group.addButton(self.today_widget)
        self.radio_button_group.addButton(self.hour_widget)
        default_period_layout = QGridLayout()
        default_period_layout.setHorizontalSpacing(85)
        default_period_layout.setVerticalSpacing(10)
        default_period_layout.addWidget(self.all_widget, 0, 0, 1, 2)
        default_period_layout.addWidget(self.year_widget, 1, 0, 1, 2)
        default_period_layout.addWidget(self.month_widget, 2, 0, 1, 2)
        default_period_layout.addWidget(self.week_widget, 0, 1, 1, 2)
        default_period_layout.addWidget(self.today_widget, 1, 1, 1, 2)
        default_period_layout.addWidget(self.hour_widget, 2, 1, 1, 2)
        self.layout().addRow("When:", default_period_layout)

        # TODO: rethink if restriction to acceptable timedelta values is required
        # from ..components.search.search_input import SearchInput
        # self.allowed = {timedelta(days=-1), timedelta(days=-30), timedelta(minutes=-60), timedelta(days=-7),
        #                 timedelta(days=-365)}
        # def time_validator(since=None, until=None):
        #     """
        #     Enforce that since and until are values that a UI can represent.
        #     This is an example similar to what will be used in the Qt UI.
        #     """
        #     now = timedelta()
        #     if isinstance(since, timedelta):
        #         if not (until is None or until == now):
        #             raise ValueError(
        #                 "This UI cannot express since=timedelta(...) unless until "
        #                 "is timedelta() or None."
        #             )
        #         for item in allowed:
        #             if since == item:
        #                 break
        #         else:
        #             # No matches
        #             raise ValueError(
        #                 "This UI can only express since as a timedelta if it is "
        #                 f"one of {allowed}. The value {since} is not allowed"
        #             )
        # s = SearchInput()
        # s.time_validator = time_validator

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

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.layout().addWidget(self.refresh_button)

        # Changes to the GUI update the model.
        self.since_widget.dateTimeChanged.connect(self.on_since_view_changed)
        self.until_widget.dateTimeChanged.connect(self.on_until_view_changed)

        self.refresh_button.clicked.connect(self.model.request_reload)
        self.model.events.reload.connect(self.on_reload)
        self.model.events.query.connect(self.on_reload)
        # Changes to the model update the GUI.
        self.model.events.since.connect(self.on_since_model_changed)
        self.model.events.until.connect(self.on_until_model_changed)

        # connect QRadioButtons and change date dropdowns (since/until widgets) accordingly
        self.hour_widget.toggled.connect(self.on_toggle_hour)
        self.today_widget.toggled.connect(self.on_toggle_24h)
        self.week_widget.toggled.connect(self.on_toggle_week)
        self.month_widget.toggled.connect(self.on_toggle_month)
        self.year_widget.toggled.connect(self.on_toggle_year)
        self.all_widget.toggled.connect(self.on_toggle_all)

        self.all_widget.setChecked(True)

    def on_reload(self, event):
        now = datetime.now().timestamp()
        if isinstance(self.model.since, timedelta):
            with _blocked(self.since_widget):
                self.since_widget.setDateTime(
                    QDateTime.fromSecsSinceEpoch(now + self.model.since.total_seconds()))
        if isinstance(self.model.until, timedelta):
            with _blocked(self.until_widget):
                self.until_widget.setDateTime(
                    QDateTime.fromSecsSinceEpoch(now + self.model.until.total_seconds()))

    def on_since_view_changed(self, qdatetime):
        # When GUI is updated
        self.model.since = qdatetime.toSecsSinceEpoch()

    def on_since_model_changed(self, event):
        # When model is updated (e.g. from console or by clicking a QRadioButton)
        now = datetime.now().timestamp()
        if isinstance(event.date, timedelta):
            qdatetime = QDateTime.fromSecsSinceEpoch(now + event.date.total_seconds())
            if event.date == timedelta(minutes=-60):
                self.hour_widget.setChecked(True)
            elif event.date == timedelta(days=-1):
                self.today_widget.setChecked(True)
            elif event.date == timedelta(days=-7):
                self.week_widget.setChecked(True)
            elif event.date == timedelta(days=-30):
                self.month_widget.setChecked(True)
            elif event.date == timedelta(days=-365):
                self.year_widget.setChecked(True)
            else:
                # No checkbox associated with this custom timedelta
                pass
        else:
            # Must be a datetime
            if event.date == ADA_LOVELACE_BIRTHDAY:
                self.all_widget.setChecked(True)
            else:
                self.uncheck_radiobuttons()
            qdatetime = QDateTime()
            qdatetime.setSecsSinceEpoch(event.date.timestamp())
        with _blocked(self.since_widget):
            self.since_widget.setDateTime(qdatetime)
        with _blocked(self.until_widget):
            self.until_widget.setDateTime(QDateTime.fromSecsSinceEpoch(now))

    def on_until_view_changed(self, qdatetime):
        # When GUI is updated
        self.model.until = qdatetime.toSecsSinceEpoch()

    def on_until_model_changed(self, event):
        # When model is updated (e.g. from console or by clicking a QRadioButton)
        if not isinstance(event.date, timedelta):
            qdatetime = QDateTime()
            qdatetime.setSecsSinceEpoch(event.date.timestamp())
            self.uncheck_radiobuttons()
            with _blocked(self.until_widget):
                self.until_widget.setDateTime(qdatetime)

    def on_toggle_24h(self):
        if self.today_widget.isChecked():
            self.model.since = timedelta(days=-1)
            self.model.until = timedelta()

    def on_toggle_hour(self):
        if self.hour_widget.isChecked():
            self.model.since = timedelta(minutes=-60)
            self.model.until = timedelta()

    def on_toggle_week(self):
        if self.week_widget.isChecked():
            self.model.since = timedelta(days=-7)
            self.model.until = timedelta()

    def on_toggle_month(self):
        if self.month_widget.isChecked():
            self.model.since = timedelta(days=-30)
            self.model.until = timedelta()

    def on_toggle_year(self):
        if self.year_widget.isChecked():
            self.model.since = timedelta(days=-365)
            self.model.until = timedelta()

    def on_toggle_all(self):
        # Search for all catalogs since Ada Lovelace's Birthday.
        if self.all_widget.isChecked():
            self.model.since = ADA_LOVELACE_BIRTHDAY
            self.model.until = timedelta()

    def uncheck_radiobuttons(self):
        self.radio_button_group.setExclusive(False)
        self.all_widget.setChecked(False)
        self.year_widget.setChecked(False)
        self.month_widget.setChecked(False)
        self.week_widget.setChecked(False)
        self.today_widget.setChecked(False)
        self.hour_widget.setChecked(False)
        self.radio_button_group.setExclusive(True)


@contextlib.contextmanager
def _blocked(qobject):
    "Block signals from this object inside the context."
    qobject.blockSignals(True)
    yield
    qobject.blockSignals(False)


# We need some concrete datetime to show in the "Since" datetime picker when
# the "All" button is checked. It should be some time old enough that it isn't
# likely to leave out wanted data. We cheekily choose this birthday as that
# time.
ADA_LOVELACE_BIRTHDAY = datetime(1815, 12, 10)
