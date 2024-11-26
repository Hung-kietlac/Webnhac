from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson import ObjectId
from django.http import JsonResponse
from bson.errors import InvalidDocument
import os

def admin_home(request):
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Nhac"]
    users_collection = mydb["User"]
    gmail_collection = mydb["UserGmail"]
    songs_collection = mydb["Nhac"]

    total_users = users_collection.count_documents({})
    total_gmails = gmail_collection.count_documents({})
    total_songs = songs_collection.count_documents({})

    total_users_combined = total_users + total_gmails

    return render(request, 'admin_app/admin_home.html', {'total_users': total_users_combined, 'total_songs': total_songs})

def user(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["User"]
    user_gmail_collection = db["UserGmail"]

    users = list(user_collection.find())
    gmail_users = list(user_gmail_collection.find())

    for user in users:
        user['id'] = str(user.pop('_id'))  # Chuyển ObjectId thành chuỗi

    for gmail_user in gmail_users:
        gmail_user['id'] = str(gmail_user.pop('_id'))  # Chuyển ObjectId thành chuỗi

    all_users = users + gmail_users

    return render(request, 'admin_app/user.html', {"users": all_users})

def delete_user(request, user_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["User"]
    gmail_collection = db["UserGmail"]

    # Xóa người dùng với `id` tương ứng
    user_collection.delete_one({'_id': ObjectId(user_id)})
    gmail_collection.delete_one({'_id': ObjectId(user_id)})

    # Redirect đến trang danh sách người dùng
    return redirect('admin_app:user')

def song(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    user_collection = db["Nhac"]

    songs = list(user_collection.find())

    # Chuyển ObjectId sang chuỗi
    for song in songs:
        song['id'] = str(song.pop('_id'))
    
    return render(request, 'admin_app/song.html', {"songs": songs})

def delete_song(request, song_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    collection = db["Nhac"]

    # Xóa bài hát
    collection.delete_one({"_id": ObjectId(song_id)})

    # Quay lại danh sách bài hát
    return redirect('admin_app:song')

def add_song(request):
    if request.method == "POST":
        try:
            # Kết nối MongoDB
            myclient = MongoClient("mongodb://localhost:27017/")
            mydb = myclient["Nhac"]
            mycol = mydb["Nhac"]

            # Lấy dữ liệu từ form
            tenbaihat = request.POST.get("tenbaihat", "").strip()
            tencasi = request.POST.get("tencasi", "").strip()
            theloai = request.POST.get("theloai", "").strip()
            linkbaihat = request.FILES.get("linkbaihat")
            thoiluong = request.POST.get("thoiluong", "").strip()

            # Kiểm tra dữ liệu hợp lệ
            if not all([tenbaihat, tencasi, theloai, linkbaihat, thoiluong]):
                return JsonResponse({"error": "Vui lòng điền đầy đủ thông tin!"}, status=400)

            # Kiểm tra định dạng file nhạc
            allowed_extensions = ['mp3']
            file_extension = linkbaihat.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse({"error": "Định dạng file không được hỗ trợ! Chỉ chấp nhận mp3!"}, status=400)

            # Xây dựng đường dẫn lưu file nhạc
            static_dir = os.path.join(os.getcwd(), 'static', 'app', 'FileNhac')
            os.makedirs(static_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại
            file_path = os.path.join(static_dir, linkbaihat.name)

            # Lưu file nhạc vào thư mục static
            with open(file_path, 'wb+') as destination:
                for chunk in linkbaihat.chunks():
                    destination.write(chunk)

            # Tạo document mới cho MongoDB
            new_song = {
                "tenbaihat": tenbaihat,
                "tencasi": tencasi,
                "theloai": theloai,
                "linkbaihat": f"/static/app/FileNhac/{linkbaihat.name}",  # Đường dẫn tĩnh
                "thoigian": thoiluong,
            }

            # Thêm dữ liệu vào MongoDB
            mycol.insert_one(new_song)

            # Chuyển hướng về trang danh sách bài hát
            return redirect('/admin_app/song')

        except InvalidDocument as e:
            return JsonResponse({"error": f"Lỗi khi lưu dữ liệu vào MongoDB: {str(e)}"}, status=500)
        except OSError as e:
            return JsonResponse({"error": f"Lỗi khi lưu file nhạc: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"Lỗi không xác định: {str(e)}"}, status=500)

    # Phương thức không hợp lệ
    return JsonResponse({"error": "Phương thức không hợp lệ!"}, status=400)

def artist(request):
    return render(request, 'admin_app/artist.html')

def playlist(request):
    return render(request, 'admin_app/playlist.html')

def category(request):
    return render(request, 'admin_app/category.html')
