import select
import socket
import threading
import random
import time
import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
from ServerMainUI import *

# class Room():
#     def __init__(self, name, socket, server):
#         self.name = name
#         self.socket = socket
#         self.server = server
#         self.userList = []  # 客户端
#         self.listSocket = []
#
#     self.channels[self.channels.index(channel)]['users'].append((ip, port))

#     def userExitRoom(self, addr):
#         for user in self.userList:
#             if addr == user[0]:
#                 self.listSocket.remove(user[1])
#                 self.userList.remove(user)
#                 message = {}
#                 message['Head'] = 'EXIT SERVER'
#                 message['Data'] = self.channels
#                 JsonData = json.dumps(message).encode('utf-8')
#                 user[1].sendall(JsonData)
#                 self.updateUserListUI()
#                 break

class Server():
    def __init__(self, UI):
        self.FrameUI = UI

        self.localIP = '127.0.0.1'
        self.serverPort = 5000
        self.channels = []
        self.udpServer = []  # channel socket
        self.userList = []  # 客户端
        self.listSocket = []

        self.buildServer()
        self.t = threading.Thread(target=self.run, args=(),)
        self.t.setDaemon(True)
        self.t.start()

        self.OpenChannel('Channel1', 'Study')
        self.OpenChannel('Channel2',  'Game')

        self.updateChannelListUI()

    def run(self):
        # self.buildServer()
        print('Server OnListen')
        while self.listSocket:
            # 有数据可读的时候，select返回(可能描述不是很准确)
            rlist, wlist, elist = select.select(self.listSocket, [], [])
            if not (rlist or wlist or elist):
                print('time out')
                break
            for sock in rlist:
                # 如果是tcpServer表示有新的客户端向我们发送连接请求了
                if sock is self.tcpServer:
                    print('connecting ...')
                    try:
                        client, addr = sock.accept()
                        print('TCP connect from', addr)
                        client.setblocking(False)
                        # 将新的客户端添加到listSocket,这样就可以被select检测了
                        self.listSocket.append(client)
                        flg = True
                        for user in self.userList:
                            if addr == user[0]:
                                flg = False
                                break
                        if flg:  # 不在列表中
                            self.userList.append((addr, client))
                        self.updateUserListUI()
                    except Exception:
                        print('exit threading')
                        break
                elif sock in self.udpServer:
                    try:
                        # udp　表示用户发送的聊天消息
                        data, addr = sock.recvfrom(1024)
                        print('UDP recvfrom ', data, ' from', addr)
                        message = json.loads(data.decode())
                        if message['To'] == 'all':
                            # 全部转发
                            for channel in self.channels:
                                if addr in channel['users']:
                                    print('Room {0} recice message:{1} From:{2}'.format(channel['name'], data, addr))
                                    # 将消息转发
                                    for user in channel['users']:
                                        # message = {}
                                        # message['From'] = addr
                                        # message['Data'] = data
                                        JsonData = json.dumps(message).encode('utf-8')
                                        self.udpServer[self.channels.index(channel)].sendto(JsonData, user)
                        else:
                            for channel in self.channels:
                                if addr in channel['users']:
                                    user = (message['To'][0], message['To'][1])
                                    JsonData = json.dumps(message).encode('utf-8')
                                    self.udpServer[self.channels.index(channel)].sendto(JsonData, user)
                        # 将消息发送到所有客户机上，转发
                        # for key, value in self.clientInfo.items():
                        #     sock.sendto(data, value)
                    except:
                        print('UDP检查到异常')
                        # self.listSocket.remove(sock)

                else:
                    # tcpClient　就是客户端发送的命令
                    try:
                        addr = sock.getpeername()
                        command = sock.recv(1024)
                        print('TCP command:', command)
                        # 当command 为空的时候　表示客户端tcp已经断开连接了
                        command = str(command, encoding='utf-8')
                        if command == 'GET':
                            message = {}
                            message['Head'] = 'CHANNELSLIST'
                            message['Data'] = self.channels
                            JsonData = json.dumps(message).encode('utf-8')
                            sock.sendall(JsonData)
                        elif command.find('ENTER') != -1:
                            para = command.split(' ')
                            name = para[1]
                            ip = para[2]
                            port = int(para[3])

                            for channel in self.channels:
                                if channel['name'] == name:
                                    # channel['users'].append(addr)
                                    # channel['users'].append((ip,int(port)))
                                    self.channels[self.channels.index(channel)]['users'].append((ip, port))
                                    break
                            message = {}
                            message['Head'] = 'USERLIST'
                            message['channel'] = name
                            for channel in self.channels:
                                if channel['name'] == name:
                                    message['Data'] = channel['users']
                                    break
                            JsonData = json.dumps(message).encode('utf-8')
                            # sock.sendall(JsonData)
                            for user in self.userList:
                                user[1].sendall(JsonData)
                            # 转发进入消息 UDP
                            for channel in self.channels:
                                if name == channel['name']:
                                    # 将消息转发
                                    for user in channel['users']:
                                        message = {}
                                        message['From'] = ('System Message', '0')
                                        message['To'] = 'all'
                                        message['Data'] = '{}:{} Enter Room {}.'.format(ip, port, name)
                                        JsonData = json.dumps(message).encode('utf-8')
                                        self.udpServer[self.channels.index(channel)].sendto(JsonData, user)
                        elif command.find('QUIT') != -1:  # 退出聊天室命令
                            para = command.split(' ')
                            name = para[1]
                            ip = para[2]
                            port = int(para[3])
                            for channel in self.channels:
                                if channel['name'] == name:
                                    self.channels[self.channels.index(channel)]['users'].remove((ip, port))
                                    for user in self.channels[self.channels.index(channel)]['users']:
                                        message = {}
                                        message['From'] = ('System Message', '0')
                                        message['To'] = 'all'
                                        message['Data'] = '{}:{} Exit Room.'.format(ip, port)
                                        JsonData = json.dumps(message).encode('utf-8')
                                        self.udpServer[self.channels.index(channel)].sendto(JsonData, user)
                                    break
                            message = {}
                            message['Head'] = 'USERLIST'
                            message['channel'] = name
                            for channel in self.channels:
                                if channel['name'] == name:
                                    message['Data'] = channel['users']
                                    break
                            JsonData = json.dumps(message).encode('utf-8')
                            # sock.sendall(JsonData)
                            for user in self.userList:
                                user[1].sendall(JsonData)
                        elif command.find('EXIT') != -1:
                            para = command.split(' ')
                            name = para[1]
                            ip = para[2]
                            port = int(para[3])
                            # sock.close()
                            self.listSocket.remove(sock)
                            for channel in self.channels:
                                if name == channel['name']:
                                    if (ip, port) in channel['users']:
                                        self.channels[self.channels.index(channel)]['users'].remove((ip, port))
                                    for user in self.channels[self.channels.index(channel)]['users']:
                                        message = {}
                                        message['From'] = ('System Message', '0')
                                        message['To'] = 'all'
                                        message['Data'] = '{}:{} Exit Room.'.format(ip, port)
                                        JsonData = json.dumps(message).encode('utf-8')
                                        self.udpServer[self.channels.index(channel)].sendto(JsonData, user)
                                    break
                            message = {}
                            message['Head'] = 'USERLIST'
                            message['channel'] = name
                            for channel in self.channels:
                                if channel['name'] == name:
                                    message['Data'] = channel['users']
                                    break
                            JsonData = json.dumps(message).encode('utf-8')
                            # sock.sendall(JsonData)
                            for user in self.userList:
                                user[1].sendall(JsonData)
                            # 列表更新
                            for user in self.userList:
                                if addr == user[0]:
                                    self.userList.remove(user)
                            self.updateUserListUI()
                            print('Exit From ', addr)
                    except:
                        self.listSocket.remove(sock)
                        addr = sock.getpeername()
                        for user in self.userList:
                            if addr == user[0]:
                                self.userList.remove(user)
                        self.updateUserListUI()
                        print('远程主机强迫关闭了一个现有的连接')
        print('out threading')
        self.tcpServer.close()

    def updateUserListUI(self):
        self.FrameUI.listWidget.clear()
        for user in self.userList:
            title = '{0}:{1}'.format(user[0][0], user[0][1])
            self.FrameUI.listWidget.addItem(title)

    def updateChannelListUI(self):
        self.FrameUI.listWidget_2.clear()
        for channel in self.channels:
            title = '{:<10s}(Theme:{:<10s}, Port:{:<5d})'.format(channel['name'], channel['Theme'], channel['port'])
            self.FrameUI.listWidget_2.addItem(title)

    def buildServer(self):
        try:
            # tcp服务器建立
            self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpServer.setblocking(False)
            self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 服务器地址绑定
            self.tcpServer.bind((self.localIP, self.serverPort))
            self.tcpServer.listen(0)
            # select 输入可读参数，意思是当这个列表里面任何一个元素可读，select就有返回值
            self.listSocket.append(self.tcpServer)
            # for server in self.udpServer:
            #     self.listSocket.append(server)
        except:
            self.status = False
        else:
            self.status = True

    def OpenChannel(self, name, Theme):
        # udp的端口是tcp端口号+1
        udpPort = random.randint(3000, 6000)
        udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpServer.bind((self.localIP, udpPort))
        udpServer.setblocking(False)
        channel = {}
        channel['name'] = name
        channel['Theme'] = Theme
        channel['port'] = udpPort
        channel['users'] = []
        self.channels.append(channel)
        self.udpServer.append(udpServer)
        self.listSocket.append(udpServer)  # 加入监听
        print('Add channel:({name}:{Theme}:{host},{port})'.format(name = name, Theme = Theme, host = self.localIP, port = udpPort))
        message = {}
        message['Head'] = 'CHANNELSLIST'
        message['Data'] = self.channels
        JsonData = json.dumps(message).encode('utf-8')
        for user in self.userList:
            # JsonData = json.dumps(self.channels).encode('utf-8')
            user[1].sendall(JsonData)
        return channel

    # def showChannel(self, name):
    #     for channel in self.channels:
    #         if channel['name'] == name:
    #             # channel['users'].append(addr)
    #             # channel['users'].append((ip,int(port)))
    #             for user in self.users:
    #                 ip = self.channels[self.channels.index(channel)][user]['ip']
    #                 port = self.channels[self.channels.index(channel)][user]['port']
    #             break
    #     if 1:
    #         pass
    #     else:
    #         reply = QMessageBox.question(self, '提示',
    #                                      'There is no channel called {0}!'.format(user),
    #                                      QMessageBox.Yes)

    def updateUsersINChannel(self, name):
        self.FrameUI.groupBox_2.setTitle('Channel:' + name)
        self.FrameUI.listWidget_3.clear()  # 聊天室用户列表
        for channel in self.channels:
            if channel['name'] == name:
                # channel['users'].append(addr)
                # channel['users'].append((ip,int(port)))
                for user in channel['users']:
                    title = '{:<8}:{:<8}:{:<8}'.format(name, user[0], user[1])
                    self.FrameUI.listWidget_3.addItem(title)

    def kickOut(self, addr, name):
        for channel in self.channels:
            # print(channel['name'])
            if channel['name'] == name:
                # print('channel')
                for user in channel['users']:
                    if addr[1] == user[1]:
                        print(user[1])
                        # self.userList.remove(user)
                        for alive_user in self.channels[self.channels.index(channel)]['users']:
                            message = {}
                            message['From'] = ('System Message', '0')
                            message['To'] = 'all'
                            message['Data'] = '{}:{} Exit Room.'.format(user[0], user[1])
                            JsonData = json.dumps(message).encode('utf-8')
                            self.udpServer[self.channels.index(channel)].sendto(JsonData, alive_user)
                            channel['users'].remove(user)
                        break
        message = {}
        message['Head'] = 'USERLIST'
        message['channel'] = name
        for channel in self.channels:
            if channel['name'] == name:
                message['Data'] = channel['users']
                break
        JsonData = json.dumps(message).encode('utf-8')
        # sock.sendall(JsonData)
        for user in self.userList:
            user[1].sendall(JsonData)
        self.updateUsersINChannel(name)

    def userEixt(self, addr):
        for user in self.userList:
            if addr == user[0]:
                self.listSocket.remove(user[1])
                self.userList.remove(user)
                message = {}
                message['Head'] = 'EXIT SERVER'
                message['Data'] = self.channels
                JsonData = json.dumps(message).encode('utf-8')
                user[1].sendall(JsonData)
                self.updateUserListUI()
                break

    def roomEixt(self, name):
        for channel in self.channels:
            if channel['name'] == name:
                # 通知所有用户
                sock = self.udpServer[self.channels.index(channel)]
                for user in channel['users']:
                    message = {}
                    message['From'] = ('System Message', '0')
                    message['To'] = 'all'
                    message['Data'] = 'channel is closed!.'
                    JsonData = json.dumps(message).encode('utf-8')
                    sock.sendto(JsonData, user)

                self.channels.remove(channel)
                # 通知所有客户端
                message = {}
                message['Head'] = 'CHANNELSLIST'
                message['Data'] = self.channels
                JsonData = json.dumps(message).encode('utf-8')
                for user in self.userList:
                    user[1].sendall(JsonData)
                self.listSocket.remove(sock)  # 监听取消
                self.udpServer.remove(sock)
                self.updateChannelListUI()
                break
        pass

    def close(self):
        print('Close Server')
        self.listSocket = []
        self.tcpServer.close()
        time.sleep(1)


