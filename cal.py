"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This GUI app helps the user to perform iteration for batch separation process of 2 binary mixture 
                      up to a defined convergence.The "sepcal.py" file is the building block for app initialization,
                      main window construction and app exit handling.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVANT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
import sys   #──'sys' library provides access to Python runtime functions
import os    #──'os' library allows us to interact with operating system 

#─────IMPORT RELEVANT CLASSES FROM THE QtWidgets MODULES───────────────────────────────────────────────────────────────
"""
QtWidgets   : A module from PyQt6 package that contains all ready-made widget classes for UI construction
QApplication: Every PyQt6 app shall contain at least 1 of this class that allow the app to initialise
QMainWindow : A class that constructs the main window pops up when the app is initialised
QTabWidget  : A class that constructs the tabs that will be displayed on the main window
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget,QMessageBox,QLabel

#─────IMPORT RELEVANT CLASSES FROM THE QtGui MODULES───────────────────────────────────────────────────────────────────
"""
QtGui   : A module that contains all classes for graphics & low-level GUI construction such as painter, brush, pen, etc.
QIcon   : A class that construct and manage the display of any imported icons
"""
from PyQt6.QtGui import QIcon

#─────IMPORT OTHER CUSTOM CLASSES FROM OTHER FILES─────────────────────────────────────────────────────────────────────
from ui.user_input import UserInputTab
from ui.module_number_calculation import CalculationTab
from ui.solute_density import soluteDensityTab
from ui.solvent_density import solventDensityTab
from ui.result_tab import finalResultTab

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────DEFINE "STYLESHEET" TO STYLE ALL THE WIDGETS GLOBALLY BASED ON OBJECT NAME───────────────────────────────────────
"""
A style sheet usually has a standard format of:

QWidgets#objectname{
    xxx:xxx;
    xxx:xxx;
}

Note: [QWidget] can be any widgets and [objectname] is to for referencing 
"""
STYLESHEET = """
/*Block 1: Global defaults features*/
    QWidget{
        background-color: #f5f7f5;
        color: #1b3a28;
        font-family: "Segoe UI",sans-serif;
        font-size:13px;    
    }

    QMainWindow {
       background-color: #f5f7f5;
        }

        
/*Block 2: Tab bar features*/

    QTabWidget::pane {         /*'::pane' is a sub-element which is the content area inside the tab widget*/
        background-color: #FFFFFF;
        border: 1px solid #d1e8da;
        border-radius: 10px;
        padding: 12px;
        }

    
/*Block 3: Individual Tabs Features*/

    QTabBar::tab {            /*'QTabBar::tab' targets each individual tab button*/
        background-color: #e8f3ec;   
        color: #4a7c5e;
        padding: 8px 15px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-size: 12px;
        font-weight: 500;               /*Normal Weight:400, Bold weight:700*/
        margin-right:4px;
        }

    QTabBar::tab:selected {       /*':selected' is a state selector, only applies when this tab is the active one*/
        background-color: #1b6b3a;
        color: #ffffff;
        }

    QTabBar::tab:hover:!selected{   /*':hover:!selected' means mouse is hovered on it, but NOT the selected tab*/
        background-color:#d1e8da;
        color: #1b6b3a;
        }

    
/*Block 4: Group Box Features*/
    QGroupBox#groupBox{
        border: 1px solid #8F8C8C;
        border-radius: 8px;
        margin-top: 14px;
        padding: 16px 12px 12px 12px;
        font-weight: 500;
        color: #000000;
        }

    QGroupBox#groupBox::title {    /*groupbox is ID selector where only targets widgets where we explicitly set it as 'groupBox' in code*/
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #8F8C8C;
        }

/*Block 5: Input Fields*/
    QLineEdit{                          /*'QLineEdit' is the default appearance always*/
        background-color: #ffffff;
        border: 1.5px solid #d1e8da;
        border-radius: 7px;
        padding: 7px 12px;
        color: #1b3a28;
        font-size: 12px;
        selection-background-color: #2e925b;
        }

    QLineEdit:focus{                    /*With ':focus', the appearance when the user has clicked into it and is typing*/
        border: 1.5px solid #1b6b3a;
        }

    QLineEdit:disabled{                /*The appearance when we call .setEnabled(False) in python*/
        background-color: #f5f7f5;
        color: #6b7280;
        border-color: #e5e7eb;
        }

