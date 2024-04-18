from flask import Flask, redirect, url_for, request, Response, render_template, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'n49m46dve2'
app.config['MYSQL_DB'] = 'electoral_bond'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # q1 = request.form['q1']
        q2 = request.form.get('q2')
        query = request.form.get('query')
        # sqlquery = 'SELECT * FROM partybond WHERE BOND_NUMBER LIKE %s'
        # searchquery = '%' + query + '%'
        if q2 == 'Bond_Number' or q2 == 'Party' or q2 == 'Denomination' or q2 == 'Payteller':

            cursor = mysql.connection.cursor()
            cursor.execute(f'SELECT Bond_Number,Party,Denomination FROM partybond WHERE {q2} = %s', (query,))
            records = cursor.fetchall()
            cursor.close()
            return render_template('result.html', records=records, name=q2)
        # elif q2 == None:
        #     return redirect('nbonds')
        else:
            cursor = mysql.connection.cursor()
            cursor.execute(f'SELECT Bondnumber,Company,Denominations FROM companybond WHERE {q2} = %s', (query,))
            records = cursor.fetchall()
            cursor.close()
            return render_template('resultcomp.html', records=records, name=q2)

    return render_template('search.html')


@app.route('/nbonds', methods=['GET', 'POST'])
def nbonds():
    if request.method == 'POST':
        q3 = request.form.get('Company')
        cursor = mysql.connection.cursor()
        cursor.execute(
            f'SELECT YEAR(Purchasedate) AS year, COUNT(*) AS bond_count, SUM(Denominations) AS total_value FROM companybond WHERE Company = %s GROUP BY YEAR(Purchasedate)',
            (q3,))
        records = cursor.fetchall()
        cursor.close()
        return render_template('q1e2results.html', records=records)

    return render_template('q1e2.html')


@app.route('/nbondsparty', methods=['GET', "POST"])
def nbondsparty():
    if request.method == 'POST':
        q4 = request.form.get('Party')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT YEAR(Purchasedate) AS year,Party as party, COUNT(*) AS bond_count, SUM(Denomination) AS total_value FROM partybond WHERE Party = %s GROUP BY YEAR(Purchasedate)',
            (q4,))
        records = cursor.fetchall()
        cursor.close()
        party = [row[1] for row in records]
        bonds = [row[2] for row in records]
        tot = [row[3] for row in records]
        return render_template('q1e3results.html', records=records)

    return render_template('q1e3.html')


@app.route('/companyparty', methods=['GET', 'POST'])
def companyparty():
    if request.method == 'POST':
        q5 = request.form.get('Companyname')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT Party,Bond_Number,Denomination FROM partybond WHERE Bond_Number IN (SELECT Bondnumber FROM companybond WHERE Company = %s)',
            (q5,))
        records = cursor.fetchall()
        combined_donation_amount = sum(int(row[2]) for row in records)
        # print(records)
        cursor.close()
        return render_template('q1e4result.html', records=records, combined_donation_amount=combined_donation_amount)
    return render_template('q1e4.html')


@app.route('/partycompany', methods=['GET', 'POST'])
def partycompany():
    if request.method == 'POST':
        q6 = request.form.get('Partyname')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT Company,Bondnumber,Denominations FROM companybond WHERE Bondnumber IN (SELECT Bond_Number FROM partybond WHERE Party = %s)',
            (q6,))
        records = cursor.fetchall()
        # print(records)
        combined_donation_amount = sum(int(row[2]) for row in records)
        cursor.close()
        return render_template('q1e5result.html', records=records, combined_donation_amount=combined_donation_amount)
    return render_template('q1e5.html')

@app.route('/pie')
def pie():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Party, SUM(Denomination) AS total_donation FROM partybond GROUP BY Party")
    party_donations = cursor.fetchall()
    cursor.close()
    # print(party_donations)
    party_labels = [row[0] for row in party_donations]
    donation_amounts = [row[1] for row in party_donations]

    return render_template('q1e6.html', party_labels=party_labels, donation_amounts=donation_amounts)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8900", debug=True)
