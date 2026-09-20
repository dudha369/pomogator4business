async def download_message_photo(bot, message):
    if not message or not message.photo:
        return None
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    buffer = await bot.download_file(file.file_path)
    return buffer.read()


async def download_user_avatar(bot, user_id):
    photos = await bot.get_user_profile_photos(user_id, limit=1)
    if not photos.photos:
        return None
    photo = photos.photos[0][-1]
    file = await bot.get_file(photo.file_id)
    buffer = await bot.download_file(file.file_path)
    return buffer.read()
