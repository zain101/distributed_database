from flask import Flask, render_template, session, redirect, url_for,request,Response
from flask import request
from flask.ext.bootstrap import Bootstrap
from flaskext.mysql import MySQL

mysql = None

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = '\xd0\xfd\x93\x19u\x98\xa3\xe04\x95S\x0e\xb7\x80\x85\x08\xbf\x07\x199\x0e]\xe5\xfc'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'indexer'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
 

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	username=None
	password=None
	headers = None
	if request.method=='POST':
 		username = request.form.get('username')
		password = request.form.get('password')
	if username==None or password==None:
		return render_template('login.html')
	conn = mysql.connect()
	cursor =conn.cursor()
	cursor.execute("select tablename from indexer.myindex where username='"+username+"'")
	db_name  = cursor.fetchall()[0][0]

	cursor.execute("select * from "+db_name+".user where username='"+username+"' and password='"+password+"'")
	data = cursor.fetchall()
	if data:
		print "login"
		session['login'] = True
		session['username'] = username
		headers = [i[0] for i in cursor.description]
		print session
		session['output_indexer'] = data
		session['headers'] = headers
	else:
		print "Failed ", db_name, data
		return render_template('login.html')
		# login_user(username, True)
	return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('username', None)
    return render_template('login.html')


@app.route('/dashboard')
def dash():
	try:

		if session['login']:
			return render_template('dashboard.html')
		else:
			return render_template('login.html')
	except:
		return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
	username = None
	password = None
	location = None
	if request.method=='POST':
 		username = request.form.get('username')
		password = request.form.get('password')
		location = request.form.get('location')
	try:	
		if session['login'] == True:
			return render_template('dashboard.html')
	except:
        	pass


	if username==None  or  password==None or location==None:
		return render_template('register.html', output="Some feild is empty")		
	else:

 		conn = mysql.connect()
		cursor =conn.cursor()
		
		count = cursor.execute("select * from myindex where username='"+username+"'") #sql3.py
		if count:
			return render_template('register.html', output="User already exist")
		table1 = cursor.execute("select count(id) from  first.user ")
		table1 = cursor.fetchall()[0][0]

		table2 = cursor.execute("select count(id) from second.user ")
		table2 = cursor.fetchall()[0][0]
		if table1>= table2:
			cursor.execute("INSERT INTO `second`.`user` (`id`, `username`, `password`, `location`) VALUES (NULL, '"+username+"', '"+password+"','"+location+"' );")
			cursor.execute("insert into `indexer`.`myindex` values('"+username+"', 'second')")
		else:
			cursor.execute("INSERT INTO `first`.`user` (`id`, `username`, `password`, `location`) VALUES (NULL, '"+username+"', '"+password+"','"+location+"' );")
			cursor.execute("insert into `indexer`.`myindex` values('"+username+"', 'first')")


		hv=cursor.fetchall()
		output= hv
		conn.commit()
		
		return render_template('register.html', output=output)
				

	return render_template('register.html')


@app.route('/viewdb')
def profile():
	try:	
		if session['login'] != True:
			return render_template('login.html')
	except:
        	return render_template('login.html')
	headers = ['Username','password']
	conn = mysql.connect()
	cursor =conn.cursor()
	cursor.execute("select * from indexer.myindex") #sql3.py
	hv=cursor.fetchall()
	conn.commit()
	output_indexer= hv
	num_fields = len(cursor.description)
	headers_indexer = [i[0] for i in cursor.description]


	cursor.execute("select * from first.user") #sql3.py
	hv=cursor.fetchall()
	conn.commit()
	output_first= hv
	num_fields = len(cursor.description)
	headers_first = [i[0] for i in cursor.description]


	cursor.execute("select * from second.user") #sql3.py
	hv=cursor.fetchall()
	conn.commit()
	output_second = hv
	num_fields = len(cursor.description)
	headers_second = [i[0] for i in cursor.description]

	return render_template('profile.html', output_indexer=output_indexer,  headers_indexer=headers_indexer,
		output_first=output_first, headers_first=headers_first,
		output_second=output_second, headers_second=headers_second
		)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


if __name__== '__main__':
	app.run(debug = True)
