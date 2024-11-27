from django.shortcuts import render, redirect
from pymongo import MongoClient
from bson import ObjectId
from django.http import JsonResponse
from bson.errors import InvalidDocument
import os
import mutagen  # Thêm thư viện để đọc thông tin file nhạc

def admin_home(request):
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Nhac"]
    users_collection = mydb["User"]
    gmail_collection = mydb["UserGmail"]
    songs_collection = mydb["Nhac"]
    artist_collection = mydb["Artist"]

    total_users = users_collection.count_documents({})
    total_gmails = gmail_collection.count_documents({})
    total_songs = songs_collection.count_documents({})
    total_artists = artist_collection.count_documents({})

    total_users_combined = total_users + total_gmails

    return render(request, 'admin_app/admin_home.html', {'total_users': total_users_combined, 'total_songs': total_songs, 'total_artists': total_artists})

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

            # Kiểm tra dữ liệu hợp lệ
            if not all([tenbaihat, tencasi, theloai, linkbaihat]):
                return JsonResponse({"error": "Vui lòng điền đầy đủ thông tin!"}, status=400)

            # Kiểm tra định dạng file nhạc
            allowed_extensions = ['mp3']
            file_extension = linkbaihat.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                return JsonResponse({"error": "Định dạng file không được hỗ trợ! Chỉ chấp nhận mp3!"}, status=400)

            # Tính toán thời gian bài hát
            audio = mutagen.File(linkbaihat)  # Đọc file nhạc
            thoigian = audio.info.length  # Lấy thời gian bài hát (tính bằng giây)
            thoigian_str = str(int(thoigian // 60)) + ":" + str(int(thoigian % 60)).zfill(2)  # Chuyển đổi sang định dạng phút:giây

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
                "thoigian": thoigian_str,  # Thêm thời gian vào document
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
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Nhac"]
    artist_collection = db["Artist"]
    songs_collection = db["Nhac"]  # Kết nối đến collection bài hát

    # Lấy danh sách nghệ sĩ từ MongoDB
    artists = list(artist_collection.find())

    # Chuyển ObjectId sang chuỗi và đếm số bài hát cho mỗi nghệ sĩ
    for artist in artists:
        artist['id'] = str(artist.pop('_id'))
        artist['so_bai_hat'] = songs_collection.count_documents({"tencasi": artist['tencasi']})  # Đếm số bài hát của nghệ sĩ

    return render(request, 'admin_app/artist.html', {'artists': artists})

def add_artist(request):
    if request.method == "POST":
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["Nhac"]
            artist_collection = db["Artist"]

            # Lấy dữ liệu từ form
            tencasi = request.POST.get("tencasi", "").strip()
            anh_dai_dien = request.FILES.get("anh_dai_dien")

            # Kiểm tra dữ liệu hợp lệ
            if not all([tencasi, anh_dai_dien]):
                return JsonResponse({"error": "Vui lòng điền đầy đủ thông tin!"}, status=400)

            # Lưu ảnh đại diện vào thư mục
            static_dir = os.path.join(os.getcwd(), 'static', 'app', 'FileArtist')
            os.makedirs(static_dir, exist_ok=True)
            file_path = os.path.join(static_dir, anh_dai_dien.name)

            with open(file_path, 'wb+') as destination:
                for chunk in anh_dai_dien.chunks():
                    destination.write(chunk)

            # Tạo document mới cho MongoDB
            new_artist = {
                "tencasi": tencasi,
                "anh_dai_dien": f"/static/app/FileArtist/{anh_dai_dien.name}",
                # "so_bai_hat": 0,  # Không cần lưu trường này
            }

            # Thêm dữ liệu vào MongoDB
            artist_collection.insert_one(new_artist)

            return redirect('/admin_app/artist')

        except Exception as e:
            return JsonResponse({"error": f"Lỗi không xác định: {str(e)}"}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ!"}, status=400)

def delete_artist(request, artist_id):
    if request.method == "DELETE":
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Nhac"]
        artist_collection = db["Artist"]

        # Xóa nghệ sĩ với `id` tương ứng
        artist_collection.delete_one({'_id': ObjectId(artist_id)})

        # Trả về phản hồi thành công
        return JsonResponse({"message": "Nghệ sĩ đã được xóa thành công!"}, status=200)

    return JsonResponse({"error": "Phương thức không hợp lệ!"}, status=400)

def edit_artist(request):
    if request.method == "POST":
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["Nhac"]
            artist_collection = db["Artist"]

            # Lấy dữ liệu từ form
            artist_id = request.POST.get("artist_id")
            tencasi = request.POST.get("tencasi", "").strip()
            anh_dai_dien = request.FILES.get("anh_dai_dien")

            # Kiểm tra dữ liệu hợp lệ
            if not all([artist_id, tencasi]):
                return JsonResponse({"error": "Vui lòng điền đầy đủ thông tin!"}, status=400)

            # Cập nhật thông tin nghệ sĩ
            update_data = {
                "tencasi": tencasi,
            }

            if anh_dai_dien:
                # Lưu ảnh đại diện mới vào thư mục
                static_dir = os.path.join(os.getcwd(), 'static', 'app', 'FileArtist')
                os.makedirs(static_dir, exist_ok=True)
                file_path = os.path.join(static_dir, anh_dai_dien.name)

                with open(file_path, 'wb+') as destination:
                    for chunk in anh_dai_dien.chunks():
                        destination.write(chunk)

                update_data["anh_dai_dien"] = f"/static/app/FileArtist/{anh_dai_dien.name}"

            # Cập nhật dữ liệu vào MongoDB
            artist_collection.update_one({'_id': ObjectId(artist_id)}, {"$set": update_data})

            return redirect('/admin_app/artist')

        except Exception as e:
            return JsonResponse({"error": f"Lỗi không xác định: {str(e)}"}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ!"}, status=400)

def playlist(request):
    return render(request, 'admin_app/playlist.html')

def category(request):
    return render(request, 'admin_app/category.html')
