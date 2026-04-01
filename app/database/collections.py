from app.config.db import db

users_collection = db["users"]
transactions_collection = db["transactions"]
audit_logs_collection = db["audit_logs"]