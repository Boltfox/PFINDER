from flask import Flask, render_template, url_for, request, redirect
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import glob
import os
import shutil
from sqlalchemy import create_engine
import json

global files_loaded
files_loaded = False

with open("config.json", "r") as f:
    config_dict = json.load(f)


pj = config_dict['current_project']

sd = os.path.dirname(os.path.abspath(__file__))
#pj = 'HTRUS'

#import riptide
#from candidate.py import Candidate
global FFA_img_path
FFA_img_path=sd+"/static/images/"+pj #path to images(.png) from the ffa 
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
app.config['SQLALCHEMY_DATABASE_URI'] = config_dict['database_uri']


def create_db(app):
    db = SQLAlchemy(app)
    return db
db = create_db(app)



class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.id

#db.create_all()
#global rowtoid
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        new_project_name = request.form['new_project_name']
        update_project_name(new_project_name)
        return redirect('/')
    return render_template('config.html')


def update_project_name(new_project_name):
    global config_dict  # Declare config_dict as global if it's defined outside this function
    
    # Update the configuration dictionary
    config_dict['current_project'] = new_project_name
    config_dict['database_uri'] = f'sqlite:///{new_project_name}.db'
    
    # Save the updated configuration back to the JSON file
    with open("config.json", "w") as f:
        json.dump(config_dict, f)
    
    print("Configuration updated. Please restart the application.")


def rename_folder_and_db(old_project_name, new_project_name):
    # Rename image folder
    old_folder_path = os.path.join(sd, "static", "images", old_project_name)
    new_folder_path = os.path.join(sd, "static", "images", new_project_name)
    shutil.move(old_folder_path, new_folder_path)
    
    # Rename database
    old_db_path = f"{old_project_name}.db"
    new_db_path = f"{new_project_name}.db"
    os.rename(old_db_path, new_db_path)



def rowtoid(row):
    row_ = compare_rowtoid()
    if row < len(row_):  # Check if the index is within the range of the list
        return row_[row]
    else:
        return None  # Return None or some other value to indicate that the index is out of range


def compare_rowtoid():
    row_list=[]
    for i in Todo.query.all():
        row_list.append(i.id)
    return row_list

def get_ffa_images():
    global FFA_list_file #Call global parameter FFA_list_file 
    global FFA_img_path #Call the path
    FFA_list_file=sorted(glob.glob(FFA_img_path+'/*.png'))
    print("We have"+str(len(FFA_list_file)))
    print("/homes/jompoj/PFINDER"+FFA_img_path)
    #rint(FFA_list_file)

@app.route('/')
def plot():
    global FFA_list_file
    global current_row
    global current_id 
    global files_loaded

    if not files_loaded:
        load_files_to_db()
    # Check if all images have been labeled
    if current_row >= len(FFA_list_file):
        current_row = 0  # Reset to the first image
        return render_template('index.html', message="You have labeled all the data. Starting over.")

    

    if len(FFA_list_file) == 0:
        return render_template('index.html', url='/static/images/welcome.png', url2='/static/images/C1_2020.pfd.png', sgan_score='1', pics_score='1', tasks=['Can not find images', 'None', 'none'], id='no images', name='Dummy')
    elif current_row < len(Todo.query.all()):
        current_id = rowtoid(current_row)
        tasks = Todo.query.order_by(Todo.id).all()
        return render_template('index.html', url='/static/images/'+pj+'/'+ FFA_list_file[current_row].split('/')[-1], url2='/static/images/C1_2020.pfd.png', sgan_score='1', pics_score='1', tasks=tasks, id=current_id)


@app.route('/')
def get_sgan_score():
    return 1

def check_and_create_db():
    db_path = os.path.join(os.getcwd(), 'htrusll.db')
    print(f"Checking database at {db_path}")
    if not os.path.exists(db_path):
        print("Database file not found. Creating a new one.")
        with app.app_context():  # Push an application context
            db.create_all()
        print("Database created.")


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
        elif request.form.get("change_project"):
            new_project_name = request.form["new_project_name"]
            update_project_name(new_project_name)
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
    global files_loaded
    if files_loaded:
        return  # Skip if files are already loaded
    
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
        files_loaded = True  # Set flag to True after first load

        #return redirect('/')
    except IndexError:
        return "No file in this project folder ok?"

if __name__ == "__main__":
    check_and_create_db()
    app.run(debug=True, port=1222)
