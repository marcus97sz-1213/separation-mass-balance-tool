"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This is the first tab on the main window that allows user to set up necessary parameters to be 
                      used in the iteration later on.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
"""
1. "pandas" is one of the library that allows data manipulation
"""
import os
import pandas as pd
import sys

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT REQUIRED WIDGET CLASSES FROM QTWIDGETS MODULE─────────────────────────────────────────────────────────────
"""
1. QWidget: The empty container widget class. Being called for widget class function inheritance.
2. QVBoxLayout: The layout widget class that allows placement of other widgets vertically
3. QGridLayout: The layout widget class that allows placmeent of other widgets in defined grid size.
4. QComboBox: The dropdown widget class.
5. QPushButton: The button widget class.
6. QFrame: The framing widget class that group widgets in a box.
7. QLineEdit: The single line text input widget class.
8. QCheckBox: The checkbox widget class.
9. QLabel: The label widget class that creates label.
10. QFileDialog: The built-in file browser popup class that allow user to browse desired folders and files.
11. QSizePolicy: Tell how widget behave when windows resize.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,QGridLayout,QLabel,
    QComboBox,QPushButton,QFileDialog,QFrame,QSizePolicy,
    QLineEdit,QCheckBox)

"""
1. QtCore: A module that contains a classes for backend operation such as timer, signals, etc.
2. Qt: A collection of named options for everything in PyQt6. 

