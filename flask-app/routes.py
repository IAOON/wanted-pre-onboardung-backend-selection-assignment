from flask import request
from flask_jwt_extended import create_access_token
from app import app, db
from models import User, Post

@app.route('/users', methods=['POST'])
def register():
    if not request.is_json:
        return {"msg": "Missing JSON in request"}, 400
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email:
        return {"msg": "Missing email parameter"}, 400
    if not password:
        return {"msg": "Missing password parameter"}, 400
    if '@' not in email:
        return {"msg": "Invalid email"}, 400
    if len(password) < 8:
        return {"msg": "Password must be at least 8 characters"}, 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        return {"msg": "User with this email already exists"}, 400
    
    new_user = User(email=email)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return {"msg": "User created successfully"}, 201

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return {"msg": "Missing JSON in request"}, 400
    
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if not email:
        return {"msg": "Missing email parameter"}, 400
    if not password:
        return {"msg": "Missing password parameter"}, 400
    if '@' not in email:
        return {"msg": "Invalid email"}, 400
    if len(password) < 8:
        return {"msg": "Password must be at least 8 characters"}, 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return {"msg": "Bad email or password"}, 401
    
    access_token = create_access_token(identity=user.id)
    return {"access_token": access_token}, 200

from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    if not request.is_json:
        return {"msg": "Missing JSON in request"}, 400
    
    title = request.json.get('title', None)
    content = request.json.get('content', None)
    
    if not title:
        return {"msg": "Missing title parameter"}, 400
    if not content:
        return {"msg": "Missing content parameter"}, 400
    
    user_id = get_jwt_identity()
    new_post = Post(title=title, content=content, author_id=user_id)
    
    db.session.add(new_post)
    db.session.commit()
    
    return {"msg": "Post created successfully", "post_id": new_post.id}, 201

@app.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    
    return {"posts": [{"id": post.id, "title": post.title, "content": post.content, "author_id": post.author_id} for post in posts]}, 200

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    
    if not post:
        return {"msg": "Post not found"}, 404
    
    return {"post": {"id": post.id, "title": post.title, "content": post.content, "author_id": post.author_id}}, 200

@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    if not request.is_json:
        return {"msg": "Missing JSON in request"}, 400
    
    title = request.json.get('title', None)
    content = request.json.get('content', None)
    
    if not title:
        return {"msg": "Missing title parameter"}, 400
    if not content:
        return {"msg": "Missing content parameter"}, 400
    
    post = Post.query.get(post_id)
    
    if not post:
        return {"msg": "Post not found"}, 404
    
    user_id = get_jwt_identity()
    
    if post.author_id != user_id:
        return {"msg": "You do not have permission to update this post"}, 403
    
    post.title = title
    post.content = content
    
    db.session.commit()
    
    return {"msg": "Post updated successfully"}, 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = Post.query.get(post_id)
    
    if not post:
        return {"msg": "Post not found"}, 404
    
    user_id = get_jwt_identity()
    
    if post.author_id != user_id:
        return {"msg": "You do not have permission to delete this post"}, 403
    
    db.session.delete(post)
    db.session.commit()
    
    return {"msg": "Post deleted successfully"}, 200
