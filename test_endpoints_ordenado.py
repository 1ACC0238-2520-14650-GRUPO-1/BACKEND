"""
ARCHIVO DE PRUEBA DE ENDPOINTS ORDENADOS
==========================================

Orden de ejecución respetando dependencias (Foreign Keys):


2. IAM - Crear cuenta 
3. IAM - Login (necesario para obtener tokens)
4. PUESTO - Crear puesto (depende de empresa_id - usar un UUID de empresa)
5. POSTULACION - Crear postulación (depende de candidato_id y puesto_id)
6. METRICAS - Consultar métricas 

El script ejecuta cada endpoint y valida las respuestas.
"""

import requests
import json
from uuid import uuid4
from datetime import datetime, timedelta
import time

# =====================================================================
# CONFIGURACIÓN
# =====================================================================

BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Almacenar IDs generados para usarlos en requests posteriores
datos_almacenados = {
    "cuenta_id": None,
    "email": None,
    "access_token": None,
    "refresh_token": None,
    "rol": None,
    "empresa_id": str(uuid4()),  # Simulamos una empresa existente
    "puesto_id": None,
    "candidato_id": None,
    "postulacion_id": None
}

# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def imprimir_resultado(num_test, titulo, metodo, url, estado, respuesta, esperado=None):
    """Imprime los resultados de cada test de forma legible"""
    print(f"\n{'='*80}")
    print(f"TEST {num_test}: {titulo}")
    print(f"{'='*80}")
    print(f"Método: {metodo}")
    print(f"URL: {url}")
    print(f"Estado HTTP: {estado}")
    
    if estado >= 200 and estado < 300:
        print(f"✅ EXITOSO")
    else:
        print(f"❌ ERROR")
    
    print(f"\nRespuesta:")
    print(json.dumps(respuesta, indent=2, default=str))
    
    if esperado:
        print(f"\nExpectativas:")
        print(f"  - {esperado}")

def hacer_peticion(metodo, endpoint, data=None, headers=None, test_num=0, titulo=""):
    """Realiza una petición HTTP y retorna el estado y la respuesta"""
    url = f"{BASE_URL}{endpoint}"
    if headers is None:
        headers = HEADERS.copy()
    
    try:
        if metodo == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif metodo == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif metodo == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif metodo == "PATCH":
            response = requests.patch(url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"Método HTTP no soportado: {metodo}")
        
        try:
            respuesta = response.json()
        except:
            respuesta = response.text
        
        imprimir_resultado(test_num, titulo, metodo, url, response.status_code, respuesta)
        return response.status_code, respuesta
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: No se puede conectar a {url}")
        print("Asegúrate de que el servidor FastAPI está corriendo en http://localhost:8000")
        return None, None
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None, None

# =====================================================================
# TESTS
# =====================================================================

def test_1_crear_perfil():
    """TEST 1: Crear un perfil de postulante (ahora usando IAM)"""
    print("\n\n" + "="*80)
    print("INICIANDO TESTS DE ENDPOINTS")
    print("="*80)
    
    email_perfil = f"candidato_{uuid4().hex[:8]}@example.com"
    
    data = {
        "nombre_completo": "Juan Carlos Pérez",
        "email": email_perfil,
        "password": "Password123!",
        "telefono": "+34 612345678",
        "ciudad": "Madrid",
        "rol": "postulante"
    }
    
    estado, respuesta = hacer_peticion(
        "POST", 
        "/iam/registrar",
        data=data,
        test_num=1,
        titulo="Crear Perfil de Postulante (via IAM)"
    )
    
    if estado and estado < 300 and isinstance(respuesta, dict):
        datos_almacenados["perfil_id"] = respuesta.get("cuenta_id") or str(uuid4())
        datos_almacenados["cuenta_id"] = respuesta.get("cuenta_id") or datos_almacenados["perfil_id"]
        datos_almacenados["email"] = respuesta.get("email") or email_perfil
        print(f"\n✅ Perfil ID almacenado: {datos_almacenados['perfil_id']}")
        print(f"✅ Cuenta ID almacenado: {datos_almacenados['cuenta_id']}")
        return True
    
    return False

