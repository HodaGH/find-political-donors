## Author: Hoda Gholami
## Purpose: -To identify the areas (zip codes) that may be fertile ground for soliciting future donations for similar candidate
##          -To identify which time periods are particularly lucrative so that an analyst might later correlate them to specific fundraising events.
## Input: An input stream/file containing campaign contributions by individual donors
## Output: - An output file contains a calculated running median, total dollar amount and total number of contributions by recipient and zip code
##         - An ouput file contains a calculated median, total dollar amount and total number of contributions by recipient and date.
## Assumptions: 
## 	1. The minimum value for year is assumed to be 1975 (I got this number from FEC archived files)
##      2. I assume it is ok to preprocess the input file by removing all spaces in a line and check other validations.
##         In other word, I assumee having spaces is not considered as malformed data. And it get fixed as a preprocessing step. 
##      3. I assume that there is space between any two lines in input file. This is because I check end of file with having space and empty line.
##      4. I assume that the number of fields (21 fields) is fixed and should not change. If a line has less than 21 fields separated by "|", it will be ignored.
##      5. Based on the challenge description, we can assume the input file follows the data dictionary noted by the FEC for the 2015-current election years. 

import datetime
import running_median
import sys
import os
from collections import defaultdict, OrderedDict
import re
from running_median import RunningMedian
import time

def checkValidDate(date):
    """
    This function take cares of validating TRANSACTION_DT.
    If TRANSACTION_DT be empty or not in the format of MMDDYYYY with valid values for day, month and year, it returns False.
    Based on FEC archive files, range of valid years is from 1975 to current year.
    Valid day is between 1 to 31, and valid month is between 1 and 12.
    
    Parameters
    ----------
    date: string
        The value of field TRANSACTION_DT.

    Returns
    -------
    True/False: boolean       
    """
    now = datetime.datetime.now()
    if not date or len(date) != 8:
        return False
    else:
        return  1 <= int(date[:2]) <= 12 and 1 <= int(date[2:4]) <= 31 and 1975<= int(date[4:8]) <= now.year
    
def checkValidLine(line):
    """
    This function takes care of input file considerations w.r.t to both medianvals_by_zip and medianvals_by_date.
    If there are not 21 fields in the line, return (False, False).
    If the OTHER_ID field is NOT empty or  CMTE_ID empty or TRANSACTION_AMT empty, return (False, False).
    If CMTE_ID is not alpha-numeric or its lenght is not equal to 9, return (False, False)  [CMTE_ID: VARCHAR2 (9) A 9-character alpha-numeric code assigned]
    If ZIP_CODE is empty or fewer than five digits and If TRANSACTION_DT is empty or malformed: return (False, False)
    If ZIP_CODE greater than four digits and If TRANSACTION_DT is empty or malformed: return (True, False)
    If ZIP_CODE is empty or fewer than five digits and If TRANSACTION_DT is valid: return (False, TRUE)
    If ZIP_CODE greater than four digits and If TRANSACTION_DT is valid: return (TRUE, TRUE)   
    
    Parameters
    ----------
    line: string
        One record from input file.

    Returns
    -------
    (validity for medianvals_by_zip, validity for medianvals_by_date): boolean, boolean
    """
    fields = line.split("|") #CMTE_ID = fields[0], ZIP_CODE = fields[10], TRANSACTION_DT = fields[13], TRANSACTION_AMT = fields[14], OTHER_ID = fields[15] 
    if len(fields) != 21:
        return (False, False)
    else:
        if fields[15] or not fields[0].isalnum() or len(fields[0]) != 9 or not fields[14]:
            return (False, False)
        else:
            return (len(fields[10]) >= 5, checkValidDate(fields[13]))
        
def removeSpace(line):
    """
    This function removes spaces from a line.

    Parameters
    ----------
    line : string

    Returns
    ---------
    line : string
        Same as line but without any possible escape characters.
    """
    escape = [("\/", "/"), ("\\\\", "\\"), (r"\'", "'"), (r'\"', '"'), ("\t", "")]
    for e in escape:
        line = line.replace(e[0], e[1]) 
    return re.sub(r" +", "", line)

