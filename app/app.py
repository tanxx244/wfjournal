from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
from apphelper import example, storeData, exportData, recentfiller, netsRate, commision

app = Flask(__name__)

details = []
summary = []

@app.route('/')
def index():
    return render_template('index.html', summary=summary)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    tempname = ''
    tempinv = ''
    temppro = ''
    if len(details) > 0:
        tempname = details[-1]['name']
        tempinv = details[-1]['invoice']
        temppro = details[-1]['procedure']

    if request.method == 'POST':
        name = request.form['name']
        invoice = request.form['invoice']
        procedure = request.form['procedure']
        chas = request.form['chas']
        cash = request.form['cash']
        paynow = request.form['paynow']
        nets = request.form['nets']
        insurance = request.form['insurance']
        labmat = request.form['labmat']
        amount = str(float(cash) + float(paynow) + float(nets))
        bc = str(netsRate * float(nets))
        total = str(float(amount) - float(bc) - float(labmat))
        nettotal = str(commision * float(total))

        if 'add' in request.form:
            if request.form['add'] == "Add Detail":
                details.append({
                    'date'      : datetime.today().strftime('%Y-%m-%d'),
                    'name'      : name,
                    'invoice'   : invoice,
                    'procedure' : procedure,
                    'amount'    : amount,
                    'chas'     : chas,
                    'cash'      : cash,
                    'paynow'    : paynow,
                    'nets'      : nets,
                    'insurance' : insurance,
                    'bc'        : bc,
                    'labmat'    : labmat,
                    'total'     : total,
                    'nettotal'  : nettotal
                })
                return redirect(url_for('create'))
        elif 'remove' in request.form:
            if request.form['remove'] == "Remove Last Detail":
                if len(details) > 0:
                    details.pop()
                return redirect(url_for('create'))
        elif 'submit' in request.form:
            if request.form['submit'] == "Submit":
                if len(details) > 0:
                    return redirect(url_for('verify'))
                return redirect(url_for('create'))
        
    return render_template('create.html', details=details, tempname=tempname, 
        tempinv=tempinv, temppro=temppro)

@app.route('/verify/', methods=('GET', 'POST'))
def verify():
    summary = recentfiller(details)
    if request.method == 'POST':
        if request.form['submit'] == "Yes":
            storeData(details)
            details.clear()
            return redirect(url_for('index'))
        elif request.form['submit'] == "No":
            details.clear()
            return redirect(url_for('index'))
    return render_template('verify.html', summary=summary)

@app.route('/export/', methods=('GET', 'POST'))
def export():
    if request.method == 'POST':
        exportpath = request.form['exportpath']
        startyear = request.form['startyear']
        startmth = request.form['startmth']
        endyear = request.form['endyear']
        endmth = request.form['endmth']

        if not exportpath:
            flash('Export path is required!')
        elif not startyear:
            flash('Start Year is required!')
        elif not startmth:
            flash('Start Month is required!')
        elif not endyear:
            flash('End Year is required!')
        elif not endmth:
            flash('End Month is required!')
        else:
            exportData(int(startyear), int(startmth), int(endyear), int(endmth), exportpath)
            return redirect(url_for('index'))
    return render_template('export.html')