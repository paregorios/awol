# -*- coding: utf-8 -*-
import os
import glob
import argparse
import csv
import logging as log
import traceback
from CreateNewZotero import CreateNewZotero
from ParseXML import ParseXML

DEFAULTOUTPATH='.//zotero_items_load.log'
recCounter = int()
recCounter = 0

##########################READ CSV###################
#Read CSV file containing the right tags to produce
dictReader = csv.DictReader(open('awol_title_strings.csv', 'rb'), 
                    fieldnames = ['titles', 'tags'], delimiter = ',', quotechar = '"')
#Build a dictionary from the CSV file-> {<string>:<tags to produce>}
titleStringsDict = dict()
for row in dictReader:
    titleStringsDict.update({row['titles']:row['tags']})

#Read awol_colon_prefixes.csv file and build a dictionary
dictReader2 = csv.DictReader(open('awol_colon_prefixes.csv', 'rb'), 
                     fieldnames = ['col_pre', 'omit_post', 'strip_title', 'mul_res'], delimiter = ',', quotechar = '"')
colPrefDict = dict()
#Build a dictionary of format {<column prefix>:<list of cols 2,3 and 4>}
for row in dictReader2:
    colPrefDict.update({row['col_pre']:[row['omit_post'], row['strip_title'], row['mul_res']]})
#############END OF READ CSV#########################

#*************************
with open('procsd_files.txt','r') as myfile:
    procFiles = myfile.read()#.replace('\n','')
    procFilesList = procFiles.split('\n')
#*************************

#Create zotero objects from XML files in the local directory by passing its path
def parseDirectory(path):
    log.info('Parsing directory %s' % path)
    x = ParseXML()
    items = glob.glob(path + '/*-atom.xml')
    for i in items:
        if i not in procFilesList:
            log.info('Now parsing:%s' % i)
            y = x.extractElementsFromFile(i)
            z = CreateNewZotero()
            z.createItem(y)
        else:
            log.info('Already processed file:%s' % i)
            print 'Already processed file:'+i

def main():
    global recCounter
    try:
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-w", "--webpath", help = "web path to XML file", action = "store_true")
        group.add_argument("-l", "--localpath", help = "local path to XML file/ directory", type = str , choices = ['f','d'])
        parser.add_argument ("-v", "--verbose", action="store_true", help="verbose output (i.e., debug logging")
        parser.add_argument("-p", "--path", help = "specify path", type = str)
    #     parser.add_argument("-n", "--numdoc", help = "specify no of documents", type = int, default = -1)
    
        args = parser.parse_args()    
        if args.verbose:
            log.basicConfig(filename=DEFAULTOUTPATH, level=log.DEBUG)
        else:
            log.basicConfig(filename=DEFAULTOUTPATH, level=log.INFO)

        x = ParseXML()
        z = CreateNewZotero()
    
        if(args.webpath):
            y = x.extractElementsFromURL(args.path)
            z.createItem(y)
        else:
            if(args.localpath == 'f'):
                y = x.extractElementsFromFile(args.path)
                z.createItem(y)
            else:
                log.debug('Reading atom XMLs in dir: %s' % args.path)
                parseDirectory(args.path)
        
        log.info(str(recCounter)+" records created in Zotero!")
        print str(recCounter) + ' records created in Zotero!'
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        log.info("********ERROR, UNEXPECTED EXCEPTION********")
        log.info(e)
        log.info("*******************************************")
        traceback.print_exc()
        os._exit(1)

if __name__ == '__main__':
    main()