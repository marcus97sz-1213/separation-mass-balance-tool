"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This is the fifth tab on the main window that display the preview of solvent density table on the
                      tab based on user selected solvent type from the drop down created in user_input.py.
"""
##══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
import os
import pandas as pd
import numpy as np
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,QLabel,QFrame,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView
    )

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────HELPER FUNCTION #7───────────────────────────────────────────────────────────────────────────────────────────────
def solvent_density_folder() -> str:
    if getattr(sys,"frozen",False):
        app_root = sys._MEIPASS
    else:
        app_root = os.path.dirname(os.path.abspath(__file__)) 

        if os.path.basename(app_root).lower()=="ui":
            app_root = os.path.dirname(app_root)
    return os.path.join(app_root,"solvent")

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 7.0──────────────────────────────────────────────────────────────────────────────────────────────────────── 
"""
Create a class to preview the density table for user selected solvent type in the UserInputTab()
"""    
class solventDensityTab(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    #─────HELPER METHOD #0─────────────────────────────────────────────────────────────────────────────────────────────
    def build_ui(self):
            root = QVBoxLayout(self)
            root.setContentsMargins(24,24,24,24)
            root.setSpacing(10)

            title = QLabel("Solvent Density Preview")
            title.setObjectName("title")
            root.addWidget(title)

            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setObjectName("divider")
            root.addWidget(divider)

            self.solvent_density_table = QTableWidget()
            self.solvent_density_table.setObjectName("table")
            self.solvent_density_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.solvent_density_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            root.addWidget(self.solvent_density_table,stretch=1)

    #─────HELPER METHOD #1─────────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method is being called in the user input tab where when a type of solvent is chosen from the drop down,
    it will automatically trace the filepath of the file that contains all solvent density data. Then, a matching 
    density table will be extracted and being displayed on the table widget.
    """
    def populate_solvent_table(self,df:pd.DataFrame):
         
        #Determine row and column numbers for the data frame
         solvent_column_count = len(df.columns)
         solvent_row_count = len(df)
         
        #Create a list to store all columns from the data frame 
         solvent_column = df.columns.to_list()

        #Set the table widget column and row based on the determined dataframe row and column count
         self.solvent_density_table.setColumnCount(solvent_column_count)
         self.solvent_density_table.setRowCount(solvent_row_count)

        #Label the column header based on data frame column names 
         self.solvent_density_table.setHorizontalHeaderLabels(solvent_column)

        #Loop through each row in the data frame
         for i,row in df.iterrows():            #'.iterrows()' returns row index and also row series
              for j,value in enumerate(row):    #Loop through each element in the series using enumerate method
                   self.solvent_density_table.setItem(i,j,QTableWidgetItem(str(np.round(value,3))))
    




    










    




  


       


