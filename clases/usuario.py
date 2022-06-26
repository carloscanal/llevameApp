import app
from datetime import datetime

def get_usuario_mensaje(id_usuario):
    u = app.get_usuario_aux(id_usuario)
    usuario = {
        'id': u['_id'],
        'nombre': u['nombre'],
        'apellidos': u['apellidos'],
        'descripcion': u['descripcion'],
        'fotografia': u['fotografia']
    }
    return usuario


def get_lista_mensajes_enviados(mensajes):
    lista_mensajes = []
    for m in mensajes:
        lista_mensajes.append({
            'id': m['_id'],
            'receptor': get_usuario_mensaje(m['receptor']),
            'mensaje': m['mensaje'],
            'fechaEnvio': m['fechaEnvio']
        })
    return lista_mensajes


def get_lista_mensajes_recibidos(mensajes):
    lista_mensajes = []
    for id_m in mensajes:
        m = app.get_mensaje_aux(id_m)
        lista_mensajes.append({
            'id': id_m,
             #'emisor': m['emisor'], 'mensaje': m['mensaje'], 'fechaEnvio': m['fecha']
        })
    return lista_mensajes

def get_reserva_origen_destino(reserva, origen, destino, fecha_trayecto, precio, conductor, valorado, plazas_disponible, coche, descripcion, mediaValoraciones, nValoraciones):
    r= {
        '_id': reserva['_id'],
        'plazasReservadas': reserva['plazasReservadas'],
        'fechaReserva': reserva['fechaReserva'],
        'origen': origen,
        'destino': destino,
        'fechaTrayecto': fecha_trayecto,
        'solicitante': reserva['solicitante'],
        'precio': precio,
        'conductor': conductor,
        'valorado': valorado,
        'plazas_disponible': plazas_disponible,
        'coche': coche,
        'descripcion': descripcion,
        'mediaValoraciones': mediaValoraciones,
        'nValoraciones': nValoraciones
        }
    return r

def get_usuario_valorador(id_usuario):
    usuario = app.get_usuario_aux(id_usuario)
    u = {
        'id': usuario['_id'],
        'nombre': usuario['nombre'],
        'apellidos': usuario['apellidos'],
        'descripcion': usuario['descripcion'],
        'fotografia': usuario['fotografia']
    } # Este no tiene valoraciones porque puede haber bucles (si dos usuarios se valoran mutuamente, por ejemplo)
    return u


def get_valoraciones_usuario(valoraciones):
    lista_valoraciones = []
    for v in valoraciones:
        lista_valoraciones.append({
            'id': v['_id'],
            'valorador': get_usuario_valorador(v['valorador']),
            'fecha': v['fechaValoracion'],
            'puntuacion': v['puntuacion'],
            'comentario': v['comentario']
        }) 
    return lista_valoraciones

def get_full_coche_usuario(id_usuario, id_coche):
    c = app.get_coche_por_id_aux(id_usuario,id_coche)
    if c:
        coche = {
            'id': c['_id'],
            'marca': c['marca'],
            'modelo': c['modelo'],
            'tipo': c['tipo'],
            'color': c['color'],
            'descripcion': c['descripcion'],
            'fotografia': c['fotografia']
        }
        return coche
    else:
        return None

def get_full_usuario(id_usuario):
    u = app.get_usuario_aux(id_usuario)
    valoracionMedia, nValoraciones = app.get_valoraciones_media_aux(id_usuario)

    usuario = {
        'id': u['_id'],
        'nombre': u['nombre'],
        'apellidos': u['apellidos'],
        'descripcion': u['descripcion'],
        'fotografia': u['fotografia'],
        'coches': u['listaCoches'],
        'valoraciones': get_valoraciones_usuario(u['listaValoracionesRecibidas']),
        'valoracionMedia': valoracionMedia,
        'numValoraciones': nValoraciones
    }
    return usuario
   
#class Mensaje:
#    def __init__(self, id):
#        self.doc_mensaje = app.get_mensaje_aux(id)
#        if self.doc_mensaje is not None:
#            self.emisor = self.doc_mensaje['emisor']
#            self.mensaje = self.doc_mensaje['mensaje']
#            self.fecha = self.doc_mensaje['fecha']

#class Usuario:
#    def __init__(self, id):
#        self.doc_usuario = app.get_usuario_aux(id)
#        self.id = id
#        self.nombre = self.doc_usuario["nombre"]
#        self.apellidos = self.doc_usuario["apellidos"]
#        self.descripcion = self.doc_usuario["descripcion"]
#        self.fotografia = self.doc_usuario["fotografia"]
#        #list_mensajes_enviados = [] # No se hace por la carga lazy de gestion de info, por los bucles

#       self.lista_mensajes_recibidos = []
#        if self.doc_usuario["listaMensajesRecibidos"] is not None:
#            for mensaje in self.doc_usuario["listaMensajesRecibidos"]:
#                self.lista_mensajes_recibidos.append(Mensaje(mensaje))
#        self.lista_coches = []
#        if self.doc_usuario["listaCoches"] is not None:
#            for coche in self.doc_usuario["listaCoches"]:
#                self.lista_coches.append(Coche(coche))

#        self.lista_valoraciones_recibidas = []
#        if self.doc_usuario["listaValoracionesRecibidas"] is not None:
#            for valoracion in self.doc_usuario["listaValoracionesRecibidas"]:
#                self.lista_valoraciones_recibidas.append(Valoracion(valoracion))

#class Coche:
#    def __init__(self, coche):
#        if coche is not None:
#            self.doc_coche = coche
#            self.id = self.doc_coche["_id"]
#            self.marca = self.doc_coche["marca"]
#            self.modelo = self.doc_coche["modelo"]
#            self.tipo = self.doc_coche["tipo"]
#            self.color = self.doc_coche["color"]
#            self.descripcion = self.doc_coche["descripcion"]
#            self.fotografia = self.doc_coche["fotografia"]
#        else:
#            self = None

#class Valoracion:
#    def __init__(self, valoracion):
#        self.doc_valoracion = valoracion
#        self.id = self.doc_valoracion["_id"]
#        self.valorador = Usuario(self.doc_valoracion["valorador"])
#        self.fechaValoracion = self.doc_valoracion["fechaValoracion"]
#        self.puntuacion = self.doc_valoracion["puntuacion"]
#        self.comentario = self.doc_valoracion["comentario"]