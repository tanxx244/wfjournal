import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

netsRate = 0.8 / 100
commision = 0.4

example = [{
    'date'      : '2001-02-15', #datetime.today().strftime('%Y-%m-%d'),
    'name'      : 'Sherlock Holmes',
    'invoice'   : '007',
    'procedure' : 'scaling',
    'amount'    : 100,
    'chas'     : 10,
    'cash'      : 10,
    'paynow'    : 10,
    'nets'      : 10,
    'insurance' : 10,
    'bc'        : 10,
    'labmat'    : 10,
    'total'     : 100,
    'nettotal'  : 80
}]

column_name = ['Date', 'Name', 'Invoice Number', 'Procedure', 'Amount', 
    'CHAS Amount', 'Cash Amount', 'PayNow Amount', 'NETS Amount', 
    'Insurance Amount', 'B/C', 'Lab Material Cost', 'Total', 'Net Total']

#database path
parentpath = os.getcwd()
dbpath = os.path.abspath(parentpath + os.sep + os.pardir)
dbpath = os.path.abspath(dbpath + os.sep + 'data')

#columnSelector
def columnSelector(details, key):
    res = []
    for detail in details:
        res.append(detail[key])
    return res

#rowSelector
def rowSelector(details, rowNumber):
    res = []
    for key in details[rowNumber]:
        res.append(details[rowNumber][key])
    return res

#dictWrapper
def dictWrapper(colname, datalist):
    res = {}
    i = 0
    for key in colname:
        res[key] = datalist[i]
        i += 1
    return res

#storedata
def storeData(details):
    monthReports = [f for f in os.listdir(dbpath) if f.endswith(".csv")]
    check = np.array(monthReports)
    newEntry = details[-1]
    # newWrappedEntry = pd.DataFrame([dictWrapper(column_name, rowSelector(details, -1))])

    wrapperArray = []
    for i in range(len(details)):
        newWrap = dictWrapper(column_name, rowSelector(details, i))
        wrapperArray.append(newWrap)
    newWrappedEntry = pd.DataFrame(wrapperArray)
        
    newDate = newEntry['date']
    breakdown = newDate.split('-')
    targetfile = breakdown[0] + '-' + breakdown[1] + '.csv'
    if len(monthReports) <= 0:
        # newReport = pd.DataFrame(columns=column_name)
        # newReport.append(newWrappedEntry, ignore_index=True)
        newReport = newWrappedEntry
        newReport.to_csv(dbpath + '\\' + targetfile, index=False)
    else:
        if len(check[check == targetfile]) <= 0:
            # newReport = pd.DataFrame(columns=column_name)
            # newReport.append(newWrappedEntry, ignore_index=True)
            newReport = newWrappedEntry
            newReport.to_csv(dbpath + '\\' + targetfile, index=False)
        else:
            newReport = pd.read_csv(dbpath + '\\' + targetfile)
            # newReport.append(newWrappedEntry, ignore_index=True)
            newReport = pd.concat([newReport, newWrappedEntry]).reset_index(drop=True)
            newReport.to_csv(dbpath + '\\' + targetfile, index=False)

def chasInsuranceCalc(DF):
    newDF = DF[(DF['CHAS Amount'] > 0) | (DF['Insurance Amount'] > 0)]
    newDF = newDF[['Date', 'Name', 'Invoice Number', 'CHAS Amount', 
        'Insurance Amount']].copy()
    newDF['Total'] = newDF['CHAS Amount'] + newDF['Insurance Amount']
    newDF['Net Total'] = newDF['Total'] * commision
    return newDF.copy()

#exportdata
def exportData(startyear, startmth, endyear, endmth, exportpath):
    exportpath = os.path.abspath(exportpath)
    startdate = datetime(startyear, startmth, 1)
    enddate = datetime(endyear, endmth, 1)
    today = datetime.today().strftime('%Y-%m-%d')
    
    monthReports = [f for f in os.listdir(dbpath) if f.endswith(".csv")]
    check = np.array(monthReports)

    newDF = pd.DataFrame(columns=column_name)
    obsdate = startdate
    while enddate - obsdate >= timedelta(days = 0):
        obsdatestr = obsdate.strftime('%Y-%m')
        targetfile = obsdatestr + '.csv'
        if len(check[check == targetfile]) > 0:
            thisReport = pd.read_csv(dbpath + '\\' + targetfile)
            # newDF.append(thisReport, ignore_index=True)
            newDF = pd.concat([newDF, thisReport]).reset_index(drop=True)
        obsdate = obsdate + relativedelta(months=1)
    
    chasDF = chasInsuranceCalc(newDF)

    prepath = os.path.abspath(exportpath + '\\' + 'Report-Others' + '.' + today + '.csv')
    prepath2 = os.path.abspath(exportpath + '\\' + 'Report-CHAS-Insurance' + '.' + today + '.csv')
    newDF.to_csv(prepath, index=False)
    if not chasDF.empty:
        chasDF.to_csv(prepath2, index=False)

def strJoiner(s1, s2, delimiter):
    if s1 == '':
        return s2
    return s1 + delimiter + s2

def uniqueArray(arr):
    temp = []
    for x in arr:
        if x not in temp:
            temp.append(x)
    return temp

def detailsGrouper(details, key, sortkey):
    res = []
    for detail in details:
        if detail[key] == sortkey:
            res.append(detail)
    return res

def detailsSummary(details):
    date = details[0]['date']
    name = details[0]['name']
    invoice = details[0]['invoice']
    procedure = ''
    total = 0.0
    nettotal = 0.0
    for detail in details:
        procedure = strJoiner(procedure, detail['procedure'], ', ')
        total += float(detail['total'])
        nettotal += float(detail['nettotal'])
    total = str(round(total, 2))
    nettotal = str(round(nettotal,2))
    return {
        'date' : date,
        'name' : name,
        'invoice' : invoice,
        'procedure' : procedure,
        'total' : total,
        'nettotal' : nettotal
    }

def recentfiller(details):
    if len(details) <= 0:
        return []
    allInvoice = columnSelector(details, 'invoice')
    uniqueInvoice = uniqueArray(allInvoice)

    #date,name,invoice,procedure,total,nettotal
    res = []
    for invoice in uniqueInvoice:
        subdetails = detailsGrouper(details, 'invoice', invoice)
        subdetailsSummary = detailsSummary(subdetails)
        res.append(subdetailsSummary)
    return res