/*Block 6: Primary Button Features*/
    QPushButton#primaryBtn{
        background-color: #1b6b3a;

        /*qlineargradient() is a Qt specific function for gradients where:
        x1:0, y1:0, x2: 1, y2: 0 means gradient flows horizontally from left to right
        stop:0 #XXXXXX means starts at [color] on the left
        stop:1 #XXXXX means starts at [color] on the right*/

        color: #FFFFFF;
        font-weight: 500;
        font-size: 13px;
        padding: 8px 20px;
        border: none;
        border-radius: 7px;
        }

    QPushButton#primaryBtn:hover {
        background-color: #2e9e5b;
        }
        
    QPushButton#primaryBtn:pressed{
        background-color:#155230;
        }

    QPushButton:disabled {
        background-color: #d1e8da;
        color: #4a7c5e;
    }

/*Block 7: Combo Box Features (Dropdown)*/
    QComboBox {
        background: #dae1da;
        border: 1.5px solid #d1e8da;
        border-radius: 6px;
        padding: 5px 5px;
        color: #1b3a28;
        font-size: 10px;
        min-width: 80px;
        }

    QComboBox::drop-down {
        border: none;
        width: 24px;
        }

    QComboBox QAbstractItemView {
        background: #ffffff;
        border: 1px solid #d1e8da;
        border-radius: 7px;
        selection-background-color: #e8f3ec;
        padding: 4px;
        }


/*Block 8: All label features*/
    QLabel#inputLabel {
        background-color: transparent;
        color: #1b3a28;
        font-size: 13px;
        border: none;
        }

    QLabel#title {
        background-color: transparent;
        color: #1b3a28;
        font-size: 25px;
        border:none;

    }


/*Block 10: Divider*/
    QFrame#divider {
        background-color: #d1e8da;
        max-height: 1px;
        min-height: 1px;
        }


/* Block 13: Check Box */
QCheckBox#inputToggle::indicator {
    width: 18px;
    height: 18px;
}

/*Block 14: Table*/
    QTableWidget#table{
        background-color: #ffffff;
        border: 1px solid #d1e8da;
        border-radius: 10px;
        gridline-color: #e8f3ec;
        font-size: 12px;
        }

    QTableWidget#table::item{
        padding: 6px 12px;
        color: #1b3a28;
        border: none;
        }

    QTableWidget#table::item:selected{
        background-color: #e8f3ec;
        color: #1b6b3a;
        }

    QTableWidget#table::item:hover{
        background-color: #f5f7f5;
    }

    QTableWidget#table QHeaderView::section{
        background-color: #1b6b3a;
        border: none;
        border-right: 1px solid #2e9e5b;
        font-weight: 500;
        font-size: 12px;
        padding: 8px 12px;
        color: #FFFFFF;
        }

    QTableWidget#table QHeaderView::section:last{
        border-right:none;
    }

    QTableWidget#table QHeaderView::section:hover{
        background-color: #2e9e5b;
    }

    QLCDNumber#display{
        background-color: #1b3a28;
        color: #2e925b;
        border: none;
        border-radius: 8px;
        padding: 4px;
    }

    QMessageBox#popup {
        background-color: #FFFFFF;
    }

    QMessageBox#popup QLabel {
        color: #1b3a28;
        font-size: 13px;
    }

    QMessageBox#popup QPushButton {
        min-width: 80px;
        padding: 7px 16px;
    }
    
"""

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────FUNCTION 1.0─────────────────────────────────────────────────────────────────────────────────────────────────────
"""
Function Descriptions:
1. Check if the app is initialized through Python or through a standalone .exe file, and return the absolute path to a 
resource file

2. "sys._MEIPASS" is a attribute created when the app is opened through .exe file. It contains just a string of the 
temporary file path created when the app runs.

3. If "sys._MEIPASS" exist, it joins the temporary file path and user defined relative path.

4. If "sys._MEIPASS" is inexistent, it joins the absolute path of the current directory and user defined relative path.

5. "." means CURRENT DIRECTORY/FOLDER, ".." means ONE FOLDER UP

