# -*- coding: utf-8 -*-
# Genera el PDF del tutorial. Lee el codigo directamente de los archivos del proyecto
# (asi lo que sale en el PDF es igual a lo que esta en el repositorio) y pega las
# capturas que esten en la carpeta "capturas".

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, Preformatted, Table, TableStyle, Flowable,
                                KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

AQUI = os.path.dirname(os.path.abspath(__file__))
PROYECTO = os.path.dirname(AQUI)
CAPTURAS = os.path.join(AQUI, "capturas")
SALIDA = os.path.join(AQUI, "Tutorial_Blazor_RickAndMorty.pdf")

C = "ApiPersonajesRickMorty.Client"
S = "ApiPersonajesRickMorty.Server"
H = "ApiPersonajesRickMorty.Shared"

ANCHO_PAG, ALTO_PAG = letter
MARGEN = 0.9 * inch
ANCHO = ANCHO_PAG - 2 * MARGEN

# ---------- estilos (blanco y negro, simples) ----------
base = ParagraphStyle("base", fontName="Helvetica", fontSize=10.5, leading=14.5, spaceAfter=6)
titulo = ParagraphStyle("titulo", parent=base, fontName="Helvetica-Bold", fontSize=22, leading=27,
                        alignment=TA_CENTER, spaceAfter=10)
subtitulo = ParagraphStyle("subtitulo", parent=base, fontSize=13, leading=18, alignment=TA_CENTER, spaceAfter=6)
centro = ParagraphStyle("centro", parent=base, alignment=TA_CENTER)
h1 = ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=15, leading=19,
                    spaceBefore=6, spaceAfter=8, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                    spaceBefore=8, spaceAfter=4, keepWithNext=1)
pie = ParagraphStyle("pie", parent=base, fontSize=9, leading=12, alignment=TA_CENTER, spaceAfter=10)
vineta = ParagraphStyle("vineta", parent=base, leftIndent=16, bulletIndent=4, spaceAfter=3)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def c(t):
    """texto de codigo dentro de un parrafo"""
    return '<font name="Courier">%s</font>' % esc(t)


def p(t, estilo=base):
    return Paragraph(t, estilo)


def lista(items, numerada=False):
    out = []
    for i, it in enumerate(items, 1):
        out.append(Paragraph(it, vineta, bulletText=("%d." % i) if numerada else "-"))
    out.append(Spacer(1, 4))
    return out


def codigo(texto, tam=None):
    """bloque de codigo con borde simple; se parte en trozos para que no se corte raro entre paginas"""
    lineas = texto.rstrip("\n").split("\n")
    maxlen = max(len(l) for l in lineas)
    ancho_util = ANCHO - 14
    if tam is None:
        tam = min(8.5, ancho_util / (0.6 * max(maxlen, 1)))
    est = ParagraphStyle("cod", fontName="Courier", fontSize=tam, leading=tam + 2.2)
    bloques = []
    TROZO = 42
    for i in range(0, len(lineas), TROZO):
        trozo = "\n".join(lineas[i:i + TROZO])
        t = Table([[Preformatted(trozo, est)]], colWidths=[ANCHO])
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.black),
                               ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        bloques.append(t)
    bloques.append(Spacer(1, 8))
    return bloques


def leer(*ruta):
    with open(os.path.join(PROYECTO, *ruta), encoding="utf-8") as f:
        return f.read()


def archivo(titulo_txt, *ruta, antes=None):
    """titulo del archivo + primer bloque de codigo siempre juntos (y con lo que se pase en "antes")"""
    bloques = codigo(leer(*ruta))
    juntos = list(antes or []) + [p("<b>Archivo:</b> " + c(titulo_txt), base), bloques[0]]
    return [KeepTogether(juntos)] + bloques[1:]


