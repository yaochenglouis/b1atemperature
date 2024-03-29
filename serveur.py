# TD4/serveur.py

# Application exemple : affichage de mes lieux préférés à la Croix-Rousse

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json
from Chercher_les_donnees import *

cordn=coordonnees()
# définition du handler
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  # version du serveur
  server_version = 'TD4/serveur.py/0.1'

  # on surcharge la méthode qui traite les requêtes GET
  def do_GET(self):
    self.init_params()

    # requete location - retourne la liste de lieux et leurs coordonnées géogrpahiques
    if self.path_info[0] == "location":
      data=cordn
      self.send_json(data)
      
#    envoie la date
    elif self.path_info[0] == "toctoc":
      self.send_html('<p>Bonjour {} {}</p>'.format(self.params['date_debut'][0],self.params['date_fin'][0],int(self.path_info[1])))
      
    # requete description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
    elif self.path_info[0] == "description":
      data=[{'id':1,'desc':"Il ne faut pas être <b>trop grand</b> pour marcher dans cette rue qui passe sous une maison"},
            {'id':2,'desc':"Cette rue est <b>si étroite</b> qu'on touche les 2 côtés en tendant les bras !"},
            {'id':3,'desc':"Ce jardin <b>méconnu</b> évoque le palais idéal du Facteur Cheval"}]
      for c in data:
        if c['id'] == int(self.path_info[1]):
          self.send_json(c)
          break

    # requête générique
    elif self.path_info[0] == "service":
      self.send_html('<p>Path info : <code>{}</p><p>Chaîne de requête : <code>{}</code></p>' \
          .format('/'.join(self.path_info),self.query_string));
                    


    else:
      self.send_static()


  # méthode pour traiter les requêtes HEAD
  def do_HEAD(self):
      self.send_static()


  # méthode pour traiter les requêtes POST - non utilisée dans l'exemple
  def do_POST(self):
    self.init_params()

    # requête générique
    if self.path_info[0] == "service":
      self.send_html(('<p>Path info : <code>{}</code></p><p>Chaîne de requête : <code>{}</code></p>' \
          + '<p>Corps :</p><pre>{}</pre>').format('/'.join(self.path_info),self.query_string,self.body));
                      

    #    envoie la date
    elif self.path_info[0] == "affichercourbe":
      dds=self.path_info[1]
      dfs=self.path_info[2]
      date_debut=self.path_info[1].split('-')
      date_debut=int(date_debut[0]+date_debut[1]+date_debut[2])
      date_fin=self.path_info[2].split('-')
      date_fin=int(date_fin[0]+date_fin[1]+date_fin[2])
      Id_station=self.path_info[4]
      T_type=self.path_info[3]
      courbe=tracer_courbe(Id_station,date_debut,date_fin,T_type,dds,dfs)
      ID=courbe[0]
      legende=courbe[1]



  # on envoie le document statique demandé
  def send_static(self):

    # on modifie le chemin d'accès en insérant le répertoire préfixe
    self.path = self.static_dir + self.path

    # on calcule le nom de la méthode parent à appeler (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    method = 'do_{}'.format(self.command)

    # on traite la requête via la classe parent
    getattr(http.server.SimpleHTTPRequestHandler,method)(self)


  # on envoie un document html dynamique
  def send_html(self,content):
     headers = [('Content-Type','text/html;charset=utf-8')]
     html = '<!DOCTYPE html><title>{}</title><meta charset="utf-8">{}' \
         .format(self.path_info[0],content)
     self.send(html,headers)

  # on envoie un contenu encodé en json
  def send_json(self,data,headers=[]):
    body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body) 

  # on envoie la réponse
  def send(self,body,headers=[]):
     encoded = bytes(body, 'UTF-8')

     self.send_response(200)

     [self.send_header(*t) for t in headers]
     self.send_header('Content-Length',int(len(encoded)))
     self.end_headers()

     self.wfile.write(encoded)


  # on analyse la requête pour initialiser nos paramètres
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = info.path.split('/')[1:]
    print(self.path_info)
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''

    print(length,ctype,self.body, self.params)


# instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()
