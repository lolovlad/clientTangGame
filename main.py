import socket_function
import socket
import json
from threading import Thread
from time import sleep

from model.Message import TypeMessage, BaseMessage
from model.ServerMessage import ServerMessage, TypeServerMessage

from MainApp import MainApp

import pygame

import event

from json import loads


def get_data_server(connection: socket.socket):
    try:
        while True:

            is_all_pac = False
            data = ""
            while not is_all_pac:
                msg = connection.recv(1024).decode("utf-8")
                data += msg
                packs = socket_function.extract_between_start_end(data)
                if packs is not None:
                    data = packs
                    is_all_pac = True

        #print(data.decode("utf-8"))

            mes = loads(packs)

            message = ServerMessage(**mes)
            if message.type_message == TypeServerMessage.RENDER_MAP:
                custome_event = pygame.event.Event(event.RENDER_MAP,
                                                   dict=message.body)
                pygame.event.post(custome_event)

            elif message.type_message == TypeServerMessage.UPDATE_OBJECTS:
                custome_event = pygame.event.Event(event.UPDATE_OBJECT,
                                                   dict=message.body)
                pygame.event.post(custome_event)

            elif message.type_message == TypeServerMessage.STOP_GAME:
                custome_event = pygame.event.Event(event.GAME_STOP,
                                                   dict=message.body)
                pygame.event.post(custome_event)
    except ConnectionResetError:
        pass



host = 'localhost'
port = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))


sock.sendall(BaseMessage(
    uuid=None,
    type_message=TypeMessage.REGISTRATION_PLAYER,
    body=None
).model_dump_json().encode("utf-8"))


reg_data = ServerMessage.model_validate_json(sock.recv(1024).decode("utf-8"))

print("reg", reg_data.body["uuid_player"])

start_game = ServerMessage.model_validate_json(socket_function.extract_between_start_end(sock.recv(1024).decode("utf-8")))

if start_game.type_message == TypeServerMessage.START_GAME:
    Thread(target=get_data_server, args=(sock, ), daemon=True).start()

    game = MainApp(reg_data.body["uuid_player"], sock)
    game.start_game()

