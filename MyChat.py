import socket
import sys
import threading
import select
class Server:
    def __init__(self, host="0.0.0.0", port=5000):
        s = socket.socket()
        s.bind((host,port))
        s.listen()
        self.__s = s
        print("Le serveur écoute à présent sur {}:{}".format(host,port))

        

    
    def run(self):
        self.handlers = {
            '/exit': self._exit,
            #'/quit': self._quit,
            '/online': self._online,
            #'/c': self._send
        }
        self.clients_connectes = []
        self.__running = True
        self.__address = None
        threading.Thread(target=self.terminalcommand).start()
        #threading.Thread(target=self.chattercommand).start()
        while self.__running:
            
            asked_connexions, wlist, xlist = select.select([self.__s],
            [], [], 0.05)
    
            for connexion in asked_connexions:
                
                client, addr = connexion.accept()
                print('connexion')
                client.send('/pseudo'.encode())
                response= False
                while not response:
                    pseudo= client.recv(1024).decode()
                    if len(pseudo)>0:
                        response=True
                        print('le pseudo est :'+ str(pseudo))
                        
                print(addr)
                # On ajoute le socket connecté à la liste des clients
                self.clients_connectes.append(addr)
            
    def terminalcommand(self):   
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()
            # Call the command handler
            if command in self.handlers:
                try:
                    self.handlers[command]() if param == '' else self.handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")
            else:
                print('Command inconnue:', command)        

    def chattercommand(self):
        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(self.clients_connectes,
                [], [], 0.05)
        except select.error:
            pass
        else:
            # On parcourt la liste des clients à lire
            for client in clients_a_lire:
                # Client est de type socket
                msg_recu = client.recv(1024)
                # Peut planter si le message contient des caractères spéciaux
                msg_recu = msg_recu.decode()
                print("Reçu {}".format(msg_recu))
                client.send(b"5 / 5")   
        
         
    def _exit(self):
        self.__running = False
        self.__address = None
        self.__s.close()

    def _online(self):
        print('List of online people : {}'.format(str(self.clients_connectes)))





class Chat:
    def __init__(self, host="0.0.0.0", port=5000):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Écoute sur {}:{}'.format(host, port))
        
    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send
        }
        self.__running = True
        self.__address = None
        threading.Thread(target=self._receive).start()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")
            else:
                print('Command inconnue:', command)
    
    def _exit(self):
        self.__running = False
        self.__address = None
        self.__s.close()
    
    def _quit(self):
        self.__address = None
    
    def _join(self, param):
        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__address = (tokens[0], int(tokens[1]))
                print('Connecté à {}:{}'.format(*self.__address))
            except OSError:
                print("Erreur lors de l'envoi du message.")
    
    def _send(self, param):
        if self.__address is not None:
            try:
                message = param.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__address)
                    totalsent += sent
            except OSError:
                print('Erreur lors de la réception du message.')
    
    def _receive(self):
        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                print(data.decode())
                print(address)
            except socket.timeout:
                pass
            except OSError:
                return

if __name__ == '__main__':
    #if len(sys.argv) == 3:
    #    Chat(sys.argv[1], int(sys.argv[2])).run()
    if len(sys.argv) == 2:
        if sys.argv[1]== 'server':
            Server().run()
        elif sys.arv[1]== 'chatter':
            Chat().run()
    elif len(sys.argv)==1:
        print('You need to add one argument to say whether'+
               ' you want to be a "server" or a "chatter"')
    else:
        print('To much arguments')