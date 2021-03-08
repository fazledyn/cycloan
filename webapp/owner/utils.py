from cycloan.settings import OWNER_PHOTO_DIR


def save_owner_photo(photo, owner_id, contact):
    photo_ext = photo.name.split('.')[-1]
    photo_path = "".join([OWNER_PHOTO_DIR, str(owner_id), '_', contact, '.', photo_ext])
    photo_static_path = "".join([ "static/", photo_path ])
    photo_file = open(photo_static_path, 'wb')

    for chunk in photo.chunks():
        photo_file.write(chunk)
    photo_file.close()

    return photo_path