# ---------- capturas ----------
class Captura(Flowable):
    def __init__(self, num, descripcion):
        super().__init__()
        self.num = num
        self.desc = descripcion
        self.ruta = None
        for ext in ("png", "jpg", "jpeg", "PNG", "JPG"):
            r = os.path.join(CAPTURAS, "captura_%d.%s" % (num, ext))
            if os.path.exists(r):
                self.ruta = r
                break

    def wrap(self, w, h):
        self.w = min(w, ANCHO)
        if self.ruta:
            iw, ih = ImageReader(self.ruta).getSize()
            esc_ = min(self.w / iw, (3.9 * inch) / ih)
            self.iw, self.ih = iw * esc_, ih * esc_
            self.h = self.ih + 22
        else:
            self.h = 2.1 * inch
        return self.w, self.h

    def draw(self):
        cv = self.canv
        if self.ruta:
            x = (self.w - self.iw) / 2
            cv.setLineWidth(0.5)
            cv.rect(x, 22, self.iw, self.ih)
            cv.drawImage(self.ruta, x, 22, self.iw, self.ih)
            cv.setFont("Helvetica-Oblique", 9)
            cv.drawCentredString(self.w / 2, 7, "Captura %d: %s" % (self.num, self.desc))
        else:
            cv.setDash(4, 3)
            cv.setLineWidth(0.8)
            cv.rect(0, 0, self.w, self.h)
            cv.setDash()
            cv.setFont("Helvetica-Bold", 11)
            cv.drawCentredString(self.w / 2, self.h / 2 + 8, "AQUI VA LA CAPTURA %d" % self.num)
            cv.setFont("Helvetica", 9)
            cv.drawCentredString(self.w / 2, self.h / 2 - 8, self.desc)
            cv.drawCentredString(self.w / 2, self.h / 2 - 22, "(archivo capturas/captura_%d.png)" % self.num)


def captura(num, desc):
    return [Captura(num, desc), Spacer(1, 8)]


# ---------- diagrama ----------
def flecha(d, x1, x2, y, num):
    d.add(Line(x1, y, x2, y, strokeWidth=1))
    sentido = 1 if x2 > x1 else -1
    d.add(Polygon([x2, y, x2 - 7 * sentido, y + 3.5, x2 - 7 * sentido, y - 3.5], fillColor=colors.black))
    xm = (x1 + x2) / 2
    d.add(Rect(xm - 7, y + 4, 14, 12, strokeWidth=0.8, fillColor=colors.white))
    d.add(String(xm, y + 7, str(num), fontName="Helvetica-Bold", fontSize=9, textAnchor="middle"))


def caja(d, x, y, w, h, lineas, dash=None):
    r = Rect(x, y, w, h, strokeWidth=1, fillColor=colors.white)
    if dash:
        r.strokeDashArray = dash
    d.add(r)
    yy = y + h - 15
    for i, l in enumerate(lineas):
        d.add(String(x + w / 2, yy, l, fontName="Helvetica-Bold" if i == 0 else "Helvetica",
                     fontSize=9 if i == 0 else 8, textAnchor="middle"))
        yy -= 12


def diagrama():
    d = Drawing(ANCHO, 190)
    w = 135
    xa, xb, xc = 0, (ANCHO - w) / 2, ANCHO - w
    caja(d, xa, 80, w, 95, ["NAVEGADOR", "Cliente Blazor", "WebAssembly", "(Index.razor)"])
    caja(d, xb, 80, w, 95, ["NUESTRO SERVIDOR", "ASP.NET Core", "PersonajesController", "api/personajes"])
    caja(d, xc, 80, w, 95, ["API EXTERNA", "Rick and Morty", "rickandmortyapi.com", "/api/character"])
    flecha(d, xa + w, xb, 145, 1)
    flecha(d, xb + w, xc, 145, 2)
    flecha(d, xc, xb + w, 108, 3)
    flecha(d, xb, xa + w, 108, 4)
    caja(d, xa, 5, xb + w - xa, 42, ["SHARED (clases compartidas)",
                                      "Character, Origin, Location, Characters, Info"], dash=[3, 2])
    d.add(Line(xa + w / 2, 80, xa + w / 2, 47, strokeWidth=0.8, strokeDashArray=[3, 2]))
    d.add(Line(xb + w / 2, 80, xb + w / 2, 47, strokeWidth=0.8, strokeDashArray=[3, 2]))
    return d


# ---------- pie de pagina ----------
def pie_pagina(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 8.5)
    canv.drawCentredString(ANCHO_PAG / 2, 0.5 * inch,
                           "Tutorial Blazor WebAssembly + API de Rick and Morty - pagina %d" % doc.page)
    canv.restoreState()


def portada_pie(canv, doc):
    pass


# =====================================================================
#  CONTENIDO
# =====================================================================
E = []

# ----- portada -----
E += [Spacer(1, 1.6 * inch),
      p("Tutorial: aplicación web con Blazor WebAssembly que consume la API de Rick and Morty", titulo),
      Spacer(1, 6),
      p("Cliente y servidor con ASP.NET Core (modelo MVC)", subtitulo),
      Spacer(1, 1.1 * inch),
      p("Nombre: ______________________________________", centro),
      p("Corporación Universitaria Americana - Ingeniería de Sistemas", centro),
      p("Trabajo individual", centro),
      p("Octubre de 2026", centro),
      Spacer(1, 0.5 * inch),
      p("Repositorio del código: ______________________________________", centro),
      p("(pegar aquí el enlace de GitHub, GitLab o Bitbucket)", pie),
      PageBreak()]

