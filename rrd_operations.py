#/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
    Script for exporting/importing observium rrd data writed for use in Grupa KKI-BCI sp. z o. o.
    Best way to use with python>=3.6

    Author:
        Dawid Małysa
    
    TODO: 
        Change functions with input to object with controling functions and 'working' functions
        Add full folder tree scaning
"""
import os
import json
import re
import tarfile
import sys
import subprocess

def export_rrd(x):
    """Preform an export of rrds
    
        Exports information of folder construction and files in it to data.json file and pute all exports to data.tar.gz file
        which boathe are needed in inport proceder

        Args:
            x: exported main folder path 

        Errors:
            Subproce exit code 1: An error ocures when  rrdtool dump cannot use rrd file ex. when it was build on difrent os bit type
    """
    tmpStor = input('Where to store data files [default={}]: '.format(os.path.abspath(os.path.dirname(__file__))))
    tmpNotToUse = input('Excluded folders (after comma): ')   # example: test,test,asdad asd,as
    tmpNotToUse = tmpNotToUse.split(',')
    output = []
    tmpStor = os.path.abspath(os.path.dirname(__file__)) if not tmpStor or tmpStor == ' ' else tmpStor
    print('LOL ' + tmpStor)
    f = os.path.join(tmpStor, "data.tar.gz")
    if os.path.exists(f):
        tmpEx = input('This file exists, delete it?[Y/n]: ')
        tmpEx = 'y' if not tmpEx or tmpEx == ' ' else tmpEx
        if tmpEx.lower() == 'y':
            os.remove(f)
    otar= tarfile.open(f,"w:gz")
    ls = subprocess.check_output(['ls', x])
    ls = ls.decode("utf-8")
    ls = ls.split('\n')
    print('Exporting directory {} ls:'.format(x))
    for elems in ls: 
        print(elems)
        if elems and not all(elems == x for x in tmpNotToUse):
            if os.path.isdir(x+'/'+elems):
                tmpElemObjectHandler = {
                    'dirName': elems, 
                    'files': []
                }
                tmpElem = subprocess.check_output(['ls', x+'/'+elems]).decode('utf-8').split('\n')
                
                print("Actual folder "+elems)
                # print(tmpElem)
                for elem in tmpElem:
                    if elem:
                        if re.match(r'^.*\.rrd',elem):
                            tmpOneString = elem.split('.')[0]
                            with open(tmpOneString+'.xml','w') as file:
                                run = subprocess.check_output(['rrdtool', 'dump', x+'/'+elems+'/'+elem])
                                file.write(run.decode("utf-8"))
                                tmpElemObjectHandler['files'].append(elems+'/'+tmpOneString+'.xml')
                                otar.add(tmpOneString+'.xml', elems+'/'+tmpOneString+'.xml')
                                os.remove(tmpOneString+'.xml')
                                file.close()
                        else:
                            print(elem)
                output.append(tmpElemObjectHandler)
    with open('data.json', "w") as file:
        file.write(json.dumps(output))
        file.close()
    otar.close()

def import_rrd(x):
    """ Importing rrds to specyfic folder
    
        Preforme an import from data.tar.gz file based on data.json file which have information on folder structure

        Args:
            x: target folder 
     """
    tmpStor = input('Where are store data files [default={}]: '.format(os.path.abspath(os.path.dirname(__file__))))
    tmpStor = os.path.abspath(os.path.dirname(__file__)) if not tmpStor or tmpStor == ' ' else tmpStor
    f = os.path.join(tmpStor, "data.tar.gz")
    if not os.path.exists(f):
        error_file_not_exist(f)
    tmpExportPlc = input('Where are exported data files should be placed [default={}]: '.format('/tmp'))
    tmpExportPlc = '/tmp' if not tmpExportPlc or tmpExportPlc == ' ' else tmpExportPlc
    print("Exporting data.tar.gz to {}\n".format(tmpExportPlc))
    tarOpen = tarfile.open('data.tar.gz', 'r')
    tarOpen.extractall(tmpExportPlc)
    tarOpen.close()
    inputObj = None
    f = os.path.join(tmpStor, "data.json")
    if not os.path.exists(f):
        error_file_not_exist(f)
    print("Starting import: \n")
    with open(f, 'r') as file:
        inputObj = json.load(file)
    for idx, elems in enumerate(inputObj,1):
        print("Actual folder: {} # [{}/{}]".format(elems['dirName'], idx, inputObj))
        if not os.path.exists(x+'/'+elems['dirName']):
            os.mkdir(x+'/'+elems['dirName'])
        for ind, elem in enumerate(elems['files'],1): 
            test = subprocess.check_output(['rrdtool','restore','-f',tmpExportPlc+'/'+elem,"{}/{}".format(x,elem.split('.')[0]+'.rrd')])
            print("Actual file: {} # Precent of lofder {}% {}\n".format(elem.split('/')[1].split('.')[0]+'.rrd', round(((ind)/len(elems['files']))*100, 2), test))
            file.close()
            os.remove(tmpExportPlc+'/'+elem)
        os.remove(tmpExportPlc+'/'+elems['dirName'])

def error_function(x):
    print('bad operation')

def error_file_not_exist(x):
    sys.exit("File don't exist: {}".format(x))

def chose_im_exp(x):
        return {
            '1': import_rrd,
            '2': export_rrd
        }.get(x, error_function)

def start_func(c = None):
    """ Function starting program

        If c is set program just showing secend line fo inputs

        Args:
            c: number to chose an options 
    """
    if not c:
        print("Choose import or export: \n1 - Import \n2 - Export")
        tmpC = input("\nPut number[1,2]: ")
        tmpF = input("\nWrite directory: ")
    else:
        tmpF = input("\nWrite directory: ")
    if os.path.exists(tmpF):
        func = chose_im_exp(tmpC)
        func(tmpF)

#   Script starts here
start_func()

#   end of procedure
