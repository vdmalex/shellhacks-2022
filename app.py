from xmlrpc.client import DateTime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)


app = Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# init database
db = SQLAlchemy(app)

class Message(db.Model):
    message_id = db.Column(db.Integer,primary_key=True)
    user_phone = db.Column(db.String(10),db.ForeignKey('volunteer.phone_num'))
    message = db.Column(db.String(500),nullable=False)

class Volunteer(db.Model):
    phone_num=db.Column(db.String(10),primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    hours=db.Column(db.Integer,nullable=False)

class Event(db.Model):
    event_id=db.Column(db.Integer,primary_key=True)
    host_id=db.Column(db.Integer,nullable=False)
    date_created=db.Column(db.String(10), default=datetime.utcnow)
    date=db.Column(db.String(10),nullable=False)
    hours=db.Column(db.Integer,nullable=False)
    name=db.Column(db.String(200),nullable=False)
    location=db.Column(db.String(200),nullable=False)
    description=db.Column(db.String(500),nullable=False)

class Host(db.Model):
    host_id=db.Column(db.Integer,primary_key=True)
    phone_num=db.Column(db.String(10))
    organization=db.Column(db.String(200),nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.organization
class Hosts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    host_id=db.Column(db.Integer)
    event_id=db.Column(db.Integer)

class Attends(db.Model):
    attending_id=db.Column(db.Integer,primary_key=True)
    volunteer_num=db.Column(db.String(10),db.ForeignKey('volunteer.phone_num'))
    event_id=db.Column(db.Integer,db.ForeignKey('event.event_id'))

@app.route('/generate',methods=['POST','GET'])
def generate():
    msg=''

    host = [
    ['YMCA','2392759622']
    ,['Food Bank','2393347007']
    ,['Habitat for Humanity','2396520434']
    ,['Salvation Army','2392781551']
    ,['Goodwill','2399952106']
]
    try:
        elete=db.session.query(Host).delete()
        db.session.commit()
    except:
        db.session.rollback()
    for i in host:
        new_host = Host(organization=i[0],phone_num=i[1])
        try:
            db.session.add(new_host) # db.session.delete(user_to_delete)
            db.session.commit()
        except:
            print(f'error on {new_host.organization}')

    msg+= 'Generated Host '

    volunteer =[
        ['1235239837','Alex van der Meulen',2],
        ['4079872931','Kaden Carr', 25],
        ['9287441210','Ronald Chatalier',200]
    ]
    try:
        elete=db.session.query(Volunteer).delete()
        db.session.commit()
    except:
        db.session.rollback()
    for v in volunteer:
        new_volunteer=Volunteer(phone_num=v[0],name=v[1],hours=v[2])
        try:
            db.session.add(new_volunteer)
            db.session.commit()
        except:
            print(f'error on {new_volunteer.name}')
    msg+='\nVolunteer generated '
    try:
        elete=db.session.query(Event).delete()
        db.session.commit()
    except:
        db.session.rollback()

    try:
        elete=db.session.query(Attends).delete()
        db.session.commit()
        msg+='Generated Attends'
    except:
        db.session.rollback()

    try:
        elete=db.session.query(Hosts).delete()
        db.session.commit()
    except:
        db.session.rollback()



    event = [
        [1,	'2022-09-10',	'2022-09-10',	3,	'Program Volunteers',	'1360 Royal Palm Square Blvd, Fort Myers, FL 33919',	'Read to children in our Kids Zone, greet members at the membership services desk, coach one of our youth sports teams and more.'],
        [1, '2022-09-10',	'2022-09-10',	3,	'Special Event Volunteers',	'1360 Royal Palm Square Blvd, Fort Myers, FL 33919',	'In small groups or as individuals these volunteers perform tasks during a special event such as 5k races, Healthy Kids Day, or a golf tournament.']
    ]
    for e in event:
        try:
            new_event=Event(host_id=1,date=e[2],hours=e[3],name=e[4],location=e[5],description=e[6])
            db.session.add(new_event)
            db.session.commit()
            msg+='Generated Event'
        except:
            print('error generating event')
    
    
    return render_template('home.html',msg=msg)



@app.route('/add',methods=['POST','GET'])
def add():
    if request.method=="POST":
        name=request.form['name'] #form input name
        phone=request.form['phone']#
        new_host=Host(organization=name,phone_num=phone)
        print(new_host)
        try:
            db.session.add(new_host) # db.session.delete(user_to_delete)
            db.session.commit()
        except:
            print(f'error on {new_host.organization}')

        return render_template('add.html')

    else:
        return render_template('add.html')



@app.route('/addevent',methods=['POST','GET'])
def addevent():
    if request.method == "POST":
        try:
            host_id = Host.query.filter_by(organization=request.form['host']).first().host_id
            if host_id is not None:
                date=(request.form['date'])[:10] # date format issues...
                hours=request.form['hours']
                name=request.form['name']
                location=request.form['location']
                description=request.form['desc']
                new=Event(host_id=host_id,date=date,hours=hours,name=name,location=location,description=description)
                try:
                    db.session.add(new)
                    db.session.commit()
                    new_hosts_event=Hosts(host_id=new.host_id,
                    event_id=new.event_id)
                    db.session.add(new_hosts_event)
                    db.session.commit()
                except:
                    print(f'error on {new.name}')
        except:
            msg='No such organization!'
            return render_template('addevent.html',msg=msg)
    else:
        return render_template('addevent.html')

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('login.html')

@app.route('/showevents',methods=['POST','GET'])
def showevents():
    hosts = Host.query.order_by(Host.host_id).all()
    names = []
    #print(hosts)
    events = db.session.query(Event,Host).filter(Event.host_id==Host.host_id)#Event.query.order_by(Event.date_created)

    return render_template("showevents.html",events=events)

@app.route('/attend/<int:id>')
def attend(id):
    volunteer_phone= '4079872931'

    #if not already attending...
    if Attends.query.filter(Attends.event_id==id,Attends.volunteer_num==volunteer_phone).count()==0:

        try:
            new_attends = Attends(volunteer_num=volunteer_phone,event_id=id)
            db.session.add(new_attends)
            db.session.commit()
        except:
            return 'error adding thing'
            
    else:
        return 'already attendintg'

    return redirect('/showevents') 

@app.route('/viewhistory/<int:id>')
def viewhistory(id):
    #return 'hi'
    if not id:
        id =1
    events = db.session.query(Event,Attends,Host).filter(Event.event_id==Attends.event_id,Host.host_id==Event.host_id,Attends.volunteer_num==id)
    for e,a,h in events:
        print(e.name,a.volunteer_num,h.organization)
    return render_template('viewhistory.html', events=events)

@app.route('/new')
def new():
    #colt steel
    events = db.session.query(Event,Attends,Host).filter(Event.event_id==Attends.event_id,Host.host_id==Event.host_id,Attends.volunteer_num=='4079872931')
    for e,a,h in events:
        print(e.name,a.volunteer_num,h.organization)
    return render_template('new.html', events=events)

@app.route('/data')
def data(): 
    events = db.session.query(Event,Host).filter(Event.host_id==Host.host_id)
    for e,h in events:
        print(f'e.name {e.name}')
    return render_template('data.html',events=events)

@app.route('/about')
def about():
    return render_template('about.html')