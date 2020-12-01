from cycloan.settings import CYCLE_PHOTO_DIR


def save_cycle_photo(cycle_photo, owner_id, cycle_model):
    
    photo_ext = cycle_photo.name.split('.')[-1]
    photo_path = "".join([ CYCLE_PHOTO_DIR, str(owner_id), '_', cycle_model, '.', photo_ext ])
    photo_static_path = "".join(["static/", photo_path ])
    photo_file = open(photo_static_path, 'wb')

    for chunk in cycle_photo.chunks():
        photo_file.write(chunk)
    photo_file.close()

    # save it in database
    return photo_path
