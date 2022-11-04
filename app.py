from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with

app=Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db=SQLAlchemy()

db.init_app(app)

class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))

api = Api(app)

task_post_args = reqparse.RequestParser()
task_post_args.add_argument('task', type=str, help='Task is required', required=True)
task_post_args.add_argument('summary', type=str, help="Summary is required", required=True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument("task", type=str)
task_update_args.add_argument("summary", type=str)

resource_fields={
    'id': fields.Integer,
    'task':fields.String,
    'summary': fields.String
}

class ToDos(Resource):
    def get(self):
        todos={}
        allTodos = ToDoModel.query.all()
        for todo in allTodos:
            todos[todo.id]={'task':todo.task, 'summary':todo.summary}
        return todos

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        todoID = ToDoModel.query.filter_by(id=todo_id).first()
        if not todoID:
            abort(404, message="Task Not Present")
        return todoID
    
    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        todoID = ToDoModel.query.filter_by(id=todo_id).first()
        if todoID:
            abort(409, message="Task ID already Present")
        newTask=ToDoModel(id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(newTask)
        db.session.commit()
        return newTask, 201
    
    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_update_args.parse_args()
        todoID = ToDoModel.query.filter_by(id=todo_id).first()
        if not todoID:
            abort(404, message="Task ID doesn't exist")
        if args['task']:
            todoID.task=args['task']
        if args['summary']:
            todoID.summary=args['summary']
        db.session.commit()
        return todoID
    
    def delete(self, todo_id):
        todoID = ToDoModel.query.filter_by(id=todo_id).first()
        db.session.delete(todoID)
        return 'To Do Deleted', 204


api.add_resource(ToDos, '/todos')
api.add_resource(ToDo, '/todos/<int:todo_id>')



if __name__ == '__main__':
    app.run(debug=True)