"""
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):  
        return sys._MEIPASS
    else:
        return os.path.join(os.path.abspath("."),relative_path)

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 1.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
1. A Class is a "blueprint" to create objects, so when a specific class is called else where, it will create objects 
based on how the objects are constructed in a defined class.

2. This class inherits from parent class (QMainWindow) so we can use all related class functions. The function of this 
class is to contruct the main window of the app.
"""
class MainWindow(QMainWindow):
    """
    1. When a class instance is created, __init__() is usually called to initialise the class.
    2. super() method is used to inherit all methods from parent class.
    """

    def __init__(self):                            #When this class is called, it creates an instance
        super().__init__()                         #super() is used to inherit all methods from QMainWindow

        #─────Construct UI for Main Window─────────────────────────────────────────────────────────────────────────────
        self.setWindowTitle ("Module Calculator")           #Define the window title name
        self.setMinimumSize(620,620)                               #The main window cannot be smaller than this size

        #─────Create Tab Container Object──────────────────────────────────────────────────────────────────────────────
        """
        QTabWidget() is a widget class that act as a container for tabs to be displayed on the main window. Without this
        class being called, no tabs can be shown on main window.
        """
        tabs = QTabWidget() 
        tabs.setDocumentMode(True)         #".setDocumentMode(True) display the tab page covering the tab widget frame"

        #─────Create object for each imported tab class ───────────────────────────────────────────────────────────────
        """
        1. All the imported classes are stored in the ui folder, and all of them are inheriting QWidget class

        2. Purpose of inheriting from QWidget class is to allow the objects to be added into the tab container as 
        valid widget.
        """
        user_input_tab = UserInputTab()
        solute_density_tab = soluteDensityTab()
        solvent_density_tab = solventDensityTab()
        result_tab = finalResultTab()
        calc_tab = CalculationTab(user_input_tab,solute_density_tab,solvent_density_tab,result_tab)
        
        #─────Add each tab into the container ─────────────────────────────────────────────────────────────────────────
        """
        1. ".addTab()" method is used to add the created tab objects into the tab container
        """
        tabs.addTab(user_input_tab, "User Input")
        tabs.addTab(calc_tab,"Module Number Calculator")
        tabs.addTab(result_tab,"Final Results")
        tabs.addTab(user_input_tab.solute_tab, "Solute Density Preview") 
        tabs.addTab(user_input_tab.solvent_tab,"Solvent Density Preview")
        
        self.setCentralWidget(tabs)    #setCentralWidget puts tab container as the main content area

    #─────Define a method to exit the app when user closes window ─────────────────────────────────────────────────────
    """
    1. closeEvent() method is a built-in method from QMainWindow where the window will close when user chooses to close
    it.

    2. However, we're overriding it with custom functionality where a message box will pop up to confirm the close.
    """
    def closeEvent(self,event):

        confirmation = QMessageBox.question(                               
            self,"Quit","Are you sure you want to quit the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirmation == QMessageBox.StandardButton.Yes:
            event.accept()      #Accept the close event, window will be closed
        else:
            event.ignore()      #Ignore the close event, window remains opened

#─────INITIALISE THE APP───────────────────────────────────────────────────────────────────────────────────────────────
"""
1. This is where the app is really initialised.

2. __name__ is a python built-in variable, it determines how the app is being run. 

3. If the app is initialised by running this file directly, __name__ will be __main__

4. If the app is initialised by running from other files. __name__ will be the filename
"""
if __name__ == "__main__":

    app = QApplication([])             #Create an object to start the app
    
    app.setStyle("Fusion")           #"Fusion" is a modern,flat style that exist in all OS           
    app.setStyleSheet(STYLESHEET)    #Apply the global widget style with defined STYLESHEET defined earlier

    #─────DEFINE OBJECT FOR THE MAIN WINDOW CLASS AND SHOW THE WINDOW ON SCREEN────────────────────────────────────────
    window = MainWindow()            #Create the window object on this app with the MainWindow() class as blueprint
    window.setWindowIcon(QIcon(resource_path("app_logo.jpeg")))  #Use company logo for the app icon
    window.showMaximized()    #show the main window in maximized when the app is initialised

    #─────SET VERSION NUMBER───────────────────────────────────────────────────────────────────────────────────────────
    version_no = "v1.0.0"
    version_label = QLabel(version_no)
    version_label.setStyleSheet('color: #80461B; font-size: 14px;')

    window.statusBar().addPermanentWidget(version_label)

    #─────EXIT THE APPLICATION WITH CONDITIONS─────────────────────────────────────────────────────────────────────────
    """
    1. sys.exit is an action where CPython shut down itself.

    2. The ".exec()" method creates an infinite event loop that hold the window on screen and only trigger the exit 
    action when the Main Window is closed.
    """
    sys.exit(app.exec())