**Software  
The file with the .py extension can be run using Python 3.9.6. No additional software is required. Python can be installed on https://www.python.org/ within 30 minutes.   
**Introduction of the code  
The CC method.py utilizes the Chinese Code for the Seismic Design of Buildings, while the NC method.py utilizes the improved simplified procedure for liquefaction assessment proposed by the National Center for Earthquake Engineering Research.The required input files include data of the soil layers, parameters and groundwater table depth as an example.  
**Input files  
The file shui.xlsx contains the coordinates of the site and its corresponding groundwater table depth.The file tuceng-CC.txt and tuceng-NC.txt contain the parameters for soil layers within a depth of 20m for CC and NC method, respectively.  
**How to run  
Rename the .py file to remove spaces, and change the corresponding .txt file name to tuceng.txt or change the file name in the code. Place the input files and the .py file in the same folder to run the program. Run the code with the given example files, and the programe will complete in under 30 seconds.  
**Expected output  
The output would be the liquefaction potential index of the sites in order.