# ----- contenido -----
E += [p("Contenido", h1)]
E += lista(["Parte 1. Qué vamos a hacer",
            "Parte 2. Cómo funciona la aplicación (idea general)",
            "Parte 3. Probar la API antes de programar",
            "Parte 4. Crear la solución y los tres proyectos",
            "Parte 5. Los modelos (proyecto Shared)",
            "Parte 6. El controlador (proyecto Server)",
            "Parte 7. Program.cs del servidor",
            "Parte 8. El cliente Blazor (proyecto Client)",
            "Parte 9. Ejecutar y probar",
            "Parte 10. Subir el código a GitHub",
            "Parte 11. Problemas que pueden salir",
            "Conclusión"])

# ----- Parte 1 -----
E += [p("Parte 1. Qué vamos a hacer", h1),
      p("En este trabajo se hace una aplicación web que muestra los personajes de la serie Rick and Morty. "
        "Los datos salen de una API pública que está en https://rickandmortyapi.com/. La pantalla muestra una "
        "tarjeta por personaje (foto, nombre, estado, especie, género, origen y cantidad de episodios) y tiene "
        "los botones Anterior y Siguiente, porque la API entrega los personajes por páginas."),
      p("Lo que se usa:", base)]
E += lista(["Visual Studio y el lenguaje C#.",
            "NET 10 (es la versión LTS actual).",
            "Blazor WebAssembly: el cliente, que corre dentro del navegador.",
            "ASP.NET Core con un controlador (modelo vista controlador): el servidor.",
            "HttpClient para pedir datos a la API y System.Text.Json para convertir el JSON a objetos C#."])
E += [p("Una aclaración sobre el video", h2),
      p("En el video se usó .NET 7 y la casilla " + c("ASP.NET Core Hosted") + " al crear el proyecto. "
        "Esa plantilla ya no existe desde .NET 8, pero según la documentación de Microsoft las soluciones "
        "hospedadas siguen funcionando. Por eso aquí se crean los tres proyectos (Client, Server y Shared) "
        "uno por uno. El resultado es el mismo que en el video: un cliente, un servidor y una carpeta de "
        "modelos compartidos.")]

# ----- Parte 2 -----
E += [KeepTogether([p("Parte 2. Cómo funciona la aplicación (idea general)", h1),
      p("La aplicación tiene tres proyectos dentro de una misma solución y además usa la API externa:"),
      Spacer(1, 4), diagrama()]), Spacer(1, 6),
      p("Lo que pasa cuando se abre la página, siguiendo los números del dibujo:")]
E += lista([
    "El navegador descarga el cliente Blazor y lo ejecuta. La página " + c("Index.razor") +
    " pide los personajes a nuestro servidor: " + c("GET api/personajes?page=1") + ".",
    "El controlador " + c("PersonajesController") + " llama a la API de Rick and Morty: " +
    c("GET https://rickandmortyapi.com/api/character?page=1") + ".",
    "La API externa responde con un JSON.",
    "El controlador convierte ese JSON a objetos " + c("Characters") + " y se los devuelve al cliente, que los "
    "convierte otra vez a objetos y dibuja las tarjetas."], numerada=True)
E += [p("¿Por qué el cliente no llama directo a la API de Rick and Morty? Porque en este ejercicio se trabaja "
        "con cliente y servidor: el cliente solo conoce nuestra API (" + c("api/personajes") + ") y el servidor es el "
        "que habla con la API externa. Si algún día cambia la API externa, solo se cambia el servidor."),
      p("El proyecto Shared tiene las clases que usan los dos lados (cliente y servidor), así no se escriben dos veces.")]

# ----- Parte 3 -----
E += [PageBreak(), p("Parte 3. Probar la API antes de programar", h1),
      p("Antes de escribir código hay que saber cómo responde la API. Para eso se usa Postman (también sirve el "
        "navegador):")]
E += lista(["En la documentación de la API se busca el endpoint " + c("Get all characters") +
            ". Dice que es una petición GET a " + c("https://rickandmortyapi.com/api/character") + ".",
            "En Postman se crea una petición GET con esa URL y se da clic en Send.",
            "La respuesta es un JSON con dos partes: " + c("info") + " y " + c("results") + "."],
           numerada=True)
