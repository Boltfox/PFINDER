from flask import Flask, render_template, url_for, request, redirect
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import glob
import os


#import riptide
#from candidate.py import Candidate
global FFA_img_path
FFA_img_path='/static/images/HTRUS/' #path to images(.png) from the ffa 
global FFA_list_file
FFA_list_file=[]

global presto_img_path
presto_img_path='/home/jompoj/HTRU-S_results' #path to images(.png) from the presto ((To be implemented in the future))
global presto_list_file
presto_list_file=[]

global presto_pfd_img_path
presto_pfd_img_path='/home/jompoj/HTRU-S_results' #path to archives(.pfd) from the presto ((To be implemented in the future with sgan and pics))
global presto_pfd_list_file
presto_pfd_file=[]
global current_id #Global dummy id for id 
current_id = 0

global current_row #Global dummy id for row
current_row = 0




app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = FFA_img_path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///htrusll.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.id


#global rowtoid


def rowtoid(row):
    row_=compare_rowtoid()
    return row_[row]

def compare_rowtoid():
    row_list=[]
    for i in Todo.query.all():
        row_list.append(i.id)
    return row_list

def get_ffa_images():
    global FFA_list_file #Call global parameter FFA_list_file 
    global FFA_img_path #Call the path
    FFA_list_file=sorted(glob.glob('/homes/jompoj/PFINDER'+FFA_img_path+'/*.png'))
    #rint(FFA_list_file)

@app.route('/')
def plot():
    global FFA_list_file
    global current_row
    global current_id
    #Todo.query.delete()
    load_files_to_db()
    if len(FFA_list_file)==0:
        return render_template('index.html', url='/static/images/welcome.png', url2='/static/images/C1_2020.pfd.png', sgan_score='1', pics_score='1', tasks=['Can not find images','None','none'], id='no images', name='Dummy')
    elif current_row<=len(Todo.query.all()):
        current_id=rowtoid(current_row)
        tasks = Todo.query.order_by(Todo.id).all()
        #return render_template('plot.html', url=FFA_list_file[0])
        return render_template('index.html', url='/static/images/HTRUS/'+FFA_list_file[current_row].split('/')[-1] , url2='/static/images/C1_2020.pfd.png', sgan_score='1', pics_score='1', tasks=tasks, id=current_id)


@app.route('/')
def get_sgan_score():
    return 1

#@app.route('/', methods=['POST', 'GET'])
#def uploadfile(): 
#    if request.method == 'POST':
#        task_content = request.form['content']
#        new_task = Todo(content=task_content)


@app.route('/', methods=['POST', 'GET'])
def submit(): 
    global current_row
    global current_id
    global rowtoid
    #return request.form
    if request.method == "POST":
        if request.form.get("RFI"):
            score=0
        elif request.form.get("Known"):
            score=5
        elif request.form.get("HarmKnown"):
            score=4    
        elif request.form.get("ClassA"):
            score=3
        elif request.form.get("ClassB"):
            score=2
        elif request.form.get("back"):
            score=-999 #Using -999 to tell the function update() not to update
        elif request.form.get("next"):
            score=999 #Using 999 to tell the function update() not to update
        elif request.form.get("jump_to"):
            score=-1000
            id_to=request.form["content"]
            current_id=int(id_to)
            #return str(id_to)
        elif request.form.get("restart"):
            Todo.query.delete()
            db.session.commit()
            return redirect('/')
    update(score)
    return redirect('/')

def back():
    global current_row
    global current_id
    global rowtoid
    current_id=rowtoid(current_row-1)
    current_row=current_row-1

def next():
    global current_row
    global current_id
    global rowtoid
    current_id=rowtoid(current_row+1)
    current_row=current_row+1


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        compare_rowtoid()
        return redirect('/')
        
    except:
        return 'There was a problem deleting that task'

def update(score):
    global current_id
    global rowtoid
    global current_row
    if score == 999:
        next()
    elif score == -999:
        back()
    elif score < 10:
        task = Todo.query.get(current_id)
        task.score = score
        db.session.commit()
        next()

        

def load_files_to_db():
    get_ffa_images()
    global FFA_list_file
    try:
        for i in FFA_list_file:
            print(i)
            if bool(Todo.query.filter_by(name=i).first()):
                print("The file is here")
            else:
                new_file = Todo(name=i)
                db.session.add(new_file)
                db.session.commit()
                print("Add the file to the database")
        #return redirect('/')
    except IndexError:
        return "No file in this project folder"

if __name__ == "__main__":
    app.run(debug=True, port=1222)