class ServerWindowDlg(QMainWindow):
    def __init__(self):
        super(ServerWindowDlg, self).__init__()
        self.ui_Window = Ui_MainWindow()
        self.ui_Window.setupUi(self)
        self.server = Server(self.ui_Window)
        if self.server.status:
            self.ui_Window.label_6.setText('On Listen')
            self.ui_Window.label_7.setText(self.server.localIP)
            self.ui_Window.label_8.setText(str(self.server.serverPort))
        else:
            self.ui_Window.label_6.setText('Open Error')

    def closeEvent(self, *args, **kwargs):
        self.server.close()

    def NewChannel(self):
        name = self.ui_Window.lineEdit.text()
        theme = self.ui_Window.lineEdit_2.text()
        self.server.OpenChannel(name, theme)
        self.server.updateChannelListUI()
        # if  channel!= {}:
        #     title = '{:<10s}(theme:{:<10s}, Port:{:<5d})'.format(channel['name'],channel['theme'],channel['port'])
        #     self.ui_Window.listWidget_2.addItem(title)
        #     # self.ui_Window.listWidget_2
        pass

    def enterChannel(self):
        name = self.ui_Window.lineEdit.text()
        theme = self.ui_Window.lineEdit_2.text()
        self.server.updateUsersINChannel(name)

    def leaveChannel(self):
        self.server.updateUsersINChannel('1')

    def userKickOut(self, item):
        user = item.text()
        reply = QMessageBox.question(self, '提示',
                                     'Are you sure to Kick Out from {0}?'.format(user),
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            channel = user.split(':')[0]
            addr = (user.split(':')[1], int(user.split(':')[2]))
            print(channel, addr)
            self.server.kickOut(addr, channel)
        else:
            pass

    def userForceExit(self, item):
        user = item.text()
        reply = QMessageBox.question(self, '提示',
                                     'Are you sure to Force Exit {0}?'.format(user),
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            addr = (user.split(':')[0], int(user.split(':')[1]))
            self.server.userEixt(addr)
        else:
            pass

    def ChannelClose(self, item):
        channel = item.text()
        reply = QMessageBox.question(self, '提示',
                                     'Are you sure to Destory {0}?'.format(channel),
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            name = channel.split(' ')[0].strip()
            self.server.roomEixt(name)
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ServerWindowDlg()
    mainWindow.show()
    sys.exit(app.exec_())