E += captura(1, "Respuesta de la API en Postman o en el navegador")
E += [p("Un ejemplo resumido de la respuesta (los datos reales pueden cambiar):"),
      ] + codigo('''{
  "info": {
    "count": 826,
    "pages": 42,
    "next": "https://rickandmortyapi.com/api/character/?page=2",
    "prev": null
  },
  "results": [
    {
      "id": 1,
      "name": "Rick Sanchez",
      "status": "Alive",
      "species": "Human",
      "type": "",
      "gender": "Male",
      "origin":   { "name": "Earth (C-137)", "url": "https://rickandmortyapi.com/api/location/1" },
      "location": { "name": "Citadel of Ricks", "url": "https://rickandmortyapi.com/api/location/3" },
      "image": "https://rickandmortyapi.com/api/character/avatar/1.jpeg",
      "episode": [ "https://rickandmortyapi.com/api/episode/1", "..." ],
      "url": "https://rickandmortyapi.com/api/character/1",
      "created": "2017-11-04T18:48:46.250Z"
    }
  ]
}''')
E += [p("Lo importante de este JSON:")]
E += lista([
    c("info") + " trae el total de personajes (" + c("count") + "), el total de páginas (" + c("pages") + ") y los "
    "enlaces a la página siguiente y a la anterior. En la primera página " + c("prev") + " es " + c("null") + ".",
    c("results") + " es la lista de personajes de esa página (la API entrega 20 por página).",
    c("origin") + " y " + c("location") + " son objetos dentro del personaje, y " + c("episode") +
    " es una lista de textos."])

# ----- Parte 4 -----
E += [PageBreak(), p("Parte 4. Crear la solución y los tres proyectos", h1),
      p("Se crea una sola solución llamada " + c("ApiPersonajesRickMorty") + " con estos proyectos:")]
t = Table([["Proyecto", "Tipo", "Para qué sirve"],
           [C, "Blazor WebAssembly", "La pantalla (cliente)"],
           [S, "ASP.NET Core vacío", "Controlador y servidor"],
           [H, "Biblioteca de clases", "Modelos compartidos"]],
          colWidths=[2.6 * inch, 1.7 * inch, ANCHO - 4.3 * inch])
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                       ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                       ("FONTNAME", (0, 1), (0, -1), "Courier"),
                       ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                       ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
E += [t, Spacer(1, 8), p("Pasos en Visual Studio:", base)]
E += lista([
    "Abrir Visual Studio y dar clic en <b>Crear un proyecto nuevo</b>. Buscar la plantilla <b>Blazor WebAssembly "
    "Standalone App</b> (Aplicación independiente de Blazor WebAssembly) y dar Siguiente.",
    "Nombre del proyecto: " + c(C) + ". Nombre de la solución: " + c("ApiPersonajesRickMorty") +
    ". Dejar sin marcar la casilla de poner la solución y el proyecto en el mismo directorio. Framework: .NET 10. "
    "Autenticación: ninguna. Clic en Crear.",
    "En el Explorador de soluciones, clic derecho sobre la solución > Agregar > Nuevo proyecto > "
    "<b>Biblioteca de clases</b> (C#). Nombre: " + c(H) + ".",
    "Otra vez clic derecho sobre la solución > Agregar > Nuevo proyecto > <b>ASP.NET Core vacío</b>. Nombre: " +
    c(S) + ".",
    "En el proyecto Server: clic derecho en Dependencias > Administrar paquetes NuGet > instalar " +
    c("Microsoft.AspNetCore.Components.WebAssembly.Server") + " (versión 10.x).",
    "Agregar las referencias entre proyectos (clic derecho en Dependencias > Agregar referencia de proyecto): "
    "Server referencia a Client y a Shared; Client referencia a Shared.",
    "Clic derecho en el proyecto Server > <b>Establecer como proyecto de inicio</b>. Es importante: el que arranca "
    "tiene que ser el servidor, porque él entrega la página del cliente y tiene el controlador.",
    "En el proyecto Client se borran los archivos de ejemplo de la plantilla: " + c("Pages/Home.razor") + ", " +
    c("Pages/Counter.razor") + " y " + c("Pages/Weather.razor") + ". Si se deja Home.razor hay dos páginas con la "
    "ruta " + c("/") + " y da error."], numerada=True)
