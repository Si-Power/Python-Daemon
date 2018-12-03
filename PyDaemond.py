from aiohttp import web
import asyncio
import os
import hashlib

dir = '/STORE'


# ПОЛНАЯ ФОРМА===============================================================================================


async def Form(request):
    return web.Response(
        text='''
            <!DOCTYPE html>
                <html>
                    <head> <meta charset = "utf-8" > <title> Python Daemon </title> </head>
                    <body>

                        <li> <h3> Загрузить файл на сервер: <h3> </li>
                        <li>
                            <form enctype = "multipart/form-data" action="/post_file" method = "post" accept - charset = "utf-8">
                                <p>
                                    <input type = "file" id = "file" name = "file">
                                    <input type = "submit" value = "Отправить">
                                </p>
                            </form>
                        </li>

                        <li> <h3> Поиск файла на сервере по его хешу: <h3> </li>
                        <li>
                            <form enctype = "multipart/form-data" action="/download_file" method = "post" accept - charset = "utf-8">
                                <p>
                                    <textarea name = "SendHash" cols = "30" rows = "5" > Введите хеш файла для поиска </textarea>
                                    <input type = "submit" value = "Отправить">
                                </p>
                            </form>
                        </li>

                        <li> <h3> Удаление файла по его хешу: <h3> </li>
                        <li>
                            <form enctype = "multipart/form-data" action="/delete_file" method = "post" accept - charset = "utf-8">
                                <p>
                                    <textarea name = "RemoveHashFile" cols = "30" rows = "5" > Введите хеш файла для поиска и удаления </textarea>
                                    <input type = "submit" value = "Отправить">
                                </p>
                            </form>
                        </li>

                    </body>
                </html >
            ''',
        content_type="text/html")


# ОТПРАВКА ФАЙЛОВ НА СЕРВЕР==============================================================================


async def Upload(request):

    reader = await request.multipart()

    field = await reader.next()
    filename = field.filename

    # Собираем файл по частям и временно сохраняем

    size = 0
    with open(os.path.join(dir, filename), 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    # Получение хеш-суммы файла

    hash_md5 = hashlib.md5()
    with open(dir + '/' + filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    md5Hashed = hash_md5.hexdigest()  # Хеш-сумма сайла

    # Сохранение файла с хешем вместо имени

    oldFile = open(dir + '/' + filename, 'rb')
    newDir = dir + '/' + md5Hashed[:2]

    try:
        os.mkdir(newDir)
    except:
        pass
    with open(os.path.join(newDir + '/', md5Hashed), 'wb') as f:
        f.write(oldFile.read())

    oldFile.close()
    os.remove(dir + '/' + filename)  # Удаляем временный файл

    return web.Response(
        text='Файл добавлен. Хеш полученного файла: ' + md5Hashed,
        content_type="text/html")


# СКАЧИВАНИЕ ФАЙЛОВ===========================================================================================


async def Download(request):
    data = await request.post()

    filename = data['SendHash']
    searchDir = dir + '/' + filename[:2]

    if os.path.exists(searchDir):
        if os.path.isfile(searchDir + '/' + filename):
            return web.FileResponse(searchDir + '/' + filename)
        else:
            return web.Response(
                text='Файл не найден.',
                content_type="text/html")
    else:
        return web.Response(
            text='Файл не найден.',
            content_type="text/html")


# УДАЛЕНИЕ ФАЙЛОВ=============================================================================================


async def Delete(request):
    data = await request.post()

    filename = data['RemoveHashFile']
    searchDir = dir + '/' + filename[:2]

    if os.path.exists(searchDir):
        if os.path.isfile(searchDir + '/' + filename):
            os.remove(searchDir + '/' + filename)
            return web.Response(
                text='Файл успешно удален.',
                content_type="text/html")
        else:
            return web.Response(
                text='Файла не существует.',
                content_type="text/html")
    else:
        return web.Response(
            text='Файла не существует.',
            content_type="text/html")


# ============================================================================================================


app = web.Application()

app.add_routes([web.get('/', Form),
                web.post('/post_file', Upload),
                web.post('/download_file', Download),
                web.post('/delete_file', Delete)])

# web.run_app(app)

loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, 'localhost', 8080)
srv = loop.run_until_complete(f)
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Выполняю задание...")

loop.close()
print("Работа сервера завершена.")
