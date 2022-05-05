## Description
This repository belongs to the paper _"Whitelisting for Characterising and 
Monitoring Process Control Communication"_, which presents an approach to 
monitor operational technology (OT) network communication with simple rules. 
This is intended to provide rudimentary protection against IT-based attacks. 
Another use case is the measurement of communication dynamics in different 
network infrastructures. With this repository, a demo application
(whitelisting_scenarios.ipynb) is provided that allows the analyses carried 
out for the evaluation to be reproduced.

Please note that only the public datasets are included into the demo application. 
Due to existing non-disclosure agreements with the operators of the real 
operating infrastructures, the associated network data cannot be published here.

---

## Repository Structure
<pre>
OT-Whitelisting
    ├── README.md......................<i>this file</i>
    ├── whitelisting_scenarios.ipynb...<i>Jupyter Notebook for the demonstration of whitelist analyses</i>
    ├── <a href="datasets/">datasets</a>.......................<i>preprocessed network traffic of public datasets</i>
    │   ├── cicids-17.json.............<i>whitelist analysis results of the CIC-IDS2017 dataset</i>
    │   ├── swat-a3.json...............<i>whitelist analysis results of the SWaT A3 dataset</i>
    │   ├── swat-a6.json...............<i>whitelist analysis results of the SWaT A6 dataset</i>    
    │   └── <a href="datasets/cogra/">cogra</a>......................<i>communication graphs of the datasets</i>
    │       ├── cicids-17
    │       ├── swat-a3
    │       └── swat-a6
    └── <a href="src/">src</a>............................<i>additional Python code used by the Jupyter Notebook</i>
    
</pre>
---

## Requirements
The Jupyter Notebook is expected to be runnable on arbitrary Linux systems with a Python3 installation and the 
following additional packages:
- `matplotlib` >= 3.3.4
- `pandas` >= 0.24.2
- `jupyter` >= 1.0.0
