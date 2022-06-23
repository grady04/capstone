from flask import render_template, request, redirect, url_for, flash
from .import bp as main
from flask_login import login_required, current_user
from app.models import Task, User, Comments

@main.route('/', methods=['GET','POST'])
@login_required
def tasks():
    tasks=current_user.ranch_tasks()
    return render_template('index.html.j2',tasks=tasks)

@main.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        body = request.form.get('body')
        new_task=Task(body=body, user_id=current_user.id, urgent=False, daily=False, completed=False)
        new_task.save()
        return redirect(url_for('main.tasks'))
    return render_template('create_task.html.j2')

@main.route('/create_urgent_task', methods=['GET', 'POST'])
@login_required
def create_urgent_task():
    if request.method == 'POST':
        body = request.form.get('body')
        new_task=Task(body=body, user_id=current_user.id, urgent=True, daily=False, completed=False)
        new_task.save()
        return redirect(url_for('main.tasks'))
    return render_template('create_urgent_task.html.j2')

@main.route('/create_daily_task', methods=['GET', 'POST'])
@login_required
def create_daily_task():
    if request.method == 'POST':
        body = request.form.get('body')
        new_task = Task(body=body, user_id=current_user.id, urgent=False, daily=True, completed=False)
        new_task.save()
        return redirect(url_for('main.tasks'))
    return render_template('create_daily_task.html.j2')

@main.route('/get_task/<int:id>', methods=['GET'])
@login_required
def get_task(id):
    task = Task.query.get(id)
    return render_template('single_task.html.j2', task=task, view_all=True)

@main.route('/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get(id)
    if task and task.author.id != current_user.id:
        flash('Unauthorized','danger')
        redirect(url_for('main.tasks'))
    if request.method=='POST':
        task.edit(request.form.get('body'))
        task.save()
        flash("Your post has been edited", "success")
        return redirect(url_for('main.tasks'))
    return render_template('edit_task.html.j2',task=task)

@main.route('/resolve_task/<int:id>', methods=['GET', 'POST'])
@login_required
def resolve_task(id):
    task = Task.query.get(id)
    if task:
        task.delete()
    return redirect(url_for('main.tasks'))

@main.route('/resolve_daily_task/<int:id>', methods=['GET', 'POST'])
@login_required
def resolve_daily_task(id):
    task = Task.query.get(id)
    if task:
        task.complete()
    return redirect(url_for('main.tasks'))

        
    

@main.route('/comment_task/<int:id>', methods=['POST'])
@login_required
def comment_task(id):
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            flash('Empty Comment', category='error')
            
        else:
            task = Task.query.get(id)
            if task:
                comment = Comments(text=text, user_id=current_user.id, task_id=task.id)
                comment.save()
    return redirect(url_for('main.tasks'))