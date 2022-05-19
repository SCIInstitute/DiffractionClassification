from __future__ import print_function
from __future__ import division

import numpy as np
from matplotlib import pyplot as plt

def vote_peaks(signal, **kwargs):
    """
        Input: 

        signal : list, contains d_spacings in the profile
        
        **kwargs:

        filter_size : int, starting bin width of each pass
        
        passes : int, number of voting rounds 
        
        thresh : 0 < float < 1, percentage votes to be considered a peak 
        
    Outputs:

        payload : dictionary, contains classification statistics and predictions
    
    """
    filter_size = kwargs.get('filter_size',10)
    passes = kwargs.get('passes',2)
    threshold = kwargs.get('peak_threshold',.6)
    
	# determine size of filter
    size = len(signal)
    
    # Pad profile so it can be indexed properly   
    signal = np.pad(signal,(filter_size,filter_size),'constant', constant_values=(0))
    print(size,signal.shape)

    # create vote holder array
    votes = np.zeros_like(signal)
    scalar = 1

    # step through the array and vote for peak locations 
    for i in range(0,size):
        
        #print(np.argmax(signal[i:i+filter_size])+i)
        votes[np.argmax(signal[i:i+filter_size])+i] += scalar
  
    # Pare down the votes to remove extraneous peaks but preserve candidates
    votes[votes<np.amax(votes)*threshold] = 0        

    print('___-____-_-__-_ votes ___-_--_-_--_---_')
#    print(votes.tolist())
    print(np.amax(votes))
    histo = np.histogram(votes,bins = 256)
    bar_string = print_histogram(votes,title = 'votes',mode = 'log')
    print(bar_string)

    # trim off the padding from the votes array
    inner = filter_size
    peak_locs_pixel = votes[inner:-inner]

    return peak_locs_pixel
    
def print_histogram(array, title = "", mode = 'linear'):
        y_res = 10
        nbins = int(np.min((128,np.amax(array))))
        histo = np.histogram(array,bins = nbins)
        y_tick = ['       ']*y_res
        
                    
        if mode == 'linear':
            y_hist = (histo[0]/np.max(histo[0])*y_res).astype(int)
            
            y_tick[0] = "%7.3g" % np.max(histo[0])
            y_tick[int(y_res/2)] = "%7.3g" % (np.max(histo[0])* (int(y_res/2)/y_res))
            y_tick[y_res-1] = "%7.3g" % 0
        elif mode == 'log':
            log_y = np.log10(histo[0])/np.log10(np.max(histo[0]))
            log_y[log_y<0] = -1/(y_res-1)
            y_hist = (log_y*(y_res-1)).astype(int)+1
            
            y_tick[0] = "10^%4.3g" % np.max(np.log10(np.max(histo[0])))
            y_tick[int((y_res-1)/2)] = "10^%4.3g" % (np.max(np.log10(np.max(histo[0])))* (int((y_res-1)/2)/(y_res-1)))
            y_tick[y_res-2] = "10^%4.3g" % 0
        elif mode == 'skip_0':
            histo = (histo[0][1:],histo[1][1:])
            y_hist = (histo[0]/np.max(histo[0])*y_res).astype(int)
            
            y_tick[0] = "%7.3g" % np.max(histo[0])
            y_tick[int(y_res/2)] = "%7.3g" % (np.max(histo[0])* (int(y_res/2)/y_res))
            y_tick[y_res-1] = "%7.3g" % 0
        elif mode == 'ignore_0':
            y_hist = (histo[0]/np.max(histo[0][1:])*y_res).astype(int)
            y_hist[y_hist>y_res] = y_res
            
            y_tick[0] = "%7.3g" % np.max(histo[0][1:])
            y_tick[int(y_res/2)] = "%7.3g" % (np.max(histo[0][1:])* (int(y_res/2)/y_res))
            y_tick[y_res-1] = "%7.3g" % 0
        else:
            raise ValueError("print_histogram: mode not recognized")
            
        
        spacer = '        '
        l_sp = len(spacer)-1
        x_tick = ' '
        x_tick += "%7.3g" % histo[1][0]
        h1 = int(len(y_hist)/4)
        h2 = int(len(y_hist)/2)
        h3 = int(3*len(y_hist)/4)
        x_tick+=' '*(h1-l_sp)
        x_tick+= "%7.3g" % (histo[1][-1] * h1/len(y_hist))
        x_tick+=' '*(h2-h1-l_sp)
        x_tick+= "%7.3g" % (histo[1][-1] * h2/len(y_hist))
        x_tick+=' '*(h3-h2-l_sp)
        x_tick+= "%7.3g" % (histo[1][-1] * h3/len(y_hist))
        x_tick+=' '*(len(y_hist)-h3-l_sp)
        x_tick+= "%7.3g" % (histo[1][-1])
        
        bar_string = spacer+title+'\n'
        for l in range(y_res,0,-1):
            string = ['%' if y>=l else ' ' for y in y_hist]
            string = ''.join(string)
            bar_string += y_tick[y_res-l]+'|'+string+'\n'
            

        bar_string+= spacer + '-'*len(y_hist) +'\n'
        bar_string+= x_tick
        

        return bar_string


def plot_peaks(signal,scale,votes,thresh = 0, **kwargs):

    """
    Inputs:
        signal : array, vector of bins in inverse D
        scale: array, pixel_size in microns/pixel
        votes: array, wave length in nanometers
        display_type: string, d or theta

    Outputs:

        None
        
    """
    
    scale_range = kwargs.get('dspace_range',[0.5, 6])

    indicies = np.where(votes>thresh)
    plt.figure(1,figsize=(6,2))
    plt.cla()
    plt.ion()
    plt.plot(scale,signal,linewidth=3)
    
    sig_min = np.amin(signal)


    peaks_h =[]
    counter = 1
    for index in indicies[0]:
        x = np.array([scale[index],scale[index]])
        y = np.array([signal[index],sig_min])
        line = plt.plot(x,y,linewidth=2,label="peak {}".format(counter))
        counter += 1 
        peaks_h.append(line)

    plt.xlim(scale_range[0],scale_range[1])
    plt.xlabel("d spacing")
    plt.ylabel("intensity")

    
    return peaks_h
    
    

