import csv
import os
import numpy as np
import time

from matplotlib import pyplot as plt
from future.builtins.misc import input

from mendeleev import element


def choose_peaks(peaks,peak_h):
    """
    prompt user to select which peaks to classify on
    """
    d = peaks
    maximum = len(d['d_spacing'])

    plt.title('select peaks.  Enter to stop.')
    
    raw_choices = []
    while True:
        pts = []
        pts = plt.ginput(100, timeout=-1)
            
        print(pts)
        print(len(pts))
        
        index = []
        for p in pts:
            index.append(np.argmin(np.abs(d['d_spacing']-p[0])))
        
        index.sort()
    
        
        
        for i in index:
            peak_h[i][0].set_linewidth(5)
      
      
        plt.title('Enter to keep peaks, or reselect points')
        
#        time.sleep(1)  # Wait a second
        
        if plt.waitforbuttonpress():
            break
    
    
    
    #raw_choices =  input("Choose which peaks you'd like to select separated by spaces.\n").split(" ")
    
    raw_choices = index

    temp_choices = []

    for choice in raw_choices:
        try:
            temp_index = int(choice)
            if temp_index > 0 and temp_index <= maximum and temp_index not in temp_choices:
                temp_choices.append(temp_index)
            else:
                print("index {} outside of available peaks".format(temp_index))
        except:
            print("couldn't convert {} into an index".format(choice))

    print(temp_choices)

    
    temp_locs = {
                "d_spacing":[d['d_spacing'][i-1] for i in temp_choices],
                #"2theta":[theta[i-1] for i in temp_choices],
                "vec":[d['vec'][i-1] for i in temp_choices]
                }

    return temp_locs

def provide_family():
    """
    prompt user and ensure proper selection of base Crystal family
    """

    family = None

    while family is None:
        temp_choice = input("Would you like to suggest a crystal family? yes or no\n")

        if temp_choice =="yes":
            family = temp_choice
        elif temp_choice =="no":
            family = temp_choice
        else:
            print("Invalid choice. Please choose yes or no\n")

    return family


def write_to_csv(path, data_dict, prediction_per_level):
    """
    save new row of results to csv
    """


#    schema = ["file_name","family","confidence", "genus 1st pred","confidence", "species_1", "confidence", "species_2", "confidence", "genus 2nd pred","confidence","species_3", "confidence", "species_4", "confidence", "peaks"]
    
    ppl = prediction_per_level

    # if no file exists create a one and inform the user
    if not os.path.exists(path):
        schema = ["file_name"]
        for k in range(ppl[0]):
            schema.append("family_"+str(k+1))
            schema.append("family_confidence_"+str(k+1))
            for l in range(ppl[1]):
                gn=k*ppl[1]+l
                schema.append("genus_"+str(gn+1))
                schema.append("genus_confidence_"+str(gn+1))
                for m in range(ppl[2]):
                    schema.append("species_"+str(gn*ppl[2]+m+1))
                    schema.append("species_confidence_"+str(gn*ppl[2]+m+1))
                    schema.append("hall_"+str(gn*ppl[2]+m+1))
        schema.append("peaks")
                    
        print("creating new output file {}".format(path))
        with open(path, "w") as csv_file:
            filewriter = csv.writer(csv_file, delimiter=",")
            filewriter.writerow(schema)

    row = []

    row.append(data_dict["file_name"])
    
    for k in range(ppl[0]):
        row.append(data_dict["family_"+str(k+1)])
        row.append(data_dict["fam_confidence_"+str(k+1)])
        for l in range(ppl[1]):
            gn=k*ppl[1]+l
            row.append(data_dict["genus_"+str(gn+1)])
            row.append(data_dict["gen_confidence_"+str(gn+1)])
            for m in range(ppl[2]):
                row.append(data_dict["species_"+str(gn*ppl[2]+m+1)])
                row.append(data_dict["spec_confidence_"+str(gn*ppl[2]+m+1)])
                row.append(data_dict["hall_"+str(gn*ppl[2]+m+1)])
                
    row.append(data_dict["peaks"])

    with open(path, "a") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(row)
        
def check_for_chemistry(session):

    # tries to identify chemistry information from session file
    
    if "chemistry" not in session or not session["chemistry"]:
        return []
    
        
    if "atomic_percentage" in session:
#        print('percentage of each element by count')
        chem_vec = session["atomic_percentage"]
        
    elif "chemical_formula" in session:
#        print('expected chemical formula')
        chem_vec = str2chem(session["chemical_formula"])
        tot_elem = 0
        for cv in chem_vec:
            tot_elem+=cv[1]
        for k in range(len(chem_vec)):
            chem_vec[k][1] /= tot_elem
        
    elif "atomic_density" in session:
#        print('percentage of each element by mass')
        print("Warning: atomic density may not improve the accuracy, especially if atomic weights of the elements are significantly different")
        chem_vec = session["atomic_density"]
        
    elif "cemical_contents" in session:
#        print('list of elements to expect')
        cc = session["cemical_contents"]
        chem_vec = []
        for elem in cc:
            chem_vec.append([element(elem).atomic_number, 1/len(cc)])
    
    else:
        print("not enough data to run chemistry prediction.  Ignoring")
        return []
        
    return chem_vec

def str2chem(string):
    
    elem_list = []
    new_elem = False
    prev_elem = ''
    prev_num = ''
    for k,c in enumerate(string):

        if c.isdigit():
            prev_num+=c
        elif c.islower():
            prev_elem+=c
        
        if c.isupper() or k==len(string)-1:
            if prev_elem:
                try:
                    elem = element(prev_elem).atomic_number
                except:
                    raise ValueError("Something wrong with Chemical formula input")
                if prev_num:
                    num = int(prev_num)
                else:
                    num = 1
                
                elem_list.append([elem,num])
            prev_elem = c
            prev_num = ''
    return elem_list
        
      

