import sys
print("Python executable in use:", sys.executable, file=sys.stderr)


# server.py
from mcp.server.fastmcp import FastMCP
import yfinance as yf
from datetime import datetime

# Crear el servidor MCP
mcp = FastMCP("Mercado Bursatil Argentino Real")

# Herramienta: obtener resumen completo de una acción
@mcp.tool()
def resumen_accion(ticker: str) -> dict:
    """
    Devuelve un resumen completo de una acción cotizada en Yahoo Finance.
    Ejemplos: YPFD.BA, GGAL.BA
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        historial = stock.history(period="1d")
        
        if historial.empty:
            return {"error": "No se encontró información histórica para el ticker proporcionado."}

        precio_actual = historial["Close"].iloc[-1]
        apertura = historial["Open"].iloc[-1]
        variacion_pct = ((precio_actual - apertura) / apertura) * 100

        resumen = {
            "empresa": info.get("longName", "Nombre no disponible"),
            "ticker": ticker.upper(),
            "precio_actual": round(precio_actual, 2),
            "variacion_pct": round(variacion_pct, 2),
            "volumen": info.get("volume", "No disponible"),
            "moneda": info.get("currency", "No disponible"),
            "mercado": info.get("exchange", "No disponible"),
            "ultimo_cierre": historial.index[-1].strftime("%Y-%m-%d"),
        }

        return resumen

    except Exception as e:
        return {"error": str(e)}

# Herramienta: comparar dos acciones
@mcp.tool()
def comparar_acciones(ticker1: str, ticker2: str) -> dict:
    """
    Compara dos acciones en base a su precio y variación porcentual diaria.
    """
    r1 = resumen_accion(ticker1)
    r2 = resumen_accion(ticker2)

    if "error" in r1 or "error" in r2:
        return {
            "error": "No se pudieron obtener datos para una o ambas acciones.",
            "detalle": {"ticker1": r1, "ticker2": r2}
        }

    return {
        "comparación": {
            ticker1.upper(): {
                "precio": r1["precio_actual"],
                "variación": r1["variacion_pct"]
            },
            ticker2.upper(): {
                "precio": r2["precio_actual"],
                "variación": r2["variacion_pct"]
            }
        }
    }

# Recurso: descripción de instrumentos bursátiles
@mcp.resource("instrumento://{nombre}")
def descripcion_instrumento(nombre: str) -> str:
    descripciones = {
        "acciones": "Participaciones en el capital de una empresa. Pueden ganar valor o generar dividendos.",
        "bonos": "Títulos de deuda emitidos por el Estado o empresas, que pagan intereses.",
        "cedears": "Certificados que representan acciones extranjeras, operables en pesos.",
        "leliqs": "Instrumento del BCRA a corto plazo para controlar la liquidez del mercado.",
        "fci": "Fondos Comunes de Inversión: instrumentos que agrupan capital de varios inversores para diversificar riesgos.",
        "etfs": "Fondos cotizados que replican índices o sectores, disponibles a través de CEDEARs."
    }
    return descripciones.get(nombre.lower(), "Instrumento no reconocido.")

# Recurso dinámico: saludo personalizado
@mcp.resource("saludo://{nombre}")
def saludo_inversor(nombre: str) -> str:
    return f"Hola {nombre}, bienvenido a tu portal del Mercado Bursátil Argentino. ¡Listo para invertir?"

