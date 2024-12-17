# DATASHARE NETWORK Implementation

By: Teo Field-Marsham

### Setup:
- **Python Version:** Ensure you have Python 3.8 or higher installed.
- **Dependencies:** Scripts use only built-in Python libraries, so no extra installations are necessary.

### Running the code:
To run the basic PSI example and interactively input your search keywords:
    python3 psi.py
Enter your desired keywords (eg. apple banana) and press Enter.

To run performance tests for PSI (small or large keyword sets or different parameters), use:
    python3 benchmarking_psi.py
Functionality of the test needs to be adjusted within the code.

To run the MS-PSI example and interactively input your search keywords:
    python3 mspsi.py
Enter your desired keywords (eg. apple apple date banana) and press Enter.

To run performance tests for MSPSI (small or large keyword sets or different parameters), use:
    python3 benchmarking_mspsi.py
Functionality of the test needs to be adjusted within the code.





### TO DO:
- get benchmarking tables for presentation  
- start working on the readme project report

Temporary notes:
N is specefied in the protocol because it may be useful for performance optimizations or bounding loops in a theoretical implementation.
Some implementations might also rely on N to preallocate memory or track progress.