E += captura(2, "Explorador de soluciones con los tres proyectos")
E += [p("Los archivos del proyecto Server y del Client que se muestran en las siguientes partes reemplazan a los "
        "que crea la plantilla. Si quieres, el proyecto completo también se puede abrir directamente desde el "
        "repositorio con el archivo " + c("ApiPersonajesRickMorty.sln") + ".")]

# ----- Parte 5 -----
E += [PageBreak(), p("Parte 5. Los modelos (proyecto Shared)", h1),
      p("Los modelos son clases de C# que tienen la misma forma que el JSON. Gracias a eso, .NET puede convertir "
        "(deserializar) el texto JSON a objetos sin que uno lo haga a mano. Para no escribir todo a mano, en el "
        "video se copia el JSON de ejemplo en una página que genera las clases (por ejemplo json2csharp.com), y "
        "después se corrigen los nombres. Aquí quedaron así, dentro de la carpeta " + c("Models") + ":"),
      ]
E += archivo("ApiPersonajesRickMorty.Shared/Models/Character.cs", H, "Models", "Character.cs")
E += [p("Explicación:", h2)]
E += lista([
    c("Character") + " tiene un atributo por cada dato del personaje (id, name, status, species, etc.).",
    c("Origin") + " y " + c("Location") + " son clases aparte porque en el JSON son objetos dentro del personaje.",
    c('[JsonPropertyName("name")]') + " le dice a .NET con qué nombre viene el dato en el JSON. Así la propiedad "
    "de C# puede empezar con mayúscula (" + c("Name") + ") y igual se llena bien. Esto es lo que se explica en el "
    "video con " + c("JsonPropertyName") + ".",
    "Las propiedades de texto empiezan con " + c("= string.Empty") + " y las listas con " + c("new List<string>()") +
    " para que nunca queden en null.",
    c("Episode") + " es una " + c("List<string>") + " con las URL de los episodios. En la pantalla solo se muestra "
    "cuántos son (" + c("Episode.Count") + ")."])
E += archivo("ApiPersonajesRickMorty.Shared/Models/Characters.cs", H, "Models", "Characters.cs")
E += [p("Explicación:", h2)]
E += lista([
    c("Characters") + " (en plural) es la respuesta completa de la API: un objeto " + c("Info") + " y una lista " +
    c("Results") + " de " + c("Character") + ". Es la clase que se usa para deserializar.",
    c("Info") + " tiene los datos de la paginación. " + c("Next") + " y " + c("Prev") + " son " + c("string?") +
    " (pueden ser null) porque, por ejemplo, en la primera página no hay página anterior y la API manda null. "
    "En el video pasa lo mismo: al venir null no se sabe el tipo y hay que ponerlo como string."])

# ----- Parte 6 -----
E += [PageBreak(), p("Parte 6. El controlador (proyecto Server)", h1),
      p("El controlador es la parte del servidor que recibe la petición del cliente. Se crea en la carpeta " +
        c("Controllers") + " del proyecto Server (clic derecho > Agregar > Clase, o un controlador vacío como en el "
        "video) y queda así:")]
E += archivo("ApiPersonajesRickMorty.Server/Controllers/PersonajesController.cs", S, "Controllers",
             "PersonajesController.cs")
E += [p("Explicación paso a paso:", h2)]
E += lista([
    c("[ApiController]") + " indica que la clase es un controlador de API.",
    c('[Route("api/[controller]")]') + ": " + c("[controller]") + " se cambia por el nombre de la clase sin la palabra "
    "Controller. Como la clase se llama " + c("PersonajesController") + ", la ruta queda " + c("api/personajes") + ".",
    "En el constructor se recibe " + c("IHttpClientFactory") + " (la fábrica de HttpClient). Con " +
    c('CreateClient("RickAndMorty")') + " se obtiene el cliente que se configuró en Program.cs con la dirección base " +
    "de la API externa.",
    c("[HttpGet]") + " hace que el método responda a peticiones GET. El parámetro " + c("page") + " se lee de la URL " +
    "(" + c("api/personajes?page=2") + ") y si no viene vale 1.",
    "Si " + c("page") + " es menor que 1 se deja en 1, para no pedir páginas que no existen.",
    c("_http.GetAsync($\"character?page={page}\")") + " llama a la API externa. Se junta con la dirección base y "
    "queda " + c("https://rickandmortyapi.com/api/character?page=2") + ".",
    "Si la respuesta no fue exitosa (por ejemplo, 404 cuando la página no existe) el controlador devuelve ese mismo "
    "código con un mensaje.",
    c("ReadFromJsonAsync<Characters>()") + " convierte el JSON a un objeto " + c("Characters") + ", y " + c("Ok(datos)") +
    " lo devuelve al cliente con código 200 (ASP.NET lo vuelve a convertir a JSON).",
    "El " + c("try / catch") + " atrapa el error cuando no hay conexión con la API externa y responde 502."])