def test_3_login():
    """TEST 3: Realizar login para obtener tokens"""
    if not datos_almacenados["email"]:
        print("\n❌ TEST SALTADO: No hay email disponible")
        return False
    
    data = {
        "email": datos_almacenados["email"],
        "password": "Password123!"
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/iam/login",
        data=data,
        test_num=3,
        titulo="Login - Obtener Tokens JWT"
    )
    
    if estado and estado < 300 and isinstance(respuesta, dict):
        datos_almacenados["access_token"] = respuesta.get("access_token")
        datos_almacenados["refresh_token"] = respuesta.get("refresh_token")
        datos_almacenados["rol"] = respuesta.get("rol")
        datos_almacenados["cuenta_id"] = respuesta.get("cuenta_id")
        
        print(f"\n✅ Access Token obtenido (primeros 50 chars): {str(datos_almacenados['access_token'])[:50]}...")
        print(f"✅ Refresh Token obtenido (primeros 50 chars): {str(datos_almacenados['refresh_token'])[:50]}...")
        print(f"✅ Rol: {datos_almacenados['rol']}")
        return True
    
    return False



def test_5_obtener_cuenta():
    """TEST 5: Obtener información de la cuenta creada"""
    if not datos_almacenados["cuenta_id"]:
        print("\n❌ TEST SALTADO: No hay cuenta_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/iam/cuenta/{datos_almacenados['cuenta_id']}",
        test_num=5,
        titulo="Obtener Cuenta IAM por ID"
    )
    
    return estado and estado < 300

def test_6_verificar_token():
    """TEST 6: Verificar que el token es válido"""
    if not datos_almacenados["access_token"]:
        print("\n❌ TEST SALTADO: No hay access_token disponible")
        return False
    
    data = {
        "refresh_token": datos_almacenados["access_token"]
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/iam/verificar-token",
        data=data,
        test_num=6,
        titulo="Verificar Token JWT"
    )
    
    return estado and estado < 300


    

def test_8_crear_puesto():
    """TEST 8: Crear un puesto de trabajo (requiere empresa_id)"""
    
    empresa_id_simula = datos_almacenados["empresa_id"]
    
    data = {
        "empresa_id": empresa_id_simula,
        "titulo": "Senior Backend Developer",
        "descripcion": "Buscamos un Senior Backend Developer con experiencia en FastAPI y PostgreSQL",
        "ubicacion": "Madrid, España",
        "salario_min": 45000,
        "salario_max": 60000,
        "moneda": "EUR",
        "tipo_contrato": "tiempo_completo",
        "requisitos": [
            {
                "tipo": "experiencia",
                "descripcion": "Mínimo 5 años de experiencia en desarrollo backend",
                "es_obligatorio": True
            },
            {
                "tipo": "educacion",
                "descripcion": "Grado en Ingeniería Informática o similar",
                "es_obligatorio": False
            },
            {
                "tipo": "habilidad",
                "descripcion": "Experiencia con FastAPI, PostgreSQL y Docker",
                "es_obligatorio": True
            }
        ]
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/puesto/",
        data=data,
        test_num=8,
        titulo="Crear Puesto de Trabajo"
    )
    
    if estado and estado < 300 and isinstance(respuesta, dict):
        datos_almacenados["puesto_id"] = respuesta.get("puesto_id") or str(uuid4())
        print(f"\n✅ Puesto ID almacenado: {datos_almacenados['puesto_id']}")
        return True
    
    return False

def test_9_obtener_puesto():
    """TEST 9: Obtener información del puesto creado"""
    if not datos_almacenados["puesto_id"]:
        print("\n❌ TEST SALTADO: No hay puesto_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/puesto/{datos_almacenados['puesto_id']}",
        test_num=9,
        titulo="Obtener Puesto por ID"
    )
    
    return estado and estado < 300

def test_10_listar_puestos():
    """TEST 10: Listar todos los puestos disponibles"""
    
    estado, respuesta = hacer_peticion(
        "GET",
        "/puesto/",
        test_num=10,
        titulo="Listar Todos los Puestos"
    )
    
    return estado and estado < 300

