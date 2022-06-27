import json
from builtins import float
from datetime import date, datetime
import mimetypes
from tokenize import Double

import urllib3
import urllib

from authlib.integrations.flask_client import OAuth
from threading import local
import pymongo
from werkzeug.exceptions import HTTPException

from clases import trayecto, usuario
import requests as requests
from flask import Flask, request, jsonify, Response, render_template, session, redirect, url_for
from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util, ObjectId

import re
from unicodedata import normalize

import cloudinary
import cloudinary.uploader
import geocoder
from geopy.geocoders import Nominatim
import pandas as pd

import paypalrestsdk

# app desplegada en Heroku llevame-app.herokuapp.com

app = Flask(__name__)

# app.config['MONGO_URI'] = 'mongodb+srv://lorenzo:lorenzo@clusterweb.yupg4.mongodb.net/iweb?retryWrites=true&w=majority'
app.config['MONGO_URI'] = 'mongodb+srv://canal:canal@cluster0.vodgj.mongodb.net/LlevameApp?retryWrites=true&w=majority'

mongo = PyMongo(app)
app.secret_key = 'sadffasfsadc xiyufevbsdasdvfssazd'

cloudinary.config(
  # cloud_name = "dkwgmat62",     
  cloud_name = "canallcc",
  # api_key = "926419554464644",   
  api_key = "457779831621397",
  # api_secret = "J8bH4s76DPOypvt89Ev7FgVrtQc"
  api_secret = "OCi5Y1KI3ieR5PufEp-bMfO3mv0"
)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    # client_id='884325304780-tu9b97m07oed9dsvu61gv4lhq3k85905.apps.googleusercontent.com',
    client_id='853416967262-2tj4veftl34oseq1jrir94lru2pstb6a.apps.googleusercontent.com',   # canal.lcc.uma.es@mail.com, misAnunciosWebApp
    # client_secret='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',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

# KEY_TIEMPO = "89a43901d7f1827633ddf6e56989ea90"
KEY_TIEMPO = "ae4a89ce4a477001dcf4ea5eac7c64d8"


paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  # "client_id": "AWP2ahcvOuOb1gvPSciS8JGITE9Tv69g7wyCEljo-bRy6QM9fFR5TIKxQ37hJdOal_NcKdnWDOKML547",
  "client_id": "Abh4GvF6wzQ_4uCAdXmXqYwd1QryRYRox50HXGJWUFR8nqKEnMwf82UqH_W_zXB7bu_kKng88uicXim9",
  # "client_secret": "ENTsuwzsiBrKOGTq9iHokd57zhs18UU2F-2JXqIPAqvcjckOnUjl2Wo9vMsXVCyR_dXPs4pQ9lXZmKsy"
  "client_secret": "EJ34OHQxNs_CoCFw--1CHgjYD7_KcIBxOdyCgCGXEt1TbHgh4HYPMrp7MacbkYNBLWjXFtjxQhbGENLt"
  })


def crear_usuario_aux(nombre, apellidos, correo, foto, des, admin):
    coches = []
    mensajes_env = []
    mensajes_rec = []
    valoraciones = []
    id_usuario = -1

    if nombre and correo and (admin or not admin):
        id_usuario = mongo.db.usuario.insert_one(
            {
                "nombre": nombre,
                "apellidos": apellidos,
                "correo": correo,
                "admin": admin,
                "descripcion": des,
                "fotografia": foto,
                "listaCoches": coches,
                "listaMensajesEnviados": mensajes_env,
                "listaMensajesRecibidos": mensajes_rec,
                "listaValoracionesRecibidas": valoraciones
            }
        ).inserted_id

    return id_usuario


@app.route('/api/usuarios/', methods=['POST'])
def crear_usuario_s():
    nombre = request.json['nombre']
    apellidos = request.json['apellidos']
    correo = request.json['correo']
    des = request.json['descripcion']
    foto = request.json['fotografia']

    try:
        admin = request.json['admin']
    except:
        admin = False

    id_usuario = crear_usuario_aux(nombre, apellidos, correo, foto, des, admin)
    if id_usuario == -1:
        response = jsonify(
            {'mensaje:' 'No se ha podido crear un usuario porque el campo nombre o apellidos estan vacios'})
        response.status_code = 400
    else:
        response = jsonify({'mensaje': 'Usuario creado con éxito con ID = ' + str(id_usuario)})
        response.status_code = 201

    return response


# @app.route('/app/usuarios/', methods=['POST'])
# def crear_usuario_c():
#     nombre = request.json['nombre']
#     apellidos = request.json['apellidos']
#     correo = request.json['correo']
#     des = request.json['descripcion']
#     foto = request.json['fotografia']
#     try:
#         admin = request.json['admin']
#     except:
#         admin = False

#     crear_usuario_aux(nombre, apellidos, correo, foto, des, admin)

#     # Falta por mirar qué hacemos con el cliente en la parte de crear
#     # return render_template
#     return None


def eliminar_usuario_aux(id_usuario):
    eliminado = mongo.db.usuario.delete_one({'_id': ObjectId(id_usuario)})
    return eliminado.deleted_count


@app.route('/api/usuarios/<id_usuario>', methods=['DELETE'])
def eliminar_usuario_s(id_usuario):
    borrado = eliminar_usuario_aux(id_usuario)

    if borrado == 1:
        response = jsonify({'mensaje': 'El usuario con el ID = ' + id_usuario + ' fue eliminado correctamente'})
        response.status_code = 200
    else:
        response = jsonify({'mensaje': 'No se ha eliminado ningun usuario porque ese usuario no existe'})
        response.status_code = 400
    return response


# @app.route('/app/usuarios/del/<id_usuario>', methods=['POST'])
# def eliminar_usuario_c(id_usuario):
#     if id_usuario == session["id"]:
#         borrado = eliminar_usuario_aux(id_usuario)
#         return None 
#     else:
#         return render_template('acceso_denegado.html')

    # Falta por mirar qué hacemos con el cliente en la parte de eliminar
    # return render_template


def actualizar_usuario_aux(id_usuario, nombre, apellidos, des, foto, coches, mensajes_env, mensajes_rec, valoraciones):
    actualizado = mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
        {'_id': ObjectId(id_usuario)},  # que haya que cambiarlo para que actualice
        {'$set': {  # sólo uno o lo que nos haga falta, ya lo veremos
            'nombre': nombre,
            'apellidos': apellidos,
            'descripcion': des,
            'fotografia': foto,
            'listaCoches': coches,
            'listaMensajesEnviados': mensajes_env,
            'listaMensajesRecibidos': mensajes_rec,
            'listaValoracionesRecibidas': valoraciones
        }}
    )
    return actualizado.modified_count


@app.route('/api/usuarios/<id_usuario>',
           methods=['PUT'])  # Usamos PUT porque PATCH sólo permite actualizar un sólo atributo del objeto
def actualizar_usuario_s(id_usuario):
    nombre = request.json['nombre']
    apellidos = request.json['apellidos']
    if nombre and apellidos:
        des = request.json['descripcion']
        foto = request.json['fotografia']
        coches = request.json['listaCoches']
        mensajes_env = request.json['listaMensajesEnviados']
        mensajes_rec = request.json['listaMensajesRecibidos']
        valoraciones = request.json['listaValoracionesRecibidas']

        actualizado = actualizar_usuario_aux(id_usuario, nombre, apellidos, des, foto, coches, mensajes_env, mensajes_rec, valoraciones)

        if actualizado == 1:
            response = jsonify({'mensaje': 'El usuario con el ID = ' + id_usuario + ' fue actualizado correctamente'})
            response.status_code = 200
        else:
            response = jsonify({'mensaje': 'No se ha actualizado ningun usuario porque ese usuario no existe'})
            response.status_code = 400
    else:
        response = jsonify(
            {'mensaje': 'No se ha podido actualizar porque falta el atributo nombre o apellidos que son obligatorios.'})
        response.status_code = 304
    return response


@app.route('/app/usuarios/actualizar',methods=['POST'])
def actualizar_usuario_c():
    id_usuario = session["id"]
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    if nombre and apellidos:
        user = get_usuario_aux(id_usuario)
        des = request.form.get('descripcion')
        foto_perfil = request.files['fotoPerfil']
        if foto_perfil:
            response = cloudinary.uploader.upload(foto_perfil)
            foto = response["url"]
        else:
            foto = user["fotografia"]
        actualizado = actualizar_usuario_aux(user['_id'], nombre, apellidos, des, foto, user["listaCoches"], user["listaMensajesEnviados"], user["listaMensajesRecibidos"], user["listaValoracionesRecibidas"])
        return redirect('/app/usuarios/'+id_usuario) #Por ahora a la pagina principal # Retorna a la vista del perfil, se puede cambiar en un futuro
    else:
        usuario_act = usuario.get_full_usuario(id_usuario)
        doc_coches = get_coches_usuario_aux(session["id"])
        return render_template('editar_perfil.html', usuario=usuario_act, coches=doc_coches)

#usuario = get_usuario_aux(session["id"])
#    usuario_act = usuario.Usuario(session["id"])
#    doc_coches = get_coches_usuario_aux(session["id"])
#    list_coches = []
#    for doc in doc_coches:
#        list_coches.append(usuario.Coche(doc))
#    return render_template('mi_perfil.html', usuario=usuario_act, coches=list_coches)



def get_usuarios_aux():
    usuarios = mongo.db.usuario.find()
    return usuarios


def get_usuario_por_correo_aux(correo):
    usuario = mongo.db.usuario.find_one({'correo': correo})
    return usuario


@app.route('/api/usuarios/', methods=['GET'])
def get_usuarios_s():  # Esto tenemos que hablarlo para ver qué código ponemos si ocurre algún error y qué consideramos un error en un get (este y los demás)
    usuarios = get_usuarios_aux()
    aux = json_util.dumps(usuarios)
    response = Response(aux, mimetype='application/json')
    response.status_code = 200
    return response


# @app.route('/app/usuarios/', methods=['GET'])
# def get_usuarios_c():
#     usuarios = get_usuarios_aux()
#     # return render_template
#     return None


def get_usuario_aux(id_usuario):
    usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
    return usuario


@app.route('/api/usuarios/<id_usuario>', methods=['GET'])
def get_usuario_s(id_usuario):
    usuario = get_usuario_aux(id_usuario)
    aux = json_util.dumps(usuario)
    response = Response(aux, mimetype='application/json')
    response.status_code = 200
    return response


@app.route('/app/usuarios/<id_usuario>', methods=['GET'])
def get_usuario_c(id_usuario):
    user = usuario.get_full_usuario(id_usuario)
    return render_template('visualizar_perfil.html', usuario=user)


def get_usuarios_en_rango_por_id_aux(id_inferior, id_superior):
    usuarios = mongo.db.usuario.find({'_id': {'$gt': ObjectId(id_inferior), '$lt': ObjectId(id_superior)}})
    return usuarios


@app.route('/api/usuarios/<id_inferior>/<id_superior>', methods=['GET'])
def get_usuarios_en_rango_por_id_s(id_inferior, id_superior):
    usuarios = get_usuarios_en_rango_por_id_aux(id_inferior, id_superior)
    aux = json_util.dumps(usuarios)
    response = Response(aux, mimetype='application/json')
    response.status_code = 200
    return response


# @app.route('/app/usuarios/por_rango_id', methods=['POST'])
# def get_usuarios_en_rango_por_id_c():
#     id_inferior = request.json['id_inferior']
#     id_superior = request.json['id_superior']
#     usuarios = get_usuarios_en_rango_por_id_aux(id_inferior, id_superior)
#     # return render_template
#     return None


def get_usuarios_contar_aux():
    cuenta = mongo.db.usuario.count_documents({})
    return cuenta


@app.route('/api/usuarios/contar', methods=['GET'])
def get_usuarios_contar_s():
    cuenta = get_usuarios_contar_aux()
    aux = json_util.dumps(cuenta)
    response = Response(aux, mimetype='application/json')
    response.status_code = 200
    return response


# @app.route('/app/usuarios/contar', methods=['GET'])
# def get_usuarios_contar_c():
#     cuenta = get_usuarios_contar_aux()
#     # return render_template
#     return None


def get_usuarios_por_nombre_apellidos_aux(nombre, apellidos):
    if nombre and apellidos:
        usuarios = mongo.db.usuario.find({'nombre': {'$regex': nombre, '$options': 'i'},
                                          'apellidos': {'$regex': apellidos, '$options': 'i'}})
    elif nombre:
        usuarios = mongo.db.usuario.find({'nombre': {'$regex': nombre, '$options': 'i'}})
    else:
        usuarios = mongo.db.usuario.find({'apellidos': {'$regex': apellidos, '$options': 'i'}})

    return usuarios


@app.route('/api/usuarios/nombre/<nombre>/apellidos/<apellidos>', methods=['GET'])
def get_usuarios_por_nombre_apellidos_s(nombre, apellidos):
    usuarios = get_usuarios_por_nombre_apellidos_aux(nombre, apellidos)
    aux = json_util.dumps(usuarios)
    response = Response(aux, mimetype='applicacion/json')
    response.status_code = 200
    return response


# @app.route('/app/usuarios/por_nombre_apellidos', methods=['POST'])
# def get_usuarios_por_nombre_apellidos_c():
#     nombre = request.json['nombre']
#     apellidos = request.json['apellidos']
#     usuarios = get_usuarios_por_nombre_apellidos_aux(nombre, apellidos)
#     # return render_template
#     return None


def get_usuarios_por_descripcion_aux(descripcion):
    usuarios = mongo.db.usuario.find({'descripcion': {'$regex': descripcion, '$options': 'i'}})
    return usuarios


@app.route('/api/usuarios/descripcion/<descripcion>', methods=['GET'])
def get_usuarios_por_descripcion_s(descripcion):
    usuarios = get_usuarios_por_descripcion_aux(descripcion)
    aux = json_util.dumps(usuarios)
    response = Response(aux, mimetype='application/json')
    response.status_code = 200
    return response


# @app.route('/app/usuarios/por_descripcion', methods=['POST'])
# def get_usuarios_por_descripcion_c():
#     descripcion = request.json['descripcion']
#     usuarios = get_usuarios_por_descripcion_aux(descripcion)
#     # return render_template
#     return None