# ----- Parte 7 -----
E += archivo("ApiPersonajesRickMorty.Server/Program.cs", S, "Program.cs", antes=[
      p("Parte 7. Program.cs del servidor", h1),
      p("Este archivo arma y configura el servidor. Se reemplaza todo el contenido del " + c("Program.cs") +
        " del proyecto Server por esto:")])
E += [p("Explicación:", h2)]
E += lista([
    c("AddControllers()") + " activa los controladores. Sin esto no existe " + c("api/personajes") + ".",
    c('AddHttpClient("RickAndMorty", ...)') + " registra un HttpClient con nombre y le pone la dirección base " +
    c("https://rickandmortyapi.com/api/") + ". Es el que usa el controlador.",
    c("UseWebAssemblyDebugging()") + " permite depurar el cliente Blazor desde Visual Studio (solo en desarrollo).",
    c("UseHttpsRedirection()") + " manda las peticiones http a https.",
    c("UseBlazorFrameworkFiles()") + " y " + c("UseStaticFiles()") + " hacen que el servidor entregue los archivos del "
    "cliente Blazor WebAssembly (la carpeta " + c("_framework") + ", el index.html, el css).",
    c("MapControllers()") + " conecta las rutas de los controladores.",
    c('MapFallbackToFile("index.html")') + ": cualquier ruta que no sea de la API devuelve el index.html del cliente."])
E += [p("En la carpeta Properties del Server queda el archivo " + c("launchSettings.json") + ", que define con qué "
        "dirección arranca la aplicación (en este proyecto " + c("https://localhost:7100") + " y " +
        c("http://localhost:5100") + ").")]

# ----- Parte 8 -----
E += [p("Parte 8. El cliente Blazor (proyecto Client)", h1),
      p("Aquí está todo lo que se ve en el navegador. Se explican los archivos en el orden en que se cargan.")]
E += archivo("ApiPersonajesRickMorty.Client/wwwroot/index.html", C, "wwwroot", "index.html", antes=[
      p("8.1 wwwroot/index.html", h2),
      p("Es la única página HTML real. Blazor dibuja todo dentro del " + c('<div id="app">') + ".")])
E += lista([
    c('<base href="/" />') + " define la ruta base para que Blazor navegue bien.",
    c('<div id="app">') + " es el lugar donde se pinta la aplicación (mientras carga dice Cargando...).",
    c("_framework/blazor.webassembly.js") + " es el script de Blazor: descarga el runtime de .NET en WebAssembly y "
    "arranca la aplicación.",
    c("blazor-error-ui") + " es un aviso que solo se ve si ocurre un error inesperado."])
E += archivo("ApiPersonajesRickMorty.Client/Program.cs", C, "Program.cs", antes=[p("8.2 Program.cs del cliente", h2)])
E += lista([
    c("RootComponents.Add<App>(\"#app\")") + " le dice a Blazor que el componente " + c("App") + " va dentro del " +
    c("#app") + " del index.html.",
    c("HeadOutlet") + " permite cambiar el título de la página desde los componentes (el " + c("<PageTitle>") + ").",
    c("AddScoped(sp => new HttpClient {...})") + " registra el HttpClient del cliente. Su " + c("BaseAddress") +
    " es la dirección de donde se cargó la página, o sea, nuestro servidor. Por eso en Index.razor se puede "
    "escribir solo " + c("api/personajes") + "."])
E += archivo("ApiPersonajesRickMorty.Client/_Imports.razor", C, "_Imports.razor",
             antes=[p("8.3 _Imports.razor, App.razor y MainLayout.razor", h2)])
E += [p("En " + c("_Imports.razor") + " están los " + c("@using") + " que valen para todos los componentes. El último "
        "(" + c("ApiPersonajesRickMorty.Shared.Models") + ") es el que permite usar " + c("Characters") + " y " +
        c("Character") + " en las páginas sin escribir el namespace completo.")]
E += archivo("ApiPersonajesRickMorty.Client/App.razor", C, "App.razor")
E += [p("En " + c("App.razor") + " está el " + c("Router") + ": mira la URL del navegador, busca la página que tenga "
        "ese " + c("@page") + " y la muestra usando el diseño " + c("MainLayout") + ".")]
