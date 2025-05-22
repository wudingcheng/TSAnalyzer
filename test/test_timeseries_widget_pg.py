import unittest
import pandas as pd
from datetime import datetime
import pyqtgraph as pg
from qtpy.QtWidgets import QApplication

# Assuming TSAnalyzer is in PYTHONPATH or project structure allows this import
from TSAnalyzer.widgets.timeseries_figure import TimeSeriesWidget
from collections import namedtuple

# Mock reader object
MockReader = namedtuple('MockReader', ['df', 'columns', 'name'])

class TestTimeSeriesWidgetPyQtGraph(unittest.TestCase):

    app = None # Hold reference to QApplication

    @classmethod
    def setUpClass(cls):
        # Ensure a QApplication instance exists for widget creation.
        # This is crucial for any Qt widget testing.
        if QApplication.instance() is None:
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_instantiation_and_basic_plot(self):
        """Test basic instantiation and plotting of data."""
        widget = TimeSeriesWidget()
        self.assertIsNotNone(widget, "TimeSeriesWidget should be instantiated.")
        self.assertIsInstance(widget.pgCanvas, pg.GraphicsLayoutWidget,
                              "Widget's pgCanvas should be a GraphicsLayoutWidget.")

        # Prepare sample data mimicking what a reader would provide
        dates = [datetime(2023, 1, 1, 0, 0, 0), 
                 datetime(2023, 1, 2, 0, 0, 0), 
                 datetime(2023, 1, 3, 0, 0, 0)]
        data = {'north': [1.0, 2.5, 3.2], 
                'east': [4.0, 5.1, 6.3],
                'up': [-0.5, 0.0, 0.5]}
        df = pd.DataFrame(data, index=pd.to_datetime(dates))
        
        # Create a mock reader object
        mock_reader = MockReader(df=df, columns=['north', 'east', 'up'], name='TestSite01')

        # Call the slot that triggers data loading and plotting
        widget.slotOnDataLoaded(mock_reader)

        # The TimeSeriesThread's start() method directly calls rendering methods.
        # We need to ensure signals are processed if the thread relies on event loop for slot execution,
        # or wait if it's truly async. However, given current structure, it might execute fairly sequentially.
        # For robustness in tests, especially if signals between threads were involved, QTest.qWait might be used.
        # For now, assume plotting completes sufficiently quickly for checks.
        # If tests become flaky, cls.app.processEvents() or QTest.qWait() might be needed here.
        if hasattr(self.app, 'processEvents'):
             self.app.processEvents()


        # Check that plot items were created as expected
        self.assertIsNotNone(widget.plotItems, "widget.plotItems should not be None after plotting.")
        self.assertEqual(len(widget.plotItems), len(mock_reader.columns),
                         f"Number of plotItems should match number of columns ({len(mock_reader.columns)}).")

        # Verify each plot item
        for i, plot_item in enumerate(widget.plotItems):
            self.assertIsInstance(plot_item, pg.PlotItem, f"Item {i} in plotItems should be a PlotItem.")
            
            # Check that data was plotted
            data_items = plot_item.listDataItems()
            self.assertTrue(len(data_items) > 0, f"PlotItem {i} ('{mock_reader.columns[i]}') should have at least one data item.")
            # Further check on data item content if necessary, e.g., number of points
            # For example, data_items[0].xData and data_items[0].yData
            self.assertEqual(len(data_items[0].yData), len(df), f"PlotDataItem in PlotItem {i} should have correct number of points.")

            # Check that the bottom axis is a DateAxisItem
            bottom_axis = plot_item.getAxis('bottom')
            self.assertIsInstance(bottom_axis, pg.DateAxisItem,
                                  f"Bottom axis of PlotItem {i} ('{mock_reader.columns[i]}') should be a DateAxisItem.")
            
            # Check that the left axis label matches the column name
            left_axis = plot_item.getAxis('left')
            self.assertEqual(left_axis.labelText, mock_reader.columns[i],
                             f"Left axis label of PlotItem {i} should be '{mock_reader.columns[i]}'.")

    @classmethod
    def tearDownClass(cls):
        # Optional: Clean up QApplication if it was created by this test class
        # However, typically the test runner handles the application lifecycle or it's a single instance.
        # If cls.app was created by setUpClass, one might consider cls.app.quit() or similar,
        # but for unittest, it's often left running or managed externally.
        pass

if __name__ == '__main__':
    # This allows running the test directly using `python -m test.test_timeseries_widget_pg`
    # Ensure QApplication is handled correctly if run this way.
    # unittest.main() might not run the event loop, so setUpClass is important.
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTimeSeriesWidgetPyQtGraph))
    runner = unittest.TextTestRunner()
    # Ensure QApplication is created before running tests if not using a Qt-aware runner
    if QApplication.instance() is None:
        _app_for_direct_run = QApplication([]) # Store to keep alive
    runner.run(suite)
    # If _app_for_direct_run was created, it will be garbage collected or exit when script ends.
    # For proper cleanup in some CI, sys.exit(not result.wasSuccessful()) might be used.