def insertar_coche_aux(id_usuario, marca, modelo, tipo, color, descripcion_c, fotografia_c):
    usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
    if marca and modelo and tipo and color and usuario != None:
        lista_coches = usuario['listaCoches']
        id_c = ObjectId()
        if fotografia_c == "":
            fotografia_c = 'https://res.cloudinary.com/dkwgmat62/image/upload/v1644286364/10484-un-coche-dibujo-para-colorear-e-imprimir_xm0sa7.jpg'

        coche = {'_id': id_c,
                 'marca': marca,
                 'modelo': modelo,
                 'tipo': tipo,
                 'color': color,
                 'descripcion': descripcion_c,
                 'fotografia': fotografia_c
                 }
        lista_coches.append(coche)

        actualizado = mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': ObjectId(id_usuario)},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaCoches': lista_coches
            }})
        aux = {'actualizado': int(actualizado.modified_count),
               'mensaje': 'El usuario con el ID = ' + id_usuario + ' tiene nuevo coche con el ID = ' + str(id_c)}
    else:
        aux = {'actualizado': 0, 'mensaje': 'No se ha podido insertar un coche.'}
    return aux


@app.route('/api/usuarios/<id_usuario>/coches', methods=['PUT'])
def insertar_coche_s(id_usuario):
    marca = request.json['marca']
    modelo = request.json['modelo']
    tipo = request.json['tipo']
    color = request.json['color']
    descripcion_c = request.json['descripcion']
    fotografia_c = request.json['fotografia']

    insertado = insertar_coche_aux(id_usuario, marca, modelo, tipo, color, descripcion_c, fotografia_c)

    if insertado['actualizado'] == 0:
        response = jsonify({'mensaje': insertado['mensaje']})
        response.status_code = 400
    else:
        response = jsonify({'mensaje': insertado['mensaje']})
        response.status_code = 201
    return response


@app.route('/app/usuarios/coches/insertar', methods=['POST'])
def insertar_coche_c():
    id_usuario = session['id']
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    tipo = request.form.get('tipo')
    color = request.form.get('color')
    descripcion_c = request.form.get('descripcion')
    if id_usuario and marca and modelo and tipo and color:
        fotografia_c = request.files['fotografia']
        if fotografia_c:
            response = cloudinary.uploader.upload(fotografia_c)
            fotografia_c = response["url"]
        else:
            fotografia_c = ""
        insertado = insertar_coche_aux(id_usuario, marca, modelo, tipo, color, descripcion_c, fotografia_c)
        return redirect('/app/usuarios/'+session['id']+'/coches')
    else:
        return render_template('crear_coche.html')


def editar_coche_aux(id_coche, marca, modelo, tipo, color, descripcion_c, fotografia_c):
    usuario = mongo.db.usuario.find_one({'listaCoches._id': ObjectId(id_coche)})
    if usuario != None and marca and modelo and tipo and color:
        lista_coches = usuario["listaCoches"]
        coche = {'_id': ObjectId(id_coche),
                 'marca': marca,
                 'modelo': modelo,
                 'tipo': tipo,
                 'color': color,
                 'descripcion': descripcion_c,
                 'fotografia': fotografia_c
                 }
        for idx, item in enumerate(lista_coches):
            if ObjectId(id_coche) == item["_id"]:
                lista_coches[idx] = coche

        mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': usuario["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaCoches': lista_coches
            }})
        response = {'editado': 2, 'mensaje': 'El usuario con el ID = ' + str(
            usuario["_id"]) + ' ha editado el coche con el ID = ' + id_coche}
    else:
        if usuario == None:
            response = {'editado': 0, 'mensaje': 'No se ha podido editar el coche porque no existe'}
        else:
            response = {'editado': 1,
                        'mensaje': 'No se ha podido editar un coche porque el campo marca, modelo, tipo o color estan vacios.'}
    return response


@app.route('/api/usuarios/coches/<id_coche>', methods=['PUT'])
def editar_coche_s(id_coche):
    marca = request.json['marca']
    modelo = request.json['modelo']
    tipo = request.json['tipo']
    color = request.json['color']
    descripcion_c = request.json['descripcion']
    fotografia_c = request.json['fotografia']

    editado = editar_coche_aux(id_coche, marca, modelo, tipo, color, descripcion_c, fotografia_c)

    response = jsonify({'mensaje': editado['mensaje']})
    if editado['editado'] == 2:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/app/usuarios/coches/editar', methods=['POST'])
def editar_coche_c():
    id_coche = request.form.get('id_coche')
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    tipo = request.form.get('tipo')
    color = request.form.get('color')
    descripcion_c = request.form.get('descripcion')
    if marca and modelo and tipo and color and id_coche:
        fotografia_c = request.files['fotografia']
        coche = get_coche_por_id_aux(session["id"],id_coche)
        if fotografia_c:
            response = cloudinary.uploader.upload(fotografia_c)
            fotografia_c = response["url"]
        else:
            fotografia_c = coche["fotografia"]
        editado = editar_coche_aux(id_coche, marca, modelo, tipo, color, descripcion_c, fotografia_c)
        return redirect('/app/usuarios/'+session['id']+'/coches')
    else:
        coche_act = usuario.get_full_coche_usuario(session["id"], id_coche)
        return render_template('editar_coche.html', coche=coche_act)

def eliminar_coche_aux(id_coche):
    usuario = mongo.db.usuario.find_one({'listaCoches._id': ObjectId(id_coche)})
    if usuario != None:
        lista_coches = usuario["listaCoches"]
        for idx, item in enumerate(lista_coches):
            if ObjectId(id_coche) == item["_id"]:
                lista_coches.remove(item)

        eliminado = mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': usuario["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaCoches': lista_coches
            }})

        response = {'eliminado': 1, 'mensaje': 'El usuario con el ID = ' + str(
            usuario["_id"]) + ' ha borrado el coche con el ID = ' + id_coche}
    else:
        response = {'eliminado': 0, 'mensaje': 'No se ha podido eliminar el coche porque no existe'}
    return response


@app.route('/api/usuarios/coches/<id_coche>', methods=['DELETE'])
def eliminar_coche_s(id_coche):
    eliminado = eliminar_coche_aux(id_coche)
    response = jsonify({'mensaje': eliminado['mensaje']})
    if eliminado['eliminado'] == 0:
        response.status_code = 400
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/coches/<id_coche>', methods=['DELETE'])
# def eliminar_coche_c(id_coche):
#     eliminado = eliminar_coche_aux(id_coche)
#     # return render_template
#     return None


@app.route('/app/usuarios/coches/eliminar', methods=['POST'])
def eliminar_coche_c():
    id_coche = request.form.get('id_coche')
    eliminado = eliminar_coche_aux(id_coche)
    return redirect('/app/usuarios/'+session['id']+'/coches')

def get_coches_aux():
    usuarios = mongo.db.usuario.find()
    listas_todos_coches = []
    for usuario in usuarios:
        lista_coches_usuario = usuario['listaCoches']
        if lista_coches_usuario:
            for coche in lista_coches_usuario:
                listas_todos_coches.append(coche)
    return listas_todos_coches


@app.route('/api/coches/', methods=['GET'])
def get_coches_s():
    listas_todos_coches = get_coches_aux()
    response = Response(json_util.dumps(listas_todos_coches), mimetype='application/json')
    if len(listas_todos_coches) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/coches/', methods=['GET'])
# def get_coches_c():
#     listas_todos_coches = get_coches_aux()
#     # return render_template
#     return None


def get_coche_por_id_aux(id_usuario, id_coche):
    coches = get_coches_usuario_aux(id_usuario)
    for coche in coches:
        if str(coche['_id']) == str(id_coche):
            return coche
    return None

def get_coches_usuario_aux(id_usuario):
    usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
    lista_coches = usuario['listaCoches']
    return lista_coches


