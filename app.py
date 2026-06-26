import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import gspread
from flask import Flask, redirect, render_template, request, session, url_for
from google.oauth2.service_account import Credentials


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cambia-esta-clave-en-railway")


# ============================================================
# CONFIGURACIÓN DEL NEGOCIO
# ============================================================

PRECIOS_PALTA = {
    "Hass": 2500,
    "Fuerte": 2500,
}

KILOS_MINIMOS = 1.0

TITULAR = "Enrique Armando Brun Urrutia"
RUT = "20.794.977-9"
BANCO = "Banco Estado"
TIPO_CUENTA = "Cuenta RUT"

WHATSAPP_NEGOCIO = "56963596523"

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1o1zvFzeOsGkDdLQbvEBvMyK6avLiMVMj04Ic0J2bzSw/edit?usp=sharing"
GOOGLE_SHEET_NAME = "Pedidos"

ARCHIVO_RESPALDO = Path("ordenes_paltas.csv")
LOCALIDADES_CERCANAS = ["La Calera", "Quillota", "La Cruz", "Hijuelas"]


REGIONES_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "General Lagos", "Putre"],
    "Tarapacá": ["Alto Hospicio", "Camiña", "Colchane", "Huara", "Iquique", "Pica", "Pozo Almonte"],
    "Antofagasta": ["Antofagasta", "Calama", "María Elena", "Mejillones", "Ollagüe", "San Pedro de Atacama", "Sierra Gorda", "Taltal", "Tocopilla"],
    "Atacama": ["Alto del Carmen", "Caldera", "Chañaral", "Copiapó", "Diego de Almagro", "Freirina", "Huasco", "Tierra Amarilla", "Vallenar"],
    "Coquimbo": ["Andacollo", "Canela", "Combarbalá", "Coquimbo", "Illapel", "La Higuera", "La Serena", "Los Vilos", "Monte Patria", "Ovalle", "Paihuano", "Punitaqui", "Río Hurtado", "Salamanca", "Vicuña"],
    "Valparaíso": ["Algarrobo", "Cabildo", "Calle Larga", "Cartagena", "Casablanca", "Catemu", "Concón", "El Quisco", "El Tabo", "Hijuelas", "Isla de Pascua", "Juan Fernández", "La Calera", "La Cruz", "La Ligua", "Limache", "Llaillay", "Los Andes", "Nogales", "Olmué", "Panquehue", "Papudo", "Petorca", "Puchuncaví", "Putaendo", "Quillota", "Quilpué", "Quintero", "Rinconada", "San Antonio", "San Esteban", "San Felipe", "Santa María", "Santo Domingo", "Valparaíso", "Villa Alemana", "Viña del Mar", "Zapallar"],
    "Metropolitana de Santiago": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Ñuñoa", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura"],
    "O'Higgins": ["Chépica", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "La Estrella", "Las Cabras", "Litueche", "Lolol", "Machalí", "Malloa", "Marchihue", "Mostazal", "Nancagua", "Navidad", "Olivar", "Palmilla", "Paredones", "Peralillo", "Peumo", "Pichidegua", "Pichilemu", "Placilla", "Pumanque", "Quinta de Tilcoco", "Rancagua", "Rengo", "Requínoa", "San Fernando", "San Vicente", "Santa Cruz"],
    "Maule": ["Cauquenes", "Chanco", "Colbún", "Constitución", "Curepto", "Curicó", "Empedrado", "Hualañé", "Licantén", "Linares", "Longaví", "Maule", "Molina", "Parral", "Pelarco", "Pelluhue", "Pencahue", "Rauco", "Retiro", "Río Claro", "Romeral", "Sagrada Familia", "San Clemente", "San Javier", "San Rafael", "Talca", "Teno", "Vichuquén", "Villa Alegre", "Yerbas Buenas"],
    "Ñuble": ["Bulnes", "Chillán", "Chillán Viejo", "Cobquecura", "Coelemu", "Coihueco", "El Carmen", "Ninhue", "Ñiquén", "Pemuco", "Pinto", "Portezuelo", "Quillón", "Quirihue", "Ránquil", "San Carlos", "San Fabián", "San Ignacio", "San Nicolás", "Treguaco", "Yungay"],
    "Biobío": ["Alto Biobío", "Antuco", "Arauco", "Cabrero", "Cañete", "Chiguayante", "Concepción", "Contulmo", "Coronel", "Curanilahue", "Florida", "Hualpén", "Hualqui", "Laja", "Lebu", "Los Álamos", "Los Ángeles", "Lota", "Mulchén", "Nacimiento", "Negrete", "Penco", "Quilaco", "Quilleco", "San Pedro de la Paz", "San Rosendo", "Santa Bárbara", "Santa Juana", "Talcahuano", "Tirúa", "Tomé", "Tucapel", "Yumbel"],
    "La Araucanía": ["Angol", "Carahue", "Cholchol", "Collipulli", "Cunco", "Curacautín", "Curarrehue", "Ercilla", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Lonquimay", "Los Sauces", "Lumaco", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Purén", "Renaico", "Saavedra", "Temuco", "Teodoro Schmidt", "Toltén", "Traiguén", "Victoria", "Vilcún", "Villarrica"],
    "Los Ríos": ["Corral", "Futrono", "La Unión", "Lago Ranco", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "Río Bueno", "Valdivia"],
    "Los Lagos": ["Ancud", "Calbuco", "Castro", "Chaitén", "Chonchi", "Cochamó", "Curaco de Vélez", "Dalcahue", "Fresia", "Frutillar", "Futaleufú", "Hualaihué", "Llanquihue", "Los Muermos", "Maullín", "Osorno", "Palena", "Puerto Montt", "Puerto Octay", "Puerto Varas", "Puqueldón", "Purranque", "Puyehue", "Queilén", "Quellón", "Quemchi", "Quinchao", "Río Negro", "San Juan de la Costa", "San Pablo"],
    "Aysén": ["Aysén", "Chile Chico", "Cisnes", "Cochrane", "Coyhaique", "Guaitecas", "Lago Verde", "O'Higgins", "Río Ibáñez", "Tortel"],
    "Magallanes": ["Antártica", "Cabo de Hornos", "Laguna Blanca", "Natales", "Porvenir", "Primavera", "Punta Arenas", "Río Verde", "San Gregorio", "Timaukel", "Torres del Paine"],
}


