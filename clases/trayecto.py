import app
from datetime import datetime
#from clases.usuario import *

def get_gasolinera(latitud, longitud, localidad, provincia, municipio, direccion):
    g = {
        'latitud': latitud,
        'longitud': longitud,
        'localidad': localidad,
        'provincia': provincia,
        'municipio': municipio,
        'direccion': direccion
    }
    return g


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
            'comentario': v['comentario'],
            'tipo': v['tipo'],
            'id_reserva': v['id_reserva']
        }) 
    return lista_valoraciones

def get_usuario_trayecto(id_usuario, id_coche):
    usuario = app.get_usuario_aux(id_usuario)
    u = {
        'id': usuario['_id'],
        'nombre': usuario['nombre'],
        'apellidos': usuario['apellidos'],
        'descripcion': usuario['descripcion'],
        'fotografia': usuario['fotografia'],
        'valoraciones': get_valoraciones_usuario(usuario['listaValoracionesRecibidas'])
    }
    if id_coche:
        c = None
        for coche in usuario['listaCoches']:
            if id_coche == coche['_id']:
                c = coche    
        return u, c
    else:
        return u


def get_coche_trayecto(id_trayecto):
    coche = app.get_coche_trayecto_aux(id_trayecto)
    return coche


def get_reservas_trayecto(reservas):
    lista_reservas = []
    for reserva in reservas:
        lista_reservas.append({
            'id': reserva['_id'],
            'plazasReservadas': reserva['plazasReservadas'],
            'fechaReserva': reserva['fechaReserva'],
            'solicitante': get_usuario_trayecto(reserva['solicitante'], None)
        })
    return lista_reservas

def get_lite_trayecto(id_trayecto):
    trayecto = app.get_trayecto_aux(id_trayecto)
    conductor, coche = get_usuario_trayecto(trayecto['conductor'], trayecto['coche'])
    t = {
        'id': trayecto['_id'],
        'conductor': conductor,
        'coche': coche,
        'descripcion': trayecto['descripcion'],
        'duracion': trayecto['duracion'],
        'periodicidad': trayecto['periodicidad'],
        'precio': trayecto['precio'],
        'ciudadOrigen': trayecto['ciudadOrigen'],
        'ciudadDestino': trayecto['ciudadDestino'],
        'direccionOrigen': trayecto['direccionOrigen'],
        'direccionDestino': trayecto['direccionDestino'],
        'latitudOrigen': trayecto['latitudOrigen'],
        'longitudOrigen': trayecto['longitudOrigen'],
        'latitudDestino': trayecto['latitudDestino'],
        'longitudDestino': trayecto['longitudDestino'],
        'fechaHora': trayecto['fechaHora'],
        'plazasOfertadas': trayecto['plazasOfertadas'],
        'plazasDisponibles': app.get_plazas_disponibles_aux(trayecto['_id'])
    }
    return t

def get_full_trayecto(id_trayecto):
    trayecto = app.get_trayecto_aux(id_trayecto)
    conductor, coche = get_usuario_trayecto(trayecto['conductor'], trayecto['coche'])
    t = {
        'id': trayecto['_id'],
        'conductor': conductor,
        'coche': coche,
        'descripcion': trayecto['descripcion'],
        'duracion': trayecto['duracion'],
        'periodicidad': trayecto['periodicidad'],
        'precio': trayecto['precio'],
        'ciudadOrigen': trayecto['ciudadOrigen'],
        'ciudadDestino': trayecto['ciudadDestino'],
        'direccionOrigen': trayecto['direccionOrigen'],
        'direccionDestino': trayecto['direccionDestino'],
        'latitudOrigen': trayecto['latitudOrigen'],
        'longitudOrigen': trayecto['longitudOrigen'],
        'latitudDestino': trayecto['latitudDestino'],
        'longitudDestino': trayecto['longitudDestino'],
        'fechaHora': trayecto['fechaHora'],
        'plazasOfertadas': trayecto['plazasOfertadas'],
        'reservas': get_reservas_trayecto(trayecto['listaReservas']),
        'plazasDisponibles': app.get_plazas_disponibles_aux(trayecto['_id'])
    }
    return t
    
#class Reserva:
#    def __init__(self, reserva):
#        self.doc_reserva = reserva
#        self.id = self.doc_reserva["_id"]
#        self.plazas_reservadas = self.doc_reserva["plazasReservadas"]
#        self.fecha_reserva = self.doc_reserva["fechaReserva"]
#        self.solicitante = Usuario(self.doc_reserva["solicitante"])


#class Trayecto:
#    def __init__(self, id):
#        self.doc_trayecto = app.get_trayecto_aux(id)
#        self.id = id
#        self.coche_id = self.doc_trayecto["coche"]
#        self.conductor_id = self.doc_trayecto["conductor"]
#        self.descripcion = self.doc_trayecto["descripcion"]
#        self.duracion = self.doc_trayecto["duracion"]
#        self.periodicidad = self.doc_trayecto["periodicidad"]
#        self.precio = self.doc_trayecto["precio"]
#        self.ciudad_destino = self.doc_trayecto["ciudadDestino"]
#        self.ciudad_origen = self.doc_trayecto["ciudadOrigen"]
#        self.direccion_destino = self.doc_trayecto["direccionDestino"]
#        self.direccion_origen = self.doc_trayecto["direccionOrigen"]
#        self.fechaHora = self.doc_trayecto["fechaHora"]
#        self.plazas_ofertadas = self.doc_trayecto["plazasOfertadas"]
#        self.listaReservas = []
#        for reserva in self.doc_trayecto["listaReservas"]:
#            self.listaReservas.append(Reserva(reserva))
#        self.conductor = Usuario(self.conductor_id)
#        self.coche = Coche(app.get_coche_trayecto_aux(self.id))
#        self.plazas_disponibles = app.get_plazas_disponibles_aux(id)