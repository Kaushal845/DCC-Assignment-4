from flask import Flask, redirect, url_for, request, Response, render_template, jsonify
from flask_mysqldb import MySQL
import requests

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'n49m46dve2'
app.config['MYSQL_DB'] = 'electoral_bond'

mysql = MySQL(app)


def indian_number(number):
    s, *d = str(number).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return "".join([r] + d)


# Add the filter to the Jinja environment
app.jinja_env.filters['indian_number'] = indian_number

API_KEY = 'YOUR_GOOGLE_API_KEY'
SEARCH_ENGINE_ID = 'YOUR_SEARCH_ENGINE_ID'

def fetch_info(name):
    search_url = f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBxx1YHuQp2MlY_rW2pKPiPzCePX9rspQ0&cx=071a0f1918a4847ce&q={name}"
    response = requests.get(search_url)
    if response.status_code == 200:
        search_results = response.json()
        if 'items' in search_results:
            return search_results['items'][0]  # Get the first result
    return None

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
        cursor.execute('SELECT DISTINCT(Company) FROM companybond')
        name = cursor.fetchall()
        cursor.execute(
            f'SELECT YEAR(Purchasedate) AS year, COUNT(*) AS bond_count, SUM(Denominations) AS total_value FROM companybond WHERE Company = %s GROUP BY YEAR(Purchasedate)',
            (q3,))
        records = cursor.fetchall()
        cursor.close()
        company_info = fetch_info(q3)
        cname = q3
        return render_template('q1e2results.html', records=records, company_info=company_info, cname=cname)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT DISTINCT(Company) FROM companybond')
    name = cursor.fetchall()

    return render_template('q1e2.html', names=name)


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
        pinfo = fetch_info(q4)
        pname = q4
        return render_template('q1e3results.html', records=records,pinfo=pinfo,pname=pname)

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT DISTINCT(Party) FROM partybond ORDER BY Party')
    name = cursor.fetchall()

    return render_template('q1e3.html', names=name)


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
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT DISTINCT(Company) FROM companybond ORDER BY Company')
    name = cursor.fetchall()
    return render_template('q1e4.html',names=name)


@app.route('/partycompany', methods=['GET', 'POST'])
def partycompany():
    if request.method == 'POST':
        q6 = request.form.get('Partyname')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT DISTINCT(Party) FROM partybond')
        name = cursor.fetchall()
        cursor.execute(
            'SELECT Company,Bondnumber,Denominations FROM companybond WHERE Bondnumber IN (SELECT Bond_Number FROM partybond WHERE Party = %s)',
            (q6,))
        records = cursor.fetchall()
        # print(records)
        combined_donation_amount = sum(int(row[2]) for row in records)
        cursor.close()
        return render_template('q1e5result.html', records=records, combined_donation_amount=combined_donation_amount)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT DISTINCT(Party) FROM partybond')
    name = cursor.fetchall()
    return render_template('q1e5.html',names=name)


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
