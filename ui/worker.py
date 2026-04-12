"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This is the file to link iteration signal released from calculation tab to the progress panel 
                      file.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
from PyQt6.QtCore import QThread, pyqtSignal
"""
1. QThread enables multithreading where code will be run in other thread separated from the main thread
2. pyqtSignal is used to define signal to trigger other methods or functions
 """

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 9.0────────────────────────────────────────────────────────────────────────────────────────────────────────
class IterationStatus(QThread):
    
    #Define the signals to deliver
    progress = pyqtSignal(int)      #signal to update iteration progress to the progress bar
    status = pyqtSignal(str)        #signal to update status displayed on the pop-up window
    finished = pyqtSignal()         #signal to update user that convergence is completed
    error = pyqtSignal(str)         #signal to trigger error pop-up raised by guard

    #─────9.1 INITIALISE THE QTHREAD CLASS THAT TAKES THE CALCULATION TAB AS ARGUMENT──────────────────────────────────
    def __init__(self, calc_tab):

        super().__init__()

        self.calc_tab = calc_tab        #Create an object for the connected tab class
        self._cancelled = False         #This object will be used as a condition later when thread runs

    #─────9.2 HELPER METHOD #1─────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method will be called
    """
    def cancel(self):
        self._cancelled = True      

    #─────9.3 HELPER METHOD #2─────────────────────────────────────────────────────────────────────────────────────────
    """
    The run() method is a built-in QThread method that executes automatically after QThread are being started. 
    We are not overriding it with custom logics.
    """
    def run(self):   
        try:
            self.calc_tab._cancelled = self._cancelled   #pass the cancellation object to target Class
            self.calc_tab._worker = self    #assign the target class's worker to be current class
            self.calc_tab.runCalculators()  #run the target class's internal method named runCalculators()
            self.progress.emit(100)         #After the method finish running, emit the progress signal as 100
            self.finished.emit()            #Finally, emit the finish signal
        
        except Exception as e:
            self.error.emit(str(e))         #Any errors emerges will emit the error signal 

