from flask import Flask, render_template, request, redirect, url_for, session , jsonify
from flaskext.mysql import MySQL
from datetime import datetime
import json

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass_root'
app.config['MYSQL_DATABASE_DB'] = 'cpa'

mysql = MySQL()
mysql.init_app(app)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Route to render the login form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle login form submission
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute("SELECT folio, mdp, nom, prenom, qualite FROM utilisateur WHERE folio = %s AND mdp = %s", (username, password))
            user = cur.fetchone()
            cur.close()

            if user:
                print(f"User data fetched: {user}")  # Print user data for debugging
                qualite = user[4]  # Accessing qualite from tuple
                session['folio'] = user[0]  # Store folio in session
                if qualite == 'Secrétaire':
                    return render_template('secretaire.html')
                elif qualite == 'Charge étude':
                    return render_template('etude.html')
                elif qualite == 'Charge de validation':
                    return render_template('validation.html')
                elif qualite == 'Directeur':
                    return render_template('directeur.html')
                else:
                    print(f"Unknown qualite: {qualite}")  # Debug print for unknown roles
                    return render_template('index.html')
            else:
                print("User not found or incorrect password")  # Print debug message for login failure
                return render_template('index.html')  # Render index.html or handle as needed
        except Exception as e:
            print(f"Error executing MySQL query: {e}")
            return render_template('index.html')
        
@app.route('/get_agences')
def get_agences():
    try:
        conn = mysql.connect()  
        cursor = conn.cursor()
        query = "SELECT Code, intitule FROM agence;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()  
        if result:
            data = [{'code': row[0], 'intitule': row[1]} for row in result]
            return json.dumps(data)
        else:
            return json.dumps([])
    except Exception as e:
        print(f"Error fetching agences: {e}")
        return json.dumps([])
@app.route('/get_profit')
def get_profit():
    try:
        conn = mysql.connect()  
        cursor = conn.cursor()
        query = "SELECT d.idclient , d.raison_sociale, d.agence, d.num_compte, DATE_FORMAT(dt.daterecp, '%Y-%m-%d') FROM dossier d, datetransmis dt WHERE d.idclient = dt.idclient;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()  
        if result:
            data = [{'idclient': row[0], 'raison_sociale': row[1], 'agence': row[2], 'num_compte': row[3], 'daterecp': row[4]} for row in result]
            return jsonify(data)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error fetching profils: {e}")
        return jsonify([])

# Route to render secretaire.html and handle form submission
@app.route('/secretaire', methods=['GET', 'POST'])
def secretaire():
    if request.method == 'POST':
        # Fetch form data
        id_client = request.form['id_client']
        num_compte = request.form['num_compte']
        nom = request.form['nom'] or None
        prenom = request.form['prenom'] or None
        agence_id = request.form['agence']
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

        daterecp = request.form['date_reception']
        dateenvoi = datetime.now().strftime('%Y-%m-%d')
        etat = None
        descriptif = None
        folio = session.get('folio')

        try:
            conn = mysql.connect()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO dossier (idclient, raison_sociale, nom, prenom, num_compte, agence, ACTIVITE, date_ouverture, DATE_CLOTURE, adresse, NUMEROTEL, CAUSE, NUM_REG_COM, DATE_REG_COM, CODE_AGENCE)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (id_client, raison_sociale, nom, prenom, num_compte, agence_id, activite, date_ouverture, date_cloture, adresse, numerotel, cause, num_reg_com, date_reg_com, code_agence))

            cur.execute("""
                INSERT INTO datetransmis (DATERECP, DATEENVOI, ETAT, DESCRIPTIF, FOLIO, idclient)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (daterecp, dateenvoi, etat, descriptif, folio, id_client))

            conn.commit()
            cur.close()

            return redirect(url_for('secretaire'))
        
        except Exception as e:
            print(f"Error submitting dossier form: {e}")
            return 'An error occurred while submitting the dossier form.'

    return render_template('secretaire.html')

# Routes for different roles
@app.route('/etude')
def etude():
    return render_template('etude.html')

@app.route('/validation')
def validation():
    return render_template('validation.html')

@app.route('/directeur')
def directeur():
    return render_template('directeur.html')

if __name__ == '__main__':
    app.run(debug=True)

