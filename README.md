# 🧪 Batch Membrane Module Calculator (PyQt6)

> Desktop application to determine the required number of membrane modules in series for an industrial-scale two-pass batch separation process.

---

## 🔍 Overview
This application provides a structured and efficient way to estimate membrane module requirements for a two-pass batch membrane separation system.

It is designed for process engineers handling:
- Industrial-scale membrane separations  
- Batch process calculations  
- Multi-stage system design  

The tool integrates rigorous engineering calculations with an intuitive GUI built using PyQt6.

---

## 🎯 Problem Statement
In membrane-based separation processes, determining the number of modules in series is critical for:
- Achieving target separation performance based on customer's capacity requirement  
- Avoiding overdesign (excess cost) or underperformance  

Manual calculation is:
- Time-consuming  
- Error-prone  
- Difficult to iterate  

This application automates the calculation and provides immediate results.

---

## ⚙️ Features
This application contains 5 different tabs on startup

### 1.User Input tab
> Allow user to select and key in core parameters to be used in the iteration:
- **Solute Selection**  
    Retrieves liquid density (kg/m³) from `solute.xlsx`.  
    Users can update or extend the dataset.

- **Solvent Selection**  
    Retrieves liquid density (kg/m³) from `solvent.xlsx`.
    Users can update or extend the dataset.

- **Operation Mode**  
    Batch and continuous modes available (current release supports batch mode only).

- **Operating Parameters**  
    Pressure, temperature, flow rate, number of modules, etc.

- **Module Size**  
    Select membrane module diameter configuration (mainly to determine pressure drop across module or linear velocity)

- **Recycle from 2nd Pass**  
    Enables iterative convergence logic between passes.(current release supports recycling convergence only)

### 2. Module Number Calculator
- Initiates calculation via **“Calculate”** button  
- Displays simplified process flow during execution  
- Progress panel shows iteration status in real-time  

---

### 3. Final Results
- Displays computed results in tabular format  
- Supports export to Excel  

---

### 4. Solute Density Preview  
### 5. Solvent Density Preview  
- Displays temperature-dependent density tables for selected components  

---

## 🧮 Methodology (Engineering Logic)
The application is based on:

- Mass balance across each membrabne module based on selected flux and rejection dataset.
- Simulate the iterative pattern of a batch separation process calculation where the iteration will stop when target retentate concentrations are reached.
- Sequential evaluation across two passes where 1st pass will iterate to achieve target final retentate concentration before moving to 2nd pass for the same iteration pattern.
- On achieving target retentate concentration on 2nd pass, remaining retentate will be recycled back to 1st pass. 1st pass feed composition will change due to the addition of recycled solution. Iteration will restart based on the newly computed 1st pass feed concentration until convergence of less than 0.1 is met.

## 🧮 Methodology (Engineering Logic)

The application is based on:

- Mass balance across each membrane module using flux and rejection data  
- Iterative simulation of batch separation behavior  
- Sequential evaluation across two passes  
- Recycle loop from second pass to first pass  

### Calculation Workflow

1. Define feed conditions, membrane performance data and tank basis
2. Perform iterative calculation for **1st pass** until target retentate concentration is achieved  
3. Use permeate from 1st pass as feed for **2nd pass**, and repeat iteration
3. Re-scale flow rate values to client's capacity using proportional method  
4. Recycle 2nd pass retentate back to 1st pass  
5. Update feed composition, 1st pass permeate flow and restart iteration  
6. Repeat until convergence criteria are met  
7. Output final results  

---

### 🔁 Convergence Criteria

Iteration stops when:

- Difference between:
  - Initial feed solute concentration  
  - Updated feed concentration after recycle  
  is **< 0.01%**

AND

- Difference between:
  - Updated 1st pass permeate flow  
  - 2nd pass feed flow  
  is **< 0.01**

---


## 🖥️ Application Interface

![Main UI](images/Main%20Interface.png)

![Iteration UI](images/Iteration%20Display.png)

![Result UI](images/Result%20Display.png)

![Preview UI](images/Density%20Preview.png)


---

## 🚀 How to Run

### Run from source

```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
python cal.py