# ============================================================
# UTILIDADES
# ============================================================

def formato_pesos(valor) -> str:
    try:
        numero = int(round(float(valor)))
    except Exception:
        numero = 0
    return "$" + f"{numero:,}".replace(",", ".")


def calcular_total(tipo_palta: str, kilos: float) -> int:
    return int(round(PRECIOS_PALTA[tipo_palta] * kilos))


def normalizar_whatsapp(numero: str) -> str:
    return "".join(c for c in numero if c.isdigit())


def columnas_internas() -> list[str]:
    return [
        "folio", "fecha_registro", "tipo_palta", "kilos", "precio_por_kg",
        "total_paltas", "modalidad_entrega", "region", "comuna", "poblacion",
        "calle", "numero", "nombre", "whatsapp", "estado",
    ]


def encabezados_google_sheets() -> list[str]:
    return [
        "Folio", "Fecha registro", "Tipo de palta", "Kilos", "Precio por kg",
        "Total paltas", "Modalidad de entrega", "Región", "Comuna",
        "Población / sector", "Calle", "Número", "Nombre cliente",
        "WhatsApp cliente", "Estado",
    ]


def obtener_service_account_info() -> dict:
    contenido = os.getenv("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not contenido:
        raise RuntimeError("Falta la variable de entorno GCP_SERVICE_ACCOUNT_JSON.")
    return json.loads(contenido)


def obtener_worksheet_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(obtener_service_account_info(), scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)

    try:
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=GOOGLE_SHEET_NAME,
            rows=1000,
            cols=len(encabezados_google_sheets()),
        )

    return worksheet


def asegurar_encabezados_google_sheets(worksheet) -> None:
    encabezados = encabezados_google_sheets()
    valores = worksheet.get_all_values()

    if not valores:
        worksheet.append_row(encabezados, value_input_option="USER_ENTERED")
        return

    primera_fila = [str(v).strip() for v in valores[0]]
    if primera_fila[: len(encabezados)] != encabezados:
        worksheet.insert_row(encabezados, index=1, value_input_option="USER_ENTERED")