@app.route('/api/usuarios/<id_usuario>/coches', methods=['GET'])
def get_coches_usuario_s(id_usuario):
    lista_coches = get_coches_usuario_aux(id_usuario)
    response = Response(json_util.dumps(lista_coches), mimetype='application/json')
    if len(json_util.dumps(lista_coches)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


@app.route('/app/usuarios/<id_usuario>/coches', methods=['GET'])
def get_coches_usuario_c(id_usuario):
    if id_usuario == session["id"]:
        user = usuario.get_full_usuario(id_usuario)
        return render_template('mis_coches.html', usuario=user)
    else:
        return render_template('acceso_denegado.html')


def get_usuarios_por_coche_marca_aux(marca):
    usuarios = mongo.db.usuario.find({'listaCoches.marca': {'$regex': marca, '$options': 'i'}})
    return usuarios


@app.route('/api/usuarios/coches/<marca>', methods=['GET'])
def get_usuarios_por_coche_marca_s(marca):
    usuarios = get_usuarios_por_coche_marca_aux(marca)
    response = Response(json_util.dumps(usuarios), mimetype='application/json')
    if len(json_util.dumps(usuarios)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/coches/por_marca', methods=['POST'])
# def get_usuarios_por_coche_marca_c():
#     marca = request.json['marca']
#     usuarios = get_usuarios_por_coche_marca_aux(marca)
#     # return render_template
#     return None


def get_usuarios_por_coche_modelo_aux(modelo):
    usuarios = mongo.db.usuario.find({'listaCoches.modelo': {'$regex': modelo, '$options': 'i'}})
    return usuarios


@app.route('/api/usuarios/coches/<modelo>', methods=['GET'])
def get_usuarios_por_coche_modelo_s(modelo):
    usuarios = get_usuarios_por_coche_modelo_aux(modelo)
    response = Response(json_util.dumps(usuarios), mimetype='application/json')
    if len(json_util.dumps(usuarios)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/coches/por_modelo', methods=['POST'])
# def get_usuarios_por_coche_modelo_c():
#     modelo = request.json['modelo']
#     usuarios = get_usuarios_por_coche_modelo_aux(modelo)
#     # return render_template
#     return None


def get_usuarios_por_coche_tipo_aux(tipo):
    usuarios = mongo.db.usuario.find({'listaCoches.tipo': {'$regex': tipo, '$options': 'i'}})
    return usuarios


@app.route('/api/usuarios/coches/<tipo>', methods=['GET'])
def get_usuarios_por_coche_tipo_s(tipo):
    usuarios = get_usuarios_por_coche_tipo_aux(tipo)
    response = Response(json_util.dumps(usuarios), mimetype='application/json')
    if len(json_util.dumps(usuarios)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/coches/por_tipo', methods=['POST'])
# def get_usuarios_por_coche_tipo_c():
#     tipo = request.json['tipo']
#     usuarios = get_usuarios_por_coche_tipo_aux(tipo)
#     # return render_template
#     return None


def get_usuarios_por_coche_marca_y_modelo_aux(marca, modelo):
    if marca and modelo:
        usuarios = mongo.db.usuario.find({'listaCoches.marca': {'$regex': marca, '$options': 'i'},
                                          'listaCoches.modelo': {'$regex': modelo, '$options': 'i'}})
    elif marca:
        usuarios = mongo.db.usuario.find({'listaCoches.marca': {'$regex': marca, '$options': 'i'}})
    else:
        usuarios = mongo.db.usuario.find({'listaCoches.modelo': {'$regex': modelo, '$options': 'i'}})
    return usuarios


@app.route('/api/usuarios/coches/<marca>/<modelo>', methods=['GET'])
def get_usuarios_por_coche_marca_y_modelo_s(marca, modelo):
    usuarios = get_usuarios_por_coche_marca_y_modelo_aux(marca, modelo)
    response = Response(json_util.dumps(usuarios), mimetype='application/json')
    if len(json_util.dumps(usuarios)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/coches/por_marca_y_modelo', methods=['POST'])
# def get_usuarios_por_coche_marca_y_modelo_c():
#     marca = request.json['marca']
#     modelo = request.json['modelo']
#     usuarios = get_usuarios_por_coche_marca_y_modelo_aux(marca, modelo)
#     # return render_template
#     return None


def get_chats_aux(id_user):
    chats1 = mongo.db.chat.find({'usuario1._id': ObjectId(id_user)})
    chats2 = mongo.db.chat.find({'usuario2._id': ObjectId(id_user)})
    lista_chats = []
    if chats1 and chats2:
        for chat in chats1:
            lista_chats.append(chat)
        for chat in chats2:
            lista_chats.append(chat)
    elif chats1:
        for chat in chats1:
            lista_chats.append(chat)
    elif chats2:
        for chat in chats2:
            lista_chats.append(chat)
    return lista_chats


def get_chat_aux(id_chat):
    chat = mongo.db.chat.find_one({'_id': ObjectId(id_chat)})
    return chat


def get_chats_mensajes_orden_recientes_no_recientes(id_user):
    chats1 = list(mongo.db.chat.find({'usuario1._id': ObjectId(id_user)}).sort('fechaUltimoMensaje', pymongo.DESCENDING))
    chats2 = list(mongo.db.chat.find({'usuario2._id': ObjectId(id_user)}).sort('fechaUltimoMensaje', pymongo.DESCENDING))
    size_1 = 0
    size_2 = 0
    if chats1:
        size_1 = len(chats1)
    if chats2:
        size_2 = len(chats2)

    # print(size_1)
    # print(size_2)
    res = []
    i, j = 0, 0
    while i < size_1 and j < size_2:
        if chats1[i]["fechaUltimoMensaje"] >= chats2[j]["fechaUltimoMensaje"]:
            res.append(chats1[i])
            i += 1
        else:
            res.append(chats2[j])
            j += 1
    res = res + chats1[i:] + chats2[j:]
    return res

@app.route('/api/usuarios/<id_usuario>/chats', methods=['GET'])
def get_chats_s(id_usuario):
    chats = get_chats_aux(id_usuario)
    response = Response(json_util.dumps(chats), mimetype='application/json')
    if len(chats) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


@app.route('/app/usuarios/<id_usuario>/chats', methods=['GET'])
def get_chats_c(id_usuario):
    chats = get_chats_mensajes_orden_recientes_no_recientes(id_usuario)
    return render_template('visualizar_chats.html', chats=chats)


@app.route('/api/usuarios/<id_usuario>/chats/<id_chat>', methods=['GET'])
def get_chat_s(id_usuario, id_chat):
    chat = get_chat_aux(id_chat)
    response = Response(json_util.dumps(chat), mimetype='application/json')
    if chat:
        response.status_code = 200
    else:
        response.status_code = 204
    return response

def get_chat_by_usuario1_usuario2(id_usuario1, id_usuario2):
    chats1 = mongo.db.chat.find_one({'usuario1._id': ObjectId(id_usuario1), 'usuario2._id': ObjectId(id_usuario2)})
    chats2 = mongo.db.chat.find_one({'usuario1._id': ObjectId(id_usuario2), 'usuario2._id': ObjectId(id_usuario1)})
    if chats1:
        return chats1
    elif chats2:
        return chats2
    else:
        return None

@app.route('/app/usuarios/<id_usuario>/chat', methods=['POST'])
def iniciar_chat_c(id_usuario):         # No tiene duplicado en el servidor debido a que es un método auxiliar
    id_usuario2 = request.form.get("id_usuario2")
    user2 = get_usuario_aux(id_usuario2)
    chat = get_chat_by_usuario1_usuario2(id_usuario, id_usuario2)
    if chat:
        return redirect(url_for('get_chat_c', id_usuario=id_usuario, id_chat=chat["_id"]))
    else:
        return render_template('visualizar_chat.html', user2=user2)


@app.route('/app/usuarios/<id_usuario>/chats/<id_chat>', methods=['GET'])
def get_chat_c(id_usuario, id_chat):
    chat = get_chat_aux(id_chat)
    user1= get_usuario_aux(chat["usuario1"]["_id"])
    user2= get_usuario_aux(chat["usuario2"]["_id"])
    return render_template('visualizar_chat.html', chat=chat, usuario1=user1, usuario2=user2)


def crear_chat_aux(id_us1, id_us2, mensaje):
    u1 = get_usuario_aux(id_us1)  #quien inicia la conversacion con un mensaje
    u2 = get_usuario_aux(id_us2)
    id_chat = -1
    chats1 = mongo.db.chat.find_one({'usuario1._id': ObjectId(id_us1), 'usuario2._id': ObjectId(id_us2)})
    chats2 = mongo.db.chat.find_one({'usuario1._id': ObjectId(id_us2), 'usuario2._id': ObjectId(id_us1)})

    if u1 and u2 and chats1 == None and chats2 == None:
        usuario1 = {'_id': ObjectId(u1['_id']), 'nombre': u1['nombre'], 'apellidos': u1['apellidos']}
        usuario2 = {'_id': ObjectId(u2['_id']), 'nombre': u2['nombre'], 'apellidos': u2['apellidos']}
        lista_mensajes = []
        id_m = ObjectId()
        fecha = datetime.now()
        mensaje_objeto = {'_id': id_m,
                          'emisor': ObjectId(id_us1),
                          'mensaje': mensaje,
                          'fecha': fecha
                          }
        lista_mensajes.append(mensaje_objeto)

        id_chat = mongo.db.chat.insert_one(
            {
                "usuario1": usuario1,
                "usuario2": usuario2,
                "listaMensaje": lista_mensajes,
                "fechaUltimoMensaje": fecha
            }
        ).inserted_id
    elif chats1 or chats2:
        id_chat = 0
    return id_chat


@app.route('/api/usuarios/<id_usuario>/chats', methods=['POST'])
def crear_chat_s(id_usuario):
    id_2 = request.json['id_usuario2']
    mensaje = request.json['mensaje']

    if id_usuario and id_2:
        id_chat = crear_chat_aux(id_usuario, id_2)
        if id_chat == 0:
            mensaje = 'Ya existe un chat entre estos usuarios'
            code = 406
        elif id_chat == -1:
            mensaje = 'No se ha podido crear el chat'
            code = 400    
        else:
            mensaje = 'Chat con ID = ' + str(id_chat) + ' creado con éxito'
            code = 201
    else:
        mensaje = 'No se ha podido crear el chat'
        code = 400
    response = jsonify({'mensaje': mensaje})
    response.status_code = code   
    return response


@app.route('/app/usuarios/<id_usuario>/chats', methods=['POST'])
def crear_chat_c(id_usuario):
    id_2 = request.form.get('id_usuario2')
    mensaje = request.form.get('mensaje')
    id_chat = crear_chat_aux(id_usuario, id_2, mensaje)
    # No controlo errores
    return redirect('/app/usuarios/' + str(id_usuario) + '/chats/' + str(id_chat))
  

def enviar_mensaje_aux(id_chat, id_emisor, mensaje):
    emisor = mongo.db.usuario.find_one({'_id': ObjectId(id_emisor)})
    chat = mongo.db.chat.find_one({'_id': ObjectId(id_chat)})
    if mensaje and emisor != None and chat != None:
        lista_mensajes = chat['listaMensaje']
        id_m = ObjectId()
        fecha = datetime.now()
        mensaje_objeto = {'_id': id_m,
                          'emisor': ObjectId(emisor['_id']),
                          'mensaje': mensaje,
                          'fecha': fecha
                          }
        lista_mensajes.append(mensaje_objeto)
        
        mongo.db.chat.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': ObjectId(id_chat)},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaMensaje': lista_mensajes,
                'fechaUltimoMensaje': fecha
            }})
        
        response = {'enviado': 2, 'mensaje': 'El usuario con el ID = ' + id_emisor + ' ha enviado un mensaje con ID = '
                                             + str(id_m) + ' al chat con ID = ' + str(id_chat)}
    else:
        if emisor == None:
            response = {'enviado': 1, 'mensaje': 'No se ha podido enviar el mensaje porque el ID del emisor no existe.'}
        elif chat == None:
            response = {'enviado': 1,
                        'mensaje': 'No se ha podido enviar el mensaje porque el ID del chat no existe.'}
        else:
            response = {'enviado': 0,
                        'mensaje': 'No se ha podido enviar el mensaje porque el campo mensaje esta vacio.'}
    return response


@app.route('/api/usuarios/<id_emisor>/chats/<id_chat>', methods=['PUT'])
def enviar_mensaje_s(id_emisor, id_chat):
    mensaje = request.json['mensaje']
    enviado = enviar_mensaje_aux(id_chat, id_emisor, mensaje)
    response = jsonify({'mensaje': enviado['mensaje']})
    if enviado['enviado'] == 2:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/app/usuarios/<id_emisor>/chats/<id_chat>', methods=['POST'])
def enviar_mensaje_c(id_emisor, id_chat):
    mensaje = request.form.get('mensaje')
    enviado = enviar_mensaje_aux(id_chat, id_emisor, mensaje)
    # No estoy contemplando errores
    return redirect('/app/usuarios/' + id_emisor + '/chats/' + id_chat)


# def editar_mensaje_aux(id_mensaje, mensaje):
#     emisor = mongo.db.usuario.find_one({'listaMensajesEnviados._id': ObjectId(id_mensaje)})
#     receptor = mongo.db.usuario.find_one({'listaMensajesRecibidos._id': ObjectId(id_mensaje)})
#     if mensaje and emisor != None and receptor != None:
#         mensajes_enviados = emisor['listaMensajesEnviados']
#         mensajes_recibidos = receptor['listaMensajesRecibidos']
#         indice = -1
#         fecha = datetime.now()
#         for idx, item in enumerate(mensajes_enviados):
#             if ObjectId(id_mensaje) == item["_id"]:
#                 indice = idx
#         mensaje_objeto1 = {'_id': ObjectId(id_mensaje),
#                           'receptor': {'_id': receptor['_id'], 'nombre': receptor['nombre'], 'apellidos': receptor['apellidos']},
#                           'mensaje': mensaje,
#                           'fechaEnvio': fecha
#                           }
#         mensajes_enviados[indice] = mensaje_objeto1
        
#         indice = -1
#         for idx, item in enumerate(mensajes_recibidos):
#             if ObjectId(id_mensaje) == item["_id"]:
#                 indice = idx
#         mensaje_objeto2 = {'_id': ObjectId(id_mensaje),
#                           'emisor': {'_id': emisor['_id'], 'nombre': emisor['nombre'], 'apellidos': emisor['apellidos']},
#                           'mensaje': mensaje,
#                           'fechaEnvio': fecha
#                           }
#         mensajes_recibidos[indice] = mensaje_objeto2

#         mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
#             {'_id': emisor["_id"]},  # que haya que cambiarlo para que actualice
#             {'$set': {
#                 'listaMensajesEnviados': mensajes_enviados
#             }})
        
#         mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
#             {'_id': receptor["_id"]},  # que haya que cambiarlo para que actualice
#             {'$set': {
#                 'listaMensajesRecibidos': mensajes_recibidos
#             }})

#         response = {'editado': 2,
#                     'mensaje': 'El usuario con el ID = ' + str(emisor["_id"]) + ' ha editado un mensaje con ID = '
#                                + str(id_mensaje) + ' al usuario con ID = ' + str(receptor['_id'])}
#     else:
#         if usuario == None:
#             response = {'editado': 1,
#                         'mensaje': 'No hay ningún usuario que contenga este mensaje en lista de enviados.'}
#         else:
#             response = {'editado': 0,
#                         'mensaje': 'No se ha podido editar el mensaje porque el campo mensaje esta vacio.'}
#     return response


# @app.route('/api/usuarios/mensajes/<id_mensaje>', methods=['PUT'])
# def editar_mensaje_s(id_mensaje):
#     mensaje = request.json['mensaje']
#     editado = editar_mensaje_aux(id_mensaje, mensaje)
#     response = jsonify({'mensaje': editado['mensaje']})
#     if editado['editado'] == 1:
#         response.status_code = 400
#     elif editado['editado'] == 0:
#         response.status_code = 304
#     else:
#         response.status_code = 200
#     return response


# @app.route('/app/usuarios/mensajes/<id_mensaje>', methods=['PUT'])
# def editar_mensaje_c(id_mensaje):
#     mensaje = request.json['mensaje']
#     editado = editar_mensaje_aux(id_mensaje, mensaje)
#     # return render_template
#     return None


# def eliminar_mensaje_aux(id_mensaje):
#     usuario_emisor = mongo.db.usuario.find_one({'listaMensajesEnviados._id': ObjectId(id_mensaje)})
#     usuario_receptor = mongo.db.usuario.find_one({'listaMensajesRecibidos._id': ObjectId(id_mensaje)})
#     if usuario_emisor != None and usuario_receptor != None:
#         mensajes_enviados = usuario_emisor['listaMensajesEnviados']
#         mensajes_recibidos = usuario_receptor['listaMensajesRecibidos']
#         for idx, item in enumerate(mensajes_enviados):
#             if ObjectId(id_mensaje) == item["_id"]:
#                 mensajes_enviados.remove(mensajes_enviados[idx])
#         for idx, item in enumerate(mensajes_recibidos):
#             if ObjectId(id_mensaje) == item["_id"]:
#                 mensajes_recibidos.remove(mensajes_recibidos[idx])
                

#         mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
#             {'_id': usuario_emisor["_id"]},  # que haya que cambiarlo para que actualice
#             {'$set': {
#                 'listaMensajesEnviados': mensajes_enviados
#             }})
#         mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
#             {'_id': usuario_receptor["_id"]},  # que haya que cambiarlo para que actualice
#             {'$set': {
#                 'listaMensajesRecibidos': mensajes_recibidos
#             }})

#         response = {'eliminado': 1, 'mensaje': ' Se ha eliminado un mensaje con ID = ' + str(id_mensaje)}
#     else:
#         response = {'eliminado': 0, 'mensaje': 'No se ha podido eliminar el mensaje porque no existe'}
#     return response


# @app.route('/api/usuarios/mensajes/<id_mensaje>', methods=['DELETE'])
# def eliminar_mensaje_s(id_mensaje):
#     eliminado = eliminar_mensaje_aux(id_mensaje)
#     response = jsonify({'mensaje': eliminado['mensaje']})
#     if eliminado['eliminado'] == 0:
#         response.status_code = 400
#     else:
#         response.status_code = 200
#     return response


# @app.route('/app/usuarios/mensajes/<id_mensaje>', methods=['DELETE'])
# def eliminar_mensaje_c(id_mensaje):
#     eliminado = eliminar_mensaje_aux(id_mensaje)
#     # return render_template
#     return None


# def get_mensajes_enviados_aux(id_usuario):
#     usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
#     lista_mensajes = usuario['listaMensajesEnviados']
#     if len(json_util.dumps(lista_mensajes)) > 1:
#         return lista_mensajes[::-1]
#     else:
#         return lista_mensajes


# @app.route('/api/usuarios/<id_usuario>/mensajes_enviados', methods=['GET'])
# def get_mensajes_enviados_s(id_usuario):
#     lista_mensajes = get_mensajes_enviados_aux(id_usuario)
#     response = Response(json_util.dumps(lista_mensajes), mimetype='application/json')
#     if len(json_util.dumps(lista_mensajes)) == 0:
#         response.status_code = 204
#     else:
#         response.status_code = 200
#     return response


# @app.route('/app/usuarios/<id_usuario>/mensajes_enviados', methods=['GET'])
# def get_mensajes_enviados_c(id_usuario):
#     lista_mensajes = get_mensajes_enviados_aux(id_usuario)
#     # return render_template
#     return None


# def get_mensaje_aux(id_mensaje):
#     chat = mongo.db.chat.find_one({'listaMensaje._id': ObjectId(id_mensaje)})
#     if chat:
#         for m in chat['listaMensaje']:
#             if m['_id'] == ObjectId(id_mensaje):
#                 return m
#     return None


# def get_mensajes_recibidos_de_aux(id_receptor, id_emisor):
#     usuario = mongo.db.usuario.find_one(
#         {'_id': ObjectId(id_emisor), 'listaMensajesEnviados.receptor': ObjectId(id_receptor)})
#     lista_mensajes = []
#     if usuario:
#         for mensaje in usuario['listaMensajesEnviados']:
#             if mensaje['receptor'] == ObjectId(id_receptor):
#                 lista_mensajes.append(mensaje)
#     return lista_mensajes


# @app.route('/api/usuarios/<id_receptor>/mensajes_de/<id_emisor>', methods=['GET'])
# def get_mensajes_recibidos_de_s(id_receptor, id_emisor):
#     lista_mensajes = get_mensajes_recibidos_de_aux(id_receptor, id_emisor)
#     response = Response(json_util.dumps(lista_mensajes), mimetype='application/json')
#     if len(lista_mensajes) == 0:
#         response.status_code = 204
#     else:
#         response.status_code = 200
#     return response


# @app.route('/app/usuarios/<id_receptor>/mensajes_de/<id_emisor>', methods=['GET'])
# def get_mensajes_recibidos_de_c(id_receptor, id_emisor):
#     lista_mensajes = get_mensajes_recibidos_de_aux(id_receptor, id_emisor)
#     # return render_template
#     return None


# def get_mensajes_recibidos_aux(id_usuario):
#     usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
#     lista_mensajes = usuario['listaMensajesRecibidos']
#     return lista_mensajes

# Hay que cambiar la bd, por lo que este método está mal
# @app.route('/app/usuarios/<id_usuario>/chats', methods=['GET'])
# def get_conversaciones(id_usuario):
    # chats = {}
    # mensajes_enviados = list(get_mensajes_enviados_aux(id_usuario))
    # mensajes_recibidos = list(get_mensajes_recibidos_aux(id_usuario))
    # cont = 0
    # while(cont < len(mensajes_enviados)):
    #     lista_aux = []
    #     chats.update({'chat'+cont+1: lista_aux})
    #     m1 = mensajes_enviados[0]
    #     lista_aux.append(m1)
    #     cont2 = 1
    #     while(cont2 < len(mensajes_enviados)):
    #         m2 = mensajes_enviados[1]
    #         if m2['receptor'] == m1['receptor']:
    #             lista_aux.append(m2)
    #             mensajes_enviados.remove(m2)
    #             cont2 -= 1
    #         cont2 += 1
    #     mensajes_enviados.remove(m1)
    #     cont += 1
    # for conv in chats.values:
    #     for m in mensajes_recibidos:
    #         if m['emisor._id'] == conv[0]['receptor._id']:
    #             conv.append(m)
    #             mensajes_recibidos.remove(m)
    # if len(mensajes_recibidos) > 0:
    #     cont = 0
    #     while(cont < len(mensajes_recibidos)):
    #         lista_aux = []
    #         chats.update({'chat'+len(chats.keys)+1: lista_aux})
    #         m1 = mensajes_recibidos[0]
    #         lista_aux.append(m1)
    #         cont2 = 1
    #         while(cont2 < len(mensajes_recibidos)):
    #             m2 = mensajes_recibidos[1]
    #             if m2['receptor'] == m1['receptor']:
    #                 lista_aux.append(m2)
    #                 mensajes_recibidos.remove(m2)
    #                 cont2 -= 1
    #             cont2 += 1
    #         mensajes_recibidos.remove(m1)
    #         cont += 1
    # return render_template('chats.html', conversaciones=chats)
    # return render_template('en_construccion.html')


def enviar_valoracion_aux(id_valorador, id_valorado, puntuacion, comentario, tipo,id_reserva):
    valorado = mongo.db.usuario.find_one({'_id': ObjectId(id_valorado)})
    valorador = mongo.db.usuario.find_one({'_id': ObjectId(id_valorador)})

    if puntuacion and comentario and valorado != None and valorador != None:
        valorado_valoraciones_recibidas = valorado['listaValoracionesRecibidas']
        id_v = ObjectId()
        valoracion = {'_id': id_v,
                      'valorador': ObjectId(id_valorador),
                      'fechaValoracion': datetime.now(),
                      'puntuacion': puntuacion,
                      'comentario': comentario,
                      'tipo': tipo,
                      'id_reserva': ObjectId(id_reserva)}
        valorado_valoraciones_recibidas.append(valoracion)
        mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': ObjectId(id_valorado)},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaValoracionesRecibidas': valorado_valoraciones_recibidas
            }})
        response = {'enviado': 2,
                    'mensaje': 'El usuario con el ID = ' + id_valorador + ' ha enviado una valoracion con ID = '
                               + str(id_v) + ' al usuario con ID = ' + id_valorado}
    else:
        if valorado == None:
            response = {'enviado': 1, 'mensaje': 'No se puede valorar un usuario que no existe.'}
        elif valorador == None:
            response = {'enviado': 1, 'mensaje': 'Un usuario que no existe no puede valorar a otro usuario.'}
        else:
            response = {'enviado': 0,
                        'mensaje': 'No se ha valorado al usuario porque el campo de puntuacion o comentario estan vacíos.'}
    return response


