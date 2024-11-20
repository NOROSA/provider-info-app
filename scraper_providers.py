import requests
from bs4 import BeautifulSoup
import spacy
from datetime import datetime, timedelta
import subprocess
import time
from transformers import pipeline


# Intenta cargar el modelo de idioma

# Cargar el modelo
nlp = spacy.load("./es_core_news_md")


# Claves de API
GNEWS_API_KEY = "fced21e37c55c04a7f927c1ee3d995f1"
MEDIASTACK_API_KEY = "36e342f19ea0d1bae2e7e85478d43491"

# Funciones de búsqueda en Google, GNews y Mediastack
def buscar_noticias_google(nombre_proveedor, meses_atras=12, max_paginas=3):
    noticias = []
    fecha_inicio = (datetime.now() - timedelta(days=meses_atras * 30)).strftime("%Y-%m-%d")
    for pagina in range(max_paginas):
        start = pagina * 10
        query = (
            f"{nombre_proveedor} problemas OR riesgos OR fraude OR demanda OR juicio OR multa "
            f"OR sanción OR quiebra OR reputación OR operación OR disrupción "
            f"after:{fecha_inicio}"
        )
        url = f"https://www.google.com/search?q={query}&start={start}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error en Google Search: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.find_all("div", class_="tF2Cxc"):
            titulo = item.find("h3").get_text() if item.find("h3") else "Sin título"
            enlace = item.find("a")["href"] if item.find("a") else "Sin enlace"
            descripcion = item.find("span", class_="aCOpRe").get_text() if item.find("span", class_="aCOpRe") else "Sin descripción"
            noticias.append({"titulo": titulo, "enlace": enlace, "descripcion": descripcion})

        time.sleep(2)
    return noticias

def buscar_noticias_gnews(nombre_proveedor, meses_atras=12, max_resultados=50):
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=meses_atras * 30)
    from_date = fecha_inicio.strftime("%Y-%m-%d")
    to_date = fecha_fin.strftime("%Y-%m-%d")

    url = (
        f"https://gnews.io/api/v4/search?q={nombre_proveedor} "
        f"AND (problemas OR riesgos OR fraude OR demanda OR juicio OR multa OR sanción OR quiebra OR reputación "
        f"OR operación OR disrupción)&from={from_date}&to={to_date}&lang=es&country=all&max={max_resultados}&token={GNEWS_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        noticias = []
        for article in data.get("articles", []):
            noticias.append({
                "titulo": article.get("title", "Sin título"),
                "enlace": article.get("url", "Sin enlace"),
                "descripcion": article.get("description", "Sin descripción")
            })
        return noticias
    else:
        print(f"Error en GNews: {response.status_code}")
        return []

def buscar_noticias_mediastack(nombre_proveedor, meses_atras=12, max_resultados=50):
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=meses_atras * 30)
    from_date = fecha_inicio.strftime("%Y-%m-%d")
    to_date = fecha_fin.strftime("%Y-%m-%d")

    url = (
        f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}"
        f"&keywords={nombre_proveedor} AND (problemas OR riesgos OR fraude OR demanda OR juicio OR multa OR sanción OR quiebra OR reputación OR operación OR disrupción)"
        f"&languages=es"
        f"&date={from_date},{to_date}"
        f"&limit={max_resultados}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        noticias = []
        for article in data.get("data", []):
            noticias.append({
                "titulo": article.get("title", "Sin título"),
                "enlace": article.get("url", "Sin enlace"),
                "descripcion": article.get("description", "Sin descripción")
            })
        return noticias
    else:
        print(f"Error en Mediastack: {response.status_code}")
        return []

# Función para analizar riesgos
def analizar_riesgos(texto):
    doc = nlp(texto)
    palabras_clave = [
        "fraude", "riesgo", "problema", "quiebra", "investigación", "conflicto",
        "sanción", "demanda", "juicio", "multa", "disrupción", "interrupción",
        "fallo", "penalización", "multas", "reputación", "tributario", "evasión",
        "suspensión", "paralización", "deuda", "morosidad", "incumplimiento",
        "hackeo", "filtración", "estafa", "corrupción", "soborno", "incidente", "bancarrota"
    ]
    riesgos = [token.text for token in doc if token.text.lower() in palabras_clave]
    return riesgos

def evaluar_riesgos(noticia):
    texto_analizar = f"{noticia['titulo']} {noticia['descripcion']}"
    riesgos_detectados = analizar_riesgos(texto_analizar)
    severidad = len(riesgos_detectados)
    return {
        "titulo": noticia["titulo"],
        "enlace": noticia["enlace"],
        "descripcion": noticia["descripcion"],
        "riesgos": riesgos_detectados,
        "severidad": severidad
    }

def filtrar_duplicados(noticias):
    enlaces_vistos = set()
    noticias_unicas = []
    for noticia in noticias:
        if noticia["enlace"] not in enlaces_vistos:
            enlaces_vistos.add(noticia["enlace"])
            noticias_unicas.append(noticia)
    return noticias_unicas

def buscar_y_analizar(nombre_proveedor, meses_atras=12, max_paginas=3):
    if not nombre_proveedor:
        print("Debe proporcionar un nombre de proveedor")
        return []

    noticias_google = buscar_noticias_google(nombre_proveedor, meses_atras=meses_atras, max_paginas=max_paginas)
    noticias_gnews = buscar_noticias_gnews(nombre_proveedor, meses_atras=meses_atras)
    noticias_mediastack = buscar_noticias_mediastack(nombre_proveedor, meses_atras=meses_atras)

    todas_noticias = filtrar_duplicados(noticias_google + noticias_gnews + noticias_mediastack)

    # Analiza las noticias con Hugging Face
    resultados = analizar_riesgos_con_huggingface(todas_noticias)
    return resultados


def analizar_riesgos_con_huggingface(noticias):
    # Carga el pipeline de Hugging Face con un modelo ligero

    classifier = pipeline("text-classification", model="distilbert-base-multilingual-cased", tokenizer="distilbert-base-multilingual-cased")
    # Descargado
    # classifier = pipeline("text-classification", model="./models/distilbert", tokenizer="./models/distilbert")

    resultados = []
    for noticia in noticias:
        texto = f"{noticia['titulo']} {noticia['descripcion']}"
        
        # Clasifica el texto como positivo o negativo
        clasificacion = classifier(texto, truncation=True, max_length=512)
        etiqueta = clasificacion[0]['label']
        puntuacion = clasificacion[0]['score']
        
        # Determina el nivel de riesgo en función de la etiqueta
        riesgo = 5 if etiqueta == "NEGATIVE" and puntuacion > 0.8 else 3 if etiqueta == "NEGATIVE" else 1

        resultados.append({
            "titulo": noticia["titulo"],
            "descripcion": noticia["descripcion"],
            "riesgo": riesgo
        })
    return resultados


if __name__ == "__main__":
    nombre_proveedor = input("Ingrese el nombre del proveedor: ")
    meses = int(input("Ingrese la cantidad de meses a analizar (por defecto 12): ") or 12)
    buscar_y_analizar(nombre_proveedor, meses_atras=meses)