**For example: 
1. Without Qt, you use label.setAlignment(4), we don't know what 4 means.
2. With Qt, you write it as label.setAlignment(Qt.AlignmentFlag.AlignCenter) --> now you can read it.
"""
from PyQt6.QtCore import Qt

"""
1. QIntValidator: A validator class that only allows user to create object of integer type.
2. QDoubleValidator: A validator class that only allows user to create object of double type.
"""
from PyQt6.QtGui import (QIntValidator,QDoubleValidator)

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT CUSTOM CLASSES FROM OTHER FILES FOR CONNECTION────────────────────────────────────────────────────────────
from ui import solute_density
from ui import solvent_density
from ui.solute_density import soluteDensityTab
from ui.solvent_density import solventDensityTab

#─────HELPER FUNCTION #1───────────────────────────────────────────────────────────────────────────────────────────────
# "This helper function traces the flux & rejection data folder from the directory."
def flux_folder() -> str:
    
   
    # 'sys.frozen' is an attribute when this app is run from a single executable file.
    if getattr(sys,"frozen",False):  

        # "If the app is run from executable file, return the directory contaning this file."
        app_root = os.path.dirname(sys.executable)
    else:

        # "If the app is run from python script, return the directory containing this file in the project folder"
        app_root = os.path.dirname(os.path.abspath(__file__))

        """
        1. 'os.path.basename() returns the last component of a path
        
        2. If the last component is named 'ui', the directory will go up 1 level. Which is 'SepCal' in this case
        """
        if os.path.basename(app_root).lower() == "ui":
            app_root = os.path.dirname(app_root)

    # "Returns the directory for folder that stores the flux & rejection data files"        
    return os.path.join(app_root,"membrane data")   #DO NOT CHANGE THIS OR THE FOLDER NAME!    

#─────HELPER FUNCTION #2───────────────────────────────────────────────────────────────────────────────────────────────
"""
This helper function traces the module size data folder from the directory.
"""
def module_spec_folder() -> str:\

    # "Code structure similar to HELPER FUNCTION #1"
    if getattr(sys,"frozen",False):  
        app_root = os.path.dirname(sys.executable)
    else:
        app_root = os.path.dirname(os.path.abspath(__file__))

        if os.path.basename(app_root).lower() == "ui":   #Go up one level if the file is inside a 'ui/' subfolder
            app_root = os.path.dirname(app_root)
    return os.path.join(app_root,"module size")
        
#─────CREATE A MAPPING FOR KEYWORDS TO TRACE COLUMNS FROM FLUX & REJECTION DATA FILE───────────────────────────────────
KEYWORDS =  {
    "concentration":["solute concentration"],
    "pressure": ["pressure","bar"],
    "flux":["flux","lmh"],
    "rejection":["average rejection"],
}

#─────HELPER FUNCTION #3───────────────────────────────────────────────────────────────────────────────────────────────
"This helper function extract required columns from a data frame and return a column map in form of dict."
def detect_columns(df: pd.DataFrame) -> dict[str,str]:

    # "First, create an empty dictionary named 'mapping' to store data later on"
    mapping = {}

    # "Loop all the key and value pairs in the KEYWORDS mapping"
    for key,value in KEYWORDS.items():
       
    #    "For each column in the data frame, convert the naming to lowercase"
       for col in df.columns:
           col_lower = str(col).lower()
           
           """
           1. any() method returns true if at least one value in a collection pair is true.

           2. This loops through every keywords in the mapping value to see if it matches the column name.

           3. If there is match, place the key & value pair to the empty dictionary created.

           4. Stop the check and go for another key & value pair once a match is found by adding a break at the end.
           """
           if any(kw in col_lower for kw in value):
               mapping[key] = col
               break

    # "If the a specific key in the KEYWORD mapping could not be found in the data frame columns, raise error messages."       
    if key not in mapping:
            raise ValueError(
                f"Could not detect '{key}' column in file.\n"
                f"Available columns:{list(df.columns)}"
                )
    
    # "After all the looping, returns the final dictionary of all columns detected from the data frame"
    return mapping

#─────HELPER FUNCTION #4───────────────────────────────────────────────────────────────────────────────────────────────
"This helper function load the flux & rejection data file based on the path traced by HELPER FUNCTION #1"
def load_flux_data(filepath:str) -> dict:

    """
    1. First, read the excel file according to the traced filepath, specifically at a fixed sheet name and start from 
    row 6 of the sheet. Store the data to a defined object named 'df_raw".

    2. pd.read_excel is a pandas function to retrieve data from excel file at specific sheet and row
    """
    df_raw = pd.read_excel(filepath, sheet_name = "flux_rejection", header = 0) #DO NOT CHANGE THE FILE STRUCTURE

    # "The '.dropna' method removes the missing values from a row"
    df_raw.dropna(how = "all", inplace = True)

    # "After dropping missing values, reset the index of each row"
    df_raw.reset_index(drop = True, inplace = True)

    # "Slice the column of the data frame where only the columns that contain specific wordings are retained"
    df_raw = df_raw.loc[:,df_raw.columns.str.contains("Solute|bar|LMH|Rejection", case=False)]

    # "From the above data frame, use HELPER FUNCTION #3 to create a column map"
    col_map = detect_columns(df_raw)

    """
    1. Create a final data frame based on a defined dictionary

    2. For the values of each key, extract the rows where the column matches the mapping keyword

    3. pd.to_numeric() converts a value to number, "coerce" will return NaN if a value cannot be converted to number.
    """
    df = pd.DataFrame({
        "concentration": pd.to_numeric(df_raw[col_map["concentration"]],errors = "coerce"),
        "pressure":pd.to_numeric(df_raw[col_map["pressure"]],errors = "coerce"),
        "flux":pd.to_numeric(df_raw[col_map["flux"]],errors = "coerce"),
        "rejection":pd.to_numeric(df_raw[col_map["rejection"]],errors = "coerce"),
    })

    # "Perform final cleaning of the final data frame by dropping missing values followed by index reset"
    df.dropna(inplace=True)
    df.reset_index(drop = True,inplace = True)

    return df

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 2.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
Create a class named UserInputTab as our 1st tab in main window. This class inherit all functions from the 
parent class QWidget. This class serves as a blueprint to construct the UIs that allows users to key in necessary
inputs to initialise the calculations and iterations of a batch membrane separation process.
"""
class UserInputTab(QWidget):
    #─────2.1: INITIALISE THE CLASS WITH PRE-DEFINED OBJECTS───────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()

        # "Create empty objects in different types for data storage later on"
        self.flux_folder: str = ""
        self.flux_data: pd.DataFrame = None
 
        # "Create objects for solute and solvent tab instance so we can access their respective methods here"
        self.solute_tab = soluteDensityTab()
        self.solvent_tab = solventDensityTab()
 
        # "When the app is initialised, locate where the flux & rejection data is stored."
        default = flux_folder()

        # "If the directory exist, store the path in the form of string to the object created earlier on."
        if os.path.isdir(default):
            self.flux_folder = default

        # "UI construction using HELPER METHOD #0"
        self.build_ui()

        # "Once the data file is stored, display the name of all the files in the drop down list using HELPER METHOD #2"
        if self.flux_folder:
            self.refresh_flux_files()
 
    #─────2.2: HELPER METHOD #0────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method constructs the UI and define how all the widgets are shown on the tab.
    """
    def build_ui(self):

        """
        1. Create a vertical box layout using QBoxLayout()
        2. All user input widgets are placed row by row using QVBoxLayout(parent widget)
        3. ".setContentsmArgins(left,top,right,bottom) defines the margin of a widget
        4. ".setSpacing() set a spacing distance between widgets in a layout
        """    
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 12, 24, 12)
        root.setSpacing(10)
 
        """
        ROW 1: TITLE
        1. Place a title named "User Input" at the top of the, and place it on the 1st row of the vertical layout
        2. ".setObjectName" is to create a unique ID as reference to the stylesheet for widget styling
        """
        title = QLabel("User Input")
        title.setObjectName("title")
        root.addWidget(title)     
 
        """
        ROW 2: DIVIDER
        1. PyQt6 has no built-in divider widget, QFrame is used for line drawing.
        2. ".setFrameShape" is a QFrame method where QFrame.Shape.HLine is to draw a horizontal line, whereas 
        QFrame.Shadow.Plain is to draw the line flat [Sunken = Recessed, Raise = does the opposite of sunken]
        """
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        root.addWidget(divider)
 
        """
        From row 3 onward, widgets are placed in a grid using the QGridLayout widget where each grid has a vertical and
        horizontal spacing of 10px. The purpose of using grid layout is to arrange all user input blocks in organised
        manner.
        """
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
 
        # Column structure:
        # 0=label | 1=input | 2=unit | 3=label | 4=input | 5=unit | 6=label | 7=input | 8=unit
        grid.setColumnMinimumWidth(0, 180)
        grid.setColumnMinimumWidth(2, 50)
        grid.setColumnMinimumWidth(3, 180)
        grid.setColumnMinimumWidth(5, 50)
        grid.setColumnMinimumWidth(6, 180)
        grid.setColumnMinimumWidth(8, 50)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(7, 1)
 
        root.addLayout(grid)
 
        # Add desired rows in sequence
        self.add_flux_data_row(grid, row=0)
        self.add_medium_row(grid, row=2)
        self.add_operation_mode_row(grid, row=3)
        self.add_operating_parameters_row(grid, row=4)
        self.add_flowrate_row(grid, row=5)
        self.add_target_conc_row(grid, row=6)
        self.add_module_number_row(grid, row=7)
        self._2p_add_module_number_row(grid, row=8)
        self.add_recycle_radio_button_row(grid, row=9)
        self.add_basis_row(grid, row=10)
 
        # Push everything to the top
        root.addStretch()
 
    #─────2.3: HELPER METHOD #1────────────────────────────────────────────────────────────────────────────────────────
    """
    1. This helper method allows the creation of label using the QLabel widget
    2. The label create has a horizontal and vertical alignment of right and center respectively.
    3. '.setWordWrap' is to allow the label to wrap into multiple rows in case the text is too long.
    """
    def make_label(self, text: str, wrap: bool = False) -> QLabel:
        lb = QLabel(text)
        lb.setObjectName("inputLabel")
        lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lb.setWordWrap(wrap) 
        return lb
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.4 ROW 1:FLUX & REJECTION DATA DROP DOWN LIST───────────────────────────────────────────────────────────────
    """
    This method creates the first user input row to allow user to select a specific flux & rejection data file from 
    a drop down list.
    """
    def add_flux_data_row(self, grid: QGridLayout, row: int):
        
        # "Add a label to the grid using the pre-defined helper method #1."
        grid.addWidget(self.make_label("Flux Data:"), row, 0)

        # "Create 2 empty data frame to store the extracted flux and rejection data later on"
        self.flux_df = pd.DataFrame()
        self.rej_df = pd.DataFrame()
 
        """
        1. Create a drop down widget to allow user to select desired flux file.
        2. '.setPlaceholderText' is used to display the initial text of the unselected drop down list.
        3. '.setSizePolicy' such that the drop down widget will expand horizontally while remain fixed vertically.
        """
        self.flux_combo = QComboBox()
        self.flux_combo.setObjectName("inputCombo")
        self.flux_combo.setPlaceholderText("-select a flux & rejection data file-")
        self.flux_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # "Connect this drop down widget to a helper method when being activated."
        self.flux_combo.activated.connect(self.on_flux_file_selected)

        # "Place the widget on the grid, specifically, on 2nd column, row span of 1 and column span of 7"
        grid.addWidget(self.flux_combo, row, 1, 1, 7)
 
        # "Create a browse button widget to allow user to input their own flux data file (with the same format)"
        browse_button = QPushButton("Browse...")
        browse_button.setObjectName("primaryBtn")
        browse_button.setFixedWidth(90)

        # "Connect this browse button widget to a helper method"
        browse_button.clicked.connect(self.browse_flux_folder)

        # "Place the button widget on the grid, specifically on the last column"
        grid.addWidget(browse_button, row, 8)
 
        """
        1. Create an empty status bar in form of QLabel widget at the row below the flux drop down widget. 
        
        2. This status bar serves the purpose to display loading status so user could know if data is successfully 
        loaded after selecting a flux & rejection data from the drop down. 
        """
        self.flux_status = QLabel("")
        self.flux_status.setObjectName("statusLabel")
        grid.addWidget(self.flux_status, row + 1, 1, 1, 8)

    #─────2.4.1 HELPER METHOD #2───────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method extract names of flux & rejection data files and insert them to the drop down list
    """
    def refresh_flux_files(self):

        # "If data folder is not detected, prevent the whole to crash"
        if not self.flux_folder or not os.path.isdir(self.flux_folder):
            return
        
        """
        1. Create an object named 'xlsx_files'

        2. Loop through each file in the data folder. 'os.listdir()' returns a list of each all files and folder in the
        folder directory. If the file ends with ".xlsx", place it in the object and finally sort the objects in 
        alphabetical order.
        """
        xlsx_files = sorted(
            f for f in os.listdir(self.flux_folder)
            if f.lower().endswith(".xlsx")
        )

        # "Clear the drop down list and re-add the item from the object list"
        self.flux_combo.clear()
        self.flux_combo.addItems(xlsx_files)

    #─────2.4.2 HELPER METHOD #3───────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method extract the flux and rejection data when a single data file is selected from the drop down list.
    """
    def on_flux_file_selected(self, filename: str):
        
        # "Store the current text being displayed on the drop down widget to an object named 'filename'"
        filename = self.flux_combo.currentText()

        # "If no data file is selected OR detected, stop the app from crashing"
        if not filename or not self.flux_folder:
            return

        # "Else, create the directory for the selected data file"
        filepath = os.path.join(self.flux_folder, filename)
        
        try:
            # "Load the flux and rejection data from the created filepath and store it to an data frame object"
            self.flux_data = load_flux_data(filepath)

            # "Slice the data frame that only the specific 4 columns are required and store it into another df object"
            df = self.flux_data[["concentration", "pressure", "flux", "rejection"]]

            # "Define the style of the status label to display when the data is loaded"
            self.flux_status.setStyleSheet("color: #db0404; font-size: 11px;")
            
            # "Define how the message will be displayed if data is successfully loaded."
            self.flux_status.setText(
                f"Loaded {len(df)} rows  |  "
                f"Conc: {df['concentration'].min()}-{df['concentration'].max()} wt%  |  "
                f"Pressure: {df['pressure'].min()}-{df['pressure'].max()} bar  |  "
                f"Flux: {df['flux'].min():.2f}-{df['flux'].max():.2f} LMH"
            )

            # "Since the data file contains both flux and rejection data, separate 2 data values into different df"
            self.flux_df = df.iloc[:, [0, 1, 2]]
            self.rej_df = df.iloc[:, [0, 1, 3]]

            """
            1. If anything goes wrong, reset the data file to nothing since loading failed and display on status label.
            
            2. 'Exception' is all type of error message in the except clause if the above try clause failed.
            """
        except Exception as exc:    
            self.flux_data = None
            self.flux_status.setStyleSheet("color: #db0404; font-size: 11px;")
            self.flux_status.setText(f"{exc}")
    
    #─────2.4.3 HELPER METHOD #4───────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method opens the browser dialog that allows user to select their own flux & rejection data file with
    the same structure in local project directory.
    """
    def browse_flux_folder(self):

        """
        1. The 'QFileDialog.getExistingDirectory()' opens a native OS folder picker window.

        2. If data folder exists, open from there, or else, open user's home directory.

        3. 'os.path.expanduser("~")' returns the full path of user's home directory. 
        """
        folder = QFileDialog.getExistingDirectory(
            self, "Select Flux Data Folder", self.flux_folder or os.path.expanduser("~")
        )

        #"If a folder is selected, replace the data folder with the selected folder, and then update the drop down list"
        if folder:
            self.flux_folder = folder
            self.refresh_flux_files()
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.5 ROW 2: SOLUTE AND SOLVENT TYPE DROP DOWN LIST ───────────────────────────────────────────────────────────
    """
    This method creates drop downs that allow user to choose the type of solute and solvent and load 
    their respective density values to be used in the calculation.
    """
    def add_medium_row(self, grid: QGridLayout, row: int):
        
        # "Add label widget for solute drop down, placed at 1st row"
        grid.addWidget(self.make_label("Solute:"), row, 0)

        # "Create a drop down widget to allow user to choose the type of solute"
        self.solute_input = QComboBox()
        self.solute_input.setObjectName("inputLine")
        self.solute_input.setPlaceholderText("-select a solute-")
        self.solute_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # "Generate the path to locate the density file for all types of solute"
        self.solute_path = os.path.join(solute_density.solute_density_folder(), "solute.xlsx")

        """
        1. From the generated path, extract all the sheet names from the excel file. Each sheet means a solute type. 
        
        2. 'pd.read_excel()' returns data frame by default, but returns dict when sheet_name is set to 'None'.
        """
        self.solute_type = list(pd.read_excel(self.solute_path, sheet_name=None).keys())

        # "Insert all the extracted solute names into the drop down widget."
        self.solute_input.addItems(self.solute_type)

        # "Connect the drop down list to HELPER METHOD 2.5.1"
        self.solute_input.currentTextChanged.connect(self.on_solute_changed)

        # "Add the drop down widget to the grid."
        grid.addWidget(self.solute_input, row, 1)

        # "Add label widget for solvent drop down, placed at 4th row."
        grid.addWidget(self.make_label("Solvent:"), row, 3)

        # "Create a drop down widget to allow user to choose the type of solvent"
        self.solvent_input = QComboBox()
        self.solvent_input.setObjectName("inputLine")
        self.solvent_input.setPlaceholderText("-select a solvent-")
        self.solvent_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # "Generate the path to locate the density file for all types of solvent"
        self.solvent_path = os.path.join(solvent_density.solvent_density_folder(), "solvent.xlsx")

        # "Similar to solute, create a list for all the sheet names from solvent excel file and place into the drop down"
        self.solvent_type = list(pd.read_excel(self.solvent_path, sheet_name=None).keys())
        self.solvent_input.addItems(self.solvent_type)

        # "Connect the drop down list to HELPER METHOD 2.5.2 when text on the drop down is changed"
        self.solvent_input.currentTextChanged.connect(self.on_solvent_changed)

        # "Create 2 empty data frame objects for later use"
        self.solute_df = pd.DataFrame()
        self.solvent_df = pd.DataFrame()

        # "Add the drop down widget to the grid."
        grid.addWidget(self.solvent_input, row, 4)
 
    #─────2.5.1 HELPER METHOD #5───────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method display the table on the solute density preview tab when the solute drop down changes.
    """
    def on_solute_changed(self, solute_name: str):
        
        # "If a solute is selected on the drop down, extract the table from a specific sheet based on what's selected"
        if solute_name:
            df = pd.read_excel(self.solute_path, sheet_name=solute_name)
            self.solute_df = df    #Store the data frame into a the empty data frame object defined previously
            self.solute_tab.populate_solute_table(df)    #Linked to 'populate_solute_table()' method on other tab.
 
    #─────2.5.2 HELPER METHOD #6───────────────────────────────────────────────────────────────────────────────────────
    """
    Refer to HELPER METHOD #5 for description.
    """
    def on_solvent_changed(self, solvent_name: str):
        if solvent_name:
            df = pd.read_excel(self.solvent_path, sheet_name=solvent_name)
            self.solvent_df = df
            self.solvent_tab.populate_solvent_table(df)
    
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.6 ROW 3: OPERATION MODE DROP DOWN LIST─────────────────────────────────────────────────────────────────────
    """
    This method creates a drop down that allows user to choose between batch or continuous operation mode for the 
    calculation.
    """
    def add_operation_mode_row(self, grid: QGridLayout, row: int):
        
        # "Add label widget for the drop down"
        grid.addWidget(self.make_label("Operation Mode:",wrap=True), row, 0)
 
        # "Create the drop down to allow user to choose between 'batch' and 'continuous'"
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("inputCombo")
        self.mode_combo.setPlaceholderText("— select an operation mode —")
        self.mode_combo.addItems(["Batch", "Continuous"])
        self.mode_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # "Create an empty object to store the text selected on the drop down"
        self.mode_text = ""

        # "Connect the drop down to HELPER METHOD #7 when the text on the drop down has changed"
        self.mode_combo.currentTextChanged.connect(self.on_mode_selected)

        # "Add the drop down widget into the grid"
        grid.addWidget(self.mode_combo, row, 1, 1, 7)

    #─────2.6.1 HELPER METHOD #7───────────────────────────────────────────────────────────────────────────────────────    
    """
    This helper method will assign the current text on the drop down when a operation mode is selected. 
    """
    def on_mode_selected(self, ope_mode: str):
        if ope_mode:
            self.mode_text = self.mode_combo.currentText()
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.7 ROW 4: OPERATING PARAMETERS TEXT INPUT───────────────────────────────────────────────────────────────────
    """
    This method creates the text box for user to input operating temperature and pressure values
    """
    def add_operating_parameters_row(self, grid: QGridLayout, row: int):
        
        # "Add label widget for operating pressure text box at first column"
        grid.addWidget(self.make_label("Operating Pressure:",wrap=True), row, 0)
 
        # "Create the text box widget for user to key in operating pressure value, and also the label for pressure unit"
        self.pressure_input = QLineEdit()
        self.pressure_input.setObjectName("inputLine")
        self.pressure_input.setPlaceholderText("e.g. 13")
        self.pressure_label = QLabel("bar")
        self.pressure_label.setObjectName("inputLabel")

        # "Add both the labels and text box widgets to the grid at planned columns"
        grid.addWidget(self.pressure_input, row, 1)
        grid.addWidget(self.pressure_label,row,2)
 
        # "Add label widget for operating temperature text box at 4th column"
        self.temp_label = QLabel("Operating Temperature:")
        self.temp_label.setWordWrap(True)
        self.temp_label.setObjectName("inputLabel")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # "Add the label widget into the grid at planned column"
        grid.addWidget(self.temp_label, row, 3)
 
        # "Create the text box widget for user to key in operating temperature value, and also the label for unit"
        self.temp_input = QLineEdit()
        self.temp_input.setObjectName("inputLine")
        self.temp_input.setPlaceholderText("e.g. 45")
        self.temp_unit = QLabel("°C")
        self.temp_unit.setObjectName("inputLabel")

        # "Add both the labels and text box widgets to the grid at planned columns"
        grid.addWidget(self.temp_input, row, 4)
        grid.addWidget(self.temp_unit, row, 5)

        """
        1. Set up double validator where the smallest and biggest value user can input are 0.0 and 999999.0 
        respecively, up to 8 decimal points.

        2. '.setNotation() is a method to restrict user to input to key in number based on a fixed notation'

        3. Only standard notation is allowed in this case
        """
        self.validator = QDoubleValidator(0.0, 999999.0, 8)
        self.validator.setNotation(QDoubleValidator.Notation.StandardNotation)

        # "Set validator to the both operating pressure and temperature text input"
        self.temp_input.setValidator(self.validator)
        self.pressure_input.setValidator(self.validator)
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.8 ROW 5: FLOW RATE INPUT───────────────────────────────────────────────────────────────────────────────────
    """
    This method creates text input widget to allow user to key in the solute and solvent mass flow in kg/hr for the 
    calculation.
    """
    def add_flowrate_row(self, grid: QGridLayout, row: int):
        
        # "Create label widget for solute flow text box widget"
        grid.addWidget(self.make_label("Solute Flow:"), row, 0)

        # "Create text box widget and place into the grid for solute flow text box"
        self.solute_flow_input = QLineEdit()
        self.solute_flow_input.setObjectName("inputLine")
        grid.addWidget(self.solute_flow_input, row, 1)
 
        # "Create label widget and place into the grid for solute flow unit"
        self.solute_unit_label = QLabel("kg/hr")
        self.solute_unit_label.setObjectName("inputLabel")
        grid.addWidget(self.solute_unit_label, row, 2)
 
        # "Create label widget and place into the grid for solvent flow label"
        self.solvent_flow_label = QLabel("Solvent Flow:")
        self.solvent_flow_label.setObjectName("inputLabel")
        self.solvent_flow_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.solvent_flow_label, row, 3)
 
        # "Create text box widget and place into the grid for solvent flow text box"
        self.solvent_flow_input = QLineEdit()
        self.solvent_flow_input.setObjectName("inputLine")
        grid.addWidget(self.solvent_flow_input, row, 4)
 
        # "Create label widget and place into the grid for solvent flow unit"
        self.solvent_unit_label = QLabel("kg/hr")
        self.solvent_unit_label.setObjectName("inputLabel")
        grid.addWidget(self.solvent_unit_label, row, 5)
 
        # "Create label widget and place into the grid for feed solute concentration"
        self.feed_conc_label = QLabel("Feed Solute Conccentration:")
        self.feed_conc_label.setObjectName("inputLabel")
        self.feed_conc_label.setWordWrap(True)
        self.feed_conc_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.feed_conc_label, row, 6)
 
        """
        Create a 'read only' text box widget that computes automatically when both solute and solvent flow rates are
        keyed in.
        """
        self.feed_conc_readonly = QLineEdit()
        self.feed_conc_readonly.setObjectName("inputLine")
        self.feed_conc_readonly.setReadOnly(True)

        # "Connect both solute and solvent text box widget to HELPER METHOD #8 when the input texts are changed"
        self.solute_flow_input.textChanged.connect(self.calculate_feed_conc)
        self.solvent_flow_input.textChanged.connect(self.calculate_feed_conc)
        grid.addWidget(self.feed_conc_readonly, row, 7)

        # "Create label widget and place into the grid for feed solute concentration unit (wt%)"
        self.feed_conc_unit = QLabel("wt%")
        self.feed_conc_unit.setObjectName("inputLabel")
        grid.addWidget(self.feed_conc_unit, row, 8)

        # "Set validator to the both flowrates text input using the double validator set at ROW 4 (LINE 631)"
        self.solvent_flow_input.setValidator(self.validator)
        self.solute_flow_input.setValidator(self.validator)
 
    #─────2.8.1: HELPER METHOD #8──────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method automatically calculates the feed solute concentration when a text change signal is received
    on either the solute or solvent mass flow rate text box widget.
    """
    def calculate_feed_conc(self):
        
        """
        1. Store both the solute and solvent mass flow rate values into 2 separated objects

        2. Calculate the feed solute concentration and use .setText() method to display on the feed conc. text box

        3. If value is errornous or cannot be display, clear the text box to notify user something's wrong.
        """
        try:
            value_1 = float(self.solute_flow_input.text())
            value_2 = float(self.solvent_flow_input.text())
            result = value_1 / (value_1 + value_2) * 100
            self.feed_conc_readonly.setText(f"{result:.2f}")
        except ValueError:
            self.feed_conc_readonly.clear()
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.9 ROW 6: TARGET RETENTATE CONCENTRAQTIONS TEXT INPUT───────────────────────────────────────────────────────
    """
    This method creates text input widget to allow user to key in the target 1st pass and 2nd pass retentate
    concentration for the feed concentration to concentrate to.
    """
    def add_target_conc_row(self, grid: QGridLayout, row: int):
        
        # "Create label widget for 1st pass target retentate concentration"
        grid.addWidget(self.make_label("Target 1<sup>st</sup> Pass\nRetentate Conc.:",wrap=True), row, 0)
 
        # "Create text box widget for 1st pass target retentate concentration and add it into the grid"
        self._1p_ret_input = QLineEdit()
        self._1p_ret_input.setObjectName("inputLine")
        self._1p_ret_input.setPlaceholderText("e.g. 40")
        grid.addWidget(self._1p_ret_input, row, 1)
 
        # "Create label widget for 1st pass target retentate concentration unit and add it into the grid"
        self._1p_conc_unit = QLabel("wt%")
        self._1p_conc_unit.setObjectName("inputLabel")
        grid.addWidget(self._1p_conc_unit, row, 2)
 
        # "Create label and text box widgets for 2nd pass target retentate concentration and add them into the grid"
        self._2p_ret_label = QLabel("Target 2<sup>nd</sup> Pass\nRetentate Conc.:")
        self._2p_ret_label.setWordWrap(True)
        self._2p_ret_label.setObjectName("inputLabel")
        self._2p_ret_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self._2p_ret_label, row, 3)
 
        self._2p_ret_input = QLineEdit()
        self._2p_ret_input.setObjectName("inputLine")
        self._2p_ret_input.setPlaceholderText("e.g. 10")
        grid.addWidget(self._2p_ret_input, row, 4)
 
        self._2p_conc_unit = QLabel("wt%")
        self._2p_conc_unit.setObjectName("inputLabel")
        grid.addWidget(self._2p_conc_unit, row, 5)
 
        # "Set validator to the both target concentration text inputs using the double validator set at ROW 4 (LINE 631)"
        self._1p_ret_input.setValidator(self.validator)
        self._2p_ret_input.setValidator(self.validator)

    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.10 ROW 7: 1ST PASS MODULE NUMBER, LINEAR VELOCITY TEXT INPUT & MODULE SIZE DROP DOWN───────────────────────
    """
    This method creates text box widget and drop down widget to that allows user to key in number of module and linear
    velocity, and also to choose desired module size for 1ST PASS iteration
    """
    def add_module_number_row(self, grid: QGridLayout, row: int):
        
        # "Create label widget for 1st pass number of module"
        grid.addWidget(self.make_label("1<sup>st</sup> Pass Module/Row:",wrap=True), row, 0)
 
        # "Create text box widget for 1st pass number of module and add it into the grid."
        self.module_no = QLineEdit()
        self.module_no.setValidator(QIntValidator())   #Setup validator where module number can only be integers
        self.module_no.setObjectName("inputLine")
        grid.addWidget(self.module_no, row, 1)
 
        # "Create label and text box widgets for 1st pass linear velocity and add them into the grid"
        self.linear_velocity_label = QLabel("1<sup>st</sup> Pass Linear Velocity:")
        self.linear_velocity_label.setObjectName("inputLabel")
        self.linear_velocity_label.setWordWrap(True)
        self.linear_velocity_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.linear_velocity_label, row, 3)
 
        self.linear_velocity = QLineEdit()
        self.linear_velocity.setValidator(QDoubleValidator(0.000001, 2.0, 6))
        self.linear_velocity.setObjectName("inputLine")
        grid.addWidget(self.linear_velocity, row, 4)
 
        self.linear_velocity_unit = QLabel("ms<sup>-1</sup>")
        self.linear_velocity_unit.setObjectName("inputLabel")
        grid.addWidget(self.linear_velocity_unit, row, 5)

        # "Create label and drop down widgets for 1st pass module size and add them into the grid"
        self.module_spec_label = QLabel("1<sup>st</sup> Pass Module Size:")
        self.module_spec_label.setObjectName("inputLabel")
        self.module_spec_label.setWordWrap(True)
        self.module_spec_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self.module_spec_label, row, 6)
 
        self.module_spec = QComboBox()
        self.module_spec.setObjectName("inputCombo")
        self.module_spec.setPlaceholderText("-select size")
        self.module_spec.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.module_spec.setFixedWidth(100)

        """
        Generate the directory to the folder that contains the data for each module size with the help of 
        HELPER FUNCTION #2. Then, generate the file path for the module size file.
        """
        self.module_folder = module_spec_folder()
        self.module_file = os.path.join(self.module_folder, "module_size.xlsx")

        # "Extract the 1st sheet from the excel file that contains the data for module size"
        self.df_raw = pd.read_excel(self.module_file, sheet_name=0)

        # "Slice the data frame such that the 2nd column (unit column) is dropped, retaining the other columns"
        self.df_clean = self.df_raw.iloc[:,:]
        self.df_clean = self.df_clean.drop(columns=self.df_clean.columns[1])
        self.df_column = self.df_clean.columns[1:].to_list()

        # "Add the column name as an item to the drop down list"
        self.module_spec.addItems(self.df_column)

        # "Add the drop down widget into the grid"
        grid.addWidget(self.module_spec, row, 7, 1, 2)

    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.11 ROW 8: 2ND PASS MODULE NUMBER, LINEAR VELOCITY TEXT INPUT & MODULE SIZE DROP DOWN───────────────────────
    """
     Generate the directory to the folder that contains the data for each module size with the help of 
     HELPER FUNCTION #2. Then, generate the file path for the module size file.
    """
    def _2p_add_module_number_row(self, grid: QGridLayout, row: int):
        
        # "All the code structure is similar to section 2.10, kindly refer to that section for annotations"
        grid.addWidget(self.make_label("2<sup>nd</sup> Pass Module/Row:",wrap=True), row, 0)
 
        self._2p_module_no = QLineEdit()
        self._2p_module_no.setValidator(QIntValidator())
        self._2p_module_no.setObjectName("inputLine")
        grid.addWidget(self._2p_module_no, row, 1)
 
        self._2p_linear_velocity_label = QLabel("2<sup>nd</sup> Pass Linear Velocity:")
        self._2p_linear_velocity_label.setObjectName("inputLabel")
        self._2p_linear_velocity_label.setWordWrap(True)
        self._2p_linear_velocity_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self._2p_linear_velocity_label, row, 3)
 
        self._2p_linear_velocity = QLineEdit()
        self._2p_linear_velocity.setValidator(QDoubleValidator(0.000001, 2.0, 6))
        self._2p_linear_velocity.setObjectName("inputLine")
        grid.addWidget(self._2p_linear_velocity, row, 4)
 
        self._2p_linear_velocity_unit = QLabel("ms<sup>-1</sup>")
        self._2p_linear_velocity_unit.setObjectName("inputLabel")
        grid.addWidget(self._2p_linear_velocity_unit, row, 5)
 
        self._2p_module_spec_label = QLabel("2<sup>nd</sup> Pass Module Size:")
        self._2p_module_spec_label.setObjectName("inputLabel")
        self._2p_module_spec_label.setWordWrap(True)
        self._2p_module_spec_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self._2p_module_spec_label, row, 6)
 
        self._2p_module_spec = QComboBox()
        self._2p_module_spec.setObjectName("inputCombo")
        self._2p_module_spec.setPlaceholderText("-select size")
        self._2p_module_spec.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._2p_module_spec.setFixedWidth(100)

        self._2p_module_folder = module_spec_folder()
        self._2p_module_file = os.path.join(self.module_folder, "module_size.xlsx")

        self._2p_df_raw = pd.read_excel(self.module_file, sheet_name=0)
        self._2p_df_clean = self.df_raw.iloc[:,:]
        self._2p_df_clean = self._2p_df_clean.drop(columns = self._2p_df_clean.columns[1])
        self._2p_df_column = self.df_clean.columns[1:].to_list()

        self._2p_module_spec.addItems(self.df_column)

        grid.addWidget(self._2p_module_spec, row, 7, 1, 2)

    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.12 ROW 9: 2ND PASS RECYCLE CONFIGURATION CHECKBOX──────────────────────────────────────────────────────────
    """
    This method allows user to choose whether to iterate both 1st and 2nd pass or solely 1st pass where if checked, 
    2nd pass retentate will be recycled back to 1st pass feed stream.
    """
    def add_recycle_radio_button_row(self, grid: QGridLayout, row: int):
        
        # "Create label widget for the checkbox widget"
        grid.addWidget(self.make_label("Recycle from 2<sup>nd</sup> Pass:",wrap=True), row, 0)

        # "Create checkbox widget to allow user to choose whether to recycle 2nd pass back to 1st pass calculation"
        self.recycle_button = QCheckBox()
        self.recycle_button.setObjectName("inputToggle")
        self.recycle_button.setChecked(True)
        grid.addWidget(self.recycle_button, row, 1)
 
    #▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    #─────2.13 ROW 10: 1ST AND 2ND PASS TANK MASS BASIS TEXT BOX───────────────────────────────────────────────────────
    """
    This method allows user to key in the 1st and 2nd pass tank mass basis to perform the iteration. Tank mass basis
    is needed to back calculate processing time and also many other resulting parameters.
    """
    def add_basis_row(self, grid: QGridLayout, row: int):
        
        # "Create label widget for the 1st pass basis text box widget"
        grid.addWidget(self.make_label("1<sup>st</sup> Pass Basis:"), row, 0)
 
        # "Create text box and label widgets for the 1st pass basis text box and place it into the grid"
        self._1p_basis_input = QLineEdit()
        self._1p_basis_input.setObjectName("inputLine")
        grid.addWidget(self._1p_basis_input, row, 1)
 
        self._1p_basis_unit = QLabel("kg")
        self._1p_basis_unit.setObjectName("inputLabel")
        grid.addWidget(self._1p_basis_unit, row, 2)
 
        # "Create text box and label widgets for the 2nd pass basis text box and place it into the grid"
        self._2p_basis_label = QLabel("2<sup>nd</sup> Pass Basis:")
        self._2p_basis_label.setObjectName("inputLabel")
        self._2p_basis_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(self._2p_basis_label, row, 3)
 
        self._2p_basis_input = QLineEdit()
        self._2p_basis_input.setObjectName("inputLine")
        grid.addWidget(self._2p_basis_input, row, 4)
 
        self._2p_basis_unit = QLabel("kg")
        self._2p_basis_unit.setObjectName("inputLabel")
        grid.addWidget(self._2p_basis_unit, row, 5)

        # "Set validator to the both basis text input using the double validator set at ROW 4 (LINE 631)"
        self._1p_basis_input.setValidator(self.validator)
        self._2p_basis_input.setValidator(self.validator)