E += archivo("ApiPersonajesRickMorty.Client/Layout/MainLayout.razor", C, "Layout", "MainLayout.razor")
E += [p("En " + c("MainLayout.razor") + " está el diseño que se repite en todas las páginas (encabezado y pie). "
        "El " + c("@Body") + " es el lugar donde Blazor mete el contenido de cada página.")]

E += archivo("ApiPersonajesRickMorty.Client/Pages/Index.razor", C, "Pages", "Index.razor", antes=[
      p("8.4 Pages/Index.razor (la pantalla principal)", h2),
      p("Este es el archivo más importante del cliente. Tiene dos partes: arriba el HTML con código de Razor, y "
        "abajo, dentro de " + c("@code") + ", la lógica en C#.")])
E += [p("Explicación de la parte de arriba (lo que se dibuja):", h2)]
E += lista([
    c('@page "/"') + " hace que esta página sea la principal (la ruta " + c("/") + ").",
    c("@inject HttpClient Http") + " pide el HttpClient que se registró en Program.cs.",
    c("@if (cargando)") + " muestra el texto Cargando... mientras llega la respuesta.",
    c("@if (error != null)") + " muestra el mensaje de error si algo falló.",
    c("@if (!cargando && datos != null)") + " muestra la lista solo cuando ya hay datos. Ahí se escribe el total de "
    "personajes (" + c("datos.Info.Count") + ") y la página actual.",
    c("@foreach") + " recorre " + c("datos.Results") + " y por cada personaje dibuja una tarjeta con la imagen y sus datos.",
    "Los dos botones usan " + c("@onclick") + " para llamar a un método de C#. El atributo " +
    c('disabled="@(datos.Info.Prev == null)"') + " deshabilita el botón Anterior cuando no hay página anterior; "
    "con Siguiente es igual pero con " + c("Next") + "."])
E += [p("Explicación de la parte de abajo (@code):", h2)]
E += lista([
    "Las variables " + c("datos") + ", " + c("paginaActual") + ", " + c("cargando") + " y " + c("error") +
    " guardan el estado de la pantalla. Cuando cambian, Blazor vuelve a dibujar lo que haga falta.",
    c("OnInitializedAsync()") + " es un método del ciclo de vida de los componentes: se ejecuta una vez cuando "
    "la página se abre. Aquí carga la página 1.",
    c("CargarPagina(int pagina)") + " pone " + c("cargando = true") + ", llama a nuestro servidor con " +
    c("Http.GetFromJsonAsync<Characters>($\"api/personajes?page={pagina}\")") + " (hace el GET y convierte el JSON a "
    "Characters en un solo paso) y guarda el resultado en " + c("datos") + ".",
    "Si el servidor responde con error, el " + c("catch") + " guarda un mensaje en " + c("error") +
    " y la página en la que estaba no cambia.",
    c("PaginaAnterior()") + " y " + c("PaginaSiguiente()") + " solo llaman a " + c("CargarPagina") +
    " con la página de antes o la de después."])
E += [p("8.5 CSS", h2),
      p("Los estilos están en " + c("wwwroot/css/app.css") + ". Lo principal es que la lista de tarjetas usa una "
        "cuadrícula que se acomoda sola según el ancho de la pantalla:")]
E += codigo(""".lista {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
}""")
E += [p("El resto del archivo (colores, bordes de las tarjetas, botones) está completo en el repositorio.")]

# ----- Parte 9 -----
E += [PageBreak(), p("Parte 9. Ejecutar y probar", h1)]
E += lista([
    "Guardar todo (Ctrl + Shift + S) y comprobar que el proyecto de inicio es " + c(S) + ".",
    "Presionar <b>F5</b> (o el botón de ejecutar con https). Se abre el navegador en " + c("https://localhost:7100") +
    ". La primera vez tarda un poco porque descarga el runtime de .NET.",
    "Se debe ver la lista de personajes con el título y el total (826 personajes, 42 páginas en el momento de "
    "escribir esto). En la página 1 el botón Anterior está deshabilitado."], numerada=True)
E += captura(3, "La aplicación en la página 1")
E += [p("Después se da clic en Siguiente: carga la página 2 y los dos botones quedan activos.")]
E += captura(4, "La aplicación en la página 2")
E += [p("Probar solo el servidor", h2),
      p("El controlador también se puede probar sin el cliente, escribiendo en el navegador la dirección " +
        c("https://localhost:7100/api/personajes?page=2") + ". Debe aparecer el JSON que el servidor sacó de la API "
        "externa (el mismo formato de la Parte 3, la página 2).")]