def test_11_crear_postulacion():
    """TEST 11: Crear una postulación (depende de candidato_id y puesto_id)"""
    if not datos_almacenados["cuenta_id"] or not datos_almacenados["puesto_id"]:
        print("\n❌ TEST SALTADO: No hay cuenta_id o puesto_id disponible")
        return False
    
    # Usar cuenta_id como candidato_id (en una app real sería diferente)
    datos_almacenados["candidato_id"] = datos_almacenados["cuenta_id"]
    
    data = {
        "candidato_id": datos_almacenados["candidato_id"],
        "puesto_id": datos_almacenados["puesto_id"],
        "documentos_adjuntos": [
            {
                "tipo": "cv",
                "url": "https://example.com/cv/juan_carlos_perez.pdf",
                "nombre": "CV_JuanCarlos.pdf"
            },
            {
                "tipo": "carta_presentacion",
                "url": "https://example.com/cartas/juan_carlos_perez.pdf",
                "nombre": "Carta_Presentacion.pdf"
            }
        ]
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/postulacion/",
        data=data,
        test_num=11,
        titulo="Crear Postulación"
    )
    
    if estado and estado < 300 and isinstance(respuesta, dict):
        datos_almacenados["postulacion_id"] = respuesta.get("postulacion_id") or str(uuid4())
        print(f"\n✅ Postulación ID almacenado: {datos_almacenados['postulacion_id']}")
        return True
    
    return False

def test_12_obtener_postulacion():
    """TEST 12: Obtener información de la postulación creada"""
    if not datos_almacenados["postulacion_id"]:
        print("\n❌ TEST SALTADO: No hay postulacion_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/postulacion/{datos_almacenados['postulacion_id']}",
        test_num=12,
        titulo="Obtener Postulación por ID"
    )
    
    return estado and estado < 300

def test_13_listar_postulaciones():
    """TEST 13: Listar postulaciones del candidato"""
    if not datos_almacenados["candidato_id"]:
        print("\n❌ TEST SALTADO: No hay candidato_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/postulacion/?candidato_id={datos_almacenados['candidato_id']}",
        test_num=13,
        titulo="Listar Postulaciones del Candidato"
    )
    
    return estado and estado < 300

def test_14_actualizar_estado_postulacion():
    """TEST 14: Cambiar estado de la postulación (pendiente -> en_revision)"""
    if not datos_almacenados["postulacion_id"]:
        print("\n❌ TEST SALTADO: No hay postulacion_id disponible")
        return False
    
    data = {
        "nuevo_estado": "en_revision"
    }
    
    estado, respuesta = hacer_peticion(
        "PATCH",
        f"/postulacion/{datos_almacenados['postulacion_id']}/estado",
        data=data,
        test_num=14,
        titulo="Actualizar Estado de Postulación a 'En Revisión'"
    )
    
    return estado and estado < 300

def test_15_actualizar_estado_postulacion_2():
    """TEST 15: Cambiar estado de postulación (en_revision -> entrevista)"""
    if not datos_almacenados["postulacion_id"]:
        print("\n❌ TEST SALTADO: No hay postulacion_id disponible")
        return False
    
    data = {
        "nuevo_estado": "entrevista"
    }
    
    estado, respuesta = hacer_peticion(
        "PATCH",
        f"/postulacion/{datos_almacenados['postulacion_id']}/estado",
        data=data,
        test_num=15,
        titulo="Actualizar Estado de Postulación a 'Entrevista'"
    )
    
    return estado and estado < 300

def test_16_cambiar_estado_puesto():
    """TEST 16: Cambiar estado del puesto (abierto -> cerrado)"""
    if not datos_almacenados["puesto_id"]:
        print("\n❌ TEST SALTADO: No hay puesto_id disponible")
        return False
    
    data = {
        "nuevo_estado": "cerrado"
    }
    
    estado, respuesta = hacer_peticion(
        "PATCH",
        f"/puesto/{datos_almacenados['puesto_id']}/estado",
        data=data,
        test_num=16,
        titulo="Cambiar Estado del Puesto a 'Cerrado'"
    )
    
    return estado and estado < 300

def test_17_obtener_metricas():
    """TEST 17: Obtener métricas del cuenta (depende de cuenta_id)"""
    if not datos_almacenados["cuenta_id"]:
        print("\n❌ TEST SALTADO: No hay cuenta_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/metricas/resumen/{datos_almacenados['cuenta_id']}",
        test_num=17,
        titulo="Obtener Resumen de Métricas"
    )
    
    return estado and estado < 300

def test_18_listar_logros():
    """TEST 18: Listar logros del cuenta"""
    if not datos_almacenados["cuenta_id"]:
        print("\n❌ TEST SALTADO: No hay cuenta_id disponible")
        return False
    
    estado, respuesta = hacer_peticion(
        "GET",
        f"/metricas/logros/{datos_almacenados['cuenta_id']}",
        test_num=18,
        titulo="Listar Logros del cuenta"
    )
    
    return estado and estado < 300

