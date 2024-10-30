import json

from Tank import Tank
from Wall import Wall
from Bullet import Bullet
from ObjectMap import ObjectMap
import pygame
from datetime import datetime
from random import randint

from socket import socket
from socket_function import extract_between_start_end
from model.Message import BaseMessage, TypeMessage

from json import loads

from event import *


class MainApp:
    def __init__(self, my_uuid_player: str, sock: socket):
        pygame.init()
        pygame.font.init()
        self.SCREEN_HEIGHT_MENU = 180
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1620, 720
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.display = pygame.display
        self.window = self.display.set_mode([self.SCREEN_WIDTH, self.SCREEN_HEIGHT + self.SCREEN_HEIGHT_MENU],
                                            pygame.RESIZABLE, 32)
        self.display.set_caption('Tanks')
        self.my_tank = None
        self.enemy_tank = None

        self.object_list_enemy = []
        self.object_list_wall = []
        self.object_list_bullet = {}

        self.map_render = []

        self.position_players = {}

        self._is_game = True
        self._screen_game = True

        self._information = {"gray_tank.png": {
                                    "bullet": 0,
                                    "broke": 0,
                                    "hit_tank": 0},
                              "yellow_tank.png": {
                                  "bullet": 0,
                                  "broke": 0,
                                  "hit_tank": 0
                              },
                              "bullet_to_bullet": 0}

        self.font_text = pygame.font.Font('freesansbold.ttf', 16)

        self.texts = []

        self.__uuid_player: str = my_uuid_player
        self.__socket: socket = sock


        self.__mes_stop = ""

    def send_server_message(self, message: BaseMessage):
        try:
            self.__socket.sendall(message.model_dump_json().encode("utf-8"))
        except ConnectionResetError:
            pass

    def menu_render(self):
        self.texts = []
        text_my_tank = self.font_text.render("X "+str(self.my_tank.live), True, (255, 255, 255), (0, 0, 0))
        text_my_tank_rect = text_my_tank.get_rect()
        text_my_tank_rect.center = (self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT + self.SCREEN_HEIGHT_MENU // 2)

        self.texts.append((text_my_tank, text_my_tank_rect))

        text_enemy_tank = self.font_text.render("X "+str(self.enemy_tank.live), True, (255, 255, 255), (0, 0, 0))
        text_enemy_tank_rect = text_enemy_tank.get_rect()
        text_enemy_tank_rect.center = (self.SCREEN_WIDTH // 2 + 100, self.SCREEN_HEIGHT + self.SCREEN_HEIGHT_MENU // 2)

        self.texts.append((text_enemy_tank, text_enemy_tank_rect))

    def show_menu(self):
        for text, rect in self.texts:
            self.window.blit(text, rect)
        pygame.draw.rect(self.window, (255, 255, 255), pygame.Rect(0, self.SCREEN_HEIGHT,
                                                                   self.SCREEN_WIDTH, self.SCREEN_HEIGHT_MENU),  10)

    def start_game(self):
        while self._is_game:
            self.window.fill([0, 0, 0])
            self.get_event()

            self.show_object()
            self.show_menu()
            self.display.update()
            self.clock.tick(self.FPS)
        print(self._is_game)
        self.game_over_screen()

    def game_over_screen(self):
        while self._screen_game:
            self.window.fill([0, 0, 0])
            font = pygame.font.Font('freesansbold.ttf', 32)

            text_in = self.__mes_stop

            text = font.render(text_in, True, (255, 255, 255), (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100)

            text_1 = font.render("Отчет об окончании игры сгенерирован", True, (255, 255, 255), (0, 0, 0))
            textRect_1 = text_1.get_rect()
            textRect_1.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)

            self.window.blit(text, textRect)
            self.window.blit(text_1, textRect_1)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.add_result_database()
                    pygame.quit()

            self.display.update()

    def show_object(self):
        for object_game in self.object_list_enemy + self.object_list_wall + list(self.object_list_bullet.values()):
            object_game.display()

    def move_tank(self, data_tank: dict):
        tank = self.my_tank if str(self.my_tank.uuid) == data_tank["uuid_player"] else self.enemy_tank
        tank.set_new_position(data_tank)

    def get_event(self):
        event_list = pygame.event.get()
        keys = pygame.key.get_pressed()

        self._move_tank_event(keys, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])

        for event in event_list:
            if event.type == RENDER_MAP:
                map_list = event.dict["dict"]
                self.render_map(map_list)
                self.menu_render()
            elif event.type == UPDATE_OBJECT:
                list_obj = event.dict["dict"]["obj"]
                for obj in list_obj:
                    obj = loads(obj)
                    if obj["type"] == "tank":
                        self.move_tank(obj)
                    elif obj["type"] == "bullet":
                        if obj["uuid"] in self.object_list_bullet:
                            self.object_list_bullet[obj["uuid"]].set_new_position(obj)
                        else:
                            self.object_list_bullet[obj["uuid"]] = Bullet(obj, self.window)
                    elif obj["type"] == "wall":
                        if obj["move"] == "destroy":
                            for i, wall in enumerate(self.object_list_wall):
                                if wall.rect.x == obj["position"]["x"] and wall.rect.y == obj["position"]["y"]:
                                    self.object_list_wall.pop(i)
                                    break
                    elif obj["type"] == "bullet_dest":
                        try:
                            del self.object_list_bullet[obj["uuid"]]
                        except KeyError:
                            pass

                    elif obj["type"] == "tank_live":
                        tank = self.my_tank if str(self.my_tank.uuid) == obj["uuid"] else self.enemy_tank
                        tank.live = obj["count"]
                        self.menu_render()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.send_server_message(BaseMessage(
                        uuid=self.__uuid_player,
                        type_message=TypeMessage.FIRE,
                        body={}
                    ))
            elif event.type == GAME_STOP:
                self.__mes_stop = event.dict["dict"]["message"]
                self._is_game = False

    def _move_tank_event(self, keys, index_keys):
        message = None
        if keys[index_keys[0]]:
            message = "up"
        elif keys[index_keys[1]]:
            message = "down"
        elif keys[index_keys[2]]:
            message = "left"
        elif keys[index_keys[3]]:
            message = "right"

        self.send_server_message(BaseMessage(
            uuid=self.__uuid_player,
            type_message=TypeMessage.MOVE_TANK,
            body={
                "side": message
            }
        ))

    def render_tank(self, tanks: list):
        for i in tanks:
            i = json.loads(i)
            if i["uuid_player"] == self.__uuid_player:
                self.my_tank = Tank(self.window,
                                    "yellow_tank.png",
                                    (i["direction"]["x"], i["direction"]["y"]),
                                    (i["size"]["height"], i["size"]["width"]),
                                    (i["position"]["x"], i["position"]["y"]),
                                    i["angle_rotate"],
                                    i["uuid_player"])

                self.position_players["my_tank"] = (i["position"]["x"], i["position"]["y"])
                self.object_list_enemy.append(self.my_tank)
            else:
                self.enemy_tank = Tank(self.window,
                                       "gray_tank.png",
                                       (i["direction"]["x"], i["direction"]["y"]),
                                       (i["size"]["height"], i["size"]["width"]),
                                       (i["position"]["x"], i["position"]["y"]),
                                       i["angle_rotate"],
                                       i["uuid_player"])
                self.object_list_enemy.append(self.enemy_tank)
                self.position_players["enemy_tank"] = (i["position"]["x"], i["position"]["y"])

    def render_map(self, map_game: dict):
        obj = map_game["map"]
        for i in obj:
            i = json.loads(i)
            self.object_list_wall.append(Wall(i["img"],
                                              i["left"],
                                              i["top"],
                                              self.window,
                                              0,
                                              (i["size"]["height"], i["size"]["width"])))
        self.render_tank(map_game["tank_players"])

    def last_id_result(self):
        with open("files/results.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) > 0:
                id_result = lines[-1].split("|")[0]
                return int(id_result) + 1
            return 1

    def generate_file_results(self, name_file):
        with open(name_file, "w+", encoding="utf-8") as file:
            file.write("Итоги игры\n")
            sum_bullet = 0
            sum_wall = 0
            sum_hit = 0
            for key in self._information:
                if key == "gray_tank.png":
                    file.write("Статистика серого танка:\n")
                    file.write(f"Количества здоровья: {self.my_tank.live}\n")
                    file.write(f"Выпущенно снарядов за игру: {self._information[key]['bullet']}\n")
                    file.write("\tИз этих снарядов:\n")
                    file.write(f"\t\tСнаряды, сломавшие стены: {self._information[key]['broke']}\n")
                    file.write(f"\t\tСнаряды, попавшие в танк противника: {self._information[key]['hit_tank']}\n")

                    sum_bullet += self._information[key]['bullet']
                    sum_wall += self._information[key]['broke']
                    sum_hit += self._information[key]['hit_tank']
                elif key == "yellow_tank.png":
                    file.write("Статистика желтого танка:\n")
                    file.write(f"Количества здоровья: {self.enemy_tank.live}\n")
                    file.write(f"Выпущенно снарядов за игру: {self._information[key]['bullet']}\n")
                    file.write("\tИз этих снарядов:\n")
                    file.write(f"\t\tСнаряды, сломавшие стены: {self._information[key]['broke']}\n")
                    file.write(f"\t\tСнаряды, попавшие в танк противника: {self._information[key]['hit_tank']}\n")

                    sum_bullet += self._information[key]['bullet']
                    sum_wall += self._information[key]['broke']
                    sum_hit += self._information[key]['hit_tank']
                else:
                    file.write("\n")
                    file.write(f"Снаряды, попавшие в снаряды противника: {self._information[key]}\n")

            file.write("-" * 60 + "\n")
            file.write("Общая статистика\n")
            file.write(f"Выпущенно снарядов за игру: {sum_bullet}\n")
            file.write("\tИз этих снарядов:\n")
            file.write(f"\t\tСнаряды, сломавшие стены: {sum_wall}\n")
            file.write(f"\t\tСнаряды, попавшие в танк: {sum_hit}\n")
            file.write(f"Снаряды, попавшие в танк: {sum_hit}\n")
            if self.my_tank.live < self.enemy_tank.live:
                file.write(f"Победил жёлтый танк")
            else:
                file.write(f"Победил серый танк")

    def add_result_database(self):
        with open("files/results.txt", "a+", encoding="utf-8") as file:
            id_result = self.last_id_result() #ID результата игры
            path_file = f"files/results/{randint(1, 10000000)}.txt"
            self.generate_file_results(path_file)
            datetime_now = datetime.now()
            file.write(f"{id_result}|{datetime_now.strftime('%d/%m/%Y, %H:%M')}|{path_file}\n")