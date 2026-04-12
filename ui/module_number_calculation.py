"""
Author              : MARCUS THAM WAI KEAN
DATE CREATED        : 3-MARCH-2026
DATE COMPLETED      : 31-MARCH-2026
ROLL-OUT VERSION    : v1.0.0
DESCRIPTION         : This is the 2nd tab on the main window that allows user to initiate iterations. In the midst of
                      iteration, then painting actions will be undergone in the background. Iterations will stop once
                      the convergences conditions are met.
"""
#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT RELEVENT LIBRARIES AND PACKAGES───────────────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import math

#Import the scipy.interpolate library to allow for double interpolation to be conducted later on in the calculation
from scipy.interpolate import RegularGridInterpolator 

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT REQUIRED WIDGET CLASSES FROM QTWIDGETS MODULE─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QComboBox,QPushButton,
    QLineEdit,QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QRect,QPoint
from PyQt6.QtGui import QPainter, QPen, QFont,QPolygon

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────IMPORT CUSTOM CLASSES FROM OTHER FILES FOR CONNECTION────────────────────────────────────────────────────────────
from ui.guard import (_check_inputs,_check_1p_basis,_check_2p_basis,
                      _check_grid,NoDataSelected,BasisTooLow,_show_error_popup)
from ui.worker import IterationStatus
from ui.progress_panel import ProgressPanel