@app.route('/api/usuarios/<id_valorador>/enviar_valoracion/<id_valorado>/<id_reserva>', methods=['PUT'])
def enviar_valoracion_s(id_valorador, id_valorado, tipo, id_reserva):
    puntuacion = request.json['puntuacion']
    comentario = request.json['comentario']
    tipo = request.json['tipo']
    enviado = enviar_valoracion_aux(id_valorador, id_valorado, puntuacion, comentario, tipo, id_reserva)
    response = jsonify({'mensaje': enviado['mensaje']})
    if enviado['enviado'] == 2:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/app/usuarios/<id_valorador>/enviar_valoracion/<id_valorado>/<id_reserva>', methods=['POST'])
def enviar_valoracion_c(id_valorador, id_valorado, id_reserva):
    if id_valorador == session["id"] and id_valorador != id_valorado:
        puntuacion = request.form.get('puntuacion')
        comentario = request.form.get('comentario')
        tipo = request.form.get('tipo')
        res = get_valorado_reserva(id_valorado, id_reserva, tipo)
        if comentario and puntuacion and not res:
            enviado = enviar_valoracion_aux(id_valorador, id_valorado, puntuacion, comentario, tipo, id_reserva)
            if tipo == 'conductor':
                return redirect('/app/usuarios/'+id_valorador+'/reservas')
            else:
                return redirect('/app/usuarios/'+id_valorador+'/trayectos')
        else:
            t,n = get_trayecto_by_reserva_and_usuario(id_reserva, None)
            r = None
            for reserva in t["reservas"]:
                if str(reserva["id"]) == str(id_reserva):
                    r = reserva
            return render_template('enviar_valoracion.html', id_valorador=id_valorador, id_valorado=id_valorado, id_reserva=id_reserva, trayecto = t, tipo = tipo, reserva = r)
    else:
        return render_template('acceso_denegado.html')


def editar_valoracion_aux(id_valoracion, puntuacion, comentario):
    usuario = mongo.db.usuario.find_one({'listaValoracionesRecibidas._id': ObjectId(id_valoracion)})
    if puntuacion and comentario and usuario != None:
        valoraciones_recibidas = usuario['listaValoracionesRecibidas']
        indice = 0
        for idx, item in enumerate(valoraciones_recibidas):
            if ObjectId(id_valoracion) == item["_id"]:
                indice = idx
        valoracion_editada = {'_id': ObjectId(id_valoracion),
                              'valorador': valoraciones_recibidas[indice]["valorador"],
                              'fechaValoracion': datetime.now(),
                              'puntuacion': puntuacion,
                              'comentario': comentario,
                              'id_reserva':ObjectId(valoraciones_recibidas[indice]["id_reserva"])}
        valoraciones_recibidas[indice] = valoracion_editada
        mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': usuario["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaValoracionesRecibidas': valoraciones_recibidas
            }})
        response = {'editado': 2, 'mensaje': ' Ha sido editada la valoracion con ID = ' + str(
            valoracion_editada["_id"]) + ' al usuario con ID = ' + str(usuario["_id"])}
    else:
        if usuario == None:
            response = {'editado': 1, 'mensaje': 'No hay ningún usuario que contenga esta valoracion.'}
        else:
            response = {'editado': 0,
                        'mensaje': 'No se ha editado la valoracion porque el campo de puntuación o comentario estan vacíos.'}
    return response


@app.route('/api/usuarios/valoraciones/<id_valoracion>', methods=['PUT'])
def editar_valoracion_s(id_valoracion):
    puntuacion = request.json['puntuacion']
    comentario = request.json['comentario']
    editado = editar_valoracion_aux(id_valoracion, puntuacion, comentario)
    response = jsonify({'mensaje': editado['mensaje']})
    if editado['editado'] == 2:
        response.status_code = 200
    elif editado['editado'] == 0:
        response.status_code = 304
    else:
        response.status_code = 400
    return response


# @app.route('/app/usuarios/valoraciones/<id_valoracion>', methods=['PUT'])
# def editar_valoracion_c(id_valoracion):
#     puntuacion = request.json['puntuacion']
#     comentario = request.json['comentario']
#     editado = editar_valoracion_aux(id_valoracion, puntuacion, comentario)
#     # return render_template
#     return None


def eliminar_valoracion_aux(id_valoracion):
    usuario = mongo.db.usuario.find_one({'listaValoracionesRecibidas._id': ObjectId(id_valoracion)})
    if usuario != None:
        valoraciones_recibidas = usuario['listaValoracionesRecibidas']

        for idx, item in enumerate(valoraciones_recibidas):
            if ObjectId(id_valoracion) == item["_id"]:
                valoraciones_recibidas.remove(valoraciones_recibidas[idx])
        mongo.db.usuario.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': usuario["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaValoracionesRecibidas': valoraciones_recibidas
            }})
        response = {'eliminado': 1,
                    'mensaje': ' Ha sido eliminada la valoracion con ID = ' + id_valoracion + ' al usuario con ID = ' + str(
                        usuario["_id"])}
    else:
        response = {'eliminado': 0, 'mensaje': 'No se ha podido eliminar la valoracion porque no existe.'}
    return response


@app.route('/api/usuarios/valoraciones/<id_valoracion>', methods=['DELETE'])
def eliminar_valoracion_s(id_valoracion):
    eliminado = eliminar_valoracion_aux(id_valoracion)
    response = jsonify({'mensaje': eliminado['mensaje']})
    if eliminado['eliminado'] == 1:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


# @app.route('/app/usuarios/valoraciones/<id_valoracion>', methods=['DELETE'])
# def eliminar_valoracion_c(id_valoracion):
#     eliminado = eliminar_valoracion_aux(id_valoracion)
#     # return render_template
#     return None


def get_valoraciones_recibidas_usuario_aux(id_usuario):
    usuario = mongo.db.usuario.find_one({'_id': ObjectId(id_usuario)})
    valoraciones = usuario['listaValoracionesRecibidas']
    return valoraciones


def get_valoraciones_media_aux(id_usuario):
    valoraciones = get_valoraciones_recibidas_usuario_aux(id_usuario)
    n_valoraciones = len(valoraciones)
    suma = 0.0
    for valoracion in valoraciones:
        suma += float(valoracion["puntuacion"])
    if suma != 0:
        return round(suma/n_valoraciones, 3), n_valoraciones
    else:
        return 0, n_valoraciones


@app.route('/api/usuarios/<id_usuario>/valoraciones_recibidas', methods=['GET'])
def get_valoraciones_recibidas_usuario_s(id_usuario):
    valoraciones = get_valoraciones_recibidas_usuario_aux(id_usuario)
    response = Response(json_util.dumps(valoraciones), mimetype='application/json')
    if len(valoraciones) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/<id_usuario>/valoraciones_recibidas', methods=['GET'])
# def get_valoraciones_recibidas_usuario_c(id_usuario):
#     valoraciones = get_valoraciones_recibidas_usuario_aux(id_usuario)
#     # return render_template
#     return None


def get_valoraciones_enviadas_usuario_aux(id_usuario):
    usuarios_valorados_por_mi = mongo.db.usuario.find({'listaValoracionesRecibidas.valorador': ObjectId(id_usuario)})
    valoraciones_enviadas_por_mi = []
    for usuario in usuarios_valorados_por_mi:
        valoraciones_recibidas_usuario = usuario['listaValoracionesRecibidas']
        for valoracion in valoraciones_recibidas_usuario:
            if valoracion['valorador'] == ObjectId(id_usuario):
                valoraciones_enviadas_por_mi.append(valoracion)
    return valoraciones_enviadas_por_mi


@app.route('/api/usuarios/<id_usuario>/valoraciones_enviadas', methods=['GET'])
def get_valoraciones_enviadas_usuario_s(id_usuario):
    valoraciones_enviadas_por_mi = get_valoraciones_enviadas_usuario_aux(id_usuario)
    response = Response(json_util.dumps(valoraciones_enviadas_por_mi), mimetype='application/json')
    if len(valoraciones_enviadas_por_mi) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/<id_usuario>/valoraciones_enviadas', methods=['GET'])
# def get_valoraciones_enviadas_usuario_c(id_usuario):
#     valoraciones_enviadas_por_mi = get_valoraciones_enviadas_usuario_aux(id_usuario)
#     # return render_template
#     return None


def crear_trayecto_aux(id_coche, id_piloto, des, duracion, periodicidad, precio, ciudad_destino, ciudad_origen,
                                direccion_destino, direccion_origen, fecha_hora, plazas_ofertadas, latitud_origen, longitud_origen, latitud_destino, longitud_destino):
    conductor = mongo.db.usuario.find_one({'listaCoches._id': ObjectId(id_coche)})
    lista_reservas = []
    if id_coche and id_piloto and precio and ciudad_destino and ciudad_origen and direccion_destino and direccion_origen and fecha_hora and plazas_ofertadas and conductor != None and conductor["_id"] == id_piloto and latitud_origen and longitud_origen and latitud_destino and longitud_destino:
        if not duracion:
            duracion = ' - '
        if not periodicidad:
            periodicidad = ' - '
        id_trayecto = mongo.db.trayecto.insert_one(
            {
                "coche": ObjectId(id_coche),
                "conductor": ObjectId(id_piloto),
                "descripcion": des,
                "duracion": duracion,
                "periodicidad": periodicidad,
                "precio": precio,
                "listaReservas": lista_reservas,
                "ciudadDestino": ciudad_destino,
                "ciudadOrigen": ciudad_origen,
                "direccionDestino": direccion_destino,
                "direccionOrigen": direccion_origen,
                "latitudOrigen": latitud_origen,
                "longitudOrigen": longitud_origen,
                "latitudDestino": latitud_destino,
                "longitudDestino": longitud_destino,
                "fechaHora": fecha_hora,
                "plazasOfertadas": plazas_ofertadas
            }
        ).inserted_id
        response = {'creado': 3, 'mensaje': 'Trayecto creado con éxito con ID = ' + str(id_trayecto)}
    else:
        if conductor == None:
            response = {'creado': 2, 'mensaje': 'No se ha añadir un trayecto porque no existe ese conductor.'}
        elif conductor["_id"] != id_piloto:
            response = {'creado': 1,
                        'mensaje': 'No se ha podido añadir un trayecto porque no coincide que ese conductor tenga ese coche'}
        else:
            response = {'creado': 0,
                        'mensaje': 'No se ha podido crear un trayecto porque el campo coche, piloto, precio, ciudad destino, ciudad origen, direccion destino, direccion origen, fechaHora o plazas ofertadas  estan vacios'}
    return response


