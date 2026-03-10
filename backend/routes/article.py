from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import text
from database import engine
import jwt
import json
from functools import wraps
from middleware import token_required

article_bp = Blueprint('article', __name__)

@article_bp.route('/api/articles', methods=['POST'])
@token_required
def create_article(current_user_id):
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    summary = data.get('summary')
    category = data.get('category')
    tags = data.get('tags') # Should be a list
    cover_image = data.get('cover_image')
    status = data.get('status', 'published') # Default to published if not provided
    
    if not title or not content:
        return jsonify({'status': 1, 'msg': '标题和内容不能为空'}), 400
        
    try:
        # Convert tags list to JSON string for storage
        tags_json = json.dumps(tags if tags else [])
        
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO articles (title, content, summary, category, tags, author_id, cover_image, status)
                    VALUES (:title, :content, :summary, :category, :tags, :author_id, :cover_image, :status)
                """),
                {
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "category": category,
                    "tags": tags_json,
                    "author_id": current_user_id,
                    "cover_image": cover_image,
                    "status": status
                }
            )
            conn.commit()
            
            # Get the ID of the inserted article
            article_id = result.lastrowid
            
            if not article_id:
                article_id_result = conn.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                article_id = article_id_result[0]

        return jsonify({
            'status': 0, 
            'msg': '文章发布成功', 
            'data': {
                'id': article_id,
                'title': title
            }
        })
        
    except Exception as e:
        print(f"Error creating article: {e}")
        return jsonify({'status': 1, 'msg': '发布失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>', methods=['PUT'])
@token_required
def update_article(current_user_id, article_id):
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    summary = data.get('summary')
    category = data.get('category')
    tags = data.get('tags')
    cover_image = data.get('cover_image')
    status = data.get('status')
    
    try:
        tags_json = json.dumps(tags if tags else [])
        
        with engine.connect() as conn:
            # First check if article exists
            article = conn.execute(
                text("SELECT author_id FROM articles WHERE id = :id"),
                {"id": article_id}
            ).fetchone()
            
            if not article:
                return jsonify({'status': 1, 'msg': '文章不存在'}), 404
                
            # Check user role for admin bypass
            user = conn.execute(
                text("SELECT role, role_id FROM users WHERE id = :id"),
                {"id": current_user_id}
            ).fetchone()
            
            is_admin = False
            if user:
                if user.role == 'admin':
                    is_admin = True
                elif user.role_id:
                     perms = conn.execute(text("""
                        SELECT p.code FROM permissions p
                        JOIN role_permissions rp ON p.id = rp.permission_id
                        WHERE rp.role_id = :rid AND p.code = 'article:manage'
                     """), {"rid": user.role_id}).fetchone()
                     if perms:
                         is_admin = True

            if article.author_id != current_user_id and not is_admin:
                return jsonify({'status': 1, 'msg': '无权修改此文章'}), 403
            
            # Construct update SQL dynamically based on provided fields
            update_parts = []
            params = {"id": article_id}
            
            if title is not None:
                update_parts.append("title=:title")
                params["title"] = title
            if content is not None:
                update_parts.append("content=:content")
                params["content"] = content
            if summary is not None:
                update_parts.append("summary=:summary")
                params["summary"] = summary
            if category is not None:
                update_parts.append("category=:category")
                params["category"] = category
            if tags is not None:
                update_parts.append("tags=:tags")
                params["tags"] = tags_json
            if cover_image is not None:
                update_parts.append("cover_image=:cover_image")
                params["cover_image"] = cover_image
            if status is not None:
                update_parts.append("status=:status")
                params["status"] = status
                
            if not update_parts:
                 return jsonify({'status': 0, 'msg': '无变更'})
                 
            update_sql = f"UPDATE articles SET {', '.join(update_parts)} WHERE id=:id"
            
            conn.execute(text(update_sql), params)
            conn.commit()
            
        return jsonify({'status': 0, 'msg': '文章更新成功'})
        
    except Exception as e:
        return jsonify({'status': 1, 'msg': '更新失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>/like', methods=['POST'])
@token_required
def toggle_like(current_user_id, article_id):
    try:
        with engine.connect() as conn:
            # Check if user already liked
            liked = conn.execute(
                text("SELECT id FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
                {"uid": current_user_id, "aid": article_id}
            ).fetchone()
            
            is_liked = False
            msg = ""
            if liked:
                # Unlike
                conn.execute(
                    text("DELETE FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
                    {"uid": current_user_id, "aid": article_id}
                )
                conn.execute(
                    text("UPDATE articles SET likes = likes - 1 WHERE id = :aid"),
                    {"aid": article_id}
                )
                msg = "已取消点赞"
                is_liked = False
            else:
                # Like
                conn.execute(
                    text("INSERT INTO article_likes (user_id, article_id) VALUES (:uid, :aid)"),
                    {"uid": current_user_id, "aid": article_id}
                )
                conn.execute(
                    text("UPDATE articles SET likes = likes + 1 WHERE id = :aid"),
                    {"aid": article_id}
                )
                msg = "点赞成功"
                is_liked = True
                
            conn.commit()
            
            # Get updated count
            likes_count = conn.execute(
                text("SELECT likes FROM articles WHERE id = :aid"),
                {"aid": article_id}
            ).scalar()
            
            return jsonify({
                'status': 0, 
                'msg': msg, 
                'data': {
                    'liked': is_liked,
                    'likes': likes_count
                }
            })
    except Exception as e:
        return jsonify({'status': 1, 'msg': '操作失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>/view', methods=['POST'])
def increment_view(article_id):
    try:
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE articles SET views = views + 1 WHERE id = :id"),
                {"id": article_id}
            )
            conn.commit()
            return jsonify({'status': 0, 'msg': '浏览量已增加'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '操作失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/my-likes', methods=['GET'])
@token_required
def get_my_likes(current_user_id):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT a.*, u.username as author_name, u.avatar as author_avatar
                    FROM articles a
                    JOIN article_likes al ON a.id = al.article_id
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE al.user_id = :uid
                    ORDER BY al.created_at DESC
                """),
                {"uid": current_user_id}
            ).mappings().fetchall()
            
            articles_list = []
            for row in result:
                article = dict(row)
                if article.get('tags'):
                    try:
                        article['tags'] = json.loads(article['tags'])
                    except:
                        article['tags'] = []
                if article.get('created_at'):
                    article['created_at'] = article['created_at'].isoformat()
                if article.get('updated_at'):
                    article['updated_at'] = article['updated_at'].isoformat()
                articles_list.append(article)
                
            return jsonify({'status': 0, 'data': articles_list})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(" ")[1]
                
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
                user_id = data['user_id']
            except:
                pass
                
        with engine.connect() as conn:
            # Join with users to get author name
            result = conn.execute(
                text("""
                    SELECT a.*, u.username as author_name, u.avatar as author_avatar
                    FROM articles a
                    LEFT JOIN users u ON a.author_id = u.id
                    WHERE a.id = :id
                """),
                {"id": article_id}
            ).mappings().fetchone()
            
            if not result:
                return jsonify({'status': 1, 'msg': '文章不存在'}), 404
            
            # Convert result to dict and handle types
            article = dict(result)
            
            # Check if current user liked this article
            article['is_liked'] = False
            if user_id:
                liked = conn.execute(
                    text("SELECT id FROM article_likes WHERE user_id = :uid AND article_id = :aid"),
                    {"uid": user_id, "aid": article_id}
                ).fetchone()
                if liked:
                    article['is_liked'] = True
            
            # Parse tags JSON
            if article.get('tags'):
                try:
                    article['tags'] = json.loads(article['tags'])
                except:
                    article['tags'] = []
            
            # Format dates
            if article.get('created_at'):
                article['created_at'] = article['created_at'].isoformat()
            if article.get('updated_at'):
                article['updated_at'] = article['updated_at'].isoformat()
                
            return jsonify({'status': 0, 'data': article})
            
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取失败', 'error': str(e)}), 500