E += captura(5, "JSON devuelto por nuestro servidor en api/personajes?page=2")
E += [p("Ver la petición desde el navegador", h2),
      p("Con F12 se abre la herramienta de desarrollo. En la pestaña Red (Network) se recarga la página y se ve la "
        "petición " + c("personajes?page=1") + ": el cliente le pidió los datos a nuestro servidor (paso 1 del dibujo "
        "de la Parte 2), no a la API externa.")]
E += captura(6, "Pestaña Red (F12) con la petición api/personajes")

# ----- Parte 10 -----
E += [p("Parte 10. Subir el código a GitHub", h1),
      p("La entrega pide el código en un repositorio. Con GitHub:")]
E += lista([
    "En github.com se crea un repositorio nuevo llamado " + c("ApiPersonajesRickMorty") + " (vacío: sin README ni .gitignore).",
    "En una terminal, dentro de la carpeta de la solución, se ejecutan estos comandos (cambiando TU_USUARIO):"],
    numerada=True)
E += codigo("""git init
git add .
git commit -m "Primera version de la app de Rick y Morty"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ApiPersonajesRickMorty.git
git push -u origin main""")
E += lista(["El archivo " + c(".gitignore") + " ya viene en el proyecto, por eso no se suben las carpetas " +
            c("bin") + " y " + c("obj") + ".",
            "Al final se actualiza la página del repositorio y se ven los tres proyectos."])
E += captura(7, "Repositorio en GitHub con los archivos subidos")

# ----- Parte 11 -----
E += [p("Parte 11. Problemas que pueden salir", h1)]
E += lista([
    "<b>Sale una página en blanco o no existe api/personajes:</b> casi siempre es porque el proyecto de inicio es "
    "el Client y no el Server. Se cambia con clic derecho en Server > Establecer como proyecto de inicio.",
    "<b>Error de versión del SDK:</b> los proyectos están en " + c("net10.0") + ". Con " + c("dotnet --list-sdks") +
    " se ve qué versión hay instalada. Si es otra, se cambia " + c("TargetFramework") + " en los tres " + c(".csproj") +
    " y la versión de los paquetes " + c("Microsoft.AspNetCore.Components.WebAssembly*") + ".",
    "<b>Error de ruta duplicada:</b> se dejó el " + c("Home.razor") + " de la plantilla junto con " + c("Index.razor") +
    ". Hay que borrar Home.razor.",
    "<b>Aparece el mensaje de error en la pantalla:</b> el servidor no pudo traer los datos (sin internet o la API "
    "no respondió). Se revisa la conexión y se vuelve a dar clic en el botón.",
    "<b>Error 404 en una página:</b> la API de Rick and Morty responde 404 si se pide una página que no existe (mayor "
    "que el total). Con los botones normales no pasa."])

# ----- Conclusión -----
E += [p("Conclusión", h1),
      p("Con este ejercicio se vio cómo se comunican las tres partes de una aplicación Blazor WebAssembly: el cliente "
        "(que corre en el navegador), el servidor (que tiene el controlador) y los modelos compartidos. También se vio "
        "cómo consumir una API externa con HttpClient, cómo convertir el JSON a objetos de C# y cómo mostrar los "
        "datos con paginación usando Razor. La parte que más ayudó a entender todo fue probar primero la API en "
        "Postman, porque así ya se sabía la forma exacta del JSON antes de crear las clases.")]


# ---------- armar el documento ----------
doc = BaseDocTemplate(SALIDA, pagesize=letter, leftMargin=MARGEN, rightMargin=MARGEN,
                      topMargin=0.85 * inch, bottomMargin=0.9 * inch,
                      title="Tutorial Blazor WebAssembly - API Rick and Morty",
                      author="")
marco = Frame(MARGEN, 0.9 * inch, ANCHO, ALTO_PAG - 0.85 * inch - 0.9 * inch, id="normal",
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="todas", frames=[marco], onPage=pie_pagina)])
doc.build(E)

faltan = [n for n in range(1, 8) if not any(os.path.exists(os.path.join(CAPTURAS, "captura_%d.%s" % (n, e)))
                                              for e in ("png", "jpg", "jpeg", "PNG", "JPG"))]
print("PDF creado:", SALIDA)
if faltan:
    print("Faltan las capturas:", ", ".join("captura_%d" % n for n in faltan))