@app.route('/api/trayectos/', methods=['POST'])
def crear_trayecto_s():
    id_coche = ObjectId(request.json['coche'])
    id_piloto = ObjectId(request.json['conductor'])
    des = request.json['descripcion']
    duracion = request.json['duracion']
    periodicidad = request.json['periodicidad']
    precio = request.json['precio']
    ciudad_destino = request.json['ciudadDestino']
    ciudad_origen = request.json['ciudadOrigen']
    direccion_destino = request.json['direccionDestino']
    direccion_origen = request.json['direccionOrigen']
    latitud_origen = request.json['latitudOrigen']
    longitud_origen = request.json['longitudOrigen']
    latitud_destino = request.json['latitudDestino']
    longitud_destino = request.json['longitudDestino']
    fecha_hora = request.json['fechaHora']
    plazas_ofertadas = request.json['plazasOfertadas']

    creado = crear_trayecto_aux(id_coche, id_piloto, des, duracion, periodicidad, precio, ciudad_destino, ciudad_origen,
                                direccion_destino, direccion_origen, fecha_hora, plazas_ofertadas, latitud_origen, longitud_origen, latitud_destino, longitud_destino)

    response = jsonify({'mensaje': creado['mensaje']})
    if creado['creado'] == 3:
        response.status_code = 201
    else:
        response.status_code = 400
    return response


@app.route('/app/trayectos/', methods=['POST'])
def crear_trayecto_c():
    id_piloto = ObjectId(session['id'])
    des = request.form.get('descripcion')
    id_coche = ObjectId(request.form.get('coche'))
    duracion = request.form.get('duracion')
    periodicidad = request.form.get('periodicidad')
    precio = request.form.get('precio')
    ciudad_destino = request.form.get('localidadDestino')
    ciudad_origen = request.form.get('localidadOrigen')
    direccion_destino = request.form.get('destino')
    direccion_origen = request.form.get('origen')
    latitud_origen = request.form.get('latitudOrigen')
    longitud_origen = request.form.get('longitudOrigen')
    latitud_destino = request.form.get('latitudDestino')
    longitud_destino = request.form.get('longitudDestino')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    plazas_ofertadas = request.form.get('plazasOfertadas')
    if fecha and hora:
        fecha_hora = datetime.combine(datetime.strptime(fecha, '%Y-%m-%d'), datetime.strptime(hora, '%H:%M').time())
    if id_piloto and id_coche and des and precio and ciudad_destino and ciudad_origen and direccion_destino and ciudad_origen and fecha and hora and latitud_origen and longitud_origen and latitud_destino and longitud_destino:
        creado = crear_trayecto_aux(id_coche, id_piloto, des, duracion, periodicidad, precio, ciudad_destino, ciudad_origen,
                                direccion_destino, direccion_origen, fecha_hora, plazas_ofertadas, latitud_origen, longitud_origen, latitud_destino, longitud_destino)
        return redirect('/app/usuarios/' + session['id'] + '/trayectos')
    else:
        doc_coches = get_coches_usuario_aux(session["id"])
        if not doc_coches:
            return redirect('/app/usuarios/coches/insertar', code=307)
        else:
            return render_template('crear_trayecto.html', coches=doc_coches)



def actualizar_trayecto_aux(id_trayecto, id_coche, des, duracion, periodicidad, precio, lista_reservas, ciudad_destino,
                            ciudad_origen, direccion_destino, direccion_origen, fecha_hora, plazas_ofertadas,  latitud_origen, longitud_origen, latitud_destino, longitud_destino):
    trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
    conductor = mongo.db.usuario.find_one({'listaCoches._id': ObjectId(id_coche)})
    if lista_reservas == None:
        lista_reservas = []
    if id_coche and precio and ciudad_destino and ciudad_origen and direccion_destino and direccion_origen and fecha_hora and plazas_ofertadas and trayecto != None and conductor != None and trayecto["conductor"] == conductor["_id"] and latitud_origen and longitud_origen and latitud_destino and longitud_destino:
        mongo.db.trayecto.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': ObjectId(id_trayecto)},  # que haya que cambiarlo para que actualice
            {'$set': {  # sólo uno o lo que nos haga falta, ya lo veremos
                "coche": ObjectId(id_coche),
                "descripcion": des,
                "duracion": duracion,
                "periodicidad": periodicidad,
                "precio": float(precio),
                "listaReservas": lista_reservas,
                "ciudadDestino": ciudad_destino,
                "ciudadOrigen": ciudad_origen,
                "direccionDestino": direccion_destino,
                "direccionOrigen": direccion_origen,
                "latitudOrigen": latitud_origen,
                "longitudOrigen": longitud_origen,
                "latitudDestino": latitud_destino,
                "longitudDestino": longitud_destino,
                "fechaHora": fecha_hora,
                "plazasOfertadas": plazas_ofertadas
            }}
        )

        response = {'actualizado': 4,
                    'mensaje': 'El trayecto con el ID = ' + id_trayecto + ' fue actualizado correctamente'}
    else:
        if trayecto == None:
            response = {'actualizado': 3, 'mensaje': 'No se ha actualizado el trayecto porque no existe ese trayecto.'}
        elif conductor == None:
            response = {'actualizado': 2,
                        'mensaje': 'No se ha actualizado el trayecto porque no existe ese conductor con ese coche.'}
        elif trayecto["conductor"] != conductor["_id"]:
            response = {'actualizado': 1,
                        'mensaje': 'No se ha actualizado este trayecto porque no coincide que el organizador tenga ese coche.'}
        else:
            response = {'actualizado': 0,
                        'mensaje': 'No se ha podido crear un trayecto porque el campo coche, piloto, precio, ciudad destino, ciudad origen, direccion destino, direccion origen, fechaHora o plazas ofertadas  estan vacios'}
    return response


@app.route('/api/trayectos/<id_trayecto>', methods=['PUT'])
def actualizar_trayecto_s(id_trayecto):
    id_coche = request.json['coche']
    des = request.json['descripcion']
    duracion = request.json['duracion']
    periodicidad = request.json['periodicidad']
    precio = request.json['precio']
    lista_reservas = request.json['listaReservas']
    ciudad_destino = request.json['ciudadDestino']
    ciudad_origen = request.json['ciudadOrigen']
    direccion_destino = request.json['direccionDestino']
    direccion_origen = request.json['direccionOrigen']
    latitud_origen = request.json['latitudOrigen']
    longitud_origen = request.json['longitudOrigen']
    latitud_destino = request.json['latitudDestino']
    longitud_destino = request.json['longitudDestino']
    fecha_hora = request.json['fechaHora']
    plazas_ofertadas = request.json['plazasOfertadas']

    actualizado = actualizar_trayecto_aux(id_trayecto, id_coche, des, duracion, periodicidad, precio, lista_reservas,
                                          ciudad_destino, ciudad_origen, direccion_destino, direccion_origen,
                                          fecha_hora, plazas_ofertadas, latitud_origen, longitud_origen, latitud_destino, longitud_destino)

    response = jsonify({'mensaje': actualizado['mensaje']})
    if actualizado['actualizado'] == 4:
        response.status_code = 200
    elif actualizado['actualizado'] == 0:
        response.status_code = 304
    else:
        response.status_code = 400
    return response

def get_reservas_trayecto_aux(id_trayecto):
    trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
    return trayecto['listaReservas']


@app.route('/app/trayectos/actualizar', methods=['POST'])
def actualizar_trayecto_c():
    id_trayecto = request.form.get("id_trayecto")
    id_coche = request.form.get('coche')
    des = request.form.get('descripcion')
    duracion = request.form.get('duracion')
    periodicidad = request.form.get('periodicidad')
    precio = request.form.get('precio')
    ciudad_destino = request.form.get('localidadDestino')
    ciudad_origen = request.form.get('localidadOrigen')
    direccion_destino = request.form.get('destino')
    direccion_origen = request.form.get('origen')
    latitud_origen = request.form.get('latitudOrigen')
    longitud_origen = request.form.get('longitudOrigen')
    latitud_destino = request.form.get('latitudDestino')
    longitud_destino = request.form.get('longitudDestino')
    plazas_ofertadas = request.form.get('plazasOfertadas')
    fecha = request.form.get('fecha')
    hora = request.form.get('hora')
    trayecto_act = trayecto.get_lite_trayecto(id_trayecto)

    if fecha and hora:
        fecha_hora = datetime.combine(datetime.strptime(fecha, '%Y-%m-%d'), datetime.strptime(hora, '%H:%M').time())

    if id_coche and des and precio and ciudad_destino and ciudad_origen and direccion_destino and direccion_origen and plazas_ofertadas and fecha and hora:
        lista_reservas = get_reservas_trayecto_aux(id_trayecto)
        actualizado = actualizar_trayecto_aux(id_trayecto, id_coche, des, duracion, periodicidad, precio, lista_reservas,
                                          ciudad_destino, ciudad_origen, direccion_destino, direccion_origen,
                                          fecha_hora, plazas_ofertadas, latitud_origen, longitud_origen, latitud_destino, longitud_destino)
        return redirect('/app/usuarios/'+str(trayecto_act["conductor"]["id"])+'/trayectos')
    else:
        trayecto_act = trayecto.get_full_trayecto(id_trayecto)
        list_coches = get_coches_usuario_aux(trayecto_act["conductor"]["id"])
        return render_template('editar_trayecto.html', trayecto=trayecto_act, coches=list_coches)


def eliminar_trayecto_aux(id_trayecto):
    eliminado = mongo.db.trayecto.delete_one({'_id': ObjectId(id_trayecto)})
    if eliminado.deleted_count == 1:
        response = {'eliminado': 1, 'mensaje': 'Se ha eliminado el trayecto con ID = ' + id_trayecto + ' correctamente'}
    else:
        response = {'eliminado': 0,
                    'mensaje': 'No se ha podido eliminar el trayecto porque no existe ningún trayecto con ese ID.'}
    return response


@app.route('/api/trayectos/<id_trayecto>', methods=['DELETE'])
def eliminar_trayecto_s(id_trayecto):
    eliminado = eliminar_trayecto_aux(id_trayecto)
    response = jsonify({'mensaje': eliminado['mensaje']})
    if eliminado['eliminado'] == 1:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/app/trayectos/eliminar', methods=['POST'])
def eliminar_trayecto_c():
    id_trayecto = request.form.get('id_trayecto')
    eliminado = eliminar_trayecto_aux(id_trayecto)
    return redirect('/app/usuarios/' + session['id'] + '/trayectos')


def get_trayectos_aux():
    trayectos = mongo.db.trayecto.find()
    return trayectos

def get_trayectos_fecha_cercana_a_lejana_aux():
    trayectos = mongo.db.trayecto.find({'fechaHora': {'$gt':datetime.now()}}).sort('fechaHora', pymongo.ASCENDING)
    return trayectos

