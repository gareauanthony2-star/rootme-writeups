import socket
import math
import re

HOST = "challenge01.root-me.org"
PORT = 52002

s = socket.create_connection((HOST, PORT)) # ouvre la co tcp vers le serveur root-me

data = s.recv(4096).decode() # Lit ce que le serveur envoie (jusqu’à 4096 octets) et le convertit de bytes en texte.
print("Reçu :", data)

m = re.search(r"square root of (\d+).*?multiply by (\d+)", data, re.S) # Cherche dans le texte la phrase square root of 198 and multiply by 9004
n1, n2 = int(m.group(1)), int(m.group(2)) # et extrait les deux nombres (198 et 9004), peu importe où ils sont dans le message.

result = round(math.sqrt(n1) * n2, 2) # Calcule √n1 × n2, arrondi à 2 décimales
print("Envoi :", result)

s.sendall(f"{result:.2f}\n".encode())

print("Réponse :", s.recv(4096).decode())
s.close()
