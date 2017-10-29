"Find-Political-Donors" Code Challenge
=====================================
This is a Python3 solution to the Insight Data Engineering Code Challenge Oct 2017.

The main goal of this callenge is to identify possible donors for a variety of upcoming election campaigns. We are asked to do this by:
 	- Identifying the areas (zip codes) that may be fertile ground for soliciting future donations for similar candidates.
 	- Identify which dates are particularly lucrative so that an analyst might later correlate them to specific fundraising events.

Input file: It's a text file listing campaign contributions by individual donors. This file is in a folder called input in root directory of the project
Output files: The program generates two text files :
	- medianvals_by_zip.txt: contains a calculated running median, total dollar amount and total number of contributions by recipient and zip code
	- medianvals_by_date.txt: has the calculated median, total dollar amount and total number of contributions by recipient and date.


Approach
========
- Removing spaces from given record in input file: as pre processing step, we remove all spaces first then go to validation part.
- Validation of each record in input file: first I validate the record based on "input considerations" and go to next step if it is valid, otherwise ignore the line
- In method called processByZip: use a dictionary of lists with CMTE-ID and ZipCode as key and a list of four items as value as follows:
  first, an instance of a RunningMedian class is kept in this list. RunningMedian class initiates one min heap and one max heap. and each time add the coming transaction amount to the heaps w.r.t related CMTE_ID and Zip-Code.
  second, we calculate the running median based on the heaps created in first item. 
  third, a counter of contributions w.r.t key.
  fourth, total value of transactions amount have been processed w.r.t. key, so far.
- After processing each line, the related key and value in dictionary is printed into output file.

In order to write records to output folder by date, first, we take the same steps as what we did in processByOutput but we get the median at the end of file, when for each key in dictionary, the whole heap is created.
        

Requirements and dependencies
============
Standard libraries for Python3 have been used. 
Packages imported to my code: datetime, sys, os, collections.defaultdict, collections.OrderedDict, re, heapq


Run Instructions
=================
To run the solution on a Linux/UNIX system, simply execute the ./run.sh in the top-level directory:
or run this script within root directory
	python3 ./src/find_political_donors.py ./input/itcont.txt ./output/medianvals_by_zip.txt ./output/medianvals_by_date.txt

I have added a series of tests. They are located in folder tests. 
They all can be run by  executing ./runtests.sh when the current directory is set to insight_testsuite.