@app.route('/api/trayectos/', methods=['GET'])
def get_trayectos_s():
    trayectos = get_trayectos_aux()
    response = Response(json_util.dumps(trayectos), mimetype='application/json')
    if len(json_util.dumps(trayectos)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/trayectos/', methods=['GET'])
# def get_trayectos_c():
#     trayectos = get_trayectos_aux()
#     # return render_template
#     return None


def get_trayecto_aux(id_trayecto):
    trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
    return trayecto


@app.route('/api/trayectos/<id_trayecto>', methods=['GET'])
def get_trayecto_s(id_trayecto):
    trayecto = get_trayecto_aux(id_trayecto)
    response = Response(json_util.dumps(trayecto), mimetype='application/json')
    if len(json_util.dumps(trayecto)) == 0:
        response.status_code = 400
    else:
        response.status_code = 200
    return response


@app.route('/app/trayectos/<id_trayecto>', methods=['GET'])
def get_trayecto_c(id_trayecto):
    if session.get("id"):
        if session.get("id_trayecto"):
            session.pop('id_trayecto')
        trayecto_aux = trayecto.get_full_trayecto(id_trayecto)
        valoracion_media, n_valoraciones = get_valoraciones_media_aux(trayecto_aux["conductor"]["id"])
        print(session.get("id_trayecto"))
        return render_template('visualizar_trayecto.html', trayecto=trayecto_aux, valoracion_media=valoracion_media, n_valoraciones=n_valoraciones, fecha_actual=datetime.now())
    else:
        session["id_trayecto"] = id_trayecto
        return redirect(url_for('index2'))

# def get_coche_trayecto_aux(id_trayecto):
#     trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
#     conductor = get_usuario_aux(trayecto["conductor"])
#     id_coche = trayecto["coche"]
#     lista_coches = conductor["listaCoches"]
#     for coche in lista_coches:
#         if (ObjectId(id_coche) == coche["_id"]):
#             return coche
#     return None


def get_plazas_disponibles_aux(id_trayecto):
    trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
    if trayecto:
        plazas_disponibles = trayecto["plazasOfertadas"]
        for reserva in trayecto["listaReservas"]:
            plazas_disponibles = int(plazas_disponibles) - int(reserva["plazasReservadas"])
        return int(plazas_disponibles)
    else:
        return None


@app.route('/api/trayectos/<id_trayecto>/plazas_disponibles', methods=['GET'])
def get_plazas_disponibles_s(id_trayecto):
    plazas_libres = get_plazas_disponibles_aux(id_trayecto)
    if plazas_libres is None:
        response = jsonify({'mensaje': 'Error: Trayecto con ID = ' + id_trayecto + ' no existe'})
        response.status_code = 400
    else:
        response = jsonify(
            {'mensaje': 'Hay ' + str(plazas_libres) + 'plazas libes en el trayecto con ID = ' + id_trayecto})
        response.status_code = 200
    return response


# @app.route('/app/trayectos/<id_trayecto>/plazas_disponibles', methods=['GET'])
# def get_plazas_disponibles_c(id_trayecto):
#     plazas_libres = get_plazas_disponibles_aux(id_trayecto)
#     # return render_template
#     return None

def get_trayectos_creados_por_usuario_id_aux(id_usuario):
    lista_trayectos = mongo.db.trayecto.find({'conductor': ObjectId(id_usuario)}).sort('fechaHora', pymongo.ASCENDING)
    return lista_trayectos


@app.route('/api/usuarios/<id_usuario>/trayectos', methods=['GET'])
def get_trayectos_creados_por_usuario_id_s(id_usuario):
    lista_trayectos = get_trayectos_creados_por_usuario_id_aux(id_usuario)
    response = Response(json_util.dumps(lista_trayectos), mimetype='application/json')
    if len(json_util.dumps(lista_trayectos)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


#@app.route('/app/mis_trayectos', methods=['GET'])
#def get_mis_trayectos_c():
#    doc_trayectos = get_trayectos_creados_por_usuario_id_aux(session["id"])
#    list_trayectos = []
#    for doc in doc_trayectos:
#        list_trayectos.append(trayecto.Trayecto(doc['_id']))
#    return render_template("mis_trayectos.html", trayectos=list_trayectos, fecha_actual=datetime.now())


@app.route('/app/usuarios/<id_usuario>/trayectos', methods=['GET'])
def get_trayectos_creados_por_usuario_id_c(id_usuario):
    lista_trayectos = get_trayectos_creados_por_usuario_id_aux(id_usuario)
    trayectos_futuro = []
    trayectos_pasado = []
    fecha = datetime.now()
    id_session = session["id"]
    if str(id_usuario) == str(id_session):
        for t in lista_trayectos:
            if str(fecha) >= str(t['fechaHora']):
                trayectos_pasado.append(trayecto.get_full_trayecto(t["_id"]))
            else: 
                trayectos_futuro.append(trayecto.get_full_trayecto(t["_id"]))
        return render_template("mis_trayectos.html", trayectos_disp=trayectos_futuro, trayectos_pas=trayectos_pasado, fecha_actual=fecha, tipo = 'pasajero')
    else:
        return render_template("acceso_denegado.html")


def get_trayectos_creados_por_usuario_nombre_apellidos_aux(nombre, apellidos):
    usuarios = get_usuarios_por_nombre_apellidos_aux(nombre, apellidos)
    lista_id_usuarios = []
    for usuario in usuarios:
        lista_id_usuarios.append(usuario['_id'])

    trayectos_creados_por_usuarios = []
    for id_usuario in lista_id_usuarios:
        trayectos_creados_por_un_usuario = mongo.db.trayecto.find({'conductor': ObjectId(id_usuario)})
        for trayecto in trayectos_creados_por_un_usuario:
            trayectos_creados_por_usuarios.append(trayecto)
    return trayectos_creados_por_usuarios


@app.route('/api/trayectos/<nombre>/<apellidos>', methods=['GET'])
def get_trayectos_creados_por_usuario_nombre_apellidos_s(nombre, apellidos):
    trayectos_creados_por_usuarios = get_trayectos_creados_por_usuario_nombre_apellidos_aux(nombre, apellidos)
    response = Response(json_util.dumps(trayectos_creados_por_usuarios), mimetype='application/json')
    if len(trayectos_creados_por_usuarios) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/trayectos/organizados_por', methods=['POST'])
# def get_trayectos_creados_por_usuario_nombre_apellidos_c():
#     nombre = request.json['nombre']
#     apellidos = request.json['apellidos']
#     trayectos_creados_por_usuarios = get_trayectos_creados_por_usuario_nombre_apellidos_aux(nombre, apellidos)
#     # return render_template
#     return None


def get_trayectos_contar_aux():
    cuenta = mongo.db.trayecto.count_documents({})
    return cuenta


@app.route('/api/trayectos/contar', methods=['GET'])
def get_trayectos_contar_s():
    cuenta = get_trayectos_contar_aux()
    response = Response(json_util.dumps(cuenta), mimetype='application/json')
    response.status_code = 200
    return response


# @app.route('/app/trayectos/contar', methods=['GET'])
# def get_trayectos_contar_c():
#     cuenta = get_trayectos_contar_aux()
#     # return render_template
#     return None


def get_trayectos_en_rango_por_precio_aux(lim_inferior, lim_superior):
    trayectos = mongo.db.trayecto.find({'precio': {'$gt': float(lim_inferior), '$lt': float(lim_superior)}})
    return trayectos


@app.route('/api/trayectos/<lim_inferior>/<lim_superior>', methods=['GET'])
def get_trayectos_en_rango_por_precio_s(lim_inferior, lim_superior):
    trayectos = get_trayectos_en_rango_por_precio_aux(lim_inferior, lim_superior)
    response = Response(json_util.dumps(trayectos), mimetype='application/json')
    if len(json_util.dumps(trayectos)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/trayectos/por_rango_precio', methods=['POST'])
# def get_trayectos_en_rango_por_precio_c():
#     lim_inferior = request.json['lim_inferior']
#     lim_superior = request.json['lim_superior']
#     trayectos = get_trayectos_en_rango_por_precio_aux(lim_inferior, lim_superior)
#     # return render_template
#     return None


def get_trayecto_from_to_aux(origen, destino):
    trayectos = mongo.db.trayecto.find({'ciudadOrigen': origen, 'ciudadDestino': destino})
    return trayectos


@app.route('/api/trayectos/<origen>/<destino>', methods=['GET'])
def get_trayecto_from_to_s(origen, destino):
    trayectos = get_trayecto_from_to_aux(origen, destino)
    response = Response(json_util.dumps(trayectos), mimetype='application/json')
    if len(json_util.dumps(trayectos)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/trayectos/por_origen_destino', methods=['POST'])
# def get_trayecto_from_to_c():
#     origen = request.json['ciudad_origen']
#     destino = request.json['ciudad_destino']
#     trayectos = get_trayecto_from_to_aux(origen, destino)
#     # return render_template
#     return None


def get_pasajeros_por_conductor_aux(nombre, apellidos):
    pasajeros_id = []
    id_conductor = None
    if nombre and apellidos:
        usuario = mongo.db.usuario.find_one(
            {'nombre': {'$regex': nombre, '$options': 'i'}, 'apellidos': {'$regex': apellidos, '$options': 'i'}})
        if usuario:
            id_conductor = usuario['_id']
    elif nombre:
        usuario = mongo.db.usuario.find_one({'nombre': {'$regex': nombre, '$options': 'i'}})
        if usuario:
            id_conductor = usuario['_id']
    else:
        usuario = mongo.db.usuario.find_one({'apellidos': {'$regex': apellidos, '$options': 'i'}})
        if usuario:
            id_conductor = usuario['_id']

    if id_conductor:
        lista_trayectos = mongo.db.trayecto.find({'conductor': ObjectId(id_conductor)})
        for trayecto in lista_trayectos:
            for reserva in trayecto['listaReservas']:
                pasajeros_id.append(reserva['solicitante'])

        resultado = []
        for id_pasajero in pasajeros_id:
            pasajero = mongo.db.usuario.find_one({'_id': ObjectId(id_pasajero)})
            if pasajero:
                resultado.append(json_util.dumps(pasajero))

        return resultado
    else:
        return None


@app.route('/api/trayectos/pasajeros/<nombre>/<apellidos>', methods=['GET'])
def get_pasajeros_por_conductor_s(nombre, apellidos):
    lista_pasajeros = get_pasajeros_por_conductor_aux(nombre, apellidos)

    if lista_pasajeros is None:
        response = jsonify({'mensaje': 'Error: Este usuario no ha tenido nunca pasajeros'})
        response.status_code = 400
    else:
        response = Response(json_util.dumps(lista_pasajeros), mimetype='application/json')
        if len(json_util.dumps(lista_pasajeros)) == 0:
            response.status_code = 204
        else:
            response.status_code = 200
    return response


# @app.route('/app/trayectos/pasajeros_por_conductor', methods=['POST'])
# def get_pasajeros_por_conductor_c():
#     nombre = request.json['nombre']
#     apellidos = request.json['apellidos']
#     lista_pasajeros = get_pasajeros_por_conductor_aux(nombre, apellidos)
#     # return render_template
#     return None


def get_pasajeros_por_id_conductor_aux(id_usuario):
    lista_trayectos = mongo.db.trayecto.find({'conductor': ObjectId(id_usuario)})
    pasajeros_id = []
    for trayecto in lista_trayectos:
        for reserva in trayecto['listaReservas']:
            pasajeros_id.append(reserva['solicitante'])

    resultado = []
    for id_pasajero in pasajeros_id:
        pasajero = mongo.db.usuario.find_one({'_id': id_pasajero})
        if pasajero:
            resultado.append(json_util.dumps(pasajero))
    return resultado


@app.route('/api/usuarios/<id_usuario>/pasajeros', methods=['GET'])
def get_pasajeros_por_id_conductor_s(id_usuario):
    lista_pasajeros = get_pasajeros_por_id_conductor_aux(id_usuario)
    response = Response(json_util.dumps(lista_pasajeros), mimetype='application/json')
    if len(lista_pasajeros) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/usuarios/<id_usuario>/pasajeros', methods=['GET'])
# def get_pasajeros_por_id_conductor_c(id_usuario):
#     lista_pasajeros = get_pasajeros_por_id_conductor_aux(id_usuario)
#     # return render_template
#     return None


def crear_reserva_aux(id_trayecto, id_solicitante, plazas_reservadas):
    solicitante = None
    trayecto = None
    if id_solicitante:
        solicitante = mongo.db.usuario.find_one({'_id': ObjectId(id_solicitante)})
    if id_trayecto:
        trayecto = mongo.db.trayecto.find_one({'_id': ObjectId(id_trayecto)})
    plazas_disponibles = 0
    if trayecto != None and solicitante != None:
        lista_reservas = trayecto["listaReservas"]
        plazas_disponibles = get_plazas_disponibles_aux(id_trayecto)
    fecha_actual = datetime.now()
    if id_trayecto and id_solicitante and plazas_reservadas and int(plazas_reservadas) <= int(
            plazas_disponibles) and int(plazas_reservadas) > 0 and trayecto != None and solicitante != None and not (
            trayecto["fechaHora"] < fecha_actual):
        id_r = ObjectId()
        id_s = ObjectId(id_solicitante)
        reserva = {'_id': id_r,
                   'plazasReservadas': plazas_reservadas,
                   'fechaReserva': fecha_actual,
                   'solicitante': id_s,
                   }
        lista_reservas.append(reserva)

        mongo.db.trayecto.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': ObjectId(id_trayecto)},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaReservas': lista_reservas
            }})
        response = {'creada': 2,
                    'mensaje': 'El usuario con el ID = ' + id_solicitante + ' ha realizado una reserva con el ID = ' + str(
                        id_r) + ' en el trayecto con el ID = ' + id_trayecto}
    else:
        if trayecto == None:
            response = {'creada': 1, 'mensaje': 'No se puede reservar un trayecto con un ID que no existe.'}
        elif solicitante == None:
            response = {'creada': 1,
                        'mensaje': 'No se puede reservar un trayecto con un solicitante que cuyo ID no se encuentra en la base de datos.'}
        elif plazas_reservadas and int(plazas_reservadas) > plazas_disponibles:
            response = {'creada': 0,
                        'mensaje': 'No se ha podido realizar una reserva porque el numero de plazas solicitadas es mayor que las disponibles.'}
        elif plazas_reservadas and int(plazas_reservadas) <= 0:
            response = {'creada': 0,
                        'mensaje': 'No se ha podido realizar una reserva porque el numero de plazas solicitadas es inferior o igual a 0.'}
        elif trayecto["fechaHora"] < fecha_actual:
            response = {'creada': 0, 'mensaje': 'No se puede realizar una reserva de un trayecto pasado.'}
        else:
            response = {'creada': 0,
                        'mensaje': 'No se puede realizar una reserva porque el campo id_trayecto, id_solicitante o plazasReservadas estan vacios.'}
    return response


@app.route('/api/trayectos/reservas', methods=['PUT'])
def crear_reserva_s():
    id_trayecto = request.json["id_trayecto"]
    id_solicitante = request.json["id_solicitante"]
    plazas_reservadas = request.json["plazasReservadas"]
    creado = crear_reserva_aux(id_trayecto, id_solicitante, plazas_reservadas)
    response = jsonify({'mensaje': creado['mensaje']})
    if creado['creada'] == 2:
        response.status_code = 201
    else:
        response.status_code = 400
    return response


@app.route('/app/trayectos/reservas', methods=['POST'])
def crear_reserva_c():
    id_trayecto = request.form.get("id_trayecto")
    id_solicitante = session["id"]
    plazas_reservadas = request.form.get("plazasReservadas")
    creado = crear_reserva_aux(id_trayecto, id_solicitante, plazas_reservadas)
    return redirect('/app/usuarios/' + session["id"] + '/reservas')


def editar_reserva_aux(id_reserva, plazas_reservadas):
    trayecto = mongo.db.trayecto.find_one({'listaReservas._id': ObjectId(id_reserva)})
    lista_reservas = trayecto['listaReservas']
    plazas_disponibles = get_plazas_disponibles_aux(str(trayecto["_id"]))
    indiceReserva = 0
    fecha_actual = datetime.now()
    for idx, item in enumerate(lista_reservas):
        if ObjectId(id_reserva) == item["_id"]:
            indiceReserva = idx
    if plazas_reservadas <= 0:
        return {'editado': -1}
    elif (plazas_reservadas <= (plazas_disponibles + int(lista_reservas[indiceReserva]["plazasReservadas"]))) and \
            trayecto["fechaHora"] >= fecha_actual:
        reserva = {'_id': ObjectId(id_reserva),
                   'plazasReservadas': plazas_reservadas,
                   'fechaReserva': fecha_actual,
                   'solicitante': lista_reservas[indiceReserva]["solicitante"]
                   }
        lista_reservas[indiceReserva] = reserva
        mongo.db.trayecto.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': trayecto["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaReservas': lista_reservas
            }})
        response = {'editado': 2, 'mensaje': ' Se ha editado una reserva con ID = ' + str(
            id_reserva) + ' del trayecto con ID = ' + str(trayecto["_id"])}
    else:
        if trayecto["fechaHora"] < fecha_actual:
            response = {'editado': 1, 'mensaje': 'No se puede editar una reserva despues de un trayecto.'}
        else:
            response = {'editado': 0,
                        'mensaje': 'No se ha podido realizar una reserva porque el numero de plazas solicitadas es mayor que las disponibles.'}
    return response


@app.route('/api/trayectos/reservas/<id_reserva>', methods=['PUT'])
def editar_reserva_s(id_reserva):
    plazas_reservadas = int(request.json["plazasReservadas"])
    editada = editar_reserva_aux(id_reserva, plazas_reservadas)
    if editada['editado'] == -1:
        return eliminar_reserva_s(id_reserva)
    elif editada['editado'] == 0:
        response = jsonify({'mensaje': editada['mensaje']})
        response.status_code = 304
    elif editada['editado'] == 1:
        response = jsonify({'mensaje': editada['mensaje']})
        response.status_code = 400
    else:
        response = jsonify({'mensaje': editada['mensaje']})
        response.status_code = 200
    return response

def get_trayecto_by_reserva_and_usuario(id_reserva, id_usuario):
    trayectos = get_trayectos_aux()
    for t in trayectos:
        reservas = t["listaReservas"]
        for r in reservas:
            if str(id_reserva) == str(r["_id"]) :
                return trayecto.get_full_trayecto(t["_id"]), r["plazasReservadas"]
    return None, None