#─────HELPER FUNCTION #5───────────────────────────────────────────────────────────────────────────────────────────────
"""
This helper function takes in data frame and generate a 2-dimensional table for flux and rejection data. This 
function also has a pre-defined arguments for column positions in a data frame
"""
def grid_2d(df:pd.DataFrame,col_x = 0, col_y = 1, col_z = 2):
    
    """
    1. The strcture of the targeting data frame for this function has 3 columns (conc., pressure, flux/rejection)

    2. use .copy() to duplicate a temporary data frame in according to the target data frame

    3. In the temporary data frame, set the columns to be x, y and z for the 3 columns.
    """
    df_temp = df.iloc[:,[col_x,col_y,col_z]].copy()
    df_temp.columns = ["x","y","z"]

    """
    1. Use the .pivot_table to generate pivot table from the temporary data frame
    
    2. Index is the row of pivot table; columns is the columns for the pivot table; values is the array for the pivot
    table.
    """
    df_pivot = df_temp.pivot_table(
        index = "x",      #Transform the 'Concentration' column into row index 
        columns="y",      #Transform the 'Pressure' column into pivot table columns
        values="z"        #Sort the array in accordance with corresponding concentration and pressure values
    )
    
    # "Store the index, columns and values attributes from the pivot table into different objects of convenient namings"
    conc_grid = df_pivot.index.values
    pressure_grid = df_pivot.columns.values
    flux_grid = df_pivot.values

    """
    1. Construct the interpolator using the 3 ttributes from pivot tables
    
    2. The RegularGridInterpolator() usually have 2 default arguments points and values where values are the array for
    x-axis and y-axis, values are the array bound to the axes.

    3. In this case, x-axis is the conc_grid, y-axis is the pressure_grid, and values is the flux_grid. 
    """
    final_grid = RegularGridInterpolator(
        (conc_grid,pressure_grid),
        flux_grid
        )

    return final_grid

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 3.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
Create a class named ModuleDrawing that takes care of any paint event initiated by CLASS 4.0: CalculationTab(). 
"""
class ModuleDrawing(QWidget):
    
    # "Set up constants for 1st pass drawing"
    MODULE_W  = 80      # module width
    MODULE_H  = 160     # module height
    ARROW_LEN = 100     # arrow length
    PERM_H    = 80      # permeate arrow length
    PADDING   = 20      # left padding
    ROW_Y     = 10      # vertical position of module row
    ARROW_W   = 8       # arrowhead width

    # "Set up constants for 2nd pass drawing"
    _2p_MODULE_W  = 80    # module width
    _2p_MODULE_H  = 160   # module height
    _2p_ARROW_LEN = 100   # arrow length
    _2p_PERM_H    = 80    # arrow length
    _2p_PADDING   = 20    # left padding
    _2p_ROW_Y     = 290   # vertical position of module row
    _2p_ARROW_W   = 8     # arrowhead width

    #─────3.1: INITIALISE THE CLASS WITH PRE-DEFINED OBJECTS───────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()

        #─────INITIAL AND STORAGE VARIABLES────────────────────────────────────────────────────────────────────────────
        self.n_modules = 0 
        self.results = []
        self._2p_results = []
    
    #─────3.2: HELPER METHOD #0────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method calculates the dimension of drawing areas based on how many number of modules are input by
    the user.
    """
    def _resize(self):

        """
        1. Total Width: padding on both sides + total number of modules * (module width + arrow length) + last arrow

        2. Total Height: upper gap + module height + permeate arrow vertical length + 1000 (space for 2nd pass)
        """
        total_width = self.PADDING*2 + self.n_modules*(self.MODULE_W + self.ARROW_LEN)+ self.ARROW_LEN 
        total_height = self.ROW_Y + self.MODULE_H + self.PERM_H + 1000

        # "Set a fixed size for the drawing event later on"
        self.setFixedSize(total_width,total_height)

    #─────3.3: HELPER METHOD #1────────────────────────────────────────────────────────────────────────────────────────
    
    # This helper method updates results to the pre-defined empty storage variable in section 3.1 for 1st pass
    def update_results(self, n_modules: int, results: list[dict]):

        # "Extract number of modules based on user input for 1P, we have 0 number of module intially"
        self.n_modules = n_modules 

        # "Create object to store the result dictionary created in section 4.7 and 4.8"
        self.results   = results 

        # "Resive the drawing area based on number of module WITH HELPER METHOD #0"
        self._resize()

        # "If number of module updates, trigger to update the custom paintEvent()"
        self.update()  

    #─────3.3: HELPER METHOD #2────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method updates results to the pre-defined empty storage variable in section 3.1 for 2nd pass
    """
    def update_2p_results(self, n_modules: int, results: list[dict]):
        
        # "Extract number of modules based on user input for 2P, we have 0 number of module initially"
        self.n_modules = n_modules 

        # "Create object to store the result dictionary created in section 4.9 and 4.10"
        self._2p_results   = results 

        # "Resive the drawing area based on number of module with HELPER METHOD #0"
        self._resize()  

        # "If number of module updates, trigger to update the custom paintEvent()"
        self.update()  

    #─────3.4: HELPER METHOD #3────────────────────────────────────────────────────────────────────────────────────────
    """
    1. The 'paintEvent()' method is a PyQt6 built-in method to draw its own widget shapes such as QLineEdit, QComboBox,
    etc.

    2. However, we can define our own custom paintEvent() method to draw shapes in our wish.

    3. The usual skeleton for the custom paintEvent method is as follow:
        def paintEvent(self,event):
            painter = QPainter(self)

            ---painting codes---

            painter.end()

    4. paintEvent() method will not run on its own, but will be triggered by self.update() for redraw within the class
    """
    def paintEvent(self,event):
        
        # "If number of modules is equal to 0, no action will be done to prevent app crash"
        if self.n_modules == 0:
            return
        
        # "Attach QPainter() to the paint event. QPainter is the drawer that draws shapes on the canva"
        painter = QPainter(self)

        # "The '.setRenderHint()' is a QPainter method to tell QPainter to use high quality rendering for shapes and text"
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # "For 1st pass, loop each module to draw the module shapes and arrows on the canva"
        for i in range(self.n_modules):

            # "Horizontal length"
            x = self.PADDING + i * (self.MODULE_W + self.ARROW_LEN)

            # "If result exists, extract necessary stream parameters to display on canva, or else leave blank"
            r = self.results[i] if self.results else {}

            self._draw_module(painter,i,x,r)

        # "Followed by 1st pass section, draw the combined permeate arros to join 2nd pass"
        self._draw_combined_permeate(painter)

        # "For 2nd pass, loop each module to draw the module shapes and arros on the canva"
        for i in range(self.n_modules):
            
            # "Horizontal length of each module drawn on the canvas"
            x = self._2p_PADDING + i * (self._2p_MODULE_W + self._2p_ARROW_LEN)

            # "Similarly, update 2nd pass results"
            r = self._2p_results[i] if self._2p_results else {}

            self._draw_2p_module(painter,i,x,r)

        painter.end()

    #─────3.5: HELPER METHOD #4────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method draws a single module block and connected arrows on the canva when paint event is triggered.
    This method takes in 4 arguments where:
    - painter   : The painter widget
    - i         : Number of module
    - x         : Horizontal starting point for each module block
    - r         : The values from the result dictionaries based on corresponding module number key
    """
    def _draw_module(self,painter,i,x,r):  

        #─────COORDINATES──────────────────────────────────────────────────────────────────────────────────────────────
        # "Set up coordinates for 1st pass module block drawing"
        mid_y = self.ROW_Y + self.MODULE_H //2      #The vertical starting point of each module block
        box_x = x + self.ARROW_LEN                  #The horizontal starting point of each module block

        ret_x = box_x + self.MODULE_W               #The horizontal starting point of retentate stream arrow

        perm_x = box_x + self.MODULE_W//2           #The horizontal starting point of permeate stream arrow
        perm_y = self.ROW_Y + self.MODULE_H         #The vertical starting point of permeate stream arrow

        # "For QPainter, set pen color of black and also font styles using QPen and QFont respectively."
        pen = QPen(Qt.GlobalColor.black,1)
        painter.setPen(pen)
        painter.setFont(QFont("Arial",9,QFont.Weight.Bold))
        painter.setBrush(Qt.BrushStyle.VerPattern)

        #─────MODULE BLOCK─────────────────────────────────────────────────────────────────────────────────────────────
        """
        Draw rectangle shape using .drawRect() method.
        The 4 arguments stand for (x,y,width,length) where x and y are the coordinates at the top left of the shape
        """
        painter.drawRect(box_x,self.ROW_Y,self.MODULE_W,self.MODULE_H)

        """
        In each module block, shows module number in text form.
        The '.drawText()' method takes in multiple arguments if it's within a rectangle with alignment:
            painter.drawText(x,y,width,length,alignment,{text})
        """
        painter.drawText(
            box_x, self.ROW_Y, self.MODULE_W, self.MODULE_H,
            Qt.AlignmentFlag.AlignCenter,
            f"Module {i+1}"  #module number i starts from 0
        )
        
        #─────INLET STREAM─────────────────────────────────────────────────────────────────────────────────────────────
        """
        Since the paint event loop only draws module block, retentate stream and permeate stream for each module 
        block, the inlet stream for the 1st module must be drawn to. 

        **Note: From 2nd module onward, the inlet stream must be overlapped with the retentate stream of the previous
        module.

        The '.drawLine()' method takes in 4 arguments:
            painter.drawLine(x1,y1,x2,y2) where (x1,y1) and (x2,y2) are coordinates of start & end points respectively
        """
        painter.drawLine(x,mid_y,x+self.ARROW_LEN,mid_y)

        # "Call HELPER METHOD #7 to draw triangular arrowhead"
        self._draw_arrowhead(painter, x + self.ARROW_LEN,mid_y,"right")

        "Create object for all stream variables to be displayed on each module block using .get() method for dict"
        inlet_c = r.get("inlet_conc", "--")
        inlet_m = r.get("inlet_total_mass_flow", "--")
        inlet_v = r.get("inlet_total_vol_flow","--")
        inlet_rho = r.get("inlet_density","--")
        inlet_p = r.get("inlet_pressure","--")
        inlet_t = r.get("inlet_temp","--")
        inlet_lv = r.get("inlet_lv","--")

        # "Display the stream variables as text for each module block"
        painter.setFont(QFont("Arial", 8))   #Reset font style here

        painter.drawText(x+4, mid_y - 80, f"C = {inlet_c} wt%")
        painter.drawText(x+4, mid_y - 67, f"ṁ = {inlet_m} kg/hr")
        painter.drawText(x+4, mid_y - 54, f"v = {inlet_v} m3/hr")
        painter.drawText(x+4, mid_y - 41, f"ρ = {inlet_rho} kg/m3")
        painter.drawText(x+4, mid_y - 28, f"P = {inlet_p} bar")
        painter.drawText(x+4, mid_y - 15, f"T = {inlet_t} °C")
        painter.drawText(x+4, mid_y - 2, f"LV = {inlet_lv} m/s")

        #────RETENTATE STREAM──────────────────────────────────────────────────────────────────────────────────────────
        # "Draw retentate line for each module block"
        painter.drawLine(ret_x, mid_y, ret_x + self.ARROW_LEN, mid_y)
        
        # "Call HELPER METHOD #7 to draw triangular arrowhead"
        self._draw_arrowhead(painter, ret_x + self.ARROW_LEN, mid_y, "right")

        # "Retentate stream variables labelling"
        ret_c = r.get("ret_conc", "--")
        ret_m = r.get("ret_total_mass_flow", "--")
        ret_v = r.get("ret_total_vol_flow", "--")
        ret_rho = r.get("ret_density", "--")
        ret_p = r.get("ret_pressure", "--")
        ret_t = r.get("inlet_temp", "--")
        ret_lv = r.get("ret_lv", "--")

        painter.drawText(ret_x+4 , mid_y - 80, f"C = {ret_c} wt%")
        painter.drawText(ret_x+4 , mid_y - 67,  f"ṁ = {ret_m} kg/hr")
        painter.drawText(ret_x+4 , mid_y - 54,  f"v = {ret_v} m3/hr")
        painter.drawText(ret_x+4 , mid_y - 41,  f"ρ = {ret_rho} kg/m3")
        painter.drawText(ret_x+4 , mid_y - 28,  f"P = {ret_p} bar")
        painter.drawText(ret_x+4 , mid_y - 15,  f"T = {ret_t} °C")
        painter.drawText(ret_x+4 , mid_y - 2,  f"LV = {ret_lv} m/s")

        #────PERMEATE STREAM───────────────────────────────────────────────────────────────────────────────────────────
        # "Draw permeate line for each module block"
        painter.drawLine(perm_x, perm_y, perm_x, perm_y + self.PERM_H)
        
        # "Call HELPER METHOD #7 to draw triangular arrowhead"
        self._draw_arrowhead(painter, perm_x, perm_y + self.PERM_H, "down")

        # "Permeate stream variables labelling"
        perm_c = r.get("perm_conc", "--")
        perm_m = r.get("perm_total_mass_flow", "--")
        perm_v = r.get("perm_total_vol_flow", "--")
        perm_rho = r.get("perm_density","--")

        painter.drawText(perm_x + 6, perm_y + 25, f"C = {perm_c} wt%")
        painter.drawText(perm_x + 6, perm_y + 38, f"ṁ = {perm_m} kg/hr")
        painter.drawText(perm_x + 6, perm_y + 51, f"v = {perm_v} m3/hr")
        painter.drawText(perm_x + 6, perm_y + 64, f"ρ = {perm_rho} kg/m3")
    
    #─────3.6: HELPER METHOD #5────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method draws the lines and arrow to combine all permeate streams from 1st pass channeling into 2nd pass
    first module inlet.
    """
    def _draw_combined_permeate(self, painter):
        
        # "As usual, set up pen style"
        pen = QPen(Qt.GlobalColor.black,1)
        painter.setPen(pen)

        # "Set up coordinates for the horizontal combined permeate line"
        perm_y    = self.ROW_Y + self.MODULE_H + self.PERM_H                    #Vertical starting point of the line
        first_x   = self.PADDING + self.ARROW_LEN + self.MODULE_W // 2          #Horizontal starting point of the line
        last_x    = (self.PADDING 
                     + (self.n_modules - 1) * (self.MODULE_W + self.ARROW_LEN)  #Horizontal ending point of the line
                     + self.ARROW_LEN + self.MODULE_W // 2)
        
        # "Draw the horizontal combined permeate line based on defined coordinates"
        painter.drawLine(first_x, perm_y, last_x, perm_y)
        
        # "Set up coordinates for the vertical arrow line continuing from the horizontal combined permeate line"
        x_vert = (last_x + first_x)//2  #Horizontal starting point of the vertical arrow line
        first_y = perm_y                #Vertical starting point of the vertical arrow line
        last_y = perm_y + 20            #Vertical ending point of the vertical arrow line

        # "Draw the vertical arrow line based on defined coordinates and also the arrowhead facing downward"
        painter.drawLine(x_vert,first_y,x_vert,last_y)
        self._draw_arrowhead(painter, x_vert, last_y, "down")
    
        # "Draw horizontal and vertical lines that connect to the inner stream arrow of 2nd pass"
        painter.drawLine(x_vert,last_y,self.PADDING ,last_y)
        painter.drawLine(self.PADDING,last_y,self.PADDING,last_y+self.ARROW_LEN)
        painter.drawLine(self.PADDING,last_y+self.ARROW_LEN,self.PADDING+self.ARROW_LEN,last_y+self.ARROW_LEN)
        self._draw_arrowhead(painter,self.PADDING+self.ARROW_LEN,last_y+self.ARROW_LEN,"right")

    #─────3.7: HELPER METHOD #6────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method is similar to HELPER METHOD #4 where it draws a single module block and connected arrows on the 
    canva when paint event is triggered. The onlyb different here is the coordinates and naming are set separately for
    2nd pass. Annotations are not shown in this method due to similarity with HELPER METHOD #4.
    """   
    def _draw_2p_module(self,painter,i,x,r):  #function to draw 1 module block

        #─────COORDINATES──────────────────────────────────────────────────────────────────────────────────────────────    
        mid_y = self._2p_ROW_Y + self._2p_MODULE_H //2  
        box_x = x + self._2p_ARROW_LEN 
        ret_x = box_x + self._2p_MODULE_W    
        perm_x = box_x + self._2p_MODULE_W//2  
        perm_y = self._2p_ROW_Y + self._2p_MODULE_H  

        pen = QPen(Qt.GlobalColor.black,1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.VerPattern)

        #─────MODULE BLOCK─────────────────────────────────────────────────────────────────────────────────────────────
        painter.drawRect(box_x,self._2p_ROW_Y,self._2p_MODULE_W,self._2p_MODULE_H)

        painter.setFont(QFont("Arial",9,QFont.Weight.Bold))
        painter.drawText(
            QRect(box_x, self._2p_ROW_Y, self._2p_MODULE_W, self._2p_MODULE_H),
            Qt.AlignmentFlag.AlignCenter,
            f"Module {i+1}"
        )
        
        #─────INLET STREAM  ───────────────────────────────────────────────────────────────────────────────────────────
        painter.drawLine(x,mid_y,x+self._2p_ARROW_LEN,mid_y)
        self._draw_arrowhead(painter, x + self._2p_ARROW_LEN,mid_y,"right")

        inlet_c = r.get("inlet_conc", "--")
        inlet_m = r.get("inlet_total_mass_flow", "--")
        inlet_v = r.get("inlet_total_vol_flow","--")
        inlet_rho = r.get("inlet_density","--")
        inlet_p = r.get("inlet_pressure","--")
        inlet_t = r.get("inlet_temp","--")
        inlet_lv = r.get("inlet_lv","--")

        painter.setFont(QFont("Arial", 8))

        painter.drawText(x+4, mid_y - 80, f"C = {inlet_c} wt%")
        painter.drawText(x+4, mid_y - 67, f"ṁ = {inlet_m} kg/hr")
        painter.drawText(x+4, mid_y - 54, f"v = {inlet_v} m3/hr")
        painter.drawText(x+4, mid_y - 41, f"ρ = {inlet_rho} kg/m3")
        painter.drawText(x+4, mid_y - 28, f"P = {inlet_p} bar")
        painter.drawText(x+4, mid_y - 15, f"T = {inlet_t} °C")
        painter.drawText(x+4, mid_y - 2, f"LV = {inlet_lv} m/s")

        #─────RETENTATE STREAM─────────────────────────────────────────────────────────────────────────────────────────
        painter.drawLine(ret_x, mid_y, ret_x + self._2p_ARROW_LEN, mid_y)
        self._draw_arrowhead(painter, ret_x + self._2p_ARROW_LEN, mid_y, "right")

        ret_c = r.get("ret_conc", "--")
        ret_m = r.get("ret_total_mass_flow", "--")
        ret_v = r.get("ret_total_vol_flow", "--")
        ret_rho = r.get("ret_density", "--")
        ret_p = r.get("ret_pressure", "--")
        ret_t = r.get("inlet_temp", "--")
        ret_lv = r.get("ret_lv", "--")

        painter.drawText(ret_x+4 , mid_y - 80, f"C = {ret_c} wt%")
        painter.drawText(ret_x+4 , mid_y - 67,  f"ṁ = {ret_m} kg/hr")
        painter.drawText(ret_x+4 , mid_y - 54,  f"v = {ret_v} m3/hr")
        painter.drawText(ret_x+4 , mid_y - 41,  f"ρ = {ret_rho} kg/m3")
        painter.drawText(ret_x+4 , mid_y - 28,  f"P = {ret_p} bar")
        painter.drawText(ret_x+4 , mid_y - 15,  f"T = {ret_t} °C")
        painter.drawText(ret_x+4 , mid_y - 2,  f"LV = {ret_lv} m/s")

        #─────PERMEATE STREAM──────────────────────────────────────────────────────────────────────────────────────────
        painter.drawLine(perm_x, perm_y, perm_x, perm_y + self._2p_PERM_H)
        self._draw_arrowhead(painter, perm_x, perm_y + self._2p_PERM_H, "down")

        perm_c = r.get("perm_conc", "--")
        perm_m = r.get("perm_total_mass_flow", "--")
        perm_v = r.get("perm_total_vol_flow", "--")
        perm_rho = r.get("perm_density","--")
        painter.drawText(perm_x + 6, perm_y + 25, f"C = {perm_c} wt%")
        painter.drawText(perm_x + 6, perm_y + 38, f"ṁ = {perm_m} kg/hr")
        painter.drawText(perm_x + 6, perm_y + 51, f"v = {perm_v} m3/hr")
        painter.drawText(perm_x + 6, perm_y + 64, f"ρ = {perm_rho} kg/m3")
    
    #─────3.8: HELPER METHOD #7────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method draws the triangular arrow head facing either right side or downward at the end of an arrow line
    """
    def _draw_arrowhead(self, painter, x, y, direction):
        
        # "Create object for arrow width"
        w = self.ARROW_W

        # "Set up pen and brush style"
        painter.setBrush(Qt.GlobalColor.black)
        painter.setPen(Qt.GlobalColor.black) 

        # "Set up painting logics where arrow head is facing right side or downward directions"
        if direction == "right":
           
            # "Set up points where the triangle is facing the right side"
            points = QPolygon([
                QPoint(x,y),
                QPoint(x - w, y - w // 2),
                QPoint(x - w, y + w // 2)
            ])

        elif direction == "down":
            
            # "Set up points where the triangle is facing downward"
            points = QPolygon([
                QPoint(x,y),
                QPoint(x - w // 2, y - w),
                QPoint(x + w // 2, y - w)
            ])

        # "Draw the triangular arrowheads"
        painter.drawPolygon(points)

#══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#─────CLASS 4.0────────────────────────────────────────────────────────────────────────────────────────────────────────
"""
Create a class named CalculationTab as our 2nd tab in main window. This class inherit all functions from the 
parent class QWidget. This class serves as a blueprint to extract the user input from the UserInputTab and perform
iteration for a batch membrane separation process to back calculate the number of modules and parallel train needed
for large scale system based on client's required capacity.
"""
class CalculationTab(QWidget):

    #─────4.1: INITIALISE THE CLASS WITH PRE-DEFINED OBJECTS───────────────────────────────────────────────────────────
    def __init__(self,user_input_tab,solute_density_tab,solvent_density_tab,result_tab):  
        super().__init__()

        """
        Pass in the other tabs' objects as arguments for this class. This is to allow access to other tabs' methods 
        and attributes.
        """
        self.ui = user_input_tab
        self.solute = solute_density_tab
        self.solvent = solvent_density_tab
        self.result_tab = result_tab

        #Build the UI interface for the calculation tab
        self.build_ui()

    #─────4.2: HELPER METHOD #0────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method constructs the UI and define how all the widgets are shown on the tab.
    """
    def build_ui(self):

        #Create a vertical box layout using QVBoxLayout, set margins and also spacing between widgets in layout
        root = QVBoxLayout(self)
        root.setContentsMargins(24,24,24,24)
        root.setSpacing(10)

        #Create a button on the first row to allow initiation of iterations
        self.calc_button = QPushButton("Calculate")
        self.calc_button.setObjectName("primaryBtn")

        #Connect the button widget to HELPER METHOD #1 and add the button widget to the layout
        self.calc_button.clicked.connect(self._start_iteration)  
        root.addWidget(self.calc_button)

        #Create a scrollable widget for painter to draw the process flow later on
        self.scroll_area = QScrollArea()

        """
        Set scroll bar policy such that the canvas area cannot be scrolled vertically as painting has fixed vertical
        length. '.setVerticalScrollBarPolicy()' will hide the vertical scroll bar, while setting 
        '.verticalScrollBar().setEnabled()' to False will restrict user to scroll vertically using mouse.
        """
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.verticalScrollBar().setEnabled(False)

        #Passing CLASS 3.0 into an object, whcih is the class that holds the painting blueprint
        self.diagram = ModuleDrawing()

        #Place the painting widget class into the scoll area canva. '.setWidget(QWidget)' is a QScrollArea method
        self.scroll_area.setWidget(self.diagram) 
        
        #Define how the canva will be constructed on the vertical layout
        root.addSpacing(10)
        root.addWidget(self.scroll_area)
        
    #─────4.3: HELPER METHOD #1────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method will be started once the button widget defined in the build_ui method is clicked (LINE 572).
    Mainly to create a separate thread to show the pop up window panel to update iteration progress without main UI 
    freezing. This method will also trigger the core iteration helper method (HELPER METHOD 4.5).
    """
    def _start_iteration(self):    
        
        #First, check all the inputs from the user input tab using the imported helper method from guard.py.
        try:
                _check_inputs(**{
                "Pressure"                        : self.ui.pressure_input,
                "Temperature"                     : self.ui.temp_input,
                "1st Pass Target Concentration"   : self.ui._1p_ret_input,
                "2nd Pass Target Concentration"   : self.ui._2p_ret_input,
                "1st Pass Linear Velocity"        : self.ui.linear_velocity,
                "2nd Pass Linear Velocity"        : self.ui._2p_linear_velocity,
                "Solute Flow"                     : self.ui.solute_flow_input,
                "Solvent Flow"                    : self.ui.solvent_flow_input,
                "1st Pass Module Number"          : self.ui.module_no,
                "2nd Pass Module Number"          : self.ui._2p_module_no,
                "1st Pass Basis"                  : self.ui._1p_basis_input,
                "2nd Pass Basis"                  : self.ui._2p_basis_input,
            })

                #Triggering guard class from guard.py when any of the data files are not selected or defined.
                if self.ui.flux_df is None or self.ui.flux_df.empty:
                    raise NoDataSelected("No flux & rejection data selected.") 
                if self.ui.solute_df is None or self.ui.solute_df.empty:
                    raise NoDataSelected("No Solute Type Selected.")
                if self.ui.solvent_df is None or self.ui.solvent_df.empty:
                    raise NoDataSelected("No Solvent Type Selected.")
                if self.ui.df_clean.iloc[:,[1]].astype(float).empty:
                    raise NoDataSelected("No 1st Pass Module Size Selected.")
                if self.ui._2p_df_clean.iloc[:,[1]].astype(float).empty:
                    raise NoDataSelected("No 2nd Pass Module Size Selected.")

        except Exception as e:
            _show_error_popup("Input Check", e)
            return  
        
        #When button is being clicked, disable the button to restrict user to press the button again
        self.calc_button.setEnabled(False) 

        #Call in the progress panel and signal worker classes defined in progress_panel.py and worker.py
        self.worker = IterationStatus(self)
        self.panel = ProgressPanel(self)

        """
        Connect the progress and status signal from worker class to the helper methods defined in the progress panel
        class. Mainly to capture signals for the progress panel to display it on the window pop-up.
        """
        self.worker.progress.connect(self.panel.update_progress)
        self.worker.status.connect(self.panel.update_status)

        """
        Connect the cancel button widget back to the worker class so when cancel button is clicked, the thread will 
        stop running and then will close the panel. 
        """
        self.panel.cancel_btn.clicked.connect(self.worker.cancel)
        self.panel.cancel_btn.clicked.connect(self.panel.close)

        """
        Connect the finishe signal from worker class to panel's helper method 'mark_done'.
        So, when the runCalculator() has finished iterating, it will release a finish signal to trigger the mark_done
        helper method that updates the status and button text accordingly. After that, unrestrict the calculation
        button so user can click again. 

        If any error signal emited, it will trigger the on_iteration error() method in this file to display respecitive
        error message through pop-up.
        """
        self.worker.finished.connect(self.panel.mark_done)
        self.worker.finished.connect(lambda: self.calc_button.setEnabled(True))
        self.worker.error.connect(self.on_iteration_error)

        #Show the panel and start the thread
        self.panel.show()
        self.worker.start()
    
    #─────4.4: HELPER METHOD #2────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method will be triggered when any error is encountered in the midst of iteration.
    """
    def on_iteration_error(self,msg):

        #When triggered, close the panel and unrestrict the calculation button
        self.panel.close()
        self.calc_button.setEnabled(True)

        #Create a pop-up box to display warning
        pop_up = QMessageBox()
        pop_up.setWindowTitle("Error Found!")
        pop_up.setIcon(QMessageBox.Icon.Warning)
        pop_up.setText(msg)
        pop_up.setInformativeText("Check inputs and try again.")
        pop_up.exec()

    #─────4.5: HELPER METHOD #3────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method initiates the iteration for the batch membrane separation process. User inputs from the 
    user_input.py will be called as initial parameters for the iteratons and calculations and the code will stop once
    a defined convergence is reached. All the results will then be tabulated in the result tab.
    """
    def runCalculators(self):
        
        """
        1. Start the iteration by calling operating parameters for the iteration that will not changed as the iteration
        begins.

        2. Other tabs have been passed into the current class, hence all the other tabs objects and method can be 
        referenced and accessed.

        3. All the text box and drop down texts will be converted to float type with the help of HELPER METHOD #4 to 
        prevent data type error.

        4. All data frame object will be passed to a new object with more friendly naming.

        """
        #────────Operating Parameters──────────────────────────────────────────────────────────────────────────────────
        self.pressure_value = self.float_toggle(self.ui.pressure_input)        #Operating Pressure for both passes
        self.temp_value = float(self.float_toggle(self.ui.temp_input))         #Operating Temperature for both passes
        self._1p_conc = float(self.float_toggle(self.ui._1p_ret_input))        #1st pass Target Retentate Concentration
        self.lv = float(self.float_toggle(self.ui.linear_velocity))            #1st pass linear velocity
        self._2p_lv = float(self.float_toggle(self.ui._2p_linear_velocity))    #2nd pass linear velocity
        self.ope_mode = self.ui.mode_text                                      #Operating mode (batch/continuous)

        #────────Data Frames───────────────────────────────────────────────────────────────────────────────────────────
        self._1p_module_size = self.ui.module_spec.currentText()                    #1st pass module size dropdown text
        self._2p_module_size = self.ui._2p_module_spec.currentText()                #2nd pass module size dropdown text
        self.module_spec_df = self.ui.df_clean[self._1p_module_size].astype(float)           #Extract 1P module data
        self._2p_module_spec_df = self.ui._2p_df_clean[self._2p_module_size].astype(float)   #Extract 2P module data
        
        self.solute_den_df = self.ui.solute_df      #Solute density table
        self.solvent_den_df = self.ui.solvent_df    #Solvent density table
        self.flux_final_df = self.ui.flux_df        #Flux table (Conc.,Pressure, Flux)
        self.rej_final_df = self.ui.rej_df          #Rejection table (Conc.,Pressure, Rejection)

        #────────Module Numbers In Series──────────────────────────────────────────────────────────────────────────────
        self.module_number = int(self.float_toggle(self.ui.module_no))              #1P no. of modules
        self._2p_module_number = int(self.float_toggle(self.ui._2p_module_no))      #2P no. of modules

        #────────Flowrates and Concentrations──────────────────────────────────────────────────────────────────────────
        self.solute_flow = float(self.float_toggle(self.ui.solute_flow_input))      #solute flow in kg/hr
        self.solvent_flow = float(self.float_toggle(self.ui.solvent_flow_input))    #solvent flow in kg/hr
        self.feed_flow = self.solute_flow + self.solvent_flow                       #total feed flow in kg/hr
        self.feed_conc = float(self.float_toggle(self.ui.feed_conc_readonly))/100   #feed solute concentration in wt%

        #────────Outer Loop Accumulator Variables──────────────────────────────────────────────────────────────────────
        current_recycle_iter = 0
        max_recycle_iter = 10000

        #────────Outer Loop Storage Variables──────────────────────────────────────────────────────────────────────────
        self.final_iterated_results = {} 
        self._2p_target_processing_rate = 0

        self.new_1p_target_processing_rate = self.feed_flow

        """
        Become the loop with the conditions of:
        1. Current iteration less than maximum of 10000
        2. 2nd Pass Recycle Check Box is checked
        3. Operation mode is set to "Batch"
        """
        while current_recycle_iter < max_recycle_iter and self.ui.recycle_button.isChecked() and self.ope_mode == "Batch":
            
            #Check if cancel button is pressed
            if hasattr(self, '_worker') and self._worker._cancelled:
                break

            #────────Inner Loop Accumulator Variables──────────────────────────────────────────────────────────────────
            self.max_iter = 10000
            self._1p_current_iter = 0
            self._2p_current_iter = 0

            #────────Inner Loop Storage Variables──────────────────────────────────────────────────────────────────────
            self.sum_perm_solute_mass = []
            self.sum_perm_solvent_mass = []
            self._2p_sum_perm_solute_mass = []
            self._2p_sum_perm_solvent_mass = []
            self.final_flux = []
            self.final_rej = []                        
            self._2p_final_flux = []
            self._2p_final_rej = []
            self._1p_process_time = 1  
            self._2p_process_time = 1

            #────────Tank Basis Variables──────────────────────────────────────────────────────────────────────────────
            """
            Tank basis related variables are dynamic.They will change as the iteration goes, hence being placed within 
            loop.
            """
            self._1p_basis = float(self.float_toggle(self.ui._1p_basis_input))         #1P basis input from user input
            self._1p_basis_solute_mass = self._1p_basis*self.feed_conc                 #1P tank solute mass
            self._1p_basis_solvent_mass = self._1p_basis-self._1p_basis_solute_mass    #1P tank solvent mass

            self._2p_basis = float(self.float_toggle(self.ui._2p_basis_input))         #2P basis input from user input
            self._2p_conc = float(self.float_toggle(self.ui._2p_ret_input))            #2P target concentration
           
            #────────Checker variables─────────────────────────────────────────────────────────────────────────────────
            """
            self.feed_conc is dynamic and will keep changing in the 1P per-minute loop. Hence, a new object is created
            out of the inner loop to lock the initial feed concentration for outer loop checking later on.
            """
            self.feed_conc_check = self.feed_conc

            #────────1st Pass inner per-minute loop────────────────────────────────────────────────────────────────────
            #Initiate the 1st pass inner per-minute loop
            while self._1p_current_iter < self.max_iter:

                #Check if cancel button is pressed
                if hasattr(self, '_worker') and self._worker._cancelled:
                    break

                #────────Storage Variables─────────────────────────────────────────────────────────────────────────────
                self.final_results = []
                self.final_perm_solute_mass = []
                self.final_perm_solvent_mass = []
                                                                                
                #Run the HELPER METHODSforR 1sr pass per minute iteration"                                                               
                self._1p_first_module_calculator()
                self._1p_middle_module_calculator()

                """
                1. Determine the total solute and solvent mass from all of the module permeate streams in 1 minute.
                2. Sum up the total solute and solvent mass for total permeate mass generate in 1 minute.
                3. From the permeate component masses, determine the overall permeate solute concentration in wt%.
                """
                self.total_perm_solute_mass = sum(self.final_perm_solute_mass)/60
                self.total_perm_solvent_mass = sum(self.final_perm_solvent_mass)/60
                self.total_perm_mass = self.total_perm_solute_mass + self.total_perm_solvent_mass
                self.overall_perm_oc = self.total_perm_solute_mass/self.total_perm_mass*100

                """
                1. Since permeate mass has been determined, we can now compute the tank balance using mass balance
                2. Determine the balance solute and solvent mass in 1P tank basis
                3. Remaining tank basis mass then can be back calculated too
                """
                self._1p_basis_balance_solute_mass = self._1p_basis_solute_mass - self.total_perm_solute_mass  #also retentate info for 1P
                self._1p_basis_balance_solvent_mass = self._1p_basis_solvent_mass - self.total_perm_solvent_mass #also retentate info for 2P
                self._1p_basis_new_mass = self._1p_basis_balance_solute_mass + self._1p_basis_balance_solvent_mass
                
                #Guard method from guard.py. Mainly to check if tank basis has dropped below 0
                _check_1p_basis(self._1p_basis_new_mass)

                #Back calculate the composition for the remaining solution in wt%
                self._1p_new_conc = self._1p_basis_balance_solute_mass/self._1p_basis_new_mass*100

                """
                1st PASS PERMEATE TANK BLOCK: Store the permeate solute and solvent masses for current minute
                """
                self.sum_perm_solute_mass.append(self.total_perm_solute_mass)
                self.sum_perm_solvent_mass.append(self.total_perm_solvent_mass)

                #Update result for ModuleDrawing() to initiate paint event
                self.diagram.update_results(self.module_number, self.final_results)

                #Check if remaining tank basis solute concentration has reached 1st pass target retentate concentration
                if self._1p_new_conc >= self._1p_conc:

                    #────────If condition is met───────────────────────────────────────────────────────────────────────
                    #Determine the total permeate mass generated from the whole 1st pass process
                    self.sum_permeate_solute_mass = sum(self.sum_perm_solute_mass)
                    self.sum_permeate_solvent_mass = sum(self.sum_perm_solvent_mass)
                    self.sum_permeate_mass = self.sum_permeate_solute_mass + self.sum_permeate_solvent_mass

                    #Back calculate the overall permeate solution solute concentration in wt%"
                    self.sum_permeate_oc = self.sum_permeate_solute_mass/self.sum_permeate_mass*100

                    """
                    Create a new object with new naming to store the overall permete solute concentration in fraction
                    to avoid confusion. This new object serves as the feed solute concentration in the loop for 2nd 
                    pass iteration.
                    """
                    self._2p_feed_conc = self.sum_permeate_solute_mass/self.sum_permeate_mass  

                    #Back calculate the 2nd pass tank basis solute mass using the 2nd pass feed solute concentration
                    self._2p_basis_solute_mass = self._2p_basis*self._2p_feed_conc
                    self._2p_starting_basis_solute_mass = self._2p_basis_solute_mass  

                    #Back calculate the 2nd pass tank basis solvent mass using the 2nd pass feed solute concentration
                    self._2p_basis_solvent_mass = self._2p_basis-self._2p_basis_solute_mass
                    self._2p_starting_basis_solvent_mass = self._2p_basis_solvent_mass 

                    #Custom guard
                    if self._1p_process_time == 1:
                        raise BasisTooLow("1st Pass concentrates too soon... Increase basis value slightly.")

                    #Determine the feed processing rate using total tank basis and process time in kg/hr
                    self._1p_feed_processing_rate = self._1p_basis/(self._1p_process_time-1)*60  

                    """
                    Back calculate the retentate mass to be sent to the retentate tank which is the sum of
                    remaining 1P tank basis solute and solvent mass  
                    """
                    self._1p_sum_retentate_mass = self._1p_basis_balance_solute_mass + self._1p_basis_balance_solvent_mass
                    self._1p_sum_retentate_oc = self._1p_basis_balance_solute_mass/self._1p_sum_retentate_mass
                    
                    #────────Re-scale to client proposed capacities────────────────────────────────────────────────────
                    #Determine the target processing rate in-scale with client capacity
                    self._1p_target_processing_rate = self.new_1p_target_processing_rate

                    #Proportionate the total number of module required in 1P in-scale with client capacity
                    self._1p_module_required = math.ceil(self._1p_target_processing_rate/(self._1p_feed_processing_rate/self.module_number))

                    #Determine the number of parallel train needed, always round up to nearest integer
                    self._1p_parallel_train = math.ceil(self._1p_module_required/self.module_number)

                    #Proportionate the retentate and permeate production rate in-scale with client capacity
                    self._1p_target_retentate_solute_rate = self._1p_target_processing_rate*self._1p_basis_balance_solute_mass/self._1p_basis
                    self._1p_target_retentate_solvent_rate = self._1p_target_processing_rate*self._1p_basis_balance_solvent_mass/self._1p_basis
                    self._1p_total_target_retentate_rate = self._1p_target_retentate_solute_rate + self._1p_target_retentate_solvent_rate
                    self._1p_target_permeate_solute_rate =  self._1p_target_processing_rate*self.sum_permeate_solute_mass/self._1p_basis
                    self._1p_target_permeate_solvent_rate = self._1p_target_processing_rate*self.sum_permeate_solvent_mass/self._1p_basis
                    self._1p_total_target_permeate_rate = self._1p_target_permeate_solute_rate+self._1p_target_permeate_solvent_rate
                    
                    break

                #────────If condition is NOT met───────────────────────────────────────────────────────────────────────
                #Update initial feed solute concentration to be remaining tank basis solute concentration in fraction
                self.feed_conc = self._1p_new_conc/100

                #Update initial tank basis masses with remaining tank basis masses
                self._1p_basis_solute_mass = self._1p_basis_balance_solute_mass
                self._1p_basis_solvent_mass = self._1p_basis_balance_solvent_mass

                #Proceed iteration and process time for 1 step
                self._1p_current_iter +=1
                self._1p_process_time +=1
    
            #Check if cancel button is pressed
            if hasattr(self, '_worker') and self._worker._cancelled:
                break

            #────────2nd Pass inner per-minute loop────────────────────────────────────────────────────────────────────
            #Initiate the 2nd pass inner per-minute loop
            while self._2p_current_iter < self.max_iter:
                
                #Check if cancel button is pressed
                if hasattr(self, '_worker') and self._worker._cancelled:
                    break
                
                #────────Storage Variable──────────────────────────────────────────────────────────────────────────────
                self._2p_final_results = []
                self._2p_final_perm_solute_mass = []
                self._2p_final_perm_solvent_mass = []

                #Run the HELPER METHODS for 2nd pass per minute iteration
                self._2p_first_module_calculator()
                self._2p_middle_module_calculator()
                
                #Determine the permeate mass generated from 2nd pass in 1 minute
                self._2p_total_perm_solute_mass = sum(self._2p_final_perm_solute_mass)/60
                self._2p_total_perm_solvent_mass = sum(self._2p_final_perm_solvent_mass)/60
                self._2p_total_perm_mass = self._2p_total_perm_solute_mass + self._2p_total_perm_solvent_mass

                #Back calculate permeate solute concentration from the generated permeate
                self._2p_overall_perm_oc = self._2p_total_perm_solute_mass/self._2p_total_perm_mass*100

                #Update remaining 2nd pass tank basis mass
                self._2p_basis_balance_solute_mass = self._2p_basis_solute_mass-self._2p_total_perm_solute_mass
                self._2p_basis_balance_solvent_mass = self._2p_basis_solvent_mass-self._2p_total_perm_solvent_mass
                self._2p_basis_new_mass = self._2p_basis_balance_solute_mass + self._2p_basis_balance_solvent_mass

                #Guard
                _check_2p_basis(self._2p_basis_new_mass)

                #Update solute concentration of remaining 2nd pass tank basis in wt%
                self._2p_new_conc = self._2p_basis_balance_solute_mass/self._2p_basis_new_mass*100

                
                #2nd PASS PERMEATE TANK BLOCK: Store the permeate solute and solvent masses for current minute
                self._2p_sum_perm_solute_mass.append(self._2p_total_perm_solute_mass)
                self._2p_sum_perm_solvent_mass.append(self._2p_total_perm_solvent_mass)

                #Update result for ModuleDrawing() to initiate paint event
                self.diagram.update_2p_results(self._2p_module_number, self._2p_final_results)

                #Check if remaining tank basis solute concentration has reached 2nd pass target retentate concentration
                #────────If condition is met───────────────────────────────────────────────────────────────────────
                if self._2p_new_conc >= self._2p_conc:

                    #Determine the total permeate mass generated from the whole 2nd pass process
                    self._2p_sum_permeate_solute_mass = sum(self._2p_sum_perm_solute_mass)
                    self._2p_sum_permeate_solvent_mass = sum(self._2p_sum_perm_solvent_mass)
                    self._2p_sum_permeate_mass = self._2p_sum_permeate_solute_mass+self._2p_sum_permeate_solvent_mass

                    #Back calculate solute concentration for the generated total permeate solution in fraction
                    self._2p_sum_permeate_oc = self._2p_sum_permeate_solute_mass/self._2p_sum_permeate_mass

                    #Custom guard
                    if self._2p_process_time ==1:
                        raise BasisTooLow("2nd Pass concentrates too soon... Increase basis value slightly.")

                    #Back calculate 2nd pass feed processing time
                    self._2p_feed_processing_rate = self._2p_basis/(self._2p_process_time+1)*60 

                    #Determine the total retentate mass to be sent to retentate tank and also its solute concentration
                    self._2p_sum_retentate_solute_mass = self._2p_starting_basis_solute_mass - self._2p_sum_permeate_solute_mass
                    self._2p_sum_retentate_solvent_mass = self._2p_starting_basis_solvent_mass - self._2p_sum_permeate_solvent_mass
                    self._2p_sum_retentate_mass = self._2p_sum_retentate_solute_mass + self._2p_sum_retentate_solvent_mass
                    self._2p_sum_retentate_oc = self._2p_sum_retentate_solute_mass/self._2p_sum_retentate_mass
                    
                    """
                    1. Proportionate the number of module required in scale with client's capacity

                    2. At 1st iteration, target processing rate is set to 0 and only will be updated in outer loop

                    3. This is because 2nd pass target processing rate is inherited from 1st pass permeate production
                    rate.
                    """
                    self._2p_module_required = math.ceil(self._2p_target_processing_rate/(self._2p_feed_processing_rate/self._2p_module_number))
                    self._2p_parallel_train = math.ceil(self._2p_module_required/self._2p_module_number)

                    """
                    1. Now here comes the core part of the iteration, which is the inclusive of recycling of 2P
                    retentate back to 1P feed tank.
                    
                    2. To determine the recycling flow rate, we must first get the retentate production rate and also 
                    the retentate solute production rate from 2P based on 2P tank basis
                    """
                    self._2p_retentate_production_rate = self._2p_sum_retentate_mass/self._2p_process_time*60
                    self._2p_retentate_solute_production_rate = self._2p_sum_retentate_solute_mass/self._2p_process_time*60

                    """
                    After that, proportion method is used to scale the retentate production rate to be in-scale with
                    target processing rate
                    """
                    self.recycling_rate = self._2p_retentate_production_rate*(self._2p_target_processing_rate/self._2p_feed_processing_rate)

                    #Here, we can know the total mass flow rate of inlet for 1st pass system
                    self._1p_feed_processing_rate_recycle = self.feed_flow + self.recycling_rate
                    
                    #Similarly, compute the recycling rate for solute component
                    self._1p_feed_solute_recycling_rate = self._2p_retentate_solute_production_rate*(self._2p_target_processing_rate/self._2p_feed_processing_rate)
                    self._1p_feed_solute_processing_rate_recycle = self.solute_flow+self._1p_feed_solute_recycling_rate
                    
                    #Here, we can get the final feed concentration after recycle
                    self._1p_recycle_feed_conc = self._1p_feed_solute_processing_rate_recycle/self._1p_feed_processing_rate_recycle 
                    
                    break
                
                #────────If condition is NOT met───────────────────────────────────────────────────────────────────────
                #Update initial 2nd pass feed solute concentration in fraction
                self._2p_feed_conc = self._2p_new_conc/100

                #Update initial 2nd pass tank basis masses
                self._2p_basis_solute_mass = self._2p_basis_balance_solute_mass
                self._2p_basis_solvent_mass = self._2p_basis_balance_solvent_mass

                #Update iteration variable and process time in minute
                self._2p_current_iter +=1
                self._2p_process_time +=1

            #Check if cancel button is pressed
            if hasattr(self, '_worker') and self._worker._cancelled:
                break
            
            #────────OUTER CONVERGENCE LOOP────────────────────────────────────────────────────────────────────────────
            """
             1. This is the condition check for the outer convergence loop.
             2. It checks for 2 conditions:
                - feed concentration after recycle and initial feed concentration has <0.01 difference
                - 1P permeate production rate and 2P target processing rate has <0.01 difference
            """
            if abs(self._1p_recycle_feed_conc*100-self.feed_conc_check*100) <= 0.01 and abs(self._2p_target_processing_rate - self._1p_total_target_permeate_rate) <= 0.01:
                
                #────────If conditions are met─────────────────────────────────────────────────────────────────────────
                #Compute final result variables
                self.data_name = self.ui.flux_combo.currentText()
                self.avg_final_flux = np.average(self.final_flux)
                self.avg_final_rej = np.average(self.final_rej)
                self._2p_avg_final_flux = np.average(self._2p_final_flux)
                self._2p_avg_final_rej = np.average(self._2p_final_rej)

                #Create a dictionary to store all necessary final variables to be displayed on the table on result tab
                self.final_iterated_results= {
                    "Pressure": ("Operating Pressure","bar",self.pressure_value,self.pressure_value),
                    "Temperature": ("Operating Temperature","°C",self.temp_value,self.temp_value),
                    "LV": ("Linear Velocity","m/s",self.lv,self._2p_lv),
                    "Module": ("Modules Required","unit",round(self._1p_module_required),self._2p_module_number),
                    "Total Module": ("Total Modules Required","unit",round(self._1p_module_required + self._2p_module_number),0),
                    "Parallel Train Required":("Parallel Train Required","unit",self._1p_parallel_train,self._2p_parallel_train),
                    "Processing Time":("Processing Time","minute",self._1p_process_time,self._2p_process_time),
                    "Retentate Conc": ("Retentate Concentration","wt %", round(self._1p_sum_retentate_oc*100,2),round(self._2p_sum_retentate_oc*100,2)),
                    "Permeate Conc": ("Permeate Concentration","wt %",round(self.sum_permeate_oc,2),round(self._2p_sum_permeate_oc*100,2)),
                    "Feed Solute Flow": ("Feed Solute Flow","kg/hr",self.solute_flow,0),
                    "Feed Solvent Flow": ("Feed Solvent Flow","kg/hr",self.solvent_flow,0),
                    "Retentate Solute Flow":("Retentate Solute Flow","kg/hr",round(self._1p_target_retentate_solute_rate,2),round(self._2p_target_retentate_solute_rate,2)),
                    "Retentate Solvent Flow": ("Retentate Solvent Flow","kg/hr",round(self._1p_target_retentate_solvent_rate,2),round(self._2p_target_retentate_solute_rate,2)),
                    "Permeate Solute Flow": ("Permeate Solute Flow","kg/hr",round(self._1p_target_permeate_solute_rate,2),round(self._2p_target_permeate_solute_rate,2)),
                    "Permeate Solvent Flow": ("Permeate Solvent Flow","kg/hr",round(self._1p_target_permeate_solvent_rate,2),round(self._2p_target_permeate_solvent_rate,2)),
                    "Solvent Recovery": ("Solvent Recovery","%",round(self._2p_target_permeate_solvent_rate/self.solvent_flow*100,2),0),
                    "Average Flux": ("Average Flux","LMH",round(self.avg_final_flux,2),round(self._2p_avg_final_flux,2)),
                    "Average Rej": ("Average Rejection","%",round(self.avg_final_rej,2),round(self._2p_avg_final_rej,2)),
                }
                
                #Call the HELPER METHOD from result_tab.py to populate the table on the result tab
                self.result_tab.populate_result_table(self.final_iterated_results)
                
                break

            #Check if cancel button is pressed
            if hasattr(self, '_worker') and self._worker._cancelled:
                break

            try:
                #Initially, '_worker' attribute is assigned to this class.
                if hasattr(self,'_worker'):

                    #Determine the gaps of convergence
                    gap1 = abs(self._1p_recycle_feed_conc*100-self.feed_conc_check*100)
                    gap2 = abs(self._2p_target_processing_rate - self._1p_total_target_permeate_rate)

                    #if it doesn't have a '_start_gap1' attribute, set minimum value for the gap at 0.011
                    if not hasattr(self,'_start_gap1'):
                        self._start_gap1 = max(gap1,0.011)
                        self._start_gap2 = max(gap2,0.011)

                    #Convert the gap values into percentage value to show on progress bar
                    p1 = (self._start_gap1 - gap1)/(self._start_gap1-0.01+1e-9)
                    p2 = (self._start_gap2 - gap2)/(self._start_gap2-0.01+1e-9)
                    pct = int(min(p1,p2)*99)
                    pct = max(0,pct)

                    self._worker.progress.emit(pct)
                    self._worker.status.emit(
                        f"""
                        Iteration               : {current_recycle_iter+1}
                        Feed Concentration Gap  : {gap1:.4f}
                        Permeate Rate Gap       : {gap2:.4f}
                        """
                    )

                if self._worker._cancelled:
                    break

            except AttributeError:
                pass
            
            #────────If outer loop conditions are NOT met──────────────────────────────────────────────────────────────
            """
            In the beginning of convergence, the 2P target processing rate will be different from the 1P permeate
            production rate. Hence, to allow 2P to scale according to client's capacity, the 2P target processing rate
            must inherit from 1P permeate production rate.
            """
            self._2p_target_processing_rate = self._1p_total_target_permeate_rate    

            #After 2P target processing rate is updated, its corresponding recycling flow rates will be updated too
            self.new_recycling_rate = self._2p_retentate_production_rate*(self._2p_target_processing_rate/self._2p_feed_processing_rate)
            self.new_solute_recycling_rate = self._2p_retentate_solute_production_rate*(self._2p_target_processing_rate/self._2p_feed_processing_rate)
            
            self.new_1p_feed_processing_rate_recycle = self.feed_flow + self.new_recycling_rate
            self.new_1p_feed_solute_processing_rate_recycle = self.solute_flow + self.new_solute_recycling_rate
            
            #Update the new feed concentration after recycle in fraction
            self.new_1p_recycle_feed_conc = self.new_1p_feed_solute_processing_rate_recycle/self.new_1p_feed_processing_rate_recycle 

            #Compute the new permeate mass flow rate in-scale with client's capacity
            self.new_1p_target_permeate_solute_rate = self.new_1p_feed_processing_rate_recycle*self.sum_permeate_solute_mass/self._1p_basis
            self.new_1p_target_permeate_solvent_rate = self.new_1p_feed_processing_rate_recycle*self.sum_permeate_solvent_mass/self._1p_basis
            self.new_1p_total_target_permeate_rate = self.new_1p_target_permeate_solute_rate+self.new_1p_target_permeate_solvent_rate

            #Update the initial 1st pass feed solute concentration for next convergence iteration
            self.feed_conc = self.new_1p_recycle_feed_conc
            
            #Determine the target 2P retentate and permeate mass flow rates in scale with client's capacity
            self._2p_target_permeate_solute_rate = self.new_1p_total_target_permeate_rate*self._2p_sum_permeate_solute_mass/self._2p_basis
            self._2p_target_permeate_solvent_rate = self.new_1p_total_target_permeate_rate*self._2p_sum_permeate_solvent_mass/self._2p_basis
            self._2p_total_target_permeate_rate = self._2p_target_permeate_solute_rate + self._2p_target_permeate_solvent_rate
            self._2p_target_retentate_solute_rate = self.new_1p_total_target_permeate_rate*self._2p_sum_retentate_solute_mass/self._2p_basis
            self._2p_target_retentate_solvent_rate = self.new_1p_total_target_permeate_rate*self._2p_sum_retentate_solvent_mass/self._2p_basis
            self._2p_total_target_retentate_rate = self._2p_target_retentate_solute_rate + self._2p_target_retentate_solvent_rate
            
            current_recycle_iter +=1
            
    #─────4.6: HELPER METHOD #4────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper function converts text box and drop widget inputs created from user_input.py into string object.
    These string object can then be converted to float using the np.float() method later on for calculation.
    """      
    def float_toggle(self,widget: QLineEdit | QComboBox,blank = "")-> str:  
            try:
                "This condition check if the input widget is a QComboBox instance"
                if isinstance(widget,QComboBox):
                    
                    "If widget is a drop down, extract the current text appearing on the drop down and trim it"
                    return widget.currentText().strip()
                else:

                    "If widget is a text box, extract the current text on the text box and trim it"
                    return widget.text().strip()
            except Exception:

                "Any exception will return blank value instead of direct app crash"
                return blank 

    #─────4.7: HELPER METHOD #5────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method performs mass balance calculations over 1st pass first membrane module using user defined flux, 
    rejection, temperature and pressure input. All parameters at the inlet, permeate outlet and retentate outlet 
    streams will then be determined. 
    """    
    def _1p_first_module_calculator(self):
             
        #─────INLET STREAM─────────────────────────────────────────────────────────────────────────────────────────────
         #Back calculate volumetric flowrate (L/h) using user defined linear velocity and module size
         self.vol_flow = 1000*3600*self.lv*self.module_spec_df.iloc[6]  

         #Determine feed binary mixture density using ideal mixing rule
         self.feed_solute_den = np.interp(self.temp_value,self.solute_den_df.iloc[:,0],self.solute_den_df.iloc[:,1])
         self.feed_solvent_den = np.interp(self.temp_value,self.solvent_den_df.iloc[:,0],self.solvent_den_df.iloc[:,1])
         self.feed_mixture_den = 1/((self.feed_conc/self.feed_solute_den)+((1-self.feed_conc)/self.feed_solvent_den))
        
         #Back calculate mass flow rate (kg/hr) using volumetric flow and mixture density
         self.total_mass_flow = self.vol_flow*self.feed_mixture_den/1000
         self.solute_mass_flow = self.total_mass_flow*self.feed_conc
         self.solvent_mass_flow = self.total_mass_flow - self.solute_mass_flow

        #─────FLUX AND REJECTION INTERPOLATION─────────────────────────────────────────────────────────────────────────
         #Calculate outlet pressure at retentate stream based on pressure drop data in module size data
         self.outlet_pressure = float(self.pressure_value) - float(self.module_spec_df.iloc[7])

         """
         Setup data grid for imported flux & rejection data frame from user input using HELPER FUNCTION #5 for 
         double linear interpolation later on
         """
         self.flux_grid = grid_2d(self.flux_final_df)
         self.rejection_grid = grid_2d(self.rej_final_df)
  
         _check_grid(self.feed_conc*100,self.pressure_value,self.flux_final_df)
         _check_grid(self.feed_conc*100,self.outlet_pressure,self.flux_final_df)

         #Determine average flux between membrane inlet and outlet streams using pre-defined flux grid
         self.inlet_flux = float(self.flux_grid([[self.feed_conc*100,float(self.pressure_value)]])[0])         
         self.reject_flux = float(self.flux_grid([[self.feed_conc*100,float(self.outlet_pressure)]])[0]) 
         self.avg_flux = np.average([self.inlet_flux,self.reject_flux])

         #Determine average rejection between membrane inlet and outlet streams using pre-defined rejection grid
         self.inlet_rej = float(self.rejection_grid([[self.feed_conc*100,float(self.pressure_value)]])[0])
         self.reject_rej = float(self.rejection_grid([[self.feed_conc*100,float(self.outlet_pressure)]])[0])
         self.avg_rej = np.average([self.inlet_rej,self.reject_rej])

        #─────PERMEATE STREAM──────────────────────────────────────────────────────────────────────────────────────────
         #Back calculate permeate solute concentration in % using average rejection and feed solute concentration
         self.permeate_oc = -1*(self.feed_conc*100)*((self.avg_rej/100)-1)  

         #Determine permeate mixture density using ideal mixing rule
         self.permeate_mixture_den = 1/(((self.permeate_oc/100)/self.feed_solute_den)+((1-(self.permeate_oc/100))/self.feed_solvent_den))

         #Back calculate permeate mass flow rates in kg/hr using mixture density, average flux and module size
         self.permeate_mass_flow = self.permeate_mixture_den*self.avg_flux*self.module_spec_df.iloc[4]/1000  
         self.permeate_solute_flow = self.permeate_mass_flow*self.permeate_oc/100
         self.permeate_solvent_flow = self.permeate_mass_flow - self.permeate_solute_flow

         #Back calculate permeate volumetric flowrate in L/h
         self.permeate_vol_flow = self.permeate_mass_flow/self.permeate_mixture_den*1000

        #─────RETENTATE STREAM─────────────────────────────────────────────────────────────────────────────────────────
         #Determine retentate mass flow rates using mass balance rule
         self.retentate_solute_flow = self.solute_mass_flow - self.permeate_solute_flow
         self.retentate_solvent_flow = self.solvent_mass_flow - self.permeate_solvent_flow
         self.retentate_mass_flow = self.retentate_solute_flow + self.retentate_solvent_flow
  
         #Back calculate retentate solute concentration in wt%
         self.retentate_oc = self.retentate_solute_flow/self.retentate_mass_flow*100

         #Determine retentate mixture density using ideal mixing rule
         self.retentate_mixture_den = 1/(((self.retentate_oc/100)/self.feed_solute_den)+((1-(self.retentate_oc/100))/self.feed_solvent_den))

         #Back calculate retentate stream volumetric flow in L/h and also linear velocity
         self.rententate_vol_flow = self.retentate_mass_flow/self.retentate_mixture_den*1000
         self.retentate_lv = self.rententate_vol_flow/1000/3600/self.module_spec_df.iloc[6]

        #─────UPDATE RESULTS IN DICTIONARY─────────────────────────────────────────────────────────────────────────────
         #Update all necessary resulting variables in form of python dictionary for later use for the 1st module
         self.final_results.append({
            "module_no"              : 1,
            "inlet_total_mass_flow"  : round(float(self.total_mass_flow), 2),
            "inlet_total_vol_flow"   : round(float(self.vol_flow), 2),
            "inlet_solute_flow"      : round(float(self.solute_mass_flow), 2),
            "inlet_solvent_flow"     : round(float(self.solvent_mass_flow), 2),
            "ret_total_mass_flow"    : round(float(self.retentate_mass_flow), 2),
            "ret_total_vol_flow"     : round(float(self.rententate_vol_flow), 2),
            "ret_solute_flow"        : round(float(self.retentate_solute_flow), 2),
            "ret_solvent_flow"       : round(float(self.retentate_solvent_flow), 2),
            "perm_total_mass_flow"   : round(float(self.permeate_mass_flow), 2),
            "perm_total_vol_flow"    : round(float(self.permeate_vol_flow), 2),
            "perm_solute_flow"       : round(float(self.permeate_solute_flow), 2),
            "perm_solvent_flow"      : round(float(self.permeate_solvent_flow), 2),
            "inlet_pressure"         : round(float(self.pressure_value), 2),
            "inlet_lv"               : round(float(self.lv), 2),
            "inlet_density"          : round(float(self.feed_mixture_den), 2),
            "inlet_conc"             : round(float(self.feed_conc * 100), 2),
            "inlet_temp"             : round(float(self.temp_value), 2),
            "ret_pressure"           : round(float(self.outlet_pressure), 2),
            "ret_lv"                 : round(float(self.retentate_lv), 2),
            "ret_density"            : round(float(self.retentate_mixture_den), 2),
            "ret_conc"               : round(float(self.retentate_oc), 2),
            "perm_density"           : round(float(self.permeate_mixture_den), 2),
            "perm_conc"              : round(float(self.permeate_oc), 2),
            "avg_flux"               : round(float(self.avg_flux), 2),
            "avg_rej"                : round(float(self.avg_rej), 2),
        })
        
         #Update the permeate solute and solvent flow for 1st module in empty lists created earlier on
         self.final_perm_solute_mass.append(float(self.permeate_solute_flow))
         self.final_perm_solvent_mass.append(float(self.permeate_solvent_flow))

         #Update the average flux and rejection for 1st module in empty lists created earlier on
         self.final_flux.append(float(self.avg_flux))
         self.final_rej.append(float(self.avg_rej))

    #─────4.8: HELPER METHOD #6────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method performs mass balance calculations over 1st pass membrane modules starts from 2nd module until
    the last module in series based on user input number of module. Since this method requires more than one module 
    required, streams variables for each modules will be determined in loop where the outlet retentate stream will
    become the next module inlet stream. The calculation methods for all the variables are similar to the ones in
    HELPER METHOD #5, and all variables/objects are named to be user friendly.
    """
    def _1p_middle_module_calculator(self):
    
       """
       Define iteration number. Since 1st module is already determined in HELPER METHOD #5, so the iteration starts
       from 2 until user defined module number. We add 1 at module_number in this case as range() does not include the 
       last number such that range(2,10) will only return 2,3,...,8,9.
       """
       self.iteration_no = range(2,self.module_number+1) 

       #─────FEED STREAM VARIABLES FOR 2ND MODULE──────────────────────────────────────────────────────────────────────
       #Define feed stream variables for 2nd module to start the loop. These values will change as the loop progress
       self.init_oc = float(self.retentate_oc)                  #initial feed solute concentration in wt%
       self.init_solute_flow = self.retentate_solute_flow       #initial solute mass flow in kg/hr
       self.init_solvent_flow = self.retentate_solvent_flow     #initial solvent mass flow in kg/hr
       self.init_total_mass_flow = self.retentate_mass_flow     #initial total mass flow in kg/hr
       self.init_lv = self.retentate_lv                         #initial linear velocity in m/s
       self.init_mixture_den = self.retentate_mixture_den       #initial mixture density in kg/m3
       self.init_vol_flow = self.rententate_vol_flow            #initial volumetric flow in L/h
       self.init_pressure = self.outlet_pressure                #initial operating pressure in bar

       #─────ITERATION FOR EACH MODULE─────────────────────────────────────────────────────────────────────────────────
       for n in self.iteration_no:

        #────PLUX AND REJECTION INTERPOLATION──────────────────────────────────────────────────────────────────────────
        #Retentate stream pressure after pressure drop
        self.n_outlet_pressure = self.init_pressure - float(self.module_spec_df.iloc[7])

        _check_grid(self.init_oc,self.init_pressure,self.flux_final_df)
        _check_grid(self.init_oc,self.n_outlet_pressure,self.flux_final_df)

        #Average flux for each module
        self.n_inlet_flux = float(self.flux_grid([[self.init_oc,float(self.init_pressure)]])[0]) #--> returns np.ndarray
        self.n_reject_flux = float(self.flux_grid([[self.init_oc,float(self.n_outlet_pressure)]])[0]) #--> returns np.ndarray
        self.n_avg_flux = np.average([self.n_inlet_flux,self.n_reject_flux])

        #Average rejection for each module"
        self.n_inlet_rej = float(self.rejection_grid([[self.init_oc,float(self.init_pressure)]])[0])
        self.n_reject_rej = float(self.rejection_grid([[self.init_oc,float(self.n_outlet_pressure)]])[0])
        self.n_avg_rej = np.average([self.n_inlet_rej,self.n_reject_rej])
        
       #────PERMEATE STREAM────────────────────────────────────────────────────────────────────────────────────────────
        #Permeate stream solute concentration for each module
        self.n_permeate_oc =  -1*(self.init_oc)*((self.n_avg_rej/100)-1)

        #Permeate stream mixture density for each module
        self.n_permeate_mixture_den = 1/(((self.n_permeate_oc/100)/self.feed_solute_den)+((1-(self.n_permeate_oc/100))/self.feed_solvent_den))

        # "Permeate stream mass and volumetric flowrates for each module"
        self.n_permeate_mass_flow = self.n_avg_flux*self.n_permeate_mixture_den*self.module_spec_df.iloc[4]/1000
        self.n_permeate_solute_flow = self.n_permeate_mass_flow*self.n_permeate_oc/100
        self.n_permeate_solvent_flow = self.n_permeate_mass_flow - self.n_permeate_solute_flow
        self.n_permeate_vol_flow = self.n_permeate_mass_flow/self.n_permeate_mixture_den*1000
        
        #────RETENTATE  STREAM─────────────────────────────────────────────────────────────────────────────────────────
        # "Retentate stream mass flow rates"
        self.n_retentate_solute_flow = self.init_solute_flow - self.n_permeate_solute_flow
        self.n_retentate_solvent_flow = self.init_solvent_flow - self.n_permeate_solvent_flow
        self.n_retentate_mass_flow = self.n_retentate_solute_flow + self.n_retentate_solvent_flow

        # "Retentate stream solute concentration"
        self.n_retentate_oc = self.n_retentate_solute_flow/self.n_retentate_mass_flow*100

        # "Retentate stream mixture density"
        self.n_retentate_mixture_den = 1/(((self.n_retentate_oc/100)/self.feed_solute_den)+((1-(self.n_retentate_oc/100))/self.feed_solvent_den))

        # "Retentate stream volumetric flow rate"
        self.n_retentate_vol_flow = self.n_retentate_mass_flow/self.n_permeate_mixture_den*1000

        # "Retentate stream linear velocity"
        self.n_retentate_lv = self.n_retentate_vol_flow/1000/3600/self.module_spec_df.iloc[6]

        #─────UPDATE RESULTS IN DICTIONARY─────────────────────────────────────────────────────────────────────────────
        # "Append the stream variables for each module to the final_result dictionary"
        self.final_results.append({
            "module_no"             : n,  
            "inlet_total_mass_flow" : round(float(self.init_total_mass_flow), 2),
            "inlet_total_vol_flow"  : round(float(self.init_vol_flow), 2),
            "inlet_solute_flow"     : round(float(self.init_solute_flow), 2),
            "inlet_solvent_flow"    : round(float(self.init_solvent_flow), 2),
            "ret_total_mass_flow"   : round(float(self.n_retentate_mass_flow), 2),
            "ret_total_vol_flow"    : round(float(self.n_retentate_vol_flow), 2),
            "ret_solute_flow"       : round(float(self.n_retentate_solute_flow), 2),
            "ret_solvent_flow"      : round(float(self.n_retentate_solvent_flow), 2),
            "perm_total_mass_flow"  : round(float(self.n_permeate_mass_flow), 2),
            "perm_total_vol_flow"   : round(float(self.n_permeate_vol_flow), 2),
            "perm_solute_flow"      : round(float(self.n_permeate_solute_flow), 2),
            "perm_solvent_flow"     : round(float(self.n_permeate_solvent_flow), 2),
            "inlet_pressure"        : round(float(self.init_pressure), 2),
            "inlet_lv"              : round(float(self.init_lv), 2),
            "inlet_density"         : round(float(self.init_mixture_den), 2),
            "inlet_conc"            : round(float(self.init_oc), 2),
            "inlet_temp"            : round(float(self.temp_value), 2),
            "ret_pressure"          : round(float(self.n_outlet_pressure), 2),
            "ret_lv"                : round(float(self.n_retentate_lv), 2),
            "ret_density"           : round(float(self.n_retentate_mixture_den), 2),
            "ret_conc"              : round(float(self.n_retentate_oc), 2),
            "perm_density"          : round(float(self.n_permeate_mixture_den), 2),
            "perm_conc"             : round(float(self.n_permeate_oc), 2),
            "avg_flux"              : round(float(self.n_avg_flux), 2),
            "avg_rej"               : round(float(self.n_avg_rej), 2),
        })

        # "Update final permeate solute and solvent mass flow into list"
        self.final_perm_solute_mass.append(float(self.n_permeate_solute_flow))
        self.final_perm_solvent_mass.append(float(self.n_permeate_solvent_flow))

        # "Update final flux and rejection values into list"
        self.final_flux.append(float(self.n_avg_flux))
        self.final_rej.append(float(self.n_avg_rej))

        #─────UPDATE INITIAL VARIABLES FOR NEXT MODULE─────────────────────────────────────────────────────────────────
        self.init_oc = float(self.n_retentate_oc)
        self.init_solute_flow = self.n_retentate_solute_flow
        self.init_solvent_flow = self.n_retentate_solvent_flow
        self.init_total_mass_flow = self.n_retentate_mass_flow
        self.init_lv = self.n_retentate_lv
        self.init_mixture_den = self.n_retentate_mixture_den
        self.init_vol_flow = self.n_retentate_vol_flow
        self.init_pressure = self.n_outlet_pressure

    #─────4.9: HELPER METHOD #7────────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method serves the same purpose as HELPER METHOD #5, the only key difference is the naming where a '_2p_'
    is added in front to indicate that the variables are for 2nd pass. Annotation will not be found in this method.
    """
    def _2p_first_module_calculator(self):  
       
       #─────FLUX AND REJECTION INTERPOLATION──────────────────────────────────────────────────────────────────────────
        self._2p_vol_flow = 1000*3600*self._2p_lv*self._2p_module_spec_df.iloc[6] 
        
        self._2p_feed_solute_den = np.interp(self.temp_value,self.solute_den_df.iloc[:,0],self.solute_den_df.iloc[:,1])
        self._2p_feed_solvent_den = np.interp(self.temp_value,self.solvent_den_df.iloc[:,0],self.solvent_den_df.iloc[:,1])
        self._2p_feed_mixture_den = 1/((self._2p_feed_conc/self.feed_solute_den)+((1-self._2p_feed_conc)/self.feed_solvent_den))
        
        self._2p_total_mass_flow = self._2p_vol_flow*self._2p_feed_mixture_den/1000
        self._2p_solute_mass_flow = self._2p_total_mass_flow*self._2p_feed_conc
        self._2p_solvent_mass_flow = self._2p_total_mass_flow - self._2p_solute_mass_flow

        self._2p_outlet_pressure = float(self.pressure_value) - float(self._2p_module_spec_df.iloc[7])

        self._2p_flux_grid = grid_2d(self.flux_final_df)
        self._2p_rejection_grid = grid_2d(self.rej_final_df)

        _check_grid(self._2p_feed_conc,self.pressure_value,self.flux_final_df)
        _check_grid(self._2p_feed_conc,self._2p_outlet_pressure,self.flux_final_df)

        self._2p_inlet_flux = float(self._2p_flux_grid([[self._2p_feed_conc*100,float(self.pressure_value)]])[0])
        self._2p_reject_flux = float(self._2p_flux_grid([[self._2p_feed_conc*100,float(self._2p_outlet_pressure)]])[0])
        self._2p_avg_flux = np.average([self._2p_inlet_flux,self._2p_reject_flux])

        self._2p_inlet_rej = float(self._2p_rejection_grid([[self._2p_feed_conc*100,float(self.pressure_value)]])[0])
        self._2p_reject_rej = float(self._2p_rejection_grid([[self._2p_feed_conc*100,float(self._2p_outlet_pressure)]])[0])
        self._2p_avg_rej = np.average([self._2p_inlet_rej,self._2p_reject_rej])

        #─────PERMEATE STREAM──────────────────────────────────────────────────────────────────────────────────────────
        self._2p_permeate_oc = -1*(self._2p_feed_conc*100)*((self._2p_avg_rej/100)-1)  #--->in %

        self._2p_permeate_mixture_den = 1/(((self._2p_permeate_oc/100)/self._2p_feed_solute_den)+((1-(self._2p_permeate_oc/100))/self._2p_feed_solvent_den))
    
        self._2p_permeate_mass_flow = self._2p_permeate_mixture_den*self._2p_avg_flux*self._2p_module_spec_df.iloc[4]/1000  
        self._2p_permeate_solute_flow = self._2p_permeate_mass_flow*self._2p_permeate_oc/100
        self._2p_permeate_solvent_flow = self._2p_permeate_mass_flow - self._2p_permeate_solute_flow

        self._2p_permeate_vol_flow = self._2p_permeate_mass_flow/self._2p_permeate_mixture_den*1000  #-->L/h
        
        #─────RETENTATE STREAM─────────────────────────────────────────────────────────────────────────────────────────
        self._2p_retentate_solute_flow = self._2p_solute_mass_flow - self._2p_permeate_solute_flow
        self._2p_retentate_solvent_flow = self._2p_solvent_mass_flow - self._2p_permeate_solvent_flow
        self._2p_retentate_mass_flow = self._2p_retentate_solute_flow + self._2p_retentate_solvent_flow

        self._2p_retentate_oc = self._2p_retentate_solute_flow/self._2p_retentate_mass_flow*100 #-->in %

        self._2p_retentate_mixture_den = 1/(((self._2p_retentate_oc/100)/self._2p_feed_solute_den)+((1-(self._2p_retentate_oc/100))/self._2p_feed_solvent_den))

        self._2p_rententate_vol_flow = self._2p_retentate_mass_flow/self._2p_retentate_mixture_den*1000
        self._2p_retentate_lv = self._2p_rententate_vol_flow/1000/3600/self._2p_module_spec_df.iloc[6]

        #─────UPDATE RESULTS IN DICTIONARY & LIST──────────────────────────────────────────────────────────────────────
        self._2p_final_results.append({
            "module_no"             : 1,
            "inlet_total_mass_flow" : round(float(self._2p_total_mass_flow), 2),
            "inlet_total_vol_flow"  : round(float(self._2p_vol_flow), 2),
            "inlet_solute_flow"     : round(float(self._2p_solute_mass_flow), 2),
            "inlet_solvent_flow"    : round(float(self._2p_solvent_mass_flow), 2),
            "ret_total_mass_flow"   : round(float(self._2p_retentate_mass_flow), 2),
            "ret_total_vol_flow"    : round(float(self._2p_rententate_vol_flow), 2),
            "ret_solute_flow"       : round(float(self._2p_retentate_solute_flow), 2),
            "ret_solvent_flow"      : round(float(self._2p_retentate_solvent_flow), 2),
            "perm_total_mass_flow"  : round(float(self._2p_permeate_mass_flow), 2),
            "perm_total_vol_flow"   : round(float(self._2p_permeate_vol_flow), 2),
            "perm_solute_flow"      : round(float(self._2p_permeate_solute_flow), 2),
            "perm_solvent_flow"     : round(float(self._2p_permeate_solvent_flow), 2),
            "inlet_pressure"        : round(float(self.pressure_value), 2),
            "inlet_lv"              : round(float(self._2p_lv), 2),
            "inlet_density"         : round(float(self._2p_feed_mixture_den), 2),
            "inlet_conc"            : round(float(self._2p_feed_conc * 100), 2),
            "inlet_temp"            : round(float(self.temp_value), 2),
            "ret_pressure"          : round(float(self._2p_outlet_pressure), 2),
            "ret_lv"                : round(float(self._2p_retentate_lv), 2),
            "ret_density"           : round(float(self._2p_retentate_mixture_den), 2),
            "ret_conc"              : round(float(self._2p_retentate_oc), 2),
            "perm_density"          : round(float(self._2p_permeate_mixture_den), 2),
            "perm_conc"             : round(float(self._2p_permeate_oc), 2),
            "avg_flux"              : round(float(self._2p_avg_flux), 2),
            "avg_rej"               : round(float(self._2p_avg_rej), 2),
        })
        
        self._2p_final_perm_solute_mass.append(float(self._2p_permeate_solute_flow))
        self._2p_final_perm_solvent_mass.append(float(self._2p_permeate_solvent_flow)) 
        self._2p_final_flux.append(float(self._2p_avg_flux))
        self._2p_final_rej.append(float(self._2p_avg_rej)) 
     
    #─────4.10: HELPER METHOD #8───────────────────────────────────────────────────────────────────────────────────────
    """
    This helper method serves the same purpose as HELPER METHOD #6, the only key difference is the naming where a 
    '_2p_' is added in front to indicate that the variables are for 2nd pass. Annotation will not be found in this 
    method.
    """ 
    def _2p_middle_module_calculator(self):
       
       self._2p_iteration_no = range(2,self._2p_module_number+1)

       #─────FEED STREAM VARIABLES FOR 2ND MODULE──────────────────────────────────────────────────────────────────────
       self._2p_init_oc = float(self._2p_retentate_oc) #---> in %
       self._2p_init_solute_flow = self._2p_retentate_solute_flow
       self._2p_init_solvent_flow = self._2p_retentate_solvent_flow
       self._2p_init_total_mass_flow = self._2p_retentate_mass_flow
       self._2p_init_lv = self._2p_retentate_lv
       self._2p_init_mixture_den = self._2p_retentate_mixture_den
       self._2p_init_vol_flow = self._2p_rententate_vol_flow
       self._2p_init_pressure = self._2p_outlet_pressure

       #─────ITERATION FOR EACH MODULE─────────────────────────────────────────────────────────────────────────────────
       for n in self._2p_iteration_no:

        #────FLUX AND REJECTION INTERPOLATION──────────────────────────────────────────────────────────────────────────
        self._2p_n_outlet_pressure = self._2p_init_pressure - float(self._2p_module_spec_df.iloc[7])

        _check_grid(self._2p_init_oc,self._2p_init_pressure,self.flux_final_df)
        _check_grid(self._2p_init_oc,self._2p_n_outlet_pressure,self.flux_final_df)

        self._2p_n_inlet_flux = float(self._2p_flux_grid([[self._2p_init_oc,float(self._2p_init_pressure)]])[0])
        self._2p_n_reject_flux = float(self._2p_flux_grid([[self._2p_init_oc,float(self._2p_n_outlet_pressure)]])[0])
        self._2p_n_avg_flux = np.average([self._2p_n_inlet_flux,self._2p_n_reject_flux])

        self._2p_n_inlet_rej = float(self._2p_rejection_grid([[self._2p_init_oc,float(self._2p_init_pressure)]])[0])
        self._2p_n_reject_rej = float(self._2p_rejection_grid([[self._2p_init_oc,float(self._2p_n_outlet_pressure)]])[0])
        self._2p_n_avg_rej = np.average([self._2p_n_inlet_rej,self._2p_n_reject_rej])
        
        #─────PERMEATE STREAM──────────────────────────────────────────────────────────────────────────────────────────
        self._2p_n_permeate_oc =  -1*(self._2p_init_oc)*((self._2p_n_avg_rej/100)-1)

        self._2p_n_permeate_mixture_den = 1/(((self._2p_n_permeate_oc/100)/self._2p_feed_solute_den)+((1-(self._2p_n_permeate_oc/100))/self._2p_feed_solvent_den))

        self._2p_n_permeate_mass_flow = self._2p_n_avg_flux*self._2p_n_permeate_mixture_den*self._2p_module_spec_df.iloc[4]/1000
        self._2p_n_permeate_solute_flow = self._2p_n_permeate_mass_flow*self._2p_n_permeate_oc/100
        self._2p_n_permeate_solvent_flow = self._2p_n_permeate_mass_flow - self._2p_n_permeate_solute_flow
        self._2p_n_permeate_vol_flow = self._2p_n_permeate_mass_flow/self._2p_n_permeate_mixture_den*1000
        
        #─────RETENTATE STREAM─────────────────────────────────────────────────────────────────────────────────────────
        self._2p_n_retentate_solute_flow = self._2p_init_solute_flow - self._2p_n_permeate_solute_flow
        self._2p_n_retentate_solvent_flow = self._2p_init_solvent_flow - self._2p_n_permeate_solvent_flow
        self._2p_n_retentate_mass_flow = self._2p_n_retentate_solute_flow + self._2p_n_retentate_solvent_flow

        self._2p_n_retentate_oc = self._2p_n_retentate_solute_flow/self._2p_n_retentate_mass_flow*100

        self._2p_n_retentate_mixture_den = 1/(((self._2p_n_retentate_oc/100)/self._2p_feed_solute_den)+((1-(self._2p_n_retentate_oc/100))/self._2p_feed_solvent_den))

        self._2p_n_retentate_vol_flow = self._2p_n_retentate_mass_flow/self._2p_n_permeate_mixture_den*1000

        self._2p_n_retentate_lv = self._2p_n_retentate_vol_flow/1000/3600/self._2p_module_spec_df.iloc[6]

        #─────UPDATE RESULTS IN DICTIONARY AND LIST────────────────────────────────────────────────────────────────────
        self._2p_final_results.append({
            "module_no"             : n,
            "inlet_total_mass_flow" : round(float(self._2p_init_total_mass_flow), 2),
            "inlet_total_vol_flow"  : round(float(self._2p_init_vol_flow), 2),
            "inlet_solute_flow"     : round(float(self._2p_init_solute_flow), 2),
            "inlet_solvent_flow"    : round(float(self._2p_init_solvent_flow), 2),
            "ret_total_mass_flow"   : round(float(self._2p_n_retentate_mass_flow), 2),
            "ret_total_vol_flow"    : round(float(self._2p_n_retentate_vol_flow), 2),
            "ret_solute_flow"       : round(float(self._2p_n_retentate_solute_flow), 2),
            "ret_solvent_flow"      : round(float(self._2p_n_retentate_solvent_flow), 2),
            "perm_total_mass_flow"  : round(float(self._2p_n_permeate_mass_flow), 2),
            "perm_total_vol_flow"   : round(float(self._2p_n_permeate_vol_flow), 2),
            "perm_solute_flow"      : round(float(self._2p_n_permeate_solute_flow), 2),
            "perm_solvent_flow"     : round(float(self._2p_n_permeate_solvent_flow), 2),
            "inlet_pressure"        : round(float(self._2p_init_pressure), 2),
            "inlet_lv"              : round(float(self._2p_init_lv), 2),
            "inlet_density"         : round(float(self._2p_init_mixture_den), 2),
            "inlet_conc"            : round(float(self._2p_init_oc), 2),
            "inlet_temp"            : round(float(self.temp_value), 2),
            "ret_pressure"          : round(float(self._2p_n_outlet_pressure), 2),
            "ret_lv"                : round(float(self._2p_n_retentate_lv), 2),
            "ret_density"           : round(float(self._2p_n_retentate_mixture_den), 2),
            "ret_conc"              : round(float(self._2p_n_retentate_oc), 2),
            "perm_density"          : round(float(self._2p_n_permeate_mixture_den), 2),
            "perm_conc"             : round(float(self._2p_n_permeate_oc), 2),
            "avg_flux"              : round(float(self._2p_n_avg_flux), 2),
            "avg_rej"               : round(float(self._2p_n_avg_rej), 2),
        })
        
        self._2p_final_perm_solute_mass.append(float(self._2p_n_permeate_solute_flow))
        self._2p_final_perm_solvent_mass.append(float(self._2p_n_permeate_solvent_flow))

        self._2p_final_flux.append(float(self._2p_n_avg_flux))
        self._2p_final_rej.append(float(self._2p_n_avg_rej))

        #─────UPDATE INITIAL VARIABLES FOR NEXT MODULE─────────────────────────────────────────────────────────────────
        self._2p_init_oc = float(self._2p_n_retentate_oc)
        self._2p_init_solute_flow = self._2p_n_retentate_solute_flow
        self._2p_init_solvent_flow = self._2p_n_retentate_solvent_flow
        self._2p_init_total_mass_flow = self._2p_n_retentate_mass_flow
        self._2p_init_lv = self._2p_n_retentate_lv
        self._2p_init_mixture_den = self._2p_n_retentate_mixture_den
        self._2p_init_vol_flow = self._2p_n_retentate_vol_flow
        self._2p_init_pressure = self._2p_n_outlet_pressure



       
           