


<div align="center">
<h2>SysVulScorer — System Vulnerability Scoring Framework</h2>

![status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)
![gui](https://img.shields.io/badge/GUI-Tkinter%20%2B%20ttkbootstrap-purple?style=flat-square)
![license](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![platform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey?style=flat-square)

</div>

---

# 🌐 **Overview**

**SysVulScorer** is a modern graphical tool for scoring cybersecurity vulnerabilities using:

- **CVSS**
- **EPSS**
- **Exposure parameters**
- **Maturity parameters**
- **Custom sensitivity analysis**
- **Visualization & CSV exporting**

It allows security analysts, SOC teams, red teams, and cybersecurity researchers to evaluate vulnerability criticality from multiple perspectives.

---

# ✨ **Features**

### 🔹 **Adjusted Score Calculation**


Adjusted Score V = CVSS × Exposure × Maturity


### 🔹 **Exposure & Maturity Switching Based on EPSS**
Automatic switching based on a user-defined maturity boundary.

### 🔹 **Aggregated Cyber-System Scores**
Includes:

- **X-Formula (Compound Risk)**
- **Maximum Adjusted Score**
- **Average Adjusted Score**

### 🔹 **Sensitivity Analysis Tab**
Modify model parameters interactively:

- Exposure (Exposed / Non-Exposed)
- Maturity (High / Low)
- EPSS Threshold

Updates:

✔ Table view  
✔ Graph view  
✔ Logs  
✔ Exportable CSV  

### 🔹 **Automated CSV Export**
- `*_adjusted.csv`
- `*_aggregated.csv`
- sensitivity export CSV

### 🔹 **Modern GUI**
Built on:

🟣 Tkinter  
💠 ttkbootstrap themes  
📊 Matplotlib graphs  

---

# 📥 **Installation**

## 1️⃣ Clone the repository
```
git clone https://github.com/<your_repo>/SysVulScorer.git
cd SysVulScorer
```

2️⃣ Install dependencies
```
pip install -r requirements.txt
```

Or manually:

'''
pip install ttkbootstrap pandas matplotlib
'''

Pandas is optional — the program falls back to Python's CSV module.

# ▶️ Launch the Application
```
python sysvulscorer.py
```

# 📄 Input Format

## Your CSV file must include:

Column	Description
CVSS	   CVSS Base Score
EPSS	   EPSS Probability (0–1)
CS	      Cyber System ID

Example:
```
CVSS,EPSS,CS
9.8,0.87,Finance-Core
8.2,0.63,Finance-Core
6.5,0.28,HR-Portal
4.2,0.15,HR-Portal
7.7,0.45,IoT-Gateway
5.0,0.12,Backup-Server
9.1,0.52,Customer-API
3.5,0.08,Customer-API
```


# 📊 Scoring Formulas

## 🔹 Adjusted Score
V = CVSS × Exposure × Maturity

### Exposure Switching:
Exposure = Exposure_Exposed       if EPSS ≥ Maturity_Boundary
Exposure = Exposure_NonExposed    otherwise

### Maturity Switching:
Maturity = Maturity_High          if EPSS ≥ Maturity_Boundary
Maturity = Maturity_Low           otherwise

## 🔹 Aggregation (per CS)
### X-Formula:
X = 1 - ∏(1 - V_i / 10)

### Max:
Max = max(V_i)

### Average:
Average = sum(V_i) / len(V_i)

# 🧪 Sensitivity Analysis

The Sensitivity Tab enables:

Real-time model tuning

Visualization of adjusted score distribution

Aggregated score recalculation

Export button for saving test scenarios

Sliders allow adjusting:
'''
Parameter	         Range	      Default
Exposure Exposed	   0–1	      1.0
Exposure Non-Exposed	0–1	      0.75
Maturity High	      0–1	      1.0
Maturity Low	      0–1	      0.75
Maturity Boundary	   0–1	      0.5
'''
# 📂 Output Files
'''
File	               Description
*_adjusted.csv	      Adjusted score per vulnerability
*_aggregated.csv	   Cyber-system aggregated scores
*_sensitivity.csv	   Exported table from Sensitivity tab
'''

# 🎨 Themes

SysVulScorer includes multiple GUI themes via ttkbootstrap:

darkly

flatly

superhero

cyborg

cosmo

minty
… and more.

# 📸 Screenshots (Add Yours Here)
[ Coming Soom ]

---

# 🤝 Contributing

Contributions are welcome!
Feel free to open issues and pull requests.

# 📜 License

This project is licensed under the MIT License.
See LICENSE for details.

# ⭐ Support the Project

If SysVulScorer helps your workflow, please star ⭐ the repository — it really helps!


# ✅ DONE!
---
