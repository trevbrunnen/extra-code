# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 14:06:50 2021

@author: trevb
"""
import pandas as pd
import numpy as np
import random as rd

def noRepeats(assignments):
    
    if '' in assignments['TA'].unique():
        return False
    
    for section in assignments['Class'].unique():
        subassignments = assignments[assignments['Class'] == section]
        if subassignments['TA'].value_counts().max() > 1:
            return False
    return True


def initialAssignment(index, neededTAs, preferences, TAneeds):
    
    while(True):
        
        assignments = pd.DataFrame(columns = ['TA', 'Cost'])
        TAs = preferences.index.values.copy()
        rd.shuffle(TAs)
        counter = 0
        assigned = 0
        for i in range(len(index)):
            for j in range(neededTAs[i]):
                attempts = 0
                place = False
                while((place == False) and (attempts < len(TAs))):
                    print(counter)
                    if preferences.loc[TAs[counter], index[i]] < 10000:
                        if(index[i][-1] == 'L'):
                            if(TAneeds.loc[TAs[counter],'Labs']<preferences.loc[TAs[counter],'Labs Needed']):
                                place = True
                        else:
                            if(TAneeds.loc[TAs[counter],'Tutorials']<preferences.loc[TAs[counter],'Tutorials Needed']):
                                place = True
                        if(place):
                            assignments.loc[assigned, 'TA'] = TAs[counter]
                            assignments.loc[assigned, 'Cost'] = preferences.loc[TAs[counter],index[i]]
                            assigned += 1
                            counter += 1
                        else:
                            if counter < len(TAs):
                                counter += 1
                            else:
                                counter = 0
                            attempts += 1
                print(j)
        
        if(noRepeats(assignments)):
            cost = assignments['Cost'].sum()
            return assignments, cost
        
    
def initialAssignment2(index, neededTAs, preferences, TAneeds):
    originalNeeds = TAneeds.copy()
    while(True):
        TAneeds = originalNeeds.copy()
        assignments = pd.DataFrame(columns = ['TA', 'Cost','Class'])
        TAs = preferences.index.values.copy()
        rd.shuffle(TAs)
        counter = 0
        assigned = 0
        
        for i in range(len(index)):
            for j in range(neededTAs[i]):    
                assignments.loc[assigned, 'TA'] = ''
                assignments.loc[assigned, 'Cost'] = 1000
                assignments.loc[assigned, 'Class'] = index[i]
                assigned += 1
        
        for row, whatever in assignments.iterrows():
            rd.shuffle(TAs)
            currentTAs = assignments[assignments['Class'] == whatever['Class']]['TA'].unique()
    
            if whatever['Class'][-1] == 'L':
                for TA in TAs:
                    if int(preferences.loc[TA, whatever['Class']]) < 10000 and (not TA in currentTAs):
                        if TAneeds.loc[TA, 'Labs'] < preferences.loc[TA,'Labs Needed']:
                            assignments.loc[row, 'TA'] = TA
                            assignments.loc[row, 'Cost'] = int(preferences.loc[TA, whatever['Class']])
                            TAneeds.loc[TA,'Labs'] += 1
                            break
            else:
                for TA in TAs:
                    if int(preferences.loc[TA, whatever['Class']]) < 10000 and (not TA in currentTAs):
                        if TAneeds.loc[TA, 'Tutorials'] < preferences.loc[TA,'Tutorials Needed']:
                            assignments.loc[row, 'TA'] = TA
                            assignments.loc[row, 'Cost'] = int(preferences.loc[TA, whatever['Class']])
                            TAneeds.loc[TA,'Tutorials'] += 1
                            break
        
        truth = noRepeats(assignments)
        print(truth)
        if(truth):
            cost = assignments['Cost'].sum()    
            return assignments, cost
        del(assignments)
    
def updateAssignment(assignments, preferences,temperature):
    
    assignmentscopy = assignments.copy()
    
    tutORlab = rd.random()
    
    
    #Only want to switch labs for labs and tutorials for tutorials.
    #This is currently hard coded in for Fall 2021. It will either need to be
    #written more elegantly for the future, or the 21 and 78 will need to be changed.
    #It's late and I'm too lazy to be clever.
    if(tutORlab< 0.5):
        num1, num2 = rd.sample(range(0,21), 2)
    else:
        num1, num2 = rd.sample(range(21,78), 2)
    
    #num1, num2 = rd.sample(range(0,assignments.shape[0]), 2)
    
    TA1 = assignments.loc[num1, 'TA']
    TA2 = assignments.loc[num2, 'TA']
    
    if (int(preferences.loc[TA1,assignments.loc[num1,'Class']])<10000):
        if(int(preferences.loc[TA2,assignments.loc[num2,'Class']])<10000):
            assignments.loc[num1, 'TA'] = TA2
            assignments.loc[num2, 'TA'] = TA1
            assignments.loc[num1,'Cost'] = int(preferences.loc[TA2,assignments.loc[num1,'Class']])
            assignments.loc[num2,'Cost'] = int(preferences.loc[TA1,assignments.loc[num2,'Class']])
    
    if(not noRepeats(assignments)):
        return assignmentscopy
    
    if assignments['Cost'].sum() < assignmentscopy['Cost'].sum():
        return assignments
    else:
        deltaCost = assignments['Cost'].sum() - assignmentscopy['Cost'].sum()
        if (rd.random() < np.exp(-(deltaCost)/temperature)):
            #print('did something!' + str(assignments['Cost'].sum()))
            return assignments
        else:
            return assignmentscopy

if __name__ == '__main__':

    preferences = pd.read_csv('./Fall2021TAPreferences.csv',index_col=0)
    
    #Folder to save to
    savepath = 'C:/Users/trevb/OneDrive/Spring2020TAAssignments/'
    
    #Give anything that they cannot do a ridiculously high cost
    preferences = preferences.replace('n',1000000)
    
    #Give anything that they don't really want or really don't want a medium cost
    preferences = preferences.fillna(10)
    
    index = ['T9L', 'T15L', 'T18L', 'W9L', 'W12L', 'W15L', 'W18L', 'TH9L', 'W1', \
           'W2', 'W3', 'W4', 'W5', 'W6','TH9', 'TH2', 'TH3', 'TH6',\
               'F9', 'F10', 'F11','F12','F1']
        
    neededTAs = [3, 3, 3, 3, 3, 3, 3, 3, 3, \
           3, 3, 3, 3, 3, 5, 3, 3, 3, \
           5, 5, 5, 5, 5]
           
    columns = ['TA 1','TA 2','TA 3','Cost']
    
#    assignments = pd.DataFrame(columns=columns,index=index)
#    assignments['Cost'] = 0
    
    TAs = preferences.index.values.copy()
    
    TAneeds = pd.DataFrame(index =TAs)
    TAneeds['Tutorials'] = 0
    TAneeds['Labs'] = 0
    finalTAneeds = TAneeds.copy()
    
    # Default cost
    default = 10
    
    assignments, cost = initialAssignment2(index, neededTAs, preferences, TAneeds)
    
    for i in range(40000):
        temperature = 1/(i+1)
        assignments = updateAssignment(assignments, preferences, temperature)
        if i%100 == 0:
            print(assignments['Cost'].sum())