def processByZip(pathInput):
    """
    This function take each line of the input file as if that record was sequentially streaming into your program as input. 
    For each input file line, calculate the running median of contributions, total number of transactions and total amount of contributions streaming in so far
    for that recipient and zip code. 
    The calculated fields should then be formatted into a pipe-delimited line and written to an output file named medianvals_by_zip.txt. 
    In the same order as the input line appeared in the input file.
    
    Parameters
    ----------
    pathInput : string

    Returns
    -------
    no return value. It just writes the processed lines to output file
    """
    dByZip = defaultdict(list) #dictionary of lists, key is a tuple of recipent ID and zipCode
    fields = []
    with open(pathInput, 'r') as f_input, open(pathOutputZip, 'w') as f_outputZip:
        # Processing input
        for line in f_input:               
            del fields[:]
            line = removeSpace(line)
            if checkValidLine(line)[0] : #valid to go to be processed for output-by-zip
                fields = line.split("|")
                CMTE_ID, ZIP_CODE, TRANSACTION_AMT = fields[0], fields[10][:5], fields[14]
                if (CMTE_ID, ZIP_CODE) in dByZip:
                    dByZip[(CMTE_ID,ZIP_CODE)][0].add(float(TRANSACTION_AMT)) 
                    dByZip[(CMTE_ID,ZIP_CODE)][1] = dByZip[(CMTE_ID,ZIP_CODE)][0].get_median()
                    dByZip[(CMTE_ID,ZIP_CODE)][2] += 1
                    dByZip[(CMTE_ID,ZIP_CODE)][3] += float(TRANSACTION_AMT)
                else:
                    rmedian = RunningMedian()
                    rmedian.add(float(TRANSACTION_AMT)) 
                    dByZip[(CMTE_ID,ZIP_CODE)].append(rmedian)
                    dByZip[(CMTE_ID,ZIP_CODE)].append(int(round(float(TRANSACTION_AMT)))) #median to be round to whole number
                    dByZip[(CMTE_ID,ZIP_CODE)].append(1)
                    dByZip[(CMTE_ID,ZIP_CODE)].append(float(TRANSACTION_AMT))
                f_outputZip.write('{0}|{1}|{2}|{3}|{4}\n'.format(CMTE_ID, ZIP_CODE, dByZip[(CMTE_ID,ZIP_CODE)][1], dByZip[(CMTE_ID,ZIP_CODE)][2], ('%f' % dByZip[(CMTE_ID,ZIP_CODE)][3]).rstrip('0').rstrip('.')))

def processByDate(pathInput):
    """
    This function take each line of the input file as if that record was sequentially streaming into your program as input.
    Each line of this second output file should list every unique combination of date and recipient from the input file with calculated total contributions and median contribution for that combination of date and recipient.
    The fields on each pipe-delimited line of medianvals_by_date.txt should be date, recipient, total number of transactions, total amount of contributions and median contribution. 
    Output file has lines sorted alphabetical by recipient and then chronologically by date.
    
    Parameters
    ----------
    line: string
        One record from input file.

    Returns
    -------
    no return value. It just writes the processed lines to output file
    """
 
    dByDate = defaultdict(list) #dictionary of lists, key is a tuple of recipent ID and Date
    fields = []
    with open(pathInput, 'r') as f_input, open(pathOutputDate, 'w') as f_outputDate:
        for line in f_input:
            del fields[:]
            line = removeSpace(line)
            if checkValidLine(line)[1] : #valid to go to be processed for output-by-date
                fields = line.split("|")
                CMTE_ID, TRANSACTION_DT, TRANSACTION_AMT = fields[0], fields[13], fields[14]
                if (CMTE_ID, TRANSACTION_DT) in dByDate:
                    dByDate[(CMTE_ID,TRANSACTION_DT)][0].add(float(TRANSACTION_AMT))
                    dByDate[(CMTE_ID,TRANSACTION_DT)][1] += 1
                    dByDate[(CMTE_ID,TRANSACTION_DT)][2] += float(TRANSACTION_AMT)
                else:
                    rmedian = RunningMedian()
                    rmedian.add(float(TRANSACTION_AMT))
                    dByDate[(CMTE_ID,TRANSACTION_DT)].append(rmedian)
                    dByDate[(CMTE_ID,TRANSACTION_DT)].append(1)
                    dByDate[(CMTE_ID,TRANSACTION_DT)].append(float(TRANSACTION_AMT))

        dByDate = OrderedDict(sorted(dByDate.items(), key=lambda t: (t[0][0],int(t[0][1][4:8]+t[0][1][2:4]+t[0][1][0:2]))))
        for (i,j) in dByDate:
            f_outputDate.write('{0}|{1}|{2}|{3}|{4}\n'.format(i, j, dByDate[(i,j)][0].get_median(), dByDate[(i,j)][1], ('%f' % dByDate[(i,j)][2]).rstrip('0').rstrip('.')))


if __name__ == '__main__':
    #start_time = time.time()
    try:
        pathInput = sys.argv[1] 
        pathOutputZip = sys.argv[2]
        pathOutputDate = sys.argv[3]
    except IndexError:
        print("The number of parameters given was insufficient. You need to provide 3: the input file and two output files")

    # Exists those files?
    if not os.path.isfile(pathInput):
        print("The given input file does not exist\n")
        sys.exit()

    try:
        f = open(pathOutputZip, 'w')
        f.close()
    except IOError:
        print("The given output file does not exist or can't be created\n")
        sys.exit()

    try:
        f = open(pathOutputDate, 'w')
        f.close()
    except IOError:
        print("The given output file does not exist or can't be created\n")
        sys.exit()

    processByZip(pathInput)
    #print("--- %s seconds ---" % (time.time() - start_time))
    processByDate(pathInput)
    #print("--- %s seconds ---" % (time.time() - start_time))


    