@app.route('/app/reservas/<id_reserva>/editar', methods=['POST'])
def editar_reserva_c(id_reserva):
    plazas_reservadas = request.form.get("plazasReservadas")
    reserva = get_reserva_usuario_aux(session["id"],id_reserva)
    if reserva:
        if plazas_reservadas:
            if int(plazas_reservadas) == 0:
                eliminada = eliminar_reserva_aux(id_reserva)
            else:
                editada = editar_reserva_aux(id_reserva, int(plazas_reservadas))
            return redirect('/app/usuarios/'+session["id"]+'/reservas')
        else:
            id_solicitante = request.form.get("id_solicitante")
            t, plazas = get_trayecto_by_reserva_and_usuario(id_reserva, id_solicitante)
            valoracion_media, n_valoraciones = get_valoraciones_media_aux(t["conductor"]["id"])
            return render_template('visualizar_trayecto.html', trayecto=t, valoracion_media=valoracion_media,
                                   n_valoraciones=n_valoraciones, fecha_actual=datetime.now(), plazas=plazas, id_reserva=id_reserva)
    else:
        return render_template("acceso_denegado.html")

def get_reserva_usuario_aux(id_usuario, id_reserva):
    lista_trayectos = get_reservas_usuario_aux(id_usuario)
    for t in lista_trayectos:
        lista_reservas = t["listaReservas"]
        for reserva in lista_reservas:
            if str(id_reserva) == str(reserva["_id"]):
                return reserva
    return None

def eliminar_reserva_aux(id_reserva):
    trayecto = mongo.db.trayecto.find_one({'listaReservas._id': ObjectId(id_reserva)})
    if trayecto != None:
        lista_reservas = trayecto['listaReservas']
        for idx, item in enumerate(lista_reservas):
            if ObjectId(id_reserva) == item["_id"]:
                lista_reservas.remove(lista_reservas[idx])

        mongo.db.trayecto.update_one(  # Esto actualiza todos los atributos, puede
            {'_id': trayecto["_id"]},  # que haya que cambiarlo para que actualice
            {'$set': {
                'listaReservas': lista_reservas
            }})
        response = {'eliminado': 1, 'mensaje': ' Se ha eliminado una reserva con ID = ' + str(
            id_reserva) + ' del trayecto con ID = ' + str(trayecto["_id"])}
    else:
        response = {'eliminado': 0,
                    'mensaje': 'No se ha eliminado la reserva porque no existe ningun ID de esa reserva.'}
    return response


@app.route('/api/trayectos/reservas/<id_reserva>', methods=['DELETE'])
def eliminar_reserva_s(id_reserva):
    eliminado = eliminar_reserva_aux(id_reserva)
    response = jsonify({'mensaje': eliminado['mensaje']})
    if eliminado['eliminado'] == 1:
        response.status_code = 200
    else:
        response.status_code = 400
    return response


@app.route('/app/reservas/<id_reserva>/eliminar', methods=['POST'])
def eliminar_reserva_c(id_reserva):
    reserva = get_reserva_usuario_aux(session["id"], id_reserva)
    if reserva:
        eliminado = eliminar_reserva_aux(id_reserva)
        return redirect('/app/usuarios/'+session["id"]+'/reservas')
    else:
        return render_template("acceso_denegado.html")

def get_reservas_usuario_aux(id_usuario):
    lista_reservas = mongo.db.trayecto.find({'listaReservas.solicitante': ObjectId(id_usuario)})
    return lista_reservas


def get_reservas_usuario_de_cercano_a_lejano_aux(id_usuario):
    lista_reservas = mongo.db.trayecto.find({'listaReservas.solicitante': ObjectId(id_usuario)}).sort('fechaHora', pymongo.ASCENDING)
    return lista_reservas

@app.route('/api/usuarios/<id_usuario>/reservas', methods=['GET'])
def get_reservas_usuario_s(id_usuario):
    lista_reservas = get_reservas_usuario_aux(id_usuario)
    response = Response(json_util.dumps(lista_reservas), mimetype='application/json')
    if len(json_util.dumps(lista_reservas)) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


@app.route('/app/usuarios/<id_usuario>/reservas', methods=['GET'])
def get_reservas_usuario_c(id_usuario):
    if str(id_usuario) == str(session["id"]):
        lista_trayecto = get_reservas_usuario_de_cercano_a_lejano_aux(id_usuario)
        lista_mis_reservas_futuro = []
        lista_mis_reservas_pasado = []
        tipo = 'conductor'
        fecha_actual = datetime.now()
        for trayecto in lista_trayecto:
            lista_reservas = trayecto["listaReservas"]
            for reserva in lista_reservas:
                if str(reserva["solicitante"]) == str(id_usuario):
                    mediaValoraciones, nValoraciones = get_valoraciones_media_aux(trayecto["conductor"])
                    if str(trayecto["fechaHora"]) >= str(fecha_actual):
                        lista_mis_reservas_futuro.append(usuario.get_reserva_origen_destino(reserva, trayecto["direccionOrigen"], trayecto["direccionDestino"], trayecto["fechaHora"], trayecto["precio"], get_usuario_aux(trayecto["conductor"]), None, get_plazas_disponibles_aux(trayecto["_id"]), get_coche_por_id_aux(trayecto["conductor"],trayecto["coche"]), trayecto["descripcion"], mediaValoraciones, nValoraciones))
                    else:
                        lista_mis_reservas_pasado.append(usuario.get_reserva_origen_destino(reserva, trayecto["direccionOrigen"], trayecto["direccionOrigen"], trayecto["fechaHora"],trayecto["precio"], get_usuario_aux(trayecto["conductor"]), get_valorado_reserva(trayecto["conductor"], reserva["_id"], tipo), get_plazas_disponibles_aux(trayecto["_id"]), get_coche_por_id_aux(trayecto["conductor"],trayecto["coche"]), trayecto["descripcion"], mediaValoraciones, nValoraciones))
        return render_template('mis_reservas.html', reservas_futuro=lista_mis_reservas_futuro, reservas_pasado=lista_mis_reservas_pasado)
    else:
        return render_template("acceso_denegado.html")
    
def get_valorado_reserva(id_conductor, id_reserva, tipo):
    valoraciones = get_valoraciones_recibidas_usuario_aux(id_conductor)
    for valoracion in valoraciones:
        if str(valoracion["id_reserva"]) == str(id_reserva) and str(valoracion["tipo"]) == str(tipo):
            return True
    return False

## DATOS ABIERTOS
def obtener_incidencias_trafico_del_recurso():
    # enlace = 'https://opendata.arcgis.com/datasets/a64659151f0a42c69a38563e9d006c6b_0.geojson'
    enlace = str('https://services1.arcgis.com/nCKYwcSONQTkPA4K/arcgis/rest/services/incidencias_DGT/FeatureServer/0' +
                 '/query?where=1%3D1&outFields=autonomia,carretera,causa,fechahora_,hacia,matricula,nivel,poblacion,' +
                 'provincia,ref_incide,sentido,tipo,actualizad,x,y&outSR=4326&f=json')
    datos = requests.get(enlace).json()['features']
    return datos


def get_incidencias_trafico_de_toda_espana_aux():
    incidencias = obtener_incidencias_trafico_del_recurso()
    lista_incidencias = []
    for incidencia in incidencias:
        lista_incidencias.append(incidencia)
    return lista_incidencias


@app.route('/api/abiertos/incidencias/espana', methods=['GET'])
def get_incidencias_trafico_de_toda_espana_s():
    lista_incidencias = get_incidencias_trafico_de_toda_espana_aux()
    response = Response(json_util.dumps(lista_incidencias), mimetype='application/json')
    if len(lista_incidencias) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/incidencias/espana', methods=['GET'])
# def get_incidencias_trafico_de_toda_espana_c():
#     lista_incidencias = get_incidencias_trafico_de_toda_espana_aux()
#     # return render_template
#     return None


def get_incidencias_trafico_por_comunidad_aux(comunidad):
    incidencias = obtener_incidencias_trafico_del_recurso()
    lista_incidencias = []
    for incidencia in incidencias:
        if incidencia['attributes']['autonomia'] == comunidad.upper():
            lista_incidencias.append(incidencia)
    return lista_incidencias


@app.route('/api/abiertos/incidencias/<comunidad>', methods=['GET'])
def get_incidencias_trafico_por_comunidad_s(comunidad):
    lista_incidencias = get_incidencias_trafico_por_comunidad_aux(comunidad)
    response = Response(json_util.dumps(lista_incidencias), mimetype='application/json')
    if len(lista_incidencias) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/incidencias/por_comunidad', methods=['POST'])
# def get_incidencias_trafico_por_comunidad_c():
#     comunidad = request.json['comunidad']
#     lista_incidencias = get_incidencias_trafico_por_comunidad_aux(comunidad)
#     # return render_template
#     return None


def get_incidencias_trafico_por_provincia_aux(provincia):
    incidencias = obtener_incidencias_trafico_del_recurso()
    lista_incidencias = []
    for incidencia in incidencias:
        if incidencia['attributes']['provincia'] == provincia.upper():
            lista_incidencias.append(incidencia)
    return lista_incidencias


@app.route('/api/abiertos/incidencias/<provincia>', methods=['GET'])
def get_incidencias_trafico_por_provincia_s(provincia):
    lista_incidencias = get_incidencias_trafico_por_provincia_aux(provincia)
    response = Response(json_util.dumps(lista_incidencias), mimetype='application/json')
    if len(lista_incidencias) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/incidencias/por_provincia', methods=['POST'])
# def get_incidencias_trafico_por_provincia_c():
#     provincia = request.json['provincia']
#     lista_incidencias = get_incidencias_trafico_por_provincia_aux(provincia)
#     # return render_template
#     return None


def get_incidencias_trafico_por_poblacion_aux(poblacion):
    incidencias = obtener_incidencias_trafico_del_recurso()
    lista_incidencias = []
    for incidencia in incidencias:
        if incidencia['attributes']['poblacion'] == poblacion.upper():
            lista_incidencias.append(incidencia)
    return lista_incidencias


@app.route('/api/abiertos/incidencias/<poblacion>', methods=['GET'])
def get_incidencias_trafico_por_poblacion_s(poblacion):
    lista_incidencias = get_incidencias_trafico_por_poblacion_aux(poblacion)
    response = Response(json_util.dumps(lista_incidencias), mimetype='application/json')
    if len(lista_incidencias) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/incidencias/por_poblacion', methods=['POST'])
# def get_incidencias_trafico_por_poblacion_c():
#     poblacion = request.json['poblacion']
#     lista_incidencias = get_incidencias_trafico_por_poblacion_aux(poblacion)
#     # return render_template
#     return None


def obtener_aeropuertos_del_recurso():
    enlace = 'https://opendata.arcgis.com/datasets/7232e84f53494f5e9b131b81f92534b8_0.geojson'
    datos = requests.get(enlace).json()['features']
    return datos


def get_aeropuertos_aux():
    aeropuertos = obtener_aeropuertos_del_recurso()
    lista_aeropuertos = []
    for aeropuerto in aeropuertos:
        lista_aeropuertos.append(aeropuerto)
    return lista_aeropuertos


@app.route('/api/abiertos/aeropuertos', methods=['GET'])
def get_aeropuertos_s():
    lista_aeropuertos = get_aeropuertos_aux()
    response = Response(json_util.dumps(lista_aeropuertos), mimetype='application/json')
    if len(lista_aeropuertos) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/aeropuertos', methods=['GET'])
# def get_aeropuertos_c():
#     lista_aeropuertos = get_aeropuertos_aux()
#     # return render_template
#     return None


def obtener_gasolineras_del_recurso():
    enlace = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    datos = requests.get(enlace).json()['ListaEESSPrecio']
    return datos


def get_gasolineras_aux():
    gasolineras = obtener_gasolineras_del_recurso()
    lista_gasolineras = []
    for gasolinera in gasolineras:
        lista_gasolineras.append(gasolinera)
    return lista_gasolineras


def get_gasolineras_corto():
    gasolineras = obtener_gasolineras_del_recurso()
    lista_gasolineras = []
    for gasolinera in gasolineras:
        latitud = gasolinera["Latitud"]
        longitud = gasolinera["Longitud (WGS84)"]
        localidad = gasolinera["Localidad"]
        provincia = gasolinera["Provincia"]
        municipio = gasolinera["Municipio"]
        direccion = gasolinera["Dirección"]
        lista_gasolineras.append(trayecto.get_gasolinera(latitud, longitud, localidad, provincia, municipio, direccion))
    return lista_gasolineras


@app.route('/api/abiertos/gasolineras', methods=['GET'])
def get_gasolineras_s():
    lista_gasolineras = get_gasolineras_aux()
    response = Response(json_util.dumps(lista_gasolineras), mimetype='application/json')
    if len(lista_gasolineras) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


@app.route('/app/abiertos/gasolineras', methods=['GET'])
def get_gasolineras_c():
    return render_template("gasolineras.html", gasolineras=[])


def get_gasolineras_por_municipio_bueno_aux(municipio):
    gasolineras = get_gasolineras_corto()
    lista_gasolineras = []
    for gasolinera in gasolineras:
        municipioAux = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
             normalize( "NFD", gasolinera['municipio']), 0, re.I)
    
        municipioAux = normalize( 'NFC', municipioAux)

        if (municipio.upper()) in municipioAux.upper():
            lista_gasolineras.append(gasolinera)
    return lista_gasolineras


@app.route('/app/abiertos/gasolineras/filtrar', methods=['GET'])
def get_gasolineras_por_municipio_bueno_c():
    municipio = request.args.get('municipio')

    municipio = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
             normalize( "NFD", municipio), 0, re.I)
    
    municipio = normalize( 'NFC', municipio)

    lista_gasolineras = get_gasolineras_por_municipio_bueno_aux(municipio)
    return render_template("gasolineras.html", gasolineras = lista_gasolineras, filtroMunicipio=municipio)


def get_gasolineras_por_provincia_aux(provincia):
    gasolineras = obtener_gasolineras_del_recurso()
    lista_gasolineras = []
    for gasolinera in gasolineras:
        if gasolinera['Provincia'] == provincia.upper():
            lista_gasolineras.append(gasolinera)
    return lista_gasolineras


@app.route('/api/abiertos/gasolineras/<provincia>', methods=['GET'])
def get_gasolineras_por_provincia_s(provincia):
    lista_gasolineras = get_gasolineras_por_provincia_aux(provincia)
    response = Response(json_util.dumps(lista_gasolineras), mimetype='application/json')
    if len(lista_gasolineras) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/gasolineras/por_provincia', methods=['POST'])
