from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime 

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pass_root'
app.config['MYSQL_DB'] = 'cpa'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)
@app.route('/')
def indx():
    return render_template('login4.html')

# Route to render the form
@app.route('/')
def index():
    return render_template('form.html')

@app.route('/')
def inx():
    return render_template('etude.html')

@app.route('/')
def inde():
    return render_template('validation.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Fetch form data
        id_client = request.form['id_client']
        num_compte = request.form['num_compte']
        nom = request.form['nom'] or None
        prenom = request.form['prenom'] or None
        raison_sociale = request.form['raison_sociale'] or None
        activite = request.form['activite'] or None
        adresse = request.form['adresse']
        numerotel = request.form['numerotel']
        date_ouverture = request.form['date_ouverture']
        date_cloture = request.form['date_cloture'] or None
        cause = request.form['cause'] or None
        num_reg_com = request.form['num_reg_com']
        date_reg_com = request.form['date_reg_com']
        code_agence = request.form['code_agence']


        daterecp = request.form['date_reception']  # Assuming this is from the session date
        dateenvoi = datetime.now().strftime('%Y-%m-%d')  # Fetch from form if available
        etat = None  # Fetch from form if available
        descriptif = None
        id_client = request.form['id_client']
        folio=  'F1' # Fetch from form if available
        
        # Insert into MySQL
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO dossier (ID_CLIENT, NUM_COMPTE, NOM, PRENOM, RAISON_SOCIALE, ACTIVITE, ADRESSE, NUMEROTEL, DATE_OUVERTURE, DATE_CLOTURE, CAUSE, NUM_REG_COM, DATE_REG_COM, CODE_AGENCE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s)",
                    (id_client, num_compte, nom, prenom, raison_sociale, activite, adresse, numerotel, date_ouverture, date_cloture,  cause, num_reg_com, date_reg_com, code_agence))
        mysql.connection.commit()

        cur.execute("""
            INSERT INTO datetransmis (DATERECP, DATEENVOI, ETAT, DESCRIPTIF, ID_CLIENT, FOLIO)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (daterecp, dateenvoi, etat, descriptif, id_client, folio))

        mysql.connection.commit()
        cur.close()

        return 'Successfully submitted dossier form!'
    else:
        return 'Method not allowed'

if __name__ == '__main__':
    app.run(debug=True)