def guardar_respaldo_csv(datos: dict) -> None:
    existe = ARCHIVO_RESPALDO.exists()
    columnas = columnas_internas()

    with ARCHIVO_RESPALDO.open("a", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)


def guardar_google_sheets(datos: dict) -> tuple[bool, str]:
    try:
        worksheet = obtener_worksheet_google_sheets()
        asegurar_encabezados_google_sheets(worksheet)
        fila = [datos.get(clave, "") for clave in columnas_internas()]
        worksheet.append_row(fila, value_input_option="USER_ENTERED")
        return True, "Guardado en Google Sheets."
    except Exception as error:
        guardar_respaldo_csv(datos)
        return False, str(error)


def crear_cuerpo_solicitud(datos: dict) -> str:
    return f"""
Nueva solicitud de pedido de paltas.

FOLIO
{datos["folio"]}

PEDIDO
Tipo de palta: {datos["tipo_palta"]}
Kilos: {datos["kilos"]} kg
Precio por kg: {formato_pesos(datos["precio_por_kg"])}
Total paltas: {formato_pesos(datos["total_paltas"])}

ENTREGA
Modalidad: {datos["modalidad_entrega"]}
Región: {datos["region"] or "No aplica"}
Comuna: {datos["comuna"] or "No aplica"}
Población / sector: {datos["poblacion"] or "No informado"}
Calle: {datos["calle"] or "No informado"}
Número: {datos["numero"] or "No informado"}

CONTACTO
Nombre: {datos["nombre"]}
WhatsApp: {datos["whatsapp"]}

TRANSFERENCIA
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto sugerido: {formato_pesos(datos["total_paltas"])}

Estado: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
"""


def link_whatsapp(datos: dict) -> str:
    mensaje = f"""Nueva solicitud de pedido de paltas.

Pedido:
• Tipo: {datos["tipo_palta"]}
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(datos["precio_por_kg"])}
• Total paltas: {formato_pesos(datos["total_paltas"])}

Entrega:
• Modalidad: {datos["modalidad_entrega"]}
• Región: {datos["region"] or "No aplica"}
• Comuna: {datos["comuna"] or "No aplica"}
• Población / sector: {datos["poblacion"] or "No informado"}
• Calle: {datos["calle"] or "No informado"}
• Número: {datos["numero"] or "No informado"}

Contacto:
• Nombre: {datos["nombre"]}
• WhatsApp: {datos["whatsapp"]}

Folio: {datos["folio"]}

Quiero coordinar la entrega."""
    return f"https://wa.me/{WHATSAPP_NEGOCIO}?text={quote(mensaje)}"


def datos_actuales() -> dict:
    pedido = session.get("pedido", {})
    return {
        "tipo_palta": pedido.get("tipo_palta", "Hass"),
        "kilos": pedido.get("kilos", KILOS_MINIMOS),
        "precio_kg": pedido.get("precio_kg", PRECIOS_PALTA["Hass"]),
        "total_paltas": pedido.get("total_paltas", PRECIOS_PALTA["Hass"]),
        "modalidad_entrega": pedido.get("modalidad_entrega", "Retiro sin costo"),
        "region": pedido.get("region", "Valparaíso"),
        "comuna": pedido.get("comuna", "La Calera"),
        "poblacion": pedido.get("poblacion", ""),
        "calle": pedido.get("calle", ""),
        "numero": pedido.get("numero", ""),
        "nombre": pedido.get("nombre", ""),
        "whatsapp": pedido.get("whatsapp", ""),
    }


def actualizar_pedido(**kwargs) -> None:
    pedido = session.get("pedido", {})
    pedido.update(kwargs)
    session["pedido"] = pedido


def validar_paso_2(modalidad: str, poblacion: str, calle: str, numero: str) -> list[str]:
    errores = []
    if modalidad != "Retiro sin costo":
        if not poblacion.strip():
            errores.append("Población / sector")
        if not calle.strip():
            errores.append("Calle")
        if not numero.strip():
            errores.append("Número")
    return errores


