from cycloan.settings import OWNER_PHOTO_DIR


# photo filename = ID + . + photo_ext
def save_owner_photo(photo, owner_id):
    photo_ext = photo.name.split('.')[-1]
    photo_path = "".join([OWNER_PHOTO_DIR, str(owner_id), '.', photo_ext])
    photo_file = open(photo_path, 'wb')

    for chunk in photo.chunks():
        photo_file.write(chunk)
    photo_file.close()

    # save it in database
    return photo_path