@article_bp.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        # Get query parameters
        search = request.args.get('search', '')
        title = request.args.get('title', '')
        category = request.args.get('category', '')
        tag = request.args.get('tag', '')
        status = request.args.get('status', '') # Add status filter
        author_id = request.args.get('author_id', '') # Add author_id filter
        
        with engine.connect() as conn:
            # Build query
            query_str = """
                SELECT a.*, u.username as author_name, u.avatar as author_avatar
                FROM articles a
                LEFT JOIN users u ON a.author_id = u.id
                WHERE 1=1
            """
            params = {}
            
            if search:
                query_str += " AND (a.title LIKE :search OR a.summary LIKE :search OR a.content LIKE :search)"
                params['search'] = f"%{search}%"
            
            if title:
                query_str += " AND a.title LIKE :title"
                params['title'] = f"%{title}%"
                
            if category:
                query_str += " AND a.category = :category"
                params['category'] = category
                
            if tag:
                # Assuming tags are stored as JSON array ["tag1", "tag2"]
                # We can use JSON_CONTAINS for exact match if MySQL version supports it
                # Or simple string search for compatibility
                query_str += " AND a.tags LIKE :tag"
                params['tag'] = f"%{tag}%"
            
            if status:
                query_str += " AND a.status = :status"
                params['status'] = status
            
            if author_id:
                query_str += " AND a.author_id = :author_id"
                params['author_id'] = author_id
                
            query_str += " ORDER BY a.created_at DESC"
            
            result = conn.execute(text(query_str), params).mappings().fetchall()
            
            articles_list = []
            for row in result:
                article = dict(row)
                # Parse tags
                if article.get('tags'):
                    try:
                        article['tags'] = json.loads(article['tags'])
                    except:
                        article['tags'] = []
                
                # Format dates
                if article.get('created_at'):
                    article['created_at'] = article['created_at'].isoformat()
                if article.get('updated_at'):
                    article['updated_at'] = article['updated_at'].isoformat()
                    
                articles_list.append(article)
                
            return jsonify({'status': 0, 'data': articles_list})
            
    except Exception as e:
        return jsonify({'status': 1, 'msg': '获取列表失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>', methods=['DELETE'])
@token_required
def delete_article(current_user_id, article_id):
    try:
        with engine.connect() as conn:
            # Check if article exists and belongs to user
            article = conn.execute(
                text("SELECT author_id FROM articles WHERE id = :id"),
                {"id": article_id}
            ).fetchone()
            
            if not article:
                return jsonify({'status': 1, 'msg': '文章不存在'}), 404
                
            # Allow deletion if it's the author
            # (In a real system, admin should also be able to delete, but for now we stick to basic logic)
            # Or we can just allow delete for now.
            if article.author_id != current_user_id:
                # Check if user is admin (assuming admin has id 1 or specific role, but we don't have roles yet)
                # For simplicity, let's just restrict to author for now.
                return jsonify({'status': 1, 'msg': '无权删除此文章'}), 403
            
            conn.execute(
                text("DELETE FROM articles WHERE id=:id"),
                {"id": article_id}
            )
            conn.commit()
            return jsonify({'status': 0, 'msg': '删除成功'})
    except Exception as e:
        return jsonify({'status': 1, 'msg': '删除失败', 'error': str(e)}), 500
