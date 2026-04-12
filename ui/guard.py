"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This is a helper file that creates multiple guard functions that display error popups to notify
                      user about errors in user friendly language.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
import pandas as pd
from PyQt6.QtWidgets import QMessageBox
    
#─────GUARD POP UP FUNCTION────────────────────────────────────────────────────────────────────────────────────────────
"""
This guard function received any kind of Exception messages when errors are captured during the iteration.
It will then create a pop up window to notify user about what kind of errors they encounter.
"""
def _show_error_popup(context: str,exc: Exception):   
    
    #Set up the display of message box when error is encountered
    pop_up = QMessageBox()
    pop_up.setObjectName("popup")
    pop_up.setWindowTitle("Error Found!")
    pop_up.setFixedSize(400,200)

    #If the error is an instance of Errors, which it is
    if isinstance(exc,Errors):
        pop_up.setIcon(QMessageBox.Icon.Warning)        
        pop_up.setText(str(exc))
        pop_up.setInformativeText("Check inputs again.")

    else:
        pop_up.setIcon(QMessageBox.Icon.Critical)
        pop_up.setText(f"Unexpected error in {context}")
        pop_up.setInformativeText(str(exc))

    #execute the command when an error is encountered
    pop_up.exec()

#─────CLASS CLUSTERS───────────────────────────────────────────────────────────────────────────────────────────────────
"""
This Errors() class inherits the Exception class. When guard methods have captured an error from the iteration, 
the Errors() class will be raised and it will pass to the Exception class, triggering the above pop up function.
"""
class Errors(Exception):
    pass

"""
These 4 are subclasses that inherits the Errors() class. Any of these subclasses will be raised when corresponding
guard methods have captured an error from the iteration.
"""
class InvalidInput(Errors):
    pass

class BasisTooLow(Errors):
    pass

class ExceedBoundary(Errors):
    pass

class NoDataSelected(Errors):
    pass


#─────GUARD #1─────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
This guard function checks if all the user_inputs are filled with objects, mainly drop down and text box
"""
def _check_inputs(**input):                 #checks all kind of keyword arguments which is a dictionary

    empty = []                              #storage variable to store widget names that did not have an input
    for label,widget in input.items():      #check the key value pairs for each widget defined in calculation tab
        if not widget.text().strip():       #if the widget does not have a input, append to the empty list
            empty.append(label)
        
    if empty:                               
         raise InvalidInput(f"These fields cannot be empty:\n"+         #Pass this error text to InvalidInput class
                               "\n".join(f"• {f}" for f in empty))
    
#─────GUARD #2─────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
This guard function checks if 1P basis falls below 0 during the iteration, notifying user to increase basis value
"""   
def _check_1p_basis(input):

    if input <= 0:
        raise BasisTooLow("1st Pass Basis too low!")

#─────GUARD #3─────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
This guard function checks if 2P basis falls below 0 during the iteration, notifying user to increase basis value
"""       
def _check_2p_basis(input):
    if input <= 0:
        raise BasisTooLow("2nd Pass basis too low!")

#─────GUARD #4─────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
This guard function checks if the operating concentration and operating pressure is out of the grid for flux and 
rejection interpolation.
"""   
def _check_grid(input_1,input_2,grid:pd.DataFrame):

    if float(input_1) > max(grid.iloc[:,0].astype(float)) or float(input_1) < min(grid.iloc[:,0].astype(float)):
        raise ExceedBoundary(f"Concentration out of bound.")
    
    if float(input_2) >max(grid.iloc[:,1].astype(float)) or float(input_2) <min(grid.iloc[:,1].astype(float)):
        raise ExceedBoundary(f"Pressure out of bound.")
    


    




    


