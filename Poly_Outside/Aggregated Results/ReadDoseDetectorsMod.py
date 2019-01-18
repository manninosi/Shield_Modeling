import sys
import os
import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('multipage.pdf')

#Function that goes through MCNP output file and determines lines where all detectors relating
#to dose are located
def findDetectors(filename):
    with open(filename, 'r') as mcnp_file:
        #print filename
        line_index = 1
        Index = []
        for lines in mcnp_file.readlines():
            if lines.startswith(" detector located at"):
                Index.append(line_index)
            # KG [
            #search for positive x value of the RPP for borated poly
            line = lines.strip()
            line = line.split() #split line into list of strings
            if "$borated" in line and "RPP" in line:
                point_of_interest = float(line[4])+30 #30 cm from shielding
            line_index += 1
            # ]
    mcnp_file.close()
    return Index, point_of_interest
    print Index

#Function that takes in neutron parameters for dose exposure
#   filename: Name of MCNP output file
#   dose_index: Line number provided by findDetectors() function
#   hours: Length of time of exposure (usually 1 hour)
#   neutron_rate: Rate of neutron emission from source  
def getDose(filename, dose_index, hours, neutron_rate):
    #print filename
    f = open(filename, 'r')
    lines = f.readlines()
    dose_list = []
    error_list = []
    x_location = []
    y_location = []
    z_location = []
    for i in dose_index:
        try:
            dose_list.append(float(lines[i].strip(" ").split()[0])*hours*neutron_rate*1000)#1000 is used to convert rem to mrem
            error_list.append(float(lines[i].strip(" ").split()[1]))            
            x_location.append(float(lines[i-1].strip(" ").split()[-3]))
            y_location.append(float(lines[i-1].strip(" ").split()[-2]))
            z_location.append(float(lines[i-1].strip(" ").split()[-1]))
            

        except:
            pass
    f.close()
    return dose_list, error_list, x_location, y_location, z_location

file_name = sys.argv[1] # variable never invoked


name_check = 0 #variable to iterate while user puts in input
hours = 1
n_rate = 1e8
dose_plot = []
error_plot = []
x_loc_plot = []
y_loc_plot = []
z_loc_plot = []
figure = plt.figure()
ax = figure.add_subplot(111)
line, = ax.plot([], [], '*')
#ax.set_title('Poly Outside 50cm of Concrete')
ax.set_ylabel('Dose Rate(mrem/hr)')
ax.set_xlabel('Distance(cm)')

#Looping through all MCNP output files listed in the command line
for i in range(1,len(sys.argv)):
    #print sys.argv[i]
    dose_index, point_of_interest = findDetectors(sys.argv[i])
    #print dose_index
    dose,error, x_location, y_location, z_location = getDose(sys.argv[i], dose_index,hours, n_rate)
    #print dose
    dose_plot.append(dose)
    error_plot.append(error)
    x_loc_plot.append(x_location)
    y_loc_plot.append(y_location)
    z_loc_plot.append(z_location)
    print "Input small description for plot in order of file inputs"
    name = raw_input("Enter Description: ")
    #Loop for user to enter description of plot to be displyed on
    #Dose rate plot
    while name_check != 1:
        print "Is the the name you wanted: %s" %name
        name_check = input("Enter 1 for okay or 0 to re-enter descprtion: ")
        if name_check != 1:
            name = raw_input("Re-enter Description: ")
    print "Named accepted for file %2.0f : %s\n" %(i, name)
    name_check = 0
    #name = sys.argv[i][:-4]  #file name without .txt
    ax.plot(x_location,dose , '-', label = name)

    # KG [
    #interpolate dose at 30 cm from shielding
    f = interpolate.interp1d(x_location, dose) #linear interpolation
    ax.plot(point_of_interest,f(point_of_interest), 'ro')
    # ]

#print dose
ax.legend()
ax.set_ylim(1e-3, 1e1)
print max(dose_plot[0])
print x_loc_plot[0]
ax.set_xlim(min(x_loc_plot[0])-50, max(x_loc_plot[0])+50)
ax.semilogy()
#line.set_xdata(x_loc_plot)
#line.set_ydata(dose_plot)
figure.canvas.draw()
plt.savefig(pp, format='pdf')
pp.close()
plt.show()


if __name__ == "__main__":
    pass