def test_19_refresh_token():
    """TEST 19: Refrescar el access token usando refresh token"""
    if not datos_almacenados["refresh_token"]:
        print("\n❌ TEST SALTADO: No hay refresh_token disponible")
        return False
    
    data = {
        "refresh_token": datos_almacenados["refresh_token"]
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/iam/refresh-token",
        data=data,
        test_num=19,
        titulo="Refrescar Access Token"
    )
    
    if estado and estado < 300 and isinstance(respuesta, dict):
        nuevo_token = respuesta.get("access_token")
        if nuevo_token:
            datos_almacenados["access_token"] = nuevo_token
            print(f"\n✅ Nuevo Access Token obtenido (primeros 50 chars): {str(nuevo_token)[:50]}...")
        return True
    
    return False

def test_20_enviar_feedback():
    """TEST 20: Enviar feedback sobre la postulación"""
    if not datos_almacenados["postulacion_id"]:
        print("\n❌ TEST SALTADO: No hay postulacion_id disponible")
        return False
    
    data = {
        "postulacion_id": datos_almacenados["postulacion_id"],
        "empresa_id": datos_almacenados["empresa_id"],
        "cuenta_id": datos_almacenados["cuenta_id"],
        "tipo_feedback": "comentario",
        "mensaje_texto": "Excelente candidato, continuaremos en contacto.",
        "motivo_rechazo": None
    }
    
    estado, respuesta = hacer_peticion(
        "POST",
        "/contacto/feedback",
        data=data,
        test_num=20,
        titulo="Enviar Feedback de Postulación"
    )
    
    return estado and estado < 300

# =====================================================================
# RESUMEN
# =====================================================================

def mostrar_resumen(resultados):
    """Muestra un resumen de los tests ejecutados"""
    print("\n\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)
    
    total = len(resultados)
    exitosos = sum(1 for r in resultados if r[1])
    fallidos = total - exitosos
    
    print(f"\nTotal de tests: {total}")
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"Tasa de éxito: {(exitosos/total)*100:.1f}%")
    
    print("\nDetalle de tests:")
    for i, (titulo, resultado) in enumerate(resultados, 1):
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"  {i:2d}. {titulo:<50} {estado}")
    
    print("\nDatos almacenados finales:")
    print(json.dumps({k: v if not isinstance(v, str) or len(str(v)) < 50 else str(v)[:50] + "..." for k, v in datos_almacenados.items()}, indent=2, default=str))
    
    print("\n" + "="*80)

# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    # Limpiar mapeo de puestos
    import tempfile
    import os
    mapeo_file = os.path.join(tempfile.gettempdir(), 'puestos_mapeo.json')
    if os.path.exists(mapeo_file):
        os.remove(mapeo_file)
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  SUITE DE PRUEBAS DE ENDPOINTS ORDENADOS".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    print("\nEsta suite prueba todos los endpoints respetando las dependencias de foreign keys.")
    print("Asegúrate de que el servidor FastAPI está corriendo: http://localhost:8000\n")
    
    # Ejecutar todos los tests
    resultados = [
        ("TEST 1: Crear Perfil (IAM)", test_1_crear_perfil()),
        ("TEST 3: Login", test_3_login()),
        ("TEST 5: Obtener Cuenta", test_5_obtener_cuenta()),
        ("TEST 6: Verificar Token", test_6_verificar_token()),
        ("TEST 8: Crear Puesto", test_8_crear_puesto()),
        ("TEST 9: Obtener Puesto", test_9_obtener_puesto()),
        ("TEST 10: Listar Puestos", test_10_listar_puestos()),
        ("TEST 11: Crear Postulación", test_11_crear_postulacion()),
        ("TEST 12: Obtener Postulación", test_12_obtener_postulacion()),
        ("TEST 13: Listar Postulaciones", test_13_listar_postulaciones()),
        ("TEST 14: Actualizar Estado Postulación 1", test_14_actualizar_estado_postulacion()),
        ("TEST 15: Actualizar Estado Postulación 2", test_15_actualizar_estado_postulacion_2()),
        ("TEST 16: Cambiar Estado Puesto", test_16_cambiar_estado_puesto()),
        ("TEST 17: Obtener Métricas", test_17_obtener_metricas()),
        ("TEST 18: Listar Logros", test_18_listar_logros()),
        ("TEST 19: Refrescar Token", test_19_refresh_token()),
        ("TEST 20: Enviar Feedback", test_20_enviar_feedback()),
    ]
    
    # Mostrar resumen
    mostrar_resumen(resultados)
