VulReScorer – Scoring Formulas

This document explains the formulas used in VulReScorer for vulnerability scoring and cyber-system aggregation.


🔢 1. Adjusted Vulnerability Score

For each vulnerability:

V = CVSS × Exposure × Maturity


Where:

Exposure Selection
Exposure = Exposure_Exposed       if EPSS ≥ Maturity_Boundary
Exposure = Exposure_NonExposed    otherwise

Maturity Selection
Maturity = Maturity_High          if EPSS ≥ Maturity_Boundary
Maturity = Maturity_Low           otherwise


Default values:

Parameter	            Default
Exposure (Exposed)	    1.0
Exposure (Non-Exposed)	0.75
Maturity High	        1.0
Maturity Low	        0.75
Maturity Boundary	    0.5


🔢 2. Aggregated Cyber-System Score

Given all Adjusted Scores Vi belonging to a Cyber System:

X-Formula (Impact Aggregation)
    X = 1 - ∏(1 - Vi / 10)

Max Score
    Max = max(Vi)

Average Score
    Average = sum(Vi) / len(Vi)

📘 Interpretation

X increases exponentially as vulnerabilities accumulate

Max shows worst-case exposure

Average shows general exposure

Sensitivity Analysis allows real-time parameter adjustments