# def get_gasolineras_por_provincia_c():
#     provincia = request.json['provincia']
#     lista_gasolineras = get_gasolineras_por_provincia_aux(provincia)
#     return None #render_template("gasolineras.html", gasolineras = lista_gasolineras)


# def get_gasolineras_por_municipio_aux(municipio):
#     gasolineras = obtener_gasolineras_del_recurso()
#     lista_gasolineras = []
#     for gasolinera in gasolineras:
#         if gasolinera['Municipio'].upper() == municipio.upper():
#             lista_gasolineras.append(gasolinera)
#     return lista_gasolineras


@app.route('/api/abiertos/gasolineras/<municipio>', methods=['GET'])
def get_gasolineras_por_municipio_s(municipio):
    lista_gasolineras = get_gasolineras_por_municipio_bueno_aux(municipio)
    response = Response(json_util.dumps(lista_gasolineras), mimetype='application/json')
    if len(lista_gasolineras) == 0:
        response.status_code = 204
    else:
        response.status_code = 200
    return response


# @app.route('/app/abiertos/gasolineras/por_municipio', methods=['POST'])
# def get_gasolineras_por_municipio_c():
#     municipio = request.json['municipio']
#     lista_gasolineras = get_gasolineras_por_municipio_aux(municipio)
#     # return render_template
#     return None


@app.route('/app', methods=['GET'])
def index():    
    doc_trayectos = get_trayectos_fecha_cercana_a_lejana_aux()
    list_trayectos = []
    for doc in doc_trayectos:
        list_trayectos.append(trayecto.get_lite_trayecto(doc['_id']))

    num_usuarios = get_usuarios_contar_aux()
    num_trayectos = get_trayectos_contar_aux()

    return render_template('index.html', trayectos=list_trayectos, numeroUsuarios=num_usuarios, numeroTrayectos=num_trayectos)


@app.route('/auth', methods=['GET'])
def login_oauth():
    
    token = google.authorize_access_token()
    
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    correo = user_info["email"]
    
    user = get_usuario_por_correo_aux(correo)
    if user:
        session['id'] = str(user['_id'])
        session['admin'] = bool(user['admin'])
    else:
        try:
            apellidos = user_info["family_name"]
        except:
            apellidos = ''
        try:
            foto = user_info["picture"]
        except:
            foto = ''
    
        id_u = crear_usuario_aux(user_info["given_name"], apellidos, correo, foto, '', False)
        session['id'] = str(id_u)
        session['admin'] = False
    
    session['token'] = token
    if session.get("id_trayecto"):
        return redirect(url_for('get_trayecto_c', id_trayecto=session["id_trayecto"]))
    else:
        return redirect('/app')


@app.route('/login')
def login_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('login_oauth', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/')
def index2():
    #google_cliente_id = '884325304780-tu9b97m07oed9dsvu61gv4lhq3k85905.apps.googleusercontent.com'
    return render_template("login.html")


@app.route('/app/logout')
def logout():
    session.clear()
    return redirect("/")


@app.route('/app/create-payment', methods=['POST'])
def crear_pago():
    precio = request.form['precio']
    nplazas = request.form['plazas']
    p = float(precio)
    pl = int(nplazas)
    cuantity = p * pl
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",  # Estas urls no hacen falta por lo visto
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Reserva de plazas",
                    "sku": "12345",
                    "price": precio,
                    "currency": "EUR",
                    "quantity": nplazas}]},
            "amount": {
                "total": cuantity,
                "currency": "EUR"},
            "description": "Pago al conductor por la reserva en su viaje en la app LlévaMe."}]})
    if not payment.create():
        return render_template('acceso_denegado.html')  # Esto es temporal hasta que hagamos algo con los errores
    
    return jsonify({'paymentID': payment.id})


@app.route('/app/execute-payment', methods=['POST'])
def realizar_pago():
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if not payment.execute({'payer_id' : request.form['payerID']}):
        return render_template('acceso_denegado.html')  # Esto es temporal hasta que hagamos algo con los errores
    else:
        solicitante = session["id"]
        id_trayecto = request.form['id_trayecto']
        plazas = request.form['nplazas']
        crear_reserva_aux(id_trayecto, solicitante, plazas)
        return jsonify({'hostapp': request.headers['host'], 'usuario': solicitante})
    #return
    


@app.route('/filtrar', methods=['GET'])
def filtrar_trayectos_c():
    origen = request.args.get('ciudadOrigen')
    destino = request.args.get('ciudadDestino')
    fecha = request.args.get('fecha')
    pasajeros = request.args.get('pasajeros')

    doc_trayectos = mongo.db.trayecto.find({'fechaHora': {'$gte': datetime.now()}}).sort('fechaHora', pymongo.ASCENDING)

    if fecha:
        fecha_hora_ini = datetime.combine(datetime.strptime(fecha, '%Y-%m-%d'), datetime.strptime("00:00", '%H:%M').time())
        fecha_hora_fin = datetime.combine(datetime.strptime(fecha, '%Y-%m-%d'), datetime.strptime("23:59", '%H:%M').time())

    if origen and destino and fecha:
        doc_trayectos = mongo.db.trayecto.find({'fechaHora': {'$gte': fecha_hora_ini, '$lt': fecha_hora_fin } , 
                                                'ciudadOrigen': {'$regex': origen, '$options':'i'},
                                                'ciudadDestino': {'$regex': destino, '$options':'i'} }).sort('fechaHora', pymongo.ASCENDING)
    elif origen and fecha:
        doc_trayectos = mongo.db.trayecto.find({'fechaHora': {'$gte': fecha_hora_ini, '$lt': fecha_hora_fin } , 
                                                'ciudadOrigen': {'$regex': origen, '$options':'i'} }).sort('fechaHora', pymongo.ASCENDING)
    elif origen and destino:
        doc_trayectos = mongo.db.trayecto.find({'fechaHora': {'$gte': datetime.now()} ,
                                                'ciudadOrigen': {'$regex': origen, '$options':'i'},
                                                'ciudadDestino': {'$regex': destino, '$options':'i'} }).sort('fechaHora', pymongo.ASCENDING)
    elif origen:
        doc_trayectos = mongo.db.trayecto.find({'fechaHora': {'$gte': datetime.now()} ,
                                                'ciudadOrigen': {'$regex': origen, '$options':'i'} }).sort('fechaHora', pymongo.ASCENDING)

    list_trayectos = []
    if pasajeros:
        for t in doc_trayectos:
            if get_plazas_disponibles_aux(t['_id']) >= int(pasajeros):
                list_trayectos.append(trayecto.get_lite_trayecto(t['_id']))
    else:
        for t in doc_trayectos:
            list_trayectos.append(trayecto.get_lite_trayecto(t['_id']))

    numUsuarios = get_usuarios_contar_aux()
    numTrayectos = get_trayectos_contar_aux()

    return render_template('index.html', trayectos=list_trayectos, filtroOrigen=origen, filtroDestino=destino, filtroFecha=fecha, filtroPasajeros=pasajeros, numeroUsuarios=numUsuarios, numeroTrayectos=numTrayectos)


def get_tiempo_por_coordenadas(latitud, longitud):
    api_url = 'https://api.openweathermap.org/data/2.5/onecall?'
    url = api_url + urllib.parse.urlencode({
        "lat": latitud,
        "lon": longitud, 
        "appid": KEY_TIEMPO,
        "lang": 'es',
    })

    datos = requests.get(url).json()
    return datos
    

def traducir_tiempo(tiempo_ingles):
    tiempo_traducido = {
        'Thunderstorm': 'Tormenta eléctrica',
        'Drizzle': 'Llovizna',
        'Rain': 'Lluvia',
        'Snow': 'Nieve',
        'Clear': 'Despejado',
        'Clouds': 'Nubes',
        'Mist': 'Neblina',
        'Smoke': 'Humo',
        'Haze': 'Calima',
        'Dust': 'Polvo',
        'Fog': 'Niebla',
        'Sand': 'Arena',
        'Ash': 'Ceniza',
        'Squall': 'Chubasco',
        'Tornado': 'Tornado'
    }

    tiempo = tiempo_traducido.get(tiempo_ingles, 'Desconocido')
    return tiempo


def get_tiempo_actual_json(latitud, longitud):
    datos = get_tiempo_por_coordenadas(latitud, longitud)

    offset_hora = datos['timezone_offset']
    hora_salida_sol_utc = datos['current']['sunrise'] + offset_hora
    hora_puesta_sol_utc = datos['current']['sunset'] + offset_hora
    temperatura_kelvin = datos['current']['temp']
    #tiempo_ingles = datos['current']['weather'][0]['main']

    hora_salida_sol = datetime.utcfromtimestamp(int(hora_salida_sol_utc)).strftime('%H:%M')
    hora_puesta_sol = datetime.utcfromtimestamp(int(hora_puesta_sol_utc)).strftime('%H:%M')
    temperatura = round(temperatura_kelvin-273.15, 1)
    #porcentaje_humedad = datos['current']['humidity']
    viento = round(datos['current']['wind_speed'] * 3.6, 2)
    porcentaje_nubes = datos['current']['clouds']
    descripcion = datos['current']['weather'][0]['description'].capitalize()
    # tiempo = traducir_tiempo(tiempo_ingles)
    # if descripcion != tiempo:
    #     informacion = tiempo + ". " + descripcion + "."
    # else:
    #     informacion = descripcion + "."

    datos_meteo = {
        'salidaSol' : hora_salida_sol,
        'puestaSol' : hora_puesta_sol,
        'temperatura' : temperatura,
        'viento' : viento,
        #'humedad' : porcentaje_humedad,
        'nubes' : porcentaje_nubes,
        'descripcion' : descripcion,
        #'tiempo' : tiempo,
        'informacion' : descripcion
    }

    return datos_meteo

def traducir_dia(dia_ingles):
    dia_traducido = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    dia = dia_traducido.get(dia_ingles, 'Desconocido')
    return dia

def obtener_fecha_con_dia_semana(fecha_utc):
    fecha_ing = datetime.utcfromtimestamp(int(fecha_utc)).strftime('%Y-%m-%d')
    fecha = datetime.utcfromtimestamp(int(fecha_utc)).strftime('%d/%m/%Y')
    fecha_actual = datetime.utcnow().strftime('%d/%m/%Y')
    temp = pd.Timestamp(fecha_ing)
    dia = traducir_dia(temp.day_name())
    if fecha == fecha_actual:
        dia = 'Hoy'
    fecha_res = dia + ", " + fecha
    
    return fecha_res


def get_tiempo_siguientes_dias_json(latitud, longitud):
    datos = get_tiempo_por_coordenadas(latitud, longitud)
    datos_lista = []
    offset_hora = datos['timezone_offset']
    for dia in datos['daily']:
        fecha_utc = dia['dt'] + offset_hora
        hora_salida_sol_utc = dia['sunrise'] + offset_hora
        hora_puesta_sol_utc = dia['sunset'] + offset_hora
        temperatura_kelvin = dia['temp']['day']
        #tiempo_ingles = dia['weather'][0]['main']

        fecha = obtener_fecha_con_dia_semana(fecha_utc)
        #fecha = datetime.utcfromtimestamp(int(fecha_utc)).strftime('%d/%m/%Y')
        hora_salida_sol = datetime.utcfromtimestamp(int(hora_salida_sol_utc)).strftime('%H:%M')
        hora_puesta_sol = datetime.utcfromtimestamp(int(hora_puesta_sol_utc)).strftime('%H:%M')
        temperatura = round(temperatura_kelvin-273.15, 1)
        viento = round(dia['wind_speed'] * 3.6, 2)
        porcentaje_nubes = dia['clouds']
        descripcion = dia['weather'][0]['description'].capitalize()
        # tiempo = traducir_tiempo(tiempo_ingles)
        # if tiempo.lower() in descripcion.lower():
        #     informacion = descripcion 
        # elif descripcion != tiempo:
        #     informacion = tiempo + ". " + descripcion
        # else:
        #     informacion = descripcion

        datos_dia = {
            'fecha' : fecha,
            'salidaSol' : hora_salida_sol,
            'puestaSol' : hora_puesta_sol,
            'temperatura' : temperatura,
            'viento' : viento,
            'nubes' : porcentaje_nubes,
            'descripcion' : descripcion,
            #'tiempo' : tiempo,
            'informacion' : descripcion
        }

        datos_lista.append(datos_dia)

    return datos_lista

def get_tiempo_aux(municipio):
    direccion = ''
    if not municipio:
        # obtengo mi ubicación actual
        g = geocoder.ip('me')
        latitud = g.latlng[0]
        longitud = g.latlng[1]
        municipio = 'vacio'
        datos_meteo = get_tiempo_actual_json(latitud, longitud)
        datos_prox_dias = get_tiempo_siguientes_dias_json(latitud, longitud)
    else:
        loc = Nominatim(user_agent="GetLoc")
        getLoc = loc.geocode(municipio.capitalize())
        if getLoc == None:
            direccion = 'imposible'
            datos_meteo = ''
            datos_prox_dias = ''
        else:
            direccionSpl = getLoc.address.split(", ")
            direccion = direccionSpl[0] + ", " + direccionSpl[len(direccionSpl)-1]
            latitud = getLoc.latitude
            longitud = getLoc.longitude
            datos_meteo = get_tiempo_actual_json(latitud, longitud)
            datos_prox_dias = get_tiempo_siguientes_dias_json(latitud, longitud)
    return datos_meteo, datos_prox_dias, direccion


@app.route('/app/abiertos/tiempo', methods=['GET'])
def get_tiempo():
    municipio = request.args.get('municipio')
    datos_meteo, datos_prox_dias, direccion = get_tiempo_aux(municipio)
    if not municipio:
        municipio = ''
    return render_template("tiempo.html", meteo = datos_meteo, meteo_prox = datos_prox_dias, filtroMunicipio = municipio, direccion = direccion)


@app.route('/api/abiertos/tiempo', methods=['GET'])
def get_tiempo_s():
    municipio = request.args.get('municipio')
    datos_meteo, datos_prox_dias, direccion = get_tiempo_aux(municipio)
    datos_tiempo_server = []
    datos_tiempo_server.append(municipio)
    datos_tiempo_server.append(direccion)
    datos_tiempo_server.append(datos_prox_dias)
    
    response = Response(json_util.dumps(datos_tiempo_server), mimetype='application/json')
    response.status_code = 200
    return response


if __name__ == "__main__":
    app.run(debug=True)
    #app.run(debug=True, port=8080, host='localhost')
