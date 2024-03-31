from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from flask import flash, redirect, render_template, request, url_for

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

class Event(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  date = db.Column(db.Date, nullable=False)
  location = db.Column(db.String(100), nullable=False)

  def __init__(self, name, date, location):
      self.name = name
      self.date = date
      self.location = location

with app.app_context():
    db.create_all()






  

@app.route('/register', methods=['GET', 'POST'])
def register():
      if request.method == 'POST':
          name = request.form['name']
          email = request.form['email']
          password = request.form['password']

          existing_user = User.query.filter_by(email=email).first()
          if existing_user:
              flash('An account with this email already exists. Please use a different email.', 'error')
              return redirect(url_for('register'))

          new_user = User(name=name, email=email, password=password)
          db.session.add(new_user)
          db.session.commit()
          flash('Registration successful. You can now log in.', 'success')
          return redirect('/login')

      return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/home')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')
  

@app.route('/add_events', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Retrieve data from the form
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_location = request.form['event_location']

        try:
            # Create a new Event object and add it to the database
            new_event = Event(name=event_name, date=event_date, location=event_location)
            db.session.add(new_event)
            db.session.commit()
            print("Adding event:", event_name, event_date, event_location)


          
            # Redirect to the events page after adding the event
            return redirect(url_for('events'))
        except Exception as e:
            # Handle any exceptions that occur during database operation
            return f"An error occurred: {str(e)}"
    else:
        # If it's a GET request, render the add_event_form.html template
        return render_template('add_events.html')

@app.route('/manage_events',methods=['GET','POST'])
def manage_events():
  try:
      # Fetch all events from the database
      events = Event.query.all()

      # Check if there are any events
      if events:
          return render_template('manage_events.html', events=events)
      else:
          return "No events found."  # Display a message if no events are found
  except Exception as e:
      return f"An error occurred: {str(e)}" 



@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

@app.route("/")
def index():
  return render_template("index.html")


@app.route("/sales")
def sales():
  return render_template("sales.html")

@app.route("/home")
def home():
  return render_template("home.html")
@app.route("/events")
def events():
  return render_template("events.html")


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
