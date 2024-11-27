from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import random
import json

def home(request):
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Nhac"]
    mycol = mydb["Nhac"]

    # Lấy từ khóa tìm kiếm từ GET request
    query = request.GET.get('q')
    if query:
        songs = list(mycol.find({
            "$or": [
                {"tenbaihat": {"$regex": query, "$options": "i"}},
                {"tencasi": {"$regex": query, "$options": "i"}}
            ]
        }))
    else:
        songs = list(mycol.find())

    if songs: 
        for song in songs:
            song['_id'] = str(song['_id'])

        # Lấy ngẫu nhiên tối đa 6 bài hát
        random_songs = random.sample(songs, min(len(songs), 6))
    else:
        random_songs = []

    return render(request, 'app/home.html', {'songs': random_songs})

def dangky(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["User"]

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Mật khẩu không trùng khớp.")
            return render(request, 'app/dangky.html')

        if user_collection.find_one({"username": username}):
            messages.error(request, "Tên người dùng đã tồn tại.")
            return render(request, 'app/dangky.html')

        if user_collection.find_one({"email": email}):
            messages.error(request, "Email đã được đăng ký.")
            return render(request, 'app/dangky.html')

        hashed_password = make_password(password)

        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password
        }
        user_collection.insert_one(user_data)

        messages.success(request, "Bạn đã đăng ký thành công!")
        return redirect('app:home')

    return render(request, 'app/dangky.html')

def dangnhap(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["User"]
    admin_collection = db["admin"]

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Kiểm tra tài khoản admin
        admin = admin_collection.find_one({"adminname": username})
        if admin and admin['password'] == password:
            messages.success(request, "Đăng nhập admin thành công!")
            return redirect('admin_app:admin_home')

        # Kiểm tra tài khoản user
        user = user_collection.find_one({"username": username})
        if user and check_password(password, user['password']):
            messages.success(request, "Đăng nhập thành công!")
            return redirect('app:home')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")

    return render(request, 'app/dangnhap.html')

def save_to_mongo(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        client = MongoClient("mongodb://localhost:27017/")
        db = client['Nhac']
        users_collection = db['UserGmail']

        user_data = {
            "username": response.get("name"),
            "email": response.get("email"),
            "picture": response.get("picture"),
            "google_id": response.get("id"),
        }
        users_collection.insert_one(user_data)

def danhsachnhac(request):
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Nhac"]
    songs_collection = mydb["Nhac"]
    artists_collection = mydb["Artist"]

    songs = list(songs_collection.find())
    artists = list(artists_collection.find())[:5]  # Lấy 5 nghệ sĩ đầu tiên

    # Chuyển ObjectId sang chuỗi cho mỗi nghệ sĩ
    for artist in artists:
        artist['_id'] = str(artist['_id'])

    return render(request, 'app/danhsachnhac.html', {'songs': songs, 'artists': artists})

def thuvien(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["User"]

    # Kiểm tra nếu người dùng đã đăng nhập
    if request.user.is_authenticated:
        user = user_collection.find_one({"username": request.user.username})

        # Lấy lịch sử nghe của người dùng
        if user:
            listening_history = user.get('listening_history', [])
        else:
            listening_history = []
    else:
        listening_history = []

    # Kiểm tra nếu có yêu cầu POST để cập nhật bài hát
    if request.method == 'POST':
        song_data = json.loads(request.body)
        
        # Lưu bài hát vào thư viện người dùng
        if request.user.is_authenticated:
            song = {
                "song_name": song_data.get('song_name'),
                "artist": song_data.get('artist'),
                "genre": song_data.get('genre'),
                "duration": song_data.get('duration')
            }

            user_collection.update_one(
                {"username": request.user.username},
                {"$push": {"listening_history": song}}
            )

            return JsonResponse({'success': True})

    return render(request, 'app/thuvien.html', {'listening_history': listening_history})

def danhsachcasi(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    artist_collection = db["Artist"]

    artists = list(artist_collection.find())

    # Chuyển ObjectId sang chuỗi
    for artist in artists:
        artist['_id'] = str(artist['_id'])

    return render(request, 'app/danhsachcasi.html', {'artists': artists})

def get_all_artists(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    artist_collection = db["Artist"]

    artists = list(artist_collection.find())

    # Chuyển ObjectId sang chuỗi
    for artist in artists:
        artist['_id'] = str(artist['_id'])

    return JsonResponse({'artists': artists})