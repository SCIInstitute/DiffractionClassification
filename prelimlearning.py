import numpy as np
import seaborn as sn
import pandas as pd
import os


from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def load_data(pattern,selected):
    data = np.zeros((0,180))
    counter = 0
    for i in selected:
        
        thetas = []
        file_to_open = pattern + "_{}.txt".format(i)
        with open(file_to_open,"r") as f:
            lines = f.readlines()
            members = len(lines)
            peaks = np.zeros(180)
            temp_array = np.zeros((members,180),dtype=np.int16)
            temp_y = np.ones((members,1)) * i 
            j = 0
            for line in lines:
                entries = line.strip().split(",")
                temp_array[j,:] += [int(float(entry)) for entry in entries[:]]
                temp_array[j,:] /= np.amax(temp_array[j,:])
                #print np.amax(temp_array[j,:]),np.amin(temp_array[j,:])
                j+=1
            if counter==0:
                y = temp_y
                counter += 1
            else:
                y = np.concatenate((y,temp_y), axis=0)
            data = np.concatenate((data,temp_array),axis=0)
            
    print np.unique(y,return_counts=True)
    return data,y


def plot_confusion(model,data_test,labels_test,selected,f_scale=3,
	f_size=60,name='testing.png',normed=True,shift=0., top_two=False,
    plot=False):
    save_name = os.path.join('Images',name) + '.png'
    pred = model.predict(data_test)
    predictions = np.argmax(pred, axis=1) + shift
    
    if top_two:
        temp_y = labels_test.reshape(labels_test.shape[0],)
        temp_guess = np.zeros((pred.shape[0],2))
        for i in xrange(pred.shape[0]):
            first = np.argmax(pred[i])
            if pred[i,first] < 1:
                mask = pred[i] != pred[i,first]
                seconds = np.argmax(pred[i][mask])
                if seconds >= first:
                    seconds+=1
            else:
                seconds = first


            temp_guess[i,0] = first
            temp_guess[i,1] = seconds

            #print first,seconds

        # Separate the guesses
        first_guess = temp_guess[:,0] + shift
        second_guess = temp_guess[:,1] + shift

        # determine which ones were already correct
        mask_cfrst = first_guess != temp_y  
        mask_cscnd = second_guess == temp_y

        # Change the predictions vector to having the correct guess if it's
        # the second guess
        #predictions[mask_cscnd] = temp_y[mask_cscnd]        
        p_top_two = predictions.copy()
        p_top_two[mask_cscnd] = temp_y[mask_cscnd]
        conf_mat = confusion_matrix(labels_test,p_top_two, labels=selected)
    
    else:
        conf_mat = confusion_matrix(labels_test,predictions, labels=selected)
    
    
    total = conf_mat.sum()
    correct = conf_mat.trace()
    acc_gross = correct/float(total)
    
    if normed == True:
        divisor = conf_mat.astype(np.float).sum(axis=1)
        divisor[divisor==0] = 1
        conf_mat = conf_mat.T / divisor 
    acc_diag = conf_mat.trace()/len(selected)
    df_cm = pd.DataFrame(conf_mat, index = selected,columns = selected)
    
    if plot:
        fig_size = (len(selected)*2,len(selected)*1.5)
        plt.figure(figsize=fig_size)
        sn.set(font_scale=f_scale)
        font=f_size
        ax = ["Expected","Predicted"]
        fig = sn.heatmap(df_cm, annot=True, fmt='.2f')
        plt.title(name+'\n', fontsize=font)
        plt.xlabel("Expected",fontsize=4*font/5)
        plt.ylabel("Predicted", fontsize=4*font/5)
        #plt.show(fig)
        plt.savefig(save_name)

    return df_cm, acc_gross, acc_diag
    #return conf_mat
   
    

