from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model import run

import requests
import json
api_key = 'api_key=27989ba887194f26874a5e95813460ab'
api_search = 'https://api.themoviedb.org/3/search/movie?'
api_movie = 'https://api.themoviedb.org/3/movie/'

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wtdauhzrayrzjv:283578ae8e61abbd97942e7b656ad37e78f25eb3f0b681e50231b443952cf0b6@ec2-44-207-133-100.compute-1.amazonaws.com:5432/db88smvb6sau0p'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    predicted = db.Column(db.Float, default=0)
    actual = db.Column(db.Float, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

# db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        searchName = request.form['search']
        responseData = run(searchName)
        new_task = Todo(name=responseData[2], content=str(responseData[0]), predicted=responseData[1], actual=responseData[3])
        print(new_task)
        for i in responseData:
            print(i)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue searching for your movie'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/more')
def more():
    return render_template('more.html')

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the task'

@app.route('/view/<int:id>', methods=['GET'])
def view(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem updating the task'
    else:
        return render_template('view.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)