from flask import Blueprint, request, jsonify
from sqlalchemy import text
from database import engine
import json
from middleware import load_optional_user, token_required, user_has_permission

article_bp = Blueprint('article', __name__)

DOCUMENT_COLUMNS = {
    "resource_type": "VARCHAR(50) DEFAULT 'note'",
    "visibility": "VARCHAR(20) DEFAULT 'private'",
    "source_url": "VARCHAR(500)",
    "document_status": "VARCHAR(20) DEFAULT 'published'",
    "ai_summary": "TEXT",
    "ai_keywords": "JSON",
    "ai_questions": "JSON",
    "favorite_count": "INT DEFAULT 0"
}

def ensure_document_columns(conn):
    existing = conn.execute(text("SHOW COLUMNS FROM articles")).mappings().fetchall()
    existing_names = {row["Field"] for row in existing}
    for column, definition in DOCUMENT_COLUMNS.items():
        if column not in existing_names:
            conn.execute(text(f"ALTER TABLE articles ADD COLUMN {column} {definition}"))


def _is_article_manager(current_user):
    return user_has_permission(current_user, "article:manage")


def _can_read_article(article, current_user):
    if (article.get("visibility") or "private") == "public":
        return True

    if not current_user:
        return False

    if article.get("author_id") == current_user.get("id"):
        return True

    return _is_article_manager(current_user)

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
    resource_type = data.get('resource_type', 'note')
    visibility = data.get('visibility', 'private')
    source_url = data.get('source_url')
    document_status = data.get('document_status', status)
    ai_summary = data.get('ai_summary')
    ai_keywords = data.get('ai_keywords')
    ai_questions = data.get('ai_questions')
    
    if not title or not content:
        return jsonify({'status': 1, 'msg': '标题和内容不能为空'}), 400
        
    try:
        # Convert tags list to JSON string for storage
        tags_json = json.dumps(tags if tags else [])
        ai_keywords_json = json.dumps(ai_keywords if ai_keywords else [])
        ai_questions_json = json.dumps(ai_questions if ai_questions else [])
        
        with engine.connect() as conn:
            ensure_document_columns(conn)
            result = conn.execute(
                text("""
                    INSERT INTO articles (
                        title, content, summary, category, tags, author_id, cover_image, status,
                        resource_type, visibility, source_url, document_status,
                        ai_summary, ai_keywords, ai_questions
                    )
                    VALUES (
                        :title, :content, :summary, :category, :tags, :author_id, :cover_image, :status,
                        :resource_type, :visibility, :source_url, :document_status,
                        :ai_summary, :ai_keywords, :ai_questions
                    )
                """),
                {
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "category": category,
                    "tags": tags_json,
                    "author_id": current_user_id,
                    "cover_image": cover_image,
                    "status": status,
                    "resource_type": resource_type,
                    "visibility": visibility,
                    "source_url": source_url,
                    "document_status": document_status,
                    "ai_summary": ai_summary,
                    "ai_keywords": ai_keywords_json,
                    "ai_questions": ai_questions_json
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
    resource_type = data.get('resource_type')
    visibility = data.get('visibility')
    source_url = data.get('source_url')
    document_status = data.get('document_status')
    ai_summary = data.get('ai_summary')
    ai_keywords = data.get('ai_keywords')
    ai_questions = data.get('ai_questions')
    
    try:
        tags_json = json.dumps(tags if tags else [])
        ai_keywords_json = json.dumps(ai_keywords if ai_keywords else [])
        ai_questions_json = json.dumps(ai_questions if ai_questions else [])
        
        with engine.connect() as conn:
            ensure_document_columns(conn)
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
            if resource_type is not None:
                update_parts.append("resource_type=:resource_type")
                params["resource_type"] = resource_type
            if visibility is not None:
                update_parts.append("visibility=:visibility")
                params["visibility"] = visibility
            if source_url is not None:
                update_parts.append("source_url=:source_url")
                params["source_url"] = source_url
            if document_status is not None:
                update_parts.append("document_status=:document_status")
                params["document_status"] = document_status
            if ai_summary is not None:
                update_parts.append("ai_summary=:ai_summary")
                params["ai_summary"] = ai_summary
            if ai_keywords is not None:
                update_parts.append("ai_keywords=:ai_keywords")
                params["ai_keywords"] = ai_keywords_json
            if ai_questions is not None:
                update_parts.append("ai_questions=:ai_questions")
                params["ai_questions"] = ai_questions_json
                
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
                    text("UPDATE articles SET likes = GREATEST(COALESCE(likes, 0) - 1, 0) WHERE id = :aid"),
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
                    text("UPDATE articles SET likes = COALESCE(likes, 0) + 1 WHERE id = :aid"),
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
                    SELECT a.*, u.username as author_name, u.avatar as author_avatar,
                           al.created_at as liked_at
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
        current_user = load_optional_user()
        user_id = current_user.get("id") if current_user else None
                
        with engine.connect() as conn:
            ensure_document_columns(conn)
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

            if not _can_read_article(article, current_user):
                return jsonify({'status': 1, 'msg': '无权查看该私有文档'}), 403
            
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

            for json_field in ['ai_keywords', 'ai_questions']:
                if article.get(json_field):
                    try:
                        article[json_field] = json.loads(article[json_field])
                    except:
                        article[json_field] = []
            
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
        current_user = load_optional_user()
        current_user_id = current_user.get("id") if current_user else None
        is_manager = _is_article_manager(current_user)

        # Get query parameters
        search = request.args.get('search', '')
        title = request.args.get('title', '')
        category = request.args.get('category', '')
        tag = request.args.get('tag', '')
        status = request.args.get('status', '') # Add status filter
        author_id = request.args.get('author_id', '') # Add author_id filter
        resource_type = request.args.get('resource_type', '')
        visibility = request.args.get('visibility', '')
        document_status = request.args.get('document_status', '')
        requested_author_id = int(author_id) if str(author_id).isdigit() else None
        is_own_author_filter = bool(current_user_id and requested_author_id == current_user_id)
        
        with engine.connect() as conn:
            ensure_document_columns(conn)
            # Build query
            query_str = """
                SELECT a.*, u.username as author_name, u.avatar as author_avatar,
                       COALESCE(cc.comments_count, 0) as comments_count
                FROM articles a
                LEFT JOIN users u ON a.author_id = u.id
                LEFT JOIN (
                    SELECT article_id, COUNT(*) as comments_count
                    FROM comments
                    GROUP BY article_id
                ) cc ON cc.article_id = a.id
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

            if resource_type:
                query_str += " AND a.resource_type = :resource_type"
                params['resource_type'] = resource_type

            if visibility:
                if visibility != 'public' and not (is_manager or is_own_author_filter):
                    return jsonify({'status': 0, 'data': []})
                query_str += " AND a.visibility = :visibility"
                params['visibility'] = visibility
            elif is_manager or is_own_author_filter:
                pass
            elif current_user_id:
                query_str += " AND (a.visibility = 'public' OR a.author_id = :current_user_id)"
                params['current_user_id'] = current_user_id
            else:
                query_str += " AND a.visibility = 'public'"

            if document_status:
                if document_status != 'published' and not (is_manager or is_own_author_filter):
                    if not current_user_id:
                        return jsonify({'status': 0, 'data': []})
                    query_str += " AND a.author_id = :current_user_id"
                    params['current_user_id'] = current_user_id
                query_str += " AND a.document_status = :document_status"
                params['document_status'] = document_status
            elif not (is_manager or is_own_author_filter):
                if current_user_id:
                    query_str += " AND (a.author_id = :current_user_id OR a.document_status = 'published')"
                    params['current_user_id'] = current_user_id
                else:
                    query_str += " AND a.document_status = 'published'"
            
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

                for json_field in ['ai_keywords', 'ai_questions']:
                    if article.get(json_field):
                        try:
                            article[json_field] = json.loads(article[json_field])
                        except:
                            article[json_field] = []
                
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

@article_bp.route('/api/articles/<int:article_id>/comments', methods=['GET'])
def get_article_comments(article_id):
    """获取文章评论列表"""
    try:
        with engine.connect() as conn:
            query = """
                SELECT c.*, u.username as user_name, u.avatar as user_avatar
                FROM comments c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.article_id = :aid
                ORDER BY c.created_at DESC
            """
            result = conn.execute(text(query), {"aid": article_id}).mappings().fetchall()
            
            comments_list = []
            for row in result:
                comment = dict(row)
                if comment.get('created_at'):
                    comment['created_at'] = comment['created_at'].isoformat()
                comments_list.append(comment)
                
            return jsonify({'status': 0, 'data': comments_list})
    except Exception as e:
        print(f"Error getting comments: {e}")
        return jsonify({'status': 1, 'msg': '获取评论失败', 'error': str(e)}), 500

@article_bp.route('/api/articles/<int:article_id>/comments', methods=['POST'])
@token_required
def create_article_comment(current_user_id, article_id):
    """发表文章评论"""
    data = request.get_json()
    content = data.get('content')
    
    if not content or not content.strip():
        return jsonify({'status': 1, 'msg': '评论内容不能为空'}), 400
        
    try:
        with engine.connect() as conn:
            # 检查文章是否存在
            article = conn.execute(
                text("SELECT id FROM articles WHERE id = :aid"),
                {"aid": article_id}
            ).fetchone()
            
            if not article:
                return jsonify({'status': 1, 'msg': '文章不存在'}), 404
                
            # 插入评论
            conn.execute(
                text("""
                    INSERT INTO comments (article_id, user_id, content)
                    VALUES (:aid, :uid, :content)
                """),
                {"aid": article_id, "uid": current_user_id, "content": content}
            )
            conn.commit()
            
            return jsonify({'status': 0, 'msg': '评论发表成功'})
    except Exception as e:
        print(f"Error creating comment: {e}")
        return jsonify({'status': 1, 'msg': '发表评论失败', 'error': str(e)}), 500
