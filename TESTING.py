from pymongo import MongoClient
try:
    client = MongoClient("mongodb+srv://asdfk:asdfghjkl@collegeproject.zftto.mongodb.net/")
    db = client["Clusters"]
    users_collection = db["Credentials"]

    # Test Query
    user = users_collection.find_one()
    print("Connected successfully! Sample User:", user)

except Exception as e:
    print("MongoDB Connection Error:", e)