from aiohttp import web
import socketio

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)


def close(sid):
    for i in sio.rooms(sid):
        if i != sid:
            sio.leave_room(sid, i)


@sio.event
def connect(sid, environ):
    print('Connected', sid)
    # await sio.emit('ready', room=None)


@sio.event
def disconnect(sid):
    close(sid)


@sio.event
async def change(sid, room):
    fullRoom = False
    try:
        if len(list(sio.manager.get_participants(room=room, namespace='/'))) >= 2:
            fullRoom = True
    except:
        print('Room not found')

    finally:
        if not fullRoom:
            print('Смена комнаты')
            sio.enter_room(sid, room)
            await sio.emit('ready', room=room, skip_sid=sid)


@sio.event
async def exitRoom(sid):
    for i in sio.rooms(sid):
        if i != sid:
            await sio.emit('exitAll', room=i, skip_sid=sid)

    close(sid)


@sio.event
async def data(sid, data, room):
    await sio.emit('data', data, room=room, skip_sid=sid)


if __name__ == '__main__':
    web.run_app(app, port=9999)
