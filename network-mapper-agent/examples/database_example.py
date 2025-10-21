# Example: Database connections
import pymongo
from pymongo import MongoClient
import redis
import psycopg2

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.test_db

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# PostgreSQL connection
conn = psycopg2.connect("host=localhost dbname=test user=postgres password=secret")
