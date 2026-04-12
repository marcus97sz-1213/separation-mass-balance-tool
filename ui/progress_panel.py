"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This file serves the purpose to create a progress panel that pops up when iteration begins and 
                      it prevents the app to freeze in the background.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import(
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QProgressBar,QPushButton
)

from PyQt6.QtCore import Qt

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 8.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
This class builds the progress panel UI that pop-ups when iteration begins.
"""
class ProgressPanel(QWidget):

    def __init__(self,parent = None):
        
        super().__init__(parent,Qt.WindowType.Tool)  #Tool is a windowtype where it is a floating utility panel
        
        #Defining window pop-up design
        self.setWindowTitle("Running Iteration...")
        self.setFixedWidth(400) 
        self.setStyleSheet("color:#000000;")

        #Create a vertical layout within the pop-up
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16,16,16,16)

        #Create label widget for title and also status update
        self.title_label = QLabel("Iteration in progress...")
        self.status_label = QLabel("Starting...")

        #Create progress bar widget to update iteration progress
        self.progress = QProgressBar()
        self.progress.setRange(0,100)       #The range of progress bar is from 0 to 100 (0% to 100%)
        self.progress.setValue(0)           #Initial value of the progress bar is 0

        #Create button for user to cancel the iteration
        self.cancel_btn = QPushButton("Cancel")

        #Create horizonral layout within the pop-up
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.cancel_btn)          #Cancel button is added to horizontal layout

        #Place the widgets into the pop-up window
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addLayout(row)
        layout.addStretch()

    #─────8.1 HELPER METHOD #1─────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method will update the progress bar based on iteration signal received as 'pct'
    """
    def update_progress(self,pct):
        self.progress.setValue(pct)

    #─────8.2 HELPER METHOD #2─────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method update the status label in the midst of iteration
    """
    def update_status(self,msg):
        self.status_label.setText(msg)

    #─────8.3 HELPER METHOD #3─────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method will be called when iteration is complete.
    """
    def mark_done(self):
        self.title_label.setText("Converged!")
        self.cancel_btn.setText("Close")