def construir_datos_finales() -> dict:
    pedido = datos_actuales()
    folio = "PALTA-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    return {
        "folio": folio,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_palta": pedido["tipo_palta"],
        "kilos": pedido["kilos"],
        "precio_por_kg": int(pedido["precio_kg"]),
        "total_paltas": int(pedido["total_paltas"]),
        "modalidad_entrega": pedido["modalidad_entrega"],
        "region": pedido["region"],
        "comuna": pedido["comuna"],
        "poblacion": pedido["poblacion"],
        "calle": pedido["calle"],
        "numero": pedido["numero"],
        "nombre": pedido["nombre"],
        "whatsapp": normalizar_whatsapp(pedido["whatsapp"]),
        "estado": "Solicitud recibida",
    }


# ============================================================
# RUTAS
# ============================================================

@app.route("/", methods=["GET"])
def index():
    paso = int(session.get("paso", 1))
    paso = max(1, min(4, paso))
    session["paso"] = paso

    return render_template(
        "index.html",
        paso=paso,
        datos=datos_actuales(),
        precios=PRECIOS_PALTA,
        localidades=LOCALIDADES_CERCANAS,
        regiones_comunas=REGIONES_COMUNAS,
        formato_pesos=formato_pesos,
        titular=TITULAR,
        rut=RUT,
        banco=BANCO,
        tipo_cuenta=TIPO_CUENTA,
        resultado=session.pop("resultado", None),
        errores=session.pop("errores", []),
    )


@app.route("/paso/1", methods=["POST"])
def paso_1():
    tipo_palta = request.form.get("tipo_palta", "Hass")
    kilos = float(request.form.get("kilos", KILOS_MINIMOS))
    precio_kg = PRECIOS_PALTA[tipo_palta]
    total = calcular_total(tipo_palta, kilos)

    actualizar_pedido(
        tipo_palta=tipo_palta,
        kilos=kilos,
        precio_kg=precio_kg,
        total_paltas=total,
    )
    session["paso"] = 2
    return redirect(url_for("index"))


@app.route("/paso/2", methods=["POST"])
def paso_2():
    modalidad = request.form.get("modalidad_entrega", "Retiro sin costo")
    region = ""
    comuna = ""
    poblacion = request.form.get("poblacion", "").strip()
    calle = request.form.get("calle", "").strip()
    numero = request.form.get("numero", "").strip()

    if modalidad == "Retiro sin costo":
        region = "Valparaíso"
        comuna = request.form.get("comuna_retiro", "La Calera")
        poblacion = calle = numero = ""
    elif modalidad == "Despacho zona cercana":
        region = "Valparaíso"
        comuna = request.form.get("comuna_local", "La Calera")
    else:
        region = request.form.get("region", "Valparaíso")
        comuna = request.form.get("comuna_otra", "La Calera")

    errores = validar_paso_2(modalidad, poblacion, calle, numero)

    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"] = 2
        return redirect(url_for("index"))

    actualizar_pedido(
        modalidad_entrega=modalidad,
        region=region,
        comuna=comuna,
        poblacion=poblacion,
        calle=calle,
        numero=numero,
    )
    session["paso"] = 3
    return redirect(url_for("index"))


@app.route("/paso/3", methods=["POST"])
def paso_3():
    nombre = request.form.get("nombre", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()

    errores = []
    if not nombre:
        errores.append("Nombre")
    if not whatsapp:
        errores.append("WhatsApp")

    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"] = 3
        return redirect(url_for("index"))

    actualizar_pedido(nombre=nombre, whatsapp=whatsapp)
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/registrar", methods=["POST"])
def registrar():
    if request.form.get("confirmar") != "si":
        session["errores"] = ["Confirma que los datos están correctos."]
        session["paso"] = 4
        return redirect(url_for("index"))

    datos = construir_datos_finales()
    google_ok, google_msg = guardar_google_sheets(datos)

    session["resultado"] = {
        "google_ok": google_ok,
        "google_msg": google_msg,
        "whatsapp_url": link_whatsapp(datos),
        "folio": datos["folio"],
        "total": formato_pesos(datos["total_paltas"]),
        "texto": crear_cuerpo_solicitud(datos),
    }
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/volver/<int:paso>", methods=["POST"])
def volver(paso: int):
    session["paso"] = max(1, min(4, paso))
    return redirect(url_for("index"))


@app.route("/nuevo", methods=["POST"])
def nuevo():
    session.clear()
    session["paso"] = 1
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