def plot_confidence_confusion(model,data_test,labels_test,selected,f_scale=3,
    f_size=60,name='testing.png',normed=True,shift=0., top_two=False,conf=.6,
    plot=False):
    save_name = os.path.join('Images',name) + '.png'
    pred = model.predict(data_test)
    predictions = np.argmax(pred, axis=1) + shift
    
    if top_two:
        temp_y = labels_test.reshape(labels_test.shape[0],)
        temp_guess = np.zeros((pred.shape[0],2))
        for i in xrange(pred.shape[0]):
            first = np.argmax(pred[i])
            if pred[i,first] < conf:# and first==4:
                mask = pred[i] != pred[i,first]
                seconds = np.argmax(pred[i][mask])
                if seconds >= first:
                    seconds+=1
                first = seconds


            temp_guess[i,0] = first
            #print first,seconds

        # Separate the guesses
        confident_guess = temp_guess[:,0] + shift
        
        # Change the predictions vector to having the correct guess if it's
        # the second guess
        conf_mat = confusion_matrix(labels_test,confident_guess, labels=selected)
    
    else:
        conf_mat = confusion_matrix(labels_test,predictions, labels=selected)
    
    
    total = conf_mat.sum()
    correct = conf_mat.trace()
    acc_gross = correct/float(total)
    
    if normed == True:
        divisor = conf_mat.astype(np.float).sum(axis=1)
        divisor[divisor==0] = 1
        conf_mat = conf_mat.T / divisor 
    acc_diag = conf_mat.trace()/len(selected)
    df_cm = pd.DataFrame(conf_mat, index = selected,columns = selected)
    
    if plot:
        fig_size = (len(selected)*2,len(selected)*1.5)
        plt.figure(figsize=fig_size)
        sn.set(font_scale=f_scale)
        font=f_size
        ax = ["Expected","Predicted"]
        fig = sn.heatmap(df_cm, annot=True, fmt='.2f')
        plt.title(name+'\n', fontsize=font)
        plt.xlabel("Expected",fontsize=4*font/5)
        plt.ylabel("Predicted", fontsize=4*font/5)
        #plt.show(fig)
        plt.savefig(save_name)

    return df_cm, acc_gross, acc_diag
    #return conf_mat


def build_models(data_train,labels_train,data_test,labels_test,by):
    # Naive Bayes - full
    clf = GaussianNB()
    clf.fit(data_train, labels_train)
    print "Naive Bayes full scored:{} percent on {}".format(clf.score(data_test,labels_test)*100,by)
    # Naive Bayes - partial
    # pretty sure these are the exact same since we didn't batch it
    # SVM
    if len(labels_train) >= 10000:
        print "SVM was omitted due to computational complexity"
        supvecmec=0
    else:
        supvecmec = svm.SVC()
        supvecmec.fit(data_train, labels_train)
        print "SVM scored:{} percent on {}".format(supvecmec.score(data_test,labels_test)*100,by)
    # Random Forest
    randfore = RandomForestClassifier(max_depth=None,min_samples_split=3)
    randfore.fit(data_train,np.reshape(labels_train, (len(labels_train),)))
    print "Random Forest scored:{} percent on {}".format(randfore.score(data_test,labels_test)*100,by)
    
    
    return {"Naive Bayes":clf,
            "Random Forest":randfore,
            "Support Vector":supvecmec}

def build_data(pattern,selected):
    data,y = load_data(pattern,selected)
    data_train, data_test, labels_train, labels_test = train_test_split(data, y, test_size=0.20, random_state=42)
    train = {"Data":data_train,"Labels":labels_train}
    test =  {"Data":data_test,"Labels":labels_test}
    return train, test

def learning(pattern,selected,by,f_scale=2.,f_size=60,name='testing.png',conf=True):
    train, test = build_data(pattern, selected)
    models = build_models(train["Data"],train["Labels"],
                          test["Data"],test["Labels"], by)
    # Naive Bayes - full
    if conf == True:
        plot_confusion(models["Random Forest"],test["Data"],test["Labels"],selected,
        	f_scale=f_scale,f_size=f_size,name=name)

    return models