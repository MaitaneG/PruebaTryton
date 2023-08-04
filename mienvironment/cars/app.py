from flask import Flask, render_template, request, redirect, url_for, session, abort, g
from flask_tryton import Tryton
from datetime import datetime
from trytond.pyson import datetime
from functools import wraps

app = Flask(__name__)
app.config['TRYTON_DATABASE'] = 'tryton'
tryton = Tryton(app, configure_jinja=True)
WebUser = tryton.pool.get('web.user')
UserSession = tryton.pool.get('web.user.session')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


Marca = tryton.pool.get('cars.marca')
Modelo = tryton.pool.get('cars.modelo')
Coche = tryton.pool.get('cars.coche')
Party = tryton.pool.get('party.party')


def login_required(func):
  @wraps(func)
  def wrapper(*args,**kwargs):
    session_key=None
    if 'session_key' in session:
      session_key=session['session_key']
    g.user=UserSession.get_user(session_key)
    if not g.user:
      return redirect(url_for('login', next=request.path))
    return func(*args,**kwargs)
  return wrapper


@app.route('/login', methods=['GET', 'POST']) 
@tryton.transaction()
def login():
  if request.method == 'POST':
    username = request.form.get('correo')
    password = request.form.get('password')
    if username and password:
      user = WebUser.authenticate(username, password)
      if user:
        session['session_key'] = WebUser.new_session(user) 
        session['username'] = user.email
        if user.party:
          session['party'] = user.party.id
        next_ = request.form.get('next',None)
        if next_:
        
          return redirect (next_)
        return redirect('/')
      else:
        return 'Usuario Incorrecto'
  return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST']) 
@tryton.transaction()
def registro():
  if request.method == 'POST':
    partyNuevo=Party()
    partyNuevo.name = request.form.get('nombre','')
    partyNuevo.save()

    userNuevo=WebUser()
    userNuevo.email=request.form.get('correo')
    userNuevo.password=request.form.get('password')
    userNuevo.party=partyNuevo.id
    userNuevo.save()
    return redirect(url_for('marcas'))

  parties = Party.search([])
  return render_template('registro.html',parties=parties)


@app.route('/logout')
@tryton.transaction (readonly=False) 
@login_required
def logout():
  if session['session_key']:
    user_sessions = UserSession.search(
    [('key', '=', session['session_key'])]) 
    UserSession.delete(user_sessions)
    session.pop('session_key', None)
    session.pop('party', None)
    session.pop('username', None)
  return redirect(request.referrer if request.referrer else url_for('index'))


@app.route("/")
@tryton.transaction()
def marcas():
  marcas = Marca.search([])
  return render_template('marcas.html',marcas=marcas)


@app.route("/crear_marca", methods=['POST','GET'])
@tryton.transaction()
def crear_marca():
  if request.method=='POST':
    marcaNueva=Marca()
    marcaNueva.nombre = request.form.get('nombre','')
    marcaNueva.save()
    return redirect(url_for('marcas'))

  return render_template('crear_marca.html')

  
@app.route('/marca/<record("cars.marca"):marca>')
@tryton.transaction()
def marca(marca):
  modelos = Modelo.search([('marca','=',marca)])
  coches = Coche.search([('marca','=',marca)])
  return render_template('marca.html', marca=marca, coches=coches, modelos=modelos)


@app.route('/crear_modelo/<record("cars.marca"):marca>', methods=['POST','GET'])
@tryton.transaction()
def crear_modelo(marca):
  if request.method=='POST':
    modeloNuevo=Modelo()
    modeloNuevo.nombre = request.form.get('nombre','')
    modeloNuevo.marca = int(request.form.get('marca',0))
    modeloNuevo.combustible = request.form.get('combustible','')
    modeloNuevo.caballos = int(request.form.get('caballos',0))
    modeloNuevo.precio = int(request.form.get('precio',0))
    modeloNuevo.fecha_lanzamiento = datetime.date.today()
    modeloNuevo.save()
    return redirect(url_for('marca', marca=modeloNuevo.marca))

  combustible=Modelo.fields_get(['combustible'])['combustible']['selection']
  return render_template('crear_modelo.html', marca=marca, combustible=combustible)


@app.route('/modelo/<record("cars.modelo"):modelo>', methods=['POST','GET'])
@tryton.transaction()
def crear_coche(modelo):
  if request.method=='POST':
    cocheNuevo=Coche()
    cocheNuevo.matricula = request.form.get('matricula','')
    cocheNuevo.propietario = int(request.form.get('propietario',None))
    cocheNuevo.marca = int(request.form.get('marca',None))
    cocheNuevo.modelo = int(request.form.get('modelo',None))
    cocheNuevo.precio = int(request.form.get('precio',0))
    #cocheNuevo.fecha_matriculacion = request.form.get('fecha_matriculacion',None)
    #cocheNuevo.fecha_baja = request.form.get('fecha_baja',None)
    cocheNuevo.save()
    return redirect(url_for('marca', marca=cocheNuevo.marca.id))

  parties = Party.search([])
  return render_template('crear_coche.html', modelo=modelo, parties=parties)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
  return render_template('hello.html', name=name)