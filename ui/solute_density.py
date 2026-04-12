"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : this is the fourth tab on the main window that display the preview of solute density table on the
                      tab based on user selected solute type from the drop down created in user_input.py.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
import os
import pandas as pd
import numpy as np
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,QLabel,QFrame,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView
    )

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────HELPER FUNCTION #6───────────────────────────────────────────────────────────────────────────────────────────────
def solute_density_folder() -> str:
    if getattr(sys,"frozen",False):
        app_root = sys._MEIPASS
    else:
        app_root = os.path.dirname(os.path.abspath(__file__))

        if os.path.basename(app_root).lower()=="ui":
            app_root = os.path.dirname(app_root)
    return os.path.join(app_root,"solute")

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 6.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
Create a class to preview the density table for user selected solute type in the UserInputTab()
"""   
class soluteDensityTab(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    #─────HELPER METHOD #0─────────────────────────────────────────────────────────────────────────────────────────────
    def build_ui(self):
            
            #Set up vertical box layout
            root = QVBoxLayout(self)
            root.setContentsMargins(24,24,24,24)
            root.setSpacing(10)

            #Set up tab title
            title = QLabel("Solute Density Preview")
            title.setObjectName("title")
            root.addWidget(title)

            #Set up divider below title
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setObjectName("divider")
            root.addWidget(divider)

            #Setup table widget to populate density table
            self.solute_density_table = QTableWidget()
            self.solute_density_table.setObjectName("table")
            self.solute_density_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.solute_density_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            root.addWidget(self.solute_density_table,stretch=1)
            root.addStretch()

    #─────HELPER METHOD #1─────────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method is being called in the user input tab where when a type of solute is chosen from the drop down,
    it will automatically trace the filepath of the file that contains all solute density data. Then, a matching 
    density table will be extracted and being displayed on the table widget.
    """
    def populate_solute_table(self,df:pd.DataFrame):
         
        #Determine row and column numbers for the data frame
         solute_column_count = len(df.columns)
         solute_row_count = len(df)

        #Create a list to store all columns from the data frame
         solute_column = df.columns.to_list()

        #Set the table widget column and row based on the determined dataframe row and column count
         self.solute_density_table.setColumnCount(solute_column_count)
         self.solute_density_table.setRowCount(solute_row_count)

        #Label the column header based on data frame column names 
         self.solute_density_table.setHorizontalHeaderLabels(solute_column)

        #Loop through each row in the data frame
         for i,row in df.iterrows():            #'.iterrows()' returns row index and also row series
              for j,value in enumerate(row):    #Loop through each element in the series using enumerate method
                   self.solute_density_table.setItem(i,j,QTableWidgetItem(str(np.round(value,3))))
                
    




    










    




  


       


