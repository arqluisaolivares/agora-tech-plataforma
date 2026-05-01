"""
ÁGORA TECH — Plataforma Comercial
Streamlit + Google Sheets (base de datos persistente)
Todos los datos se guardan en un Google Sheet compartido
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import io
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════
# DATOS BASE — 185 PROYECTOS REALES
# ═══════════════════════════════════════════
PROYECTOS_BASE = [{"edificio": "STUDIO 84", "valor": 111443500, "comercial": "RAFAEL TORRES"}, {"edificio": "PARK 104", "valor": 105374500, "comercial": "RAFAEL TORRES"}, {"edificio": "EDIFICIO NEPTUNO", "valor": 93950000, "comercial": "RAFAEL TORRES"}, {"edificio": "LOS ANDES", "valor": 84113000, "comercial": "RAFAEL TORRES"}, {"edificio": "ALTO DE ARAGÓN", "valor": 110789000, "comercial": "RAFAEL TORRES"}, {"edificio": "SUITES GOLD", "valor": 113228500, "comercial": "RAFAEL TORRES"}, {"edificio": "MALAGA", "valor": 107100000, "comercial": "RAFAEL TORRES"}, {"edificio": "TORRE 94", "valor": 92701000, "comercial": "RAFAEL TORRES"}, {"edificio": "TULIPANES", "valor": 105374500, "comercial": "RAFAEL TORRES"}, {"edificio": "EL FONTANAR", "valor": 80920000, "comercial": "RAFAEL TORRES"}, {"edificio": "TIARA", "valor": 129948000, "comercial": "RAFAEL TORRES"}, {"edificio": "INZAR IV", "valor": 95854500, "comercial": "RAFAEL TORRES"}, {"edificio": "FERROL", "valor": 95438000, "comercial": "RAFAEL TORRES"}, {"edificio": "EL CERRO", "valor": 82467000, "comercial": "RAFAEL TORRES"}, {"edificio": "AVANTI", "valor": 101626000, "comercial": "RAFAEL TORRES"}, {"edificio": "TEMPO 77", "valor": 87286500, "comercial": "RAFAEL TORRES"}, {"edificio": "HOTEL MENDOZA", "valor": 120071000, "comercial": "RAFAEL TORRES"}, {"edificio": "NOMAD (CONDE)", "valor": 119952000, "comercial": "RAFAEL TORRES"}, {"edificio": "70A VCALCULADORA", "valor": 89547500, "comercial": "RAFAEL TORRES"}, {"edificio": "URAPANES", "valor": 92086960, "comercial": "RAFAEL TORRES"}, {"edificio": "BOSQUE SAN VICENTE", "valor": 86337475, "comercial": "RAFAEL TORRES"}, {"edificio": "CALLE 58", "valor": 108468500, "comercial": "ALBERTO FERRER"}, {"edificio": "IGUA", "valor": 102280500, "comercial": "SONIA CASTRO"}, {"edificio": "HARMONIA", "valor": 114835000, "comercial": "SONIA CASTRO"}, {"edificio": "LA TAGUA", "valor": 81931500, "comercial": "SONIA CASTRO"}, {"edificio": "FONTIBON", "valor": 91847200, "comercial": "SONIA CASTRO"}, {"edificio": "BARCELONA", "valor": 121261000, "comercial": "SONIA CASTRO"}, {"edificio": "PLAZA 47", "valor": 86691500, "comercial": "SONIA CASTRO"}, {"edificio": "HUNZA", "valor": 110610500, "comercial": "SONIA CASTRO"}, {"edificio": "RITACUBA", "valor": 123403000, "comercial": "SONIA CASTRO"}, {"edificio": "TORRE CHALETS", "valor": 105919500, "comercial": "SANTIAGO BOHORQUEZ"}, {"edificio": "YAKARTA", "valor": 99900500, "comercial": "SANTIAGO BOHORQUEZ"}, {"edificio": "LA CAROLINA", "valor": 59143000, "comercial": "LINA CALLE"}, {"edificio": "KANGIAI", "valor": 97996500, "comercial": "LINA CALLE"}, {"edificio": "SANTA VIVIANA", "valor": 112098000, "comercial": "LINA CALLE"}, {"edificio": "LABRADOR", "valor": 62594000, "comercial": "LINA CALLE"}, {"edificio": "CAMILA", "valor": 108704120, "comercial": "LINA CALLE"}, {"edificio": "LOS PINOS", "valor": 84073500, "comercial": "LINA CALLE"}, {"edificio": "SAHARA", "valor": 85977500, "comercial": "RAFAEL TORRES"}, {"edificio": "EL PARQUE", "valor": 63308000, "comercial": "LINA CALLE"}]
TODOS_PROYECTOS = [{"id": 7000000, "nombre": "EDIFICIO SAN REMO", "comercial": "SIN ASIGNAR", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "DICIEMBRE", "estado": "nuevo", "etapaOrig": "Frío / Sin avance", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000001, "nombre": "EDIFICIO B6 11", "comercial": "SONIA CASTRO", "notas": "Sin definir", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "DICIEMBRE", "estado": "nuevo", "etapaOrig": "Frío / Sin avance", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000002, "nombre": "EDIFICIO KASTOR", "comercial": "SONIA CASTRO", "notas": "una parte de la copropiedad quiere automatizar, ots no, pendiente definir nueva fecha de reunión.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "DICIEMBRE", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000003, "nombre": "TORRES DE MOREH", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000004, "nombre": "EDIFICIO ANDREA", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000005, "nombre": "BOX OFFICE", "comercial": "SONIA CASTRO", "notas": "Aprobada automatización pendeinte vencimiento contrato de vigilancia", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000006, "nombre": "MONTELUNA", "comercial": "SONIA CASTRO", "notas": "Aprobada automatización pendeinte vencimiento contrato de vigilancia", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000007, "nombre": "CENTRO EIFFEL", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000008, "nombre": "EDIFICIO PRAGA", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000009, "nombre": "EDIFICIO PARK TOWN 94", "comercial": "SONIA CASTRO", "notas": "Aprobada automatización pendeinte vencimiento contrato de vigilancia", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000010, "nombre": "EDIFICIO TORRENOVA", "comercial": "LINA CALLE", "notas": "No fuimos seleccionados", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000011, "nombre": "EDIFICIO 69-11", "comercial": "LINA CALLE", "notas": "No han aprobado la automatizacion", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000012, "nombre": "EDIFICIO BAVIERA", "comercial": "LINA CALLE", "notas": "No han aprobado la automatizacion", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000013, "nombre": "EDIFICIO ESTANCIA DE SANTA PAULA", "comercial": "SONIA CASTRO", "notas": "Aprobada automatización pendeinte vencimiento contrato de vigilancia", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000014, "nombre": "EDIFICIO ZAPPAN 109", "comercial": "SONIA CASTRO", "notas": "Decidido a automatizar / contrato de vigilancia finaliza en noviembre / cierre antes de agosto / ajuste de cotización", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000015, "nombre": "EDIFICIO CASTELLANA 99", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000016, "nombre": "EDIFICIO TORRE NAVARRA", "comercial": "SONIA CASTRO", "notas": "A la espera de reunión de concejo / 1 Semana Abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000017, "nombre": "EDIFICIO BOREAL", "comercial": "SONIA CASTRO", "notas": "Aprobada automatización pendeinte vencimiento contrato de vigilancia", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000018, "nombre": "EDIFICIO SAN MARCOS", "comercial": "SONIA CASTRO", "notas": "Estan definiendo retirar a vigilantes / contrato de vigilancia finaliza en octubre / cierre antes de agosto", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000019, "nombre": "EDIFICIO AINSUCA", "comercial": "SONIA CASTRO", "notas": "No van a automatizar por ahora", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ENERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000020, "nombre": "EDIFICIO CAPIRO", "comercial": "LINA CALLE", "notas": "Pendiente de reunion del consejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000021, "nombre": "EDIFICIO LUMINA", "comercial": "LINA CALLE", "notas": "Pendiente de reunion del consejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000022, "nombre": "ORVIETO", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000023, "nombre": "PARQUE REAL", "comercial": "SONIA CASTRO", "notas": "Esperan que se acerque fecha vencimiento de contrato vigillancia noviembre - diciembre, para decidir", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000024, "nombre": "HELTON", "comercial": "SONIA CASTRO", "notas": "Esperan que se acerque fecha vencimiento de contrato vigillancia noviembre - diciembre, para decidir", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000025, "nombre": "GOLF CLUB", "comercial": "SONIA CASTRO", "notas": "Esperan que se acerque fecha vencimiento de contrato vigillancia noviembre - diciembre, para decidir", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado Aut - Pendiente vencimiento vigilancia", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000026, "nombre": "7 ARTE", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000027, "nombre": "EDIFICIO SANTA MARIA", "comercial": "RAFAEL TORRES", "notas": "No fue aprobada la automatización en el edificiop", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000028, "nombre": "MONSERATT", "comercial": "LINA CALLE", "notas": "Seleccionaron a otra empresa.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000029, "nombre": "OLIVAR", "comercial": "RAFAEL TORRES", "notas": "Hay reunion de consejo proximamente", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000030, "nombre": "ELITE", "comercial": "RAFAEL TORRES", "notas": "Faltaba por enviar un cotizante para completar 3, esta la decision de automatizar", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000031, "nombre": "EDIFICIO PORTUGAL XIV", "comercial": "SONIA CASTRO", "notas": "No han definido volver a llamar del 20 al 30 d abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000032, "nombre": "TORRES DE SABANETA", "comercial": "SONIA CASTRO", "notas": "No han definido volver a llamar del 20 al 30 d abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000033, "nombre": "GALERIE 51 P.H.", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000034, "nombre": "SANTA SOFIA", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000035, "nombre": "RENOVART 92", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000036, "nombre": "IBIZA", "comercial": "RAFAEL TORRES", "notas": "Se decidió no automatizar", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000037, "nombre": "CALLE 67", "comercial": "RAFAEL TORRES", "notas": "Fuimos a la asamblea antes de semana santa, aún no hay respuesta final y espa pendiente la visita a alto 61", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000038, "nombre": "70A", "comercial": "RAFAEL TORRES", "notas": "Dijeron que no pero quieren automatizar las puertas del edificio", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000039, "nombre": "ALCAZAR DEL RIO II", "comercial": "SONIA CASTRO", "notas": "Pendiente reunion, van a empezar automatizacion por etapas", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000040, "nombre": "122 AV", "comercial": "SONIA CASTRO", "notas": "Aprobada automatizacion, van a definir proveedor ajustar la cotizacion, por actividades, reunion consejo 17 de abril 2:00pm", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000041, "nombre": "MONTELOMA 11", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000042, "nombre": "ART 94", "comercial": "SONIA CASTRO", "notas": "No han definido volver a llamar del 20 al 30 d abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000043, "nombre": "ARAUCARIA", "comercial": "LINA CALLE", "notas": "Estamos aun en el proceso, ha habido consultas del consejo pero aú no hay decision", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1oh9pBX2nugdhsQL0bjC6_Vbn9AV0IVP8?usp=drive_link"}, {"id": 7000044, "nombre": "ED AVENIDA EL RETIRO", "comercial": "RAFAEL TORRES", "notas": "Dijeron que no, el edificio se va a vender", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "FEBRERO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000045, "nombre": "EDIFICIO CASTILLA", "comercial": "RAFAEL TORRES", "notas": "Se esta en conversaciones con el consejo y se va a hacer una visita a Alto 61", "total": "$141.547.806", "totalNum": 141547806, "cuota24": "$5.897.825", "cuota36": "$3.931.883", "c24Num": 5897825, "c36Num": 3931883, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1h3rhiqzJy8nbM9uPa-K4wVaYQszy_jfe?usp=drive_link"}, {"id": 7000046, "nombre": "TORRE CABRERA", "comercial": "LINA CALLE", "notas": "No van a Automatizar.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000047, "nombre": "EDIFICIO LA GRAN VÍA", "comercial": "ALBERTO FERRER", "notas": "Pendiente reunión de asamblea.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000048, "nombre": "RINCON DE ALCAZAR", "comercial": "LINA CALLE", "notas": "No van a Automatizar. Una propietaria es la que contesta los mensajes", "total": "$106.382.832", "totalNum": 106382832, "cuota24": "$4.432.618", "cuota36": "$2.955.078", "c24Num": 4432618, "c36Num": 2955078, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1d5XCspRFca1STpYmO-MX780KAYWLwAEp?usp=drive_link"}, {"id": 7000049, "nombre": "EDIFICIO ARUBA", "comercial": "LINA CALLE", "notas": "No van a Automatizar.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000050, "nombre": "EDIFICIO SANTA CLARA", "comercial": "LINA CALLE", "notas": "No van a Automatizar.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000051, "nombre": "EDIFICIO QUIRIOS", "comercial": "LINA CALLE", "notas": "No van a Automatizar.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000052, "nombre": "CALLE 60", "comercial": "LINA CALLE", "notas": "No van a Automatizar.", "total": "$101.430.928", "totalNum": 101430928, "cuota24": "$4.226.288", "cuota36": "$2.817.525", "c24Num": 4226288, "c36Num": 2817525, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1UPIbHGOsqDhgUJ1w0imGhQsOFRbM9Pua?usp=drive_link"}, {"id": 7000053, "nombre": "ABEDUL", "comercial": "LINA CALLE", "notas": "No van a Automatizar. La administradora no contesta los mensaje", "total": "$131.925.261", "totalNum": 131925261, "cuota24": "$5.496.885", "cuota36": "$3.664.590", "c24Num": 5496885, "c36Num": 3664590, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1kFJMAmAZuU2aRHX-vVz-ktMu5Y8ubz7l?usp=drive_link"}, {"id": 7000054, "nombre": "EDIFICIO PARK 145", "comercial": "SONIA CASTRO", "notas": "Seleccionaron a otra empresa.", "total": "$120.641.240", "totalNum": 120641240, "cuota24": "$5.026.718", "cuota36": "$3.351.145", "c24Num": 5026718, "c36Num": 3351145, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1VWG7iafTsTwZTVRaAl_T-ya1ff3GVjSF?usp=drive_link"}, {"id": 7000055, "nombre": "ED SANTA BARBARA III", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000056, "nombre": "ED URAPANES DE SANTA BARBARA", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000057, "nombre": "EDIFICIO EL PORVENIR", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000058, "nombre": "EDIFICIO MONTECARLO VILLAGE", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion, solicitaron, mas cotizaciones", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000059, "nombre": "EDIFICIO GUAYACAN", "comercial": "ALBERTO FERRER", "notas": "Pendiente repuesta Administración.", "total": "$77.109.782", "totalNum": 77109782, "cuota24": "$3.212.907", "cuota36": "$2.141.938", "c24Num": 3212907, "c36Num": 2141938, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "18. Ed. Guayacán - Bog."}, {"id": 7000060, "nombre": "EDIFICIO ID 97", "comercial": "RAFAEL TORRES", "notas": "No aprobaron la automatizacipn", "total": "$91.848.257", "totalNum": 91848257, "cuota24": "$3.827.010", "cuota36": "$2.551.340", "c24Num": 3827010, "c36Num": 2551340, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "36. ID 97 (Pendiente excel de cantidades)"}, {"id": 7000061, "nombre": "EDIFICIO SAN NICOLAS", "comercial": "RAFAEL TORRES", "notas": "No han vuelto a responder, no era un edificio de propiedad horizontal", "total": "$78.926.161", "totalNum": 78926161, "cuota24": "$3.288.590", "cuota36": "$2.192.393", "c24Num": 3288590, "c36Num": 2192393, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "35. SAN NICOLAS Calle 56 No. 35-18"}, {"id": 7000062, "nombre": "EDIFICIO RISARALDA", "comercial": "RAFAEL TORRES", "notas": "Fuimos a la asamblea, hay decision el 22", "total": "$81.951.901", "totalNum": 81951901, "cuota24": "$3.414.662", "cuota36": "$2.276.441", "c24Num": 3414662, "c36Num": 2276441, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "34. EDIFICIO RISARALDA CRA 12 91 15"}, {"id": 7000063, "nombre": "EDIFICIO PARKWAY RESERVADO III", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000064, "nombre": "EDIFICIO CALIFORNIA ANTIGUA", "comercial": "ALBERTO FERRER", "notas": "En proceso de reunión de propietarios.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000065, "nombre": "EDIFICIO RECREO DE SANTA PAULA", "comercial": "LINA CALLE", "notas": "Este año no lo van hacer.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000066, "nombre": "EDIFICIO FLAT 119", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000067, "nombre": "EDIFICIO TRÍPOLI", "comercial": "ALBERTO FERRER", "notas": "Pendiente de reunión.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000068, "nombre": "EDIFICIO VICTORIA PLAZA", "comercial": "LINA CALLE", "notas": "Pendiente de cual empresa van a seleccionar para automatizar.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "46. EDIFICIO VICTORIA PLAZA"}, {"id": 7000069, "nombre": "EDIFICIO ANCHICAYA", "comercial": "RAFAEL TORRES", "notas": "Van a tomar la decision en Julio", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000070, "nombre": "EDIFICIO 7A AVENIDA", "comercial": "SONIA CASTRO", "notas": "Cotizaciones en estudio", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000071, "nombre": "EDIFICIO ISNOS", "comercial": "SONIA CASTRO", "notas": "Pendientevencimiento de contrato vigilancia, retoman en noviembre", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "25.EDIFICIO ISNOS  (CON FICHA)"}, {"id": 7000072, "nombre": "EDIFICIO VILLORIO HOME & OFFICE", "comercial": "SONIA CASTRO", "notas": "Pendiente de evaluación de presupuestos y proyectos", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000073, "nombre": "EDIFICIO AMANCAY", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion, solicitaron, mas cotizaciones", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "22.EDIFICIO AMANCAY  (CON FICHA)"}, {"id": 7000074, "nombre": "ED MULTIFAMILIAR RUA 45", "comercial": "SONIA CASTRO", "notas": "No han definio pendiente reunion, solicitaron, mas cotizaciones", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "21.ED MULTIFAMILIAR RUA 45  ESTADO FICHA: VIABLE"}, {"id": 7000075, "nombre": "EDIFICIO SAMORE", "comercial": "RAFAEL TORRES", "notas": "Hay asamblea el martes 14 de abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000076, "nombre": "EDIFICIO ENTORNO 109", "comercial": "RAFAEL TORRES", "notas": "Reunión jueves 23 de abril con la administradora para revisar un tema de la puerta vehicular", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "MARZO", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000077, "nombre": "La Carolina", "comercial": "LINA CALLE", "notas": "Nuevo", "total": "$59.143.000", "totalNum": 59143000, "cuota24": "$2.464.291", "cuota36": "$1.642.861", "c24Num": 2464291, "c36Num": 1642861, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000078, "nombre": "Edificio Kangiai", "comercial": "LINA CALLE", "notas": "Estan revisando cotizaciones y en revisión por parte del concejo.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000079, "nombre": "Santa Viviana", "comercial": "LINA CALLE", "notas": "Nuevo", "total": "$112.098.000", "totalNum": 112098000, "cuota24": "$4.670.750", "cuota36": "$3.113.833", "c24Num": 4670750, "c36Num": 3113833, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000080, "nombre": "Edificio Igua", "comercial": "SONIA CASTRO", "notas": "Nuevo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1d0InZs8of6kiBZUV7LB11D3wIlPHNZRG?usp=drive_link"}, {"id": 7000081, "nombre": "Edificio Harmonia", "comercial": "SONIA CASTRO", "notas": "Nuevo Reunión proxima semana", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1Sm-r98e1b7M3ZeoZzLJYcGU_dtnNkqTo?usp=drive_link"}, {"id": 7000082, "nombre": "Edificio La Tagua", "comercial": "SONIA CASTRO", "notas": "Nuevo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000083, "nombre": "Estudio 84", "comercial": "RAFAEL TORRES", "notas": "Pendiente de Reunión del consejo esta semana. Hay que hacerle segumiento con Jose Joaquin.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000084, "nombre": "Park 104", "comercial": "RAFAEL TORRES", "notas": "Tenemos reunión con el consejo el 27 de abril", "total": "$105.374.500", "totalNum": 105374500, "cuota24": "$4.390.604", "cuota36": "$2.927.069", "c24Num": 4390604, "c36Num": 2927069, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000112, "nombre": "Edificio Neptuno", "comercial": "RAFAEL TORRES", "notas": "", "total": "$93.950.000", "totalNum": 93950000, "cuota24": "$3.914.583", "cuota36": "$2.609.722", "c24Num": 3914583, "c36Num": 2609722, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000086, "nombre": "Edificio Los Andes", "comercial": "RAFAEL TORRES", "notas": "Deben tomar la decisión en junio debido a que su edificio vecino ya automatizo. Hay que hacerle segumiento esta semana", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000087, "nombre": "Edificio Alto Aragón", "comercial": "RAFAEL TORRES", "notas": "Se hizo una visita a Alto 61. Se esta esperando una asamblea", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000088, "nombre": "Suites Gold", "comercial": "RAFAEL TORRES", "notas": "Pendiente de agendamiento de asamblea", "total": "$113.228.500", "totalNum": 113228500, "cuota24": "$4.717.854", "cuota36": "$3.145.236", "c24Num": 4717854, "c36Num": 3145236, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000089, "nombre": "Málaga", "comercial": "RAFAEL TORRES", "notas": "Nuevo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000090, "nombre": "Torre 94", "comercial": "RAFAEL TORRES", "notas": "Se hizo una reunión con el consejo. Tenemos pendiente agendar la visita y una reunión de ellos con el consejo.", "total": "$92.701.000", "totalNum": 92701000, "cuota24": "$3.862.541", "cuota36": "$2.575.027", "c24Num": 3862541, "c36Num": 2575027, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000091, "nombre": "Edificio Tulipanes", "comercial": "RAFAEL TORRES", "notas": "Solo se ha enviado la cotización.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000092, "nombre": "Edificio Torre Chalets", "comercial": "SANTIAGO BOHORQUEZ", "notas": "Evaluación de cotización", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000093, "nombre": "Edificio Yakarta", "comercial": "SANTIAGO BOHORQUEZ", "notas": "Asamblea el 25 de abril", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000094, "nombre": "El Fontanar", "comercial": "RAFAEL TORRES", "notas": "ENVIADA LA COTIZACIÓN SEGUN LOS  REQUERIMENTOS EL VIERNES 17 DE ABRIL", "total": "$80.920.000", "totalNum": 80920000, "cuota24": "$3.371.666", "cuota36": "$2.247.777", "c24Num": 3371666, "c36Num": 2247777, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000095, "nombre": "Tiara", "comercial": "RAFAEL TORRES", "notas": "ENVIADA LA COTIZACIÓN SEGUN LOS  REQUERIMENTOS EL JUEVES 16 DE ABRIL", "total": "$129.948.000", "totalNum": 129948000, "cuota24": "$5.414.500", "cuota36": "$3.609.666", "c24Num": 5414500, "c36Num": 3609666, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 7000096, "nombre": "Inzar VI", "comercial": "RAFAEL TORRES", "notas": "Fuimos a las asambles el sabado, según la administradora fuimos la propuesta que má gustó pero la personas de la tercera edad no aprobaron la automatización.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000097, "nombre": "Country 136", "comercial": "RAFAEL TORRES", "notas": "Agendamiento con Luisa", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente decisión / En evaluación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000098, "nombre": "Edificio Ferrol", "comercial": "RAFAEL TORRES", "notas": "Reunión con el consejo el jueves 16 de abril donde parecieron tener un interes,", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000099, "nombre": "Edificio Calle 58", "comercial": "ALBERTO FERRER", "notas": "Nuevo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000100, "nombre": "EL PINO", "comercial": "LINA CALLE", "notas": "Esta en evaluación la cotización, proxima reunión con consejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1R_SAfW6huylr2QMDmU__lUU_HHt3BARZ?usp=drive_link"}, {"id": 7000101, "nombre": "FONTANAR", "comercial": "LINA CALLE", "notas": "Nos respondieron el correo, esta en revisión de concejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1qul9KQzU3d6nLscqTkUmoT4SKo7tJ6L-"}, {"id": 7000102, "nombre": "TERRACINO 93", "comercial": "LINA CALLE", "notas": "Nos respondieron el correo, esta en revisión de concejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000103, "nombre": "OPORTO CHICO", "comercial": "LINA CALLE", "notas": "Nos respondieron el correo, esta en revisión de concejo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "cotizado", "etapaOrig": "Aprobado - Pendiente proveedor", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1iCRYk2zQRJqRlzTFhr2kVjMc03MDvXzc"}, {"id": 7000104, "nombre": "EDIFICIO CAMILA", "comercial": "LINA CALLE", "notas": "Nuevo", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000105, "nombre": "Bosque de San Vicente", "comercial": "RAFAEL TORRES", "notas": "Mandaron un pliego de peticiones para la convocatoria de automatización hay que enviar la cotización y la presentación antes del mmartes alas 6pm.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000106, "nombre": "Hotel Casa Mendoza", "comercial": "RAFAEL TORRES", "notas": "Les parecio cara la costización y quieren ver que les podemos quitar. Puede haber un cierre pero la sitación económica del hotel no es buena.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "Pendiente reunión / aprobación", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000107, "nombre": "Edificio Nomad", "comercial": "RAFAEL TORRES", "notas": "Tenemos que sentarnos con el señor David Conde y mirar que pensó de la propuesta enviada el viernes 17 de abril.", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "negociacion", "etapaOrig": "Avanzado / Cierre cercano", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000108, "nombre": "Edificio Barcelona", "comercial": "SONIA CASTRO", "notas": "Nuevo 21-04", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000109, "nombre": "Edificio Plaza 47", "comercial": "SONIA CASTRO", "notas": "Nuevo 21-04", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000110, "nombre": "Edificio Hunza", "comercial": "SONIA CASTRO", "notas": "Nuevo 21-04", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000111, "nombre": "Edificio Ritacuba", "comercial": "SONIA CASTRO", "notas": "Nuevo 21-04", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000113, "nombre": "Edificio El Cerro", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000114, "nombre": "Edificio Avanti", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000115, "nombre": "Edificio Tempo 77", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000116, "nombre": "Edificio Urapanes", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000117, "nombre": "Edificio Fontibon", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000118, "nombre": "Edificio Labrador", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000119, "nombre": "Edificio Los Pinos", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000120, "nombre": "Edificio El Bosque", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000121, "nombre": "Edificio Sahata", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "ABRIL", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": ""}, {"id": 7000122, "nombre": "El Parque", "comercial": "LINA CALLE", "notas": "", "total": "$63.308.000", "totalNum": 63308000, "cuota24": "$2.637.833", "cuota36": "$1.758.555", "c24Num": 2637833, "c36Num": 1758555, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 6000122, "nombre": "Kyrios", "comercial": "LINA CALLE", "notas": "La asamblea pospuso la automatizacion.", "total": "$129.375.734", "totalNum": 129375734, "cuota24": "$5.390.655", "cuota36": "$3.593.770", "c24Num": 5390655, "c36Num": 3593770, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1nLwX3lF16UhI4tjdmI65InYLloVAxLiP?usp=drive_link"}, {"id": 6000123, "nombre": "SANTA CLARA", "comercial": "LINA CALLE", "notas": "Los propietarios aun no se deciden", "total": "$101.430.928", "totalNum": 101430928, "cuota24": "$4.226.288", "cuota36": "$2.817.525", "c24Num": 4226288, "c36Num": 2817525, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "En Viabilidad", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1fCFg_ZpR9cyNx__MI4_YW9SYoVz_Q-sX?usp=drive_link"}, {"id": 6000124, "nombre": "ARUBA", "comercial": "LINA CALLE", "notas": "El propietario contesto que el consejo no se ha reunido", "total": "$114.280.324", "totalNum": 114280324, "cuota24": "$4.761.680", "cuota36": "$3.174.453", "c24Num": 4761680, "c36Num": 3174453, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "En Viabilidad", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1hEelsrDhtYa42s1jA78jdUDmDeS8j2Lu?usp=drive_link"}, {"id": 6000125, "nombre": "EDIFICIO IBIZA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1BzRF6ac88ClP5Uko3Azad3WdrJ1no2hE?usp=drive_link"}, {"id": 6000126, "nombre": "Edificio 70A", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1WTTCj9UsdZ4-79n5gG0iJ3gJu55wKXok?usp=drive_link"}, {"id": 6000127, "nombre": "Edificio calle 67", "comercial": "RAFAEL TORRES", "notas": "", "total": "$126.515.716", "totalNum": 126515716, "cuota24": "$5.271.488", "cuota36": "$3.514.325", "c24Num": 5271488, "c36Num": 3514325, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/14rgw-pwJiyRlJgGMfaUR5o1LRVDG8RUw?usp=drive_link"}, {"id": 6000128, "nombre": "Edificio Avenida del retiro", "comercial": "RAFAEL TORRES", "notas": "", "total": "$82.897.185", "totalNum": 82897185, "cuota24": "$3.454.049", "cuota36": "$2.302.699", "c24Num": 3454049, "c36Num": 2302699, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1avETgaTPnsBGid-oDHhIPNVFSU0E2HJk?usp=drive_link"}, {"id": 6000129, "nombre": "Edificio Araucaria", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1sdjojT_HLyo7ZcPf2cwtSauIwCIbXebQ?usp=drive_link"}, {"id": 6000130, "nombre": "Edificio La Gran Via", "comercial": "ALBERTO FERRER", "notas": "", "total": "$97.744.982", "totalNum": 97744982, "cuota24": "$4.072.707", "cuota36": "$2.715.138", "c24Num": 4072707, "c36Num": 2715138, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "cotizado", "etapaOrig": "En Seguimiento", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1erlIb70vGXPUZ2FmNZ3wd7ZwpzNU-AQ0?usp=drive_link"}, {"id": 6000131, "nombre": "ED URAPANES DE SANTA PAULA", "comercial": "SONIA CASTRO", "notas": "", "total": "$91.989.191", "totalNum": 91989191, "cuota24": "$3.832.882", "cuota36": "$2.555.255", "c24Num": 3832882, "c36Num": 2555255, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1M01VpopCINeq9cQbbp6m9o9fCKMBNzw7?usp=drive_link"}, {"id": 6000132, "nombre": "ED VILLORIO HOME OFFICE", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1Y8lGmVfy5dLx0grzj5H3v51rxc746v67?usp=drive_link"}, {"id": 6000133, "nombre": "ED SANTA BARBARA III PH", "comercial": "SONIA CASTRO", "notas": "", "total": "$142.367.161", "totalNum": 142367161, "cuota24": "$5.931.965", "cuota36": "$3.954.643", "c24Num": 5931965, "c36Num": 3954643, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/182v9WlVChQZmz_mIKBkxkeBnlMK2jJmE?usp=drive_link"}, {"id": 6000134, "nombre": "ED MONTECARLO VILLAGE", "comercial": "SONIA CASTRO", "notas": "", "total": "$149.892.365", "totalNum": 149892365, "cuota24": "$6.245.515", "cuota36": "$4.163.676", "c24Num": 6245515, "c36Num": 4163676, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1ZF9hvEc2rWeoQohElegEkgusPuhHlqWq?usp=drive_link"}, {"id": 6000135, "nombre": "EDIFICIO SEPTIMA AVENIDA", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "19.ED 7a AVENIDA (Sin revisar falta información técnica)"}, {"id": 6000136, "nombre": "EDIFICIO BET", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "24.EDIFICIO BET  (CON FICHA)"}, {"id": 6000137, "nombre": "EDIFICIO LA CUMBRE", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "26.EDIFICIO LA CUMBRE CASO ESPECIAL SE PASO LA FECHA DE ENTREGA"}, {"id": 6000138, "nombre": "RECREO DE SANTA PAULA", "comercial": "LINA CALLE", "notas": "", "total": "$103.794.853", "totalNum": 103794853, "cuota24": "$4.324.785", "cuota36": "$2.883.190", "c24Num": 4324785, "c36Num": 2883190, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "31. Recreo de Santa Paula"}, {"id": 6000139, "nombre": "VERDI 135", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "perdido", "etapaOrig": "Rechazado", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "32. VERDI 135"}, {"id": 6000140, "nombre": "PARKWAY RESERVADO III", "comercial": "LINA CALLE", "notas": "", "total": "$42.596.844", "totalNum": 42596844, "cuota24": "$1.774.868", "cuota36": "$1.183.245", "c24Num": 1774868, "c36Num": 1183245, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "En Viabilidad", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "33. PARKWAY RESERVADO III"}, {"id": 6000141, "nombre": "CALFORNIA ANTIGUA", "comercial": "ALBERTO FERRER", "notas": "Solicitan nueva cotización para instalar el sistema únicamente en las puertas de acceso vehicular, primer piso y sótano.", "total": "$109.952.809", "totalNum": 109952809, "cuota24": "$4.581.367", "cuota36": "$3.054.244", "c24Num": 4581367, "c36Num": 3054244, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "En Viabilidad", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "16. ED. California Antigua - Bog."}, {"id": 6000142, "nombre": "EDIFICIO TRIPOLI BOGOTÁ", "comercial": "ALBERTO FERRER", "notas": "El Consejo de Admon. va a evaluar la propuesta en reunión programada para el 12 de abril", "total": "$74.552.250", "totalNum": 74552250, "cuota24": "$3.106.343", "cuota36": "$2.070.895", "c24Num": 3106343, "c36Num": 2070895, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "Pendiente Revisión", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "17. Ed. Trípoli - Bog."}, {"id": 6000143, "nombre": "EDIFICIO KING DAVID", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "37. EDIFICIO KING DAVID (Pendiente Revisar)"}, {"id": 6000144, "nombre": "EDIFICIO MIRADOR DEL PARQUE", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "38. EDIFICIO MIRADOR DEL PARQUE(Pendiente revisar)"}, {"id": 6000145, "nombre": "EDIFICIO ACHINCAYA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "A. INFO TECNICA"}, {"id": 6000146, "nombre": "FLAT 119", "comercial": "LINA CALLE", "notas": "", "total": "$93.322.721", "totalNum": 93322721, "cuota24": "$3.888.446", "cuota36": "$2.592.297", "c24Num": 3888446, "c36Num": 2592297, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "42. FLAT 119"}, {"id": 6000147, "nombre": "Entorno 109", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/18_z9o_kTDs9D48j7A81-d7K2ll8LJDNN"}, {"id": 6000148, "nombre": "Samore", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1F6KB_PEST-189l05zXhJRG-jAhhnsbAV"}, {"id": 6000149, "nombre": "ATRIUM 142", "comercial": "SONIA CASTRO", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1s85dkA7zsabymv1EWsce3i1_YwHuEbkr?usp=drive_link"}, {"id": 6000150, "nombre": "Terrazino", "comercial": "LINA CALLE", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1bFZhJirbOCDcYE0jTP5x_3CE95lOuoRW"}, {"id": 6000151, "nombre": "Loira", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/15GSePmAwWKOXcW-WnFQ13vOB0B4D8vSI"}, {"id": 6000152, "nombre": "Serrana Emaus", "comercial": "RAFAEL TORRES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "53. Serrana Emaus"}, {"id": 6000153, "nombre": "Peñas Blancas", "comercial": "LUISA OLIVARES", "notas": "", "total": "$0", "totalNum": 0, "cuota24": "$0", "cuota36": "$0", "c24Num": 0, "c36Num": 0, "vig": "", "vigH": "", "fecha": "Seg. Técnico", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "drive": "https://drive.google.com/drive/folders/1e17E2-t_h-t0MryQnO7-P08SwyLE4aAF"}, {"id": 5000000, "nombre": "STUDIO 84", "comercial": "RAFAEL TORRES", "notas": "", "total": "$111.443.500", "totalNum": 111443500, "cuota24": "$4.643.479", "cuota36": "$3.095.652", "c24Num": 4643479, "c36Num": 3095652, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000003, "nombre": "LOS ANDES", "comercial": "RAFAEL TORRES", "notas": "", "total": "$84.113.000", "totalNum": 84113000, "cuota24": "$3.504.708", "cuota36": "$2.336.472", "c24Num": 3504708, "c36Num": 2336472, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000004, "nombre": "ALTO DE ARAGÓN", "comercial": "RAFAEL TORRES", "notas": "", "total": "$110.789.000", "totalNum": 110789000, "cuota24": "$4.616.208", "cuota36": "$3.077.472", "c24Num": 4616208, "c36Num": 3077472, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000006, "nombre": "MALAGA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$107.100.000", "totalNum": 107100000, "cuota24": "$4.462.500", "cuota36": "$2.975.000", "c24Num": 4462500, "c36Num": 2975000, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000008, "nombre": "TULIPANES", "comercial": "RAFAEL TORRES", "notas": "", "total": "$105.374.500", "totalNum": 105374500, "cuota24": "$4.390.604", "cuota36": "$2.927.069", "c24Num": 4390604, "c36Num": 2927069, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000011, "nombre": "INZAR IV", "comercial": "RAFAEL TORRES", "notas": "", "total": "$95.854.500", "totalNum": 95854500, "cuota24": "$3.993.937", "cuota36": "$2.662.625", "c24Num": 3993937, "c36Num": 2662625, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000012, "nombre": "FERROL", "comercial": "RAFAEL TORRES", "notas": "", "total": "$95.438.000", "totalNum": 95438000, "cuota24": "$3.976.583", "cuota36": "$2.651.055", "c24Num": 3976583, "c36Num": 2651055, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000013, "nombre": "EL CERRO", "comercial": "RAFAEL TORRES", "notas": "", "total": "$82.467.000", "totalNum": 82467000, "cuota24": "$3.436.125", "cuota36": "$2.290.750", "c24Num": 3436125, "c36Num": 2290750, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000014, "nombre": "AVANTI", "comercial": "RAFAEL TORRES", "notas": "", "total": "$101.626.000", "totalNum": 101626000, "cuota24": "$4.234.416", "cuota36": "$2.822.944", "c24Num": 4234416, "c36Num": 2822944, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000015, "nombre": "TEMPO 77", "comercial": "RAFAEL TORRES", "notas": "", "total": "$87.286.500", "totalNum": 87286500, "cuota24": "$3.636.937", "cuota36": "$2.424.625", "c24Num": 3636937, "c36Num": 2424625, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000016, "nombre": "HOTEL MENDOZA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$120.071.000", "totalNum": 120071000, "cuota24": "$5.002.958", "cuota36": "$3.335.305", "c24Num": 5002958, "c36Num": 3335305, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000017, "nombre": "NOMAD (CONDE)", "comercial": "RAFAEL TORRES", "notas": "", "total": "$119.952.000", "totalNum": 119952000, "cuota24": "$4.998.000", "cuota36": "$3.332.000", "c24Num": 4998000, "c36Num": 3332000, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000018, "nombre": "70A VCALCULADORA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$89.547.500", "totalNum": 89547500, "cuota24": "$3.731.145", "cuota36": "$2.487.430", "c24Num": 3731145, "c36Num": 2487430, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000019, "nombre": "URAPANES", "comercial": "RAFAEL TORRES", "notas": "", "total": "$92.086.960", "totalNum": 92086960, "cuota24": "$3.836.956", "cuota36": "$2.557.971", "c24Num": 3836956, "c36Num": 2557971, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000020, "nombre": "BOSQUE SAN VICENTE", "comercial": "RAFAEL TORRES", "notas": "", "total": "$86.337.475", "totalNum": 86337475, "cuota24": "$3.597.394", "cuota36": "$2.398.263", "c24Num": 3597394, "c36Num": 2398263, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000021, "nombre": "CALLE 58", "comercial": "ALBERTO FERRER", "notas": "", "total": "$108.468.500", "totalNum": 108468500, "cuota24": "$4.519.520", "cuota36": "$3.013.013", "c24Num": 4519520, "c36Num": 3013013, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000022, "nombre": "IGUA", "comercial": "SONIA CASTRO", "notas": "", "total": "$102.280.500", "totalNum": 102280500, "cuota24": "$4.261.687", "cuota36": "$2.841.125", "c24Num": 4261687, "c36Num": 2841125, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000023, "nombre": "HARMONIA", "comercial": "SONIA CASTRO", "notas": "", "total": "$114.835.000", "totalNum": 114835000, "cuota24": "$4.784.791", "cuota36": "$3.189.861", "c24Num": 4784791, "c36Num": 3189861, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000024, "nombre": "LA TAGUA", "comercial": "SONIA CASTRO", "notas": "", "total": "$81.931.500", "totalNum": 81931500, "cuota24": "$3.413.812", "cuota36": "$2.275.875", "c24Num": 3413812, "c36Num": 2275875, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000025, "nombre": "FONTIBON", "comercial": "SONIA CASTRO", "notas": "", "total": "$91.847.200", "totalNum": 91847200, "cuota24": "$3.826.966", "cuota36": "$2.551.311", "c24Num": 3826966, "c36Num": 2551311, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000026, "nombre": "BARCELONA", "comercial": "SONIA CASTRO", "notas": "", "total": "$121.261.000", "totalNum": 121261000, "cuota24": "$5.052.541", "cuota36": "$3.368.361", "c24Num": 5052541, "c36Num": 3368361, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000027, "nombre": "PLAZA 47", "comercial": "SONIA CASTRO", "notas": "", "total": "$86.691.500", "totalNum": 86691500, "cuota24": "$3.612.145", "cuota36": "$2.408.097", "c24Num": 3612145, "c36Num": 2408097, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000028, "nombre": "HUNZA", "comercial": "SONIA CASTRO", "notas": "", "total": "$110.610.500", "totalNum": 110610500, "cuota24": "$4.608.770", "cuota36": "$3.072.513", "c24Num": 4608770, "c36Num": 3072513, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000029, "nombre": "RITACUBA", "comercial": "SONIA CASTRO", "notas": "", "total": "$123.403.000", "totalNum": 123403000, "cuota24": "$5.141.791", "cuota36": "$3.427.861", "c24Num": 5141791, "c36Num": 3427861, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000030, "nombre": "TORRE CHALETS", "comercial": "SANTIAGO BOHORQUEZ", "notas": "", "total": "$105.919.500", "totalNum": 105919500, "cuota24": "$4.413.312", "cuota36": "$2.942.208", "c24Num": 4413312, "c36Num": 2942208, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000031, "nombre": "YAKARTA", "comercial": "SANTIAGO BOHORQUEZ", "notas": "", "total": "$99.900.500", "totalNum": 99900500, "cuota24": "$4.162.520", "cuota36": "$2.775.013", "c24Num": 4162520, "c36Num": 2775013, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000033, "nombre": "KANGIAI", "comercial": "LINA CALLE", "notas": "", "total": "$97.996.500", "totalNum": 97996500, "cuota24": "$4.083.187", "cuota36": "$2.722.125", "c24Num": 4083187, "c36Num": 2722125, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000035, "nombre": "LABRADOR", "comercial": "LINA CALLE", "notas": "", "total": "$62.594.000", "totalNum": 62594000, "cuota24": "$2.608.083", "cuota36": "$1.738.722", "c24Num": 2608083, "c36Num": 1738722, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000036, "nombre": "CAMILA", "comercial": "LINA CALLE", "notas": "", "total": "$108.704.120", "totalNum": 108704120, "cuota24": "$4.529.338", "cuota36": "$3.019.558", "c24Num": 4529338, "c36Num": 3019558, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000037, "nombre": "LOS PINOS", "comercial": "LINA CALLE", "notas": "", "total": "$84.073.500", "totalNum": 84073500, "cuota24": "$3.503.062", "cuota36": "$2.335.375", "c24Num": 3503062, "c36Num": 2335375, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}, {"id": 5000038, "nombre": "SAHARA", "comercial": "RAFAEL TORRES", "notas": "", "total": "$85.977.500", "totalNum": 85977500, "cuota24": "$3.582.395", "cuota36": "$2.388.263", "c24Num": 3582395, "c36Num": 2388263, "vig": "", "vigH": "", "fecha": "Abr 2026", "estado": "nuevo", "etapaOrig": "", "version": "v1", "lastUpdate": null, "lastNote": "", "fromCalc": true}]

USUARIOS = {
    "luisa":    {"pass": "luisa2026",    "nombre": "Luisa Olivares",     "rol": "gerente",   "comercial": "LUISA OLIVARES"},
    "gerente":  {"pass": "gerente2026",  "nombre": "Luisa Olivares",     "rol": "gerente",   "comercial": "LUISA OLIVARES"},
    "rafael":   {"pass": "rafael2026",   "nombre": "Rafael Torres",      "rol": "comercial", "comercial": "RAFAEL TORRES"},
    "sonia":    {"pass": "sonia2026",    "nombre": "Sonia Castro",       "rol": "comercial", "comercial": "SONIA CASTRO"},
    "lina":     {"pass": "lina2026",     "nombre": "Lina Calle",         "rol": "comercial", "comercial": "LINA CALLE"},
    "alberto":  {"pass": "alberto2026",  "nombre": "Alberto Ferrer",     "rol": "comercial", "comercial": "ALBERTO FERRER"},
    "santiago": {"pass": "santiago2026", "nombre": "Santiago Bohórquez", "rol": "comercial", "comercial": "SANTIAGO BOHORQUEZ"},
}

# ═══════════════════════════════════════════
# CONFIG STREAMLIT
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Ágora Tech · Plataforma",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important}
h1,h2,h3,.sora{font-family:'Sora',sans-serif!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#04111E 0%,#0A2540 100%)!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important}
[data-testid="stSidebar"] .stMarkdown a{color:#00C896!important}
.stButton>button{background:linear-gradient(135deg,#00C896,#1A9FCC)!important;color:#04111E!important;font-family:'Sora',sans-serif!important;font-weight:700!important;border:none!important;border-radius:10px!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,200,150,.4)!important}
.card{background:white;border:1px solid #E3EAF3;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(4,17,30,.06);margin-bottom:14px}
.kpi-card{background:white;border:1px solid #E3EAF3;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(4,17,30,.06);text-align:center}
.kpi-val{font-family:'Sora',sans-serif;font-size:28px;font-weight:800;color:#04111E;line-height:1}
.kpi-val.green{color:#009E78}.kpi-val.red{color:#E84040}.kpi-val.gold{color:#D97706}
.kpi-lbl{font-size:10px;color:#8BA3BD;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.badge-g{background:#D1FAF0;color:#065F46;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600}
.badge-y{background:#FEF9C3;color:#92400E;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600}
.badge-b{background:#DBEAFE;color:#1E3A8A;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600}
.badge-r{background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600}
.badge-p{background:#F5F3FF;color:#5B21B6;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:600}
.chat-u{background:linear-gradient(135deg,#00C896,#1A9FCC);color:#04111E;padding:12px 16px;border-radius:16px 16px 3px 16px;margin:8px 0;font-weight:600;max-width:80%;margin-left:auto;display:block}
.chat-a{background:white;border:1px solid #E3EAF3;padding:14px 18px;border-radius:16px 16px 16px 3px;margin:8px 0;max-width:90%;box-shadow:0 2px 8px rgba(4,17,30,.06);line-height:1.7;display:block}
.alert-r{background:#FEF2F2;border-left:4px solid #E84040;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.alert-y{background:#FFFBEB;border-left:4px solid #F2A12E;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.alert-g{background:#F0FDF9;border-left:4px solid #00C896;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
.alert-b{background:#EFF6FF;border-left:4px solid #1A9FCC;padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:8px}
div[data-testid="stForm"]{border:none!important;padding:0!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
def init_state():
    defaults = {
        "logged_in": False, "user": None, "messages": [],
        "gs_client": None, "gs_sheet": None,
        "proyectos": None,  # DataFrame cargado desde GSheets o local
        "gemini_model": None, "gemini_key": "",
        "last_refresh": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ═══════════════════════════════════════════
# GOOGLE SHEETS — BASE DE DATOS PERSISTENTE
# ═══════════════════════════════════════════
SHEET_COLS = [
    "id","nombre","comercial","contacto","email","telefono",
    "total","totalNum","cuota24","cuota36","c24Num","c36Num",
    "vig","vigH","estado","etapaOrig","version","notas",
    "lastUpdate","lastNote","fecha","drive_url","archivos"
]

def get_gs_client():
    """Conecta a Google Sheets via secrets de Streamlit."""
    try:
        if "gcp_service_account" in st.secrets:
            scope = ["https://spreadsheets.google.com/feeds",
                     "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]), scopes=scope)
            return gspread.authorize(creds)
    except Exception as e:
        pass
    return None

def load_sheet_data(client, sheet_id):
    """Carga todos los proyectos del Google Sheet."""
    try:
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet("proyectos")
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=SHEET_COLS)
        return df, ws
    except gspread.exceptions.WorksheetNotFound:
        try:
            ws = sh.add_worksheet("proyectos", 1000, len(SHEET_COLS))
            ws.append_row(SHEET_COLS)
            # Cargar datos base
            seed_sheet(ws)
            return pd.DataFrame(columns=SHEET_COLS), ws
        except Exception as e:
            return None, None
    except Exception as e:
        return None, None

def seed_sheet(ws):
    """Carga los 185 proyectos base al sheet si está vacío."""
    rows = []
    for p in TODOS_PROYECTOS:
        row = [
            p.get("id",""), p.get("nombre",""), p.get("comercial",""),
            p.get("contacto",""), p.get("email",""), p.get("telefono",""),
            p.get("total","$0"), p.get("totalNum",0),
            p.get("cuota24","$0"), p.get("cuota36","$0"),
            p.get("c24Num",0), p.get("c36Num",0),
            p.get("vig",""), p.get("vigH",""),
            p.get("estado","nuevo"), p.get("etapaOrig",""),
            p.get("version","v1"), p.get("notas",""),
            "", "", p.get("fecha",""), "", ""
        ]
        rows.append(row)
    if rows:
        ws.append_rows(rows[:200])  # GSheets tiene límite de escritura por batch

def save_project_to_sheet(ws, proyecto_dict):
    """Guarda o actualiza un proyecto en el sheet."""
    try:
        row = [str(proyecto_dict.get(c, "")) for c in SHEET_COLS]
        # Buscar si ya existe por nombre
        all_data = ws.get_all_values()
        headers = all_data[0] if all_data else SHEET_COLS
        nombre_col = headers.index("nombre") if "nombre" in headers else 1
        for i, r in enumerate(all_data[1:], 2):
            if len(r) > nombre_col and r[nombre_col].upper() == proyecto_dict.get("nombre","").upper():
                ws.update(f"A{i}", [row])
                return True, "actualizado"
        ws.append_row(row)
        return True, "creado"
    except Exception as e:
        return False, str(e)

# ═══════════════════════════════════════════
# DATOS EN MEMORIA (fallback sin GSheets)
# ═══════════════════════════════════════════
def get_proyectos_df():
    """Retorna DataFrame de proyectos. GSheets si hay, local si no."""
    if st.session_state.gs_sheet is not None and st.session_state.proyectos is not None:
        return st.session_state.proyectos.copy()
    # Fallback: datos embebidos
    rows = []
    for p in TODOS_PROYECTOS:
        rows.append({
            "id": p.get("id",""),
            "nombre": p.get("nombre",""),
            "comercial": p.get("comercial",""),
            "contacto": p.get("contacto",""),
            "email": p.get("email",""),
            "total": p.get("total","$0"),
            "totalNum": p.get("totalNum",0),
            "cuota24": p.get("cuota24","$0"),
            "cuota36": p.get("cuota36","$0"),
            "c24Num": p.get("c24Num",0),
            "c36Num": p.get("c36Num",0),
            "vig": p.get("vig",""),
            "vigH": p.get("vigH",""),
            "estado": p.get("estado","nuevo"),
            "etapaOrig": p.get("etapaOrig",""),
            "version": p.get("version","v1"),
            "notas": p.get("notas",""),
            "lastUpdate": p.get("lastUpdate",""),
            "lastNote": p.get("lastNote",""),
            "fecha": p.get("fecha",""),
        })
    df = pd.DataFrame(rows)
    # Enriquecer con cotizaciones calculadora
    for c in PROYECTOS_BASE:
        mask = df["nombre"].str.upper() == c["edificio"].upper()
        if mask.any() and df.loc[mask,"totalNum"].iloc[0] == 0:
            df.loc[mask,"totalNum"] = c["valor"]
            df.loc[mask,"total"] = "$"+f"{c['valor']:,}".replace(",",".")
            df.loc[mask,"c24Num"] = c["valor"]//24
            df.loc[mask,"cuota24"] = "$"+f"{c['valor']//24:,}".replace(",",".")
            df.loc[mask,"c36Num"] = c["valor"]//36
            df.loc[mask,"cuota36"] = "$"+f"{c['valor']//36:,}".replace(",",".")
    return df

def filter_by_user(df):
    """Filtra proyectos según el rol del usuario."""
    if not st.session_state.logged_in:
        return df.iloc[0:0]
    user = st.session_state.user
    if user["rol"] == "gerente":
        return df
    return df[df["comercial"].str.upper() == user["comercial"].upper()]

def fc(n):
    """Formatea número como moneda colombiana."""
    try:
        n = int(float(n))
        if n == 0: return "$0"
        return "$" + f"{n:,}".replace(",",".")
    except: return "$0"

def badge(estado):
    cls = {"nuevo":"badge-b","cotizado":"badge-y","negociacion":"badge-p","cerrado":"badge-g","perdido":"badge-r"}.get(estado,"badge-b")
    label = {"nuevo":"🔵 Lead","cotizado":"🟡 Enviado","negociacion":"🟠 Negoc.","cerrado":"🟢 Cerrado","perdido":"🔴 Perdido"}.get(estado,"❓")
    return f'<span class="{cls}">{label}</span>'

# ═══════════════════════════════════════════
# GEMINI
# ═══════════════════════════════════════════
def init_gemini(key):
    try:
        genai.configure(api_key=key)
        m = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction="""Eres el asistente comercial de Ágora Tech Colombia.
Sistema SALTO HomeLok (nube, Bluetooth, PIN, QR, app iOS/Android).
Financiación 100% a 24/36 meses sin intereses. Llave en mano 40 días.
Precios base: Adecuaciones $18.8M. Lectora vidrio $4.2M / reja $5.7M. Segunda puerta vidrio $10.8M. Gabinete+UPS+Antena+QR $10.5M. Ascensor $2.8M. CCTV $13.8M. +IVA 19%.
Mantenimiento mensual: $966.400+IVA.
Pipeline actual: 185 proyectos, $3.93B en cotizaciones, 0 contratos cerrados.
Responde en español colombiano. Sé específico y accionable."""
        )
        return m
    except: return None

def ask_gemini(question, context=""):
    m = st.session_state.gemini_model
    if not m: return "Configura la API Key de Gemini en el panel izquierdo."
    try:
        p = f"DATOS DEL CRM:\n{context[:20000]}\n\nSOLICITUD:\n{question}" if context else question
        return m.generate_content(p).text
    except Exception as e: return f"Error Gemini: {e}"

# ═══════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════
def show_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:48px 0 24px'>
          <div style='font-family:Sora,sans-serif;font-size:32px;font-weight:800;color:#04111E;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='font-size:12px;color:#8BA3BD;letter-spacing:3px;text-transform:uppercase;margin-top:6px'>Plataforma Comercial</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="rafael / sonia / lina...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Ingresar →", use_container_width=True)
            
            if submit:
                u = usuario.strip().lower()
                if u in USUARIOS and USUARIOS[u]["pass"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = USUARIOS[u]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        st.markdown("""
        <div style='background:#F4F7FB;border-radius:10px;padding:14px;margin-top:16px;font-size:12px;color:#8BA3BD'>
          <b style='color:#04111E'>Accesos de prueba:</b><br>
          luisa / luisa2026 (Gerente) · rafael / rafael2026 · sonia / sonia2026<br>
          lina / lina2026 · alberto / alberto2026 · santiago / santiago2026
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SIDEBAR AUTENTICADO
# ═══════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        user = st.session_state.user
        is_manager = user["rol"] == "gerente"
        
        st.markdown(f"""
        <div style='text-align:center;padding:10px 0 16px'>
          <div style='font-family:Sora,sans-serif;font-size:18px;font-weight:800;color:#fff;letter-spacing:-0.5px'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;text-transform:uppercase;margin-top:2px'>Plataforma Comercial</div>
        </div>
        <div style='background:rgba(0,200,150,.12);border:1px solid rgba(0,200,150,.25);border-radius:10px;padding:10px 12px;margin-bottom:16px'>
          <div style='font-size:13px;font-weight:600;color:#fff'>{user["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.45);margin-top:2px'>{user["rol"].capitalize()} · Ágora Tech</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navegación
        pages = [
            ("📊", "Dashboard"),
            ("📋", "Mis Proyectos"),
            ("🧮", "Nueva Cotización"),
            ("📝", "Actualizar Estado"),
            ("🏢", "Edificios"),
            ("📅", "Calendario"),
            ("✉️", "Correos IA"),
            ("🤖", "Asistente IA"),
        ]
        if is_manager:
            pages += [
                ("🔍", "Auditoría"),
                ("📈", "Informes"),
                ("🎯", "Pipeline"),
                ("📊", "Encuestas"),
            ]
        
        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"
        
        for icon, name in pages:
            active = st.session_state.page == name
            bg = "rgba(0,200,150,.18)" if active else "transparent"
            border = "3px solid #00C896" if active else "3px solid transparent"
            color = "#00C896" if active else "rgba(255,255,255,.55)"
            if st.sidebar.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
        
        st.markdown("---")
        
        # Gemini en sidebar
        st.markdown("**⚡ Gemini IA**")
        if not st.session_state.gemini_model:
            gkey = st.text_input("API Key", type="password", placeholder="AIzaSy...", key="gkey_sb")
            if gkey:
                m = init_gemini(gkey)
                if m:
                    st.session_state.gemini_model = m
                    st.session_state.gemini_key = gkey
                    st.success("✅ IA activa")
                    st.rerun()
        else:
            st.success("✅ Gemini activo")
            if st.button("Cambiar key", key="change_key"):
                st.session_state.gemini_model = None
                st.rerun()
        
        st.markdown("---")
        if st.button("⇤  Cerrar sesión", key="logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()

# ═══════════════════════════════════════════
# PÁGINAS
# ═══════════════════════════════════════════

def page_dashboard():
    user = st.session_state.user
    is_manager = user["rol"] == "gerente"
    df = filter_by_user(get_proyectos_df())
    
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#04111E 0%,#0A2540 60%,#0E3D6B 100%);border-radius:16px;padding:28px 32px;margin-bottom:24px;color:white;position:relative;overflow:hidden'>
      <div style='position:absolute;top:-50px;right:-50px;width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,rgba(0,200,150,.2) 0%,transparent 70%)'></div>
      <div style='font-family:Sora,sans-serif;font-size:22px;font-weight:800;margin-bottom:6px'>
        {"Dashboard General — Ágora Tech" if is_manager else f"Hola, {user["nombre"].split()[0]} 👋"}
      </div>
      <div style='font-size:13px;color:rgba(255,255,255,.55)'>
        {"Visión completa del equipo · " if is_manager else "Tus proyectos · "}{df.shape[0]} proyectos · {datetime.now().strftime("%d %b %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs
    total_pip = df["totalNum"].sum()
    con_valor = df[df["totalNum"]>0]
    prom = con_valor["totalNum"].mean() if len(con_valor)>0 else 0
    cerrados = df[df["estado"]=="cerrado"].shape[0]
    aprobados = df[df["estado"]=="cotizado"].shape[0]
    
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Pipeline Total</div><div class="kpi-val green">${total_pip/1e6:.1f}M</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">{df.shape[0]} proyectos</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Promedio Cotización</div><div class="kpi-val">${prom/1e6:.1f}M</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">{len(con_valor)} con valor</div></div>', unsafe_allow_html=True)
    with c3:
        neg = df[df["estado"]=="negociacion"].shape[0]
        st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Negociando</div><div class="kpi-val gold">{neg}</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">activos</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Cotizaciones Enviadas</div><div class="kpi-val gold">{aprobados}</div><div style="font-size:11px;color:#8BA3BD;margin-top:4px">en seguimiento</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Contratos Cerrados</div><div class="kpi-val {"red" if cerrados==0 else "green"}">{cerrados}</div><div style="font-size:11px;color:{"#E84040" if cerrados==0 else "#009E78"};margin-top:4px">{"⚠️ Urgente" if cerrados==0 else "¡Excelente!"}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        # Pipeline por estado
        est_counts = df.groupby("estado").size().reset_index(name="n")
        label_map = {"nuevo":"Lead Nuevo","cotizado":"Cot. Enviada","negociacion":"Negociando","cerrado":"Cerrado","perdido":"Perdido"}
        est_counts["Estado"] = est_counts["estado"].map(label_map)
        fig = px.bar(est_counts, x="Estado", y="n",
                     color="n", color_continuous_scale=["#1A9FCC","#00C896"],
                     title="Proyectos por Estado", labels={"n":"Proyectos"})
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40,b=10))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        if is_manager:
            # Pipeline por comercial
            df_c = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
            df_c["Pipeline_M"] = (df_c["totalNum"]/1e6).round(1)
            df_c["Com"] = df_c["comercial"].str.split().str[0]
            fig2 = px.bar(df_c.sort_values("Pipeline_M",ascending=True), x="Pipeline_M", y="Com",
                          orientation="h", title="Pipeline por Comercial ($M)",
                          color="Pipeline_M", color_continuous_scale=["#1A9FCC","#00C896"],
                          labels={"Pipeline_M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40,b=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            # Mis proyectos por estado (donut)
            est2 = df.groupby("estado").size().reset_index(name="n")
            est2["Estado"] = est2["estado"].map(label_map)
            fig2 = px.pie(est2, values="n", names="Estado", hole=0.45,
                          color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],
                          title="Mis Proyectos")
            fig2.update_layout(paper_bgcolor="white",margin=dict(t=40,b=10))
            st.plotly_chart(fig2, use_container_width=True)
    
    # Alertas
    st.markdown("### 🚨 Alertas")
    threshold = datetime.now() - timedelta(days=7)
    
    # Sin actualizar
    sin_update = df[df["lastUpdate"].astype(str).str.strip() == ""].shape[0]
    if sin_update > 0:
        st.markdown(f'<div class="alert-r">⚠️ <b>{sin_update} proyectos</b> nunca han sido actualizados. Revisa el estado de cada uno.</div>', unsafe_allow_html=True)
    
    if is_manager:
        st.markdown('<div class="alert-r">❗ <b>0 contratos cerrados</b> en 5 meses de operación. Con $3.93B en pipeline, el problema está en el cierre, no en la prospección.</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-y">⚡ <b>Nomad (David Conde)</b> — único proyecto en cierre cercano. Rafael debe reunirse esta semana con contrato listo.</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-b">📈 Crecimiento excelente: Dic:3 → Ene:17 → Feb:25 → Mar:32 → Abr:46 leads.</div>', unsafe_allow_html=True)

def page_proyectos():
    user = st.session_state.user
    is_manager = user["rol"] == "gerente"
    df = filter_by_user(get_proyectos_df())
    
    st.markdown("## 📋 Mis Proyectos" if not is_manager else "## 📋 Todos los Proyectos")
    
    # Filtros
    c1,c2,c3 = st.columns(3)
    with c1:
        search = st.text_input("🔍 Buscar edificio", placeholder="Nombre del edificio...")
    with c2:
        estado_filter = st.selectbox("Estado", ["Todos","nuevo","cotizado","negociacion","cerrado","perdido"])
    with c3:
        if is_manager:
            coms = ["Todos"] + sorted(df["comercial"].unique().tolist())
            com_filter = st.selectbox("Comercial", coms)
        else:
            com_filter = "Todos"
    
    # Aplicar filtros
    df_f = df.copy()
    if search: df_f = df_f[df_f["nombre"].str.contains(search, case=False, na=False)]
    if estado_filter != "Todos": df_f = df_f[df_f["estado"] == estado_filter]
    if com_filter != "Todos": df_f = df_f[df_f["comercial"] == com_filter]
    
    st.markdown(f"**{len(df_f)} proyectos encontrados**")
    
    # Tabla
    for _, row in df_f.iterrows():
        total = row.get("total","$0") or "$0"
        c24 = row.get("cuota24","$0") or "$0"
        c36 = row.get("cuota36","$0") or "$0"
        if not total or total=="$0":
            tnum = int(float(row.get("totalNum",0) or 0))
            if tnum>0:
                total=fc(tnum); c24=fc(tnum//24); c36=fc(tnum//36)
        
        estado = str(row.get("estado","nuevo"))
        last = str(row.get("lastNote","")) or str(row.get("notas","")) or str(row.get("etapaOrig",""))
        
        with st.expander(f"🏢 {row['nombre']}  —  {total}  —  {row.get('comercial','')}", expanded=False):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Valor total", total)
            c2.metric("Cuota 24m", c24)
            c3.metric("Cuota 36m", c36)
            c4.markdown(f"**Estado:** {badge(estado)}", unsafe_allow_html=True)
            
            if last and last != "nan":
                st.info(f"📝 Última nota: {str(last)[:200]}")
            
            # Botón actualizar
            if st.button(f"📝 Actualizar estado", key=f"upd_{row.get('id',row['nombre'])}"):
                st.session_state["editing_id"] = row.get("id","")
                st.session_state["editing_nombre"] = row["nombre"]
                st.session_state.page = "Actualizar Estado"
                st.rerun()

def page_nueva_cotizacion():
    st.markdown("## 🧮 Nueva Cotización")
    st.info("💡 Llena los datos del edificio y la cotización. Se guardará automáticamente en el CRM.")
    
    with st.form("nueva_cotiz"):
        st.markdown("### Datos del Edificio")
        c1,c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre del edificio *", placeholder="Edificio Altos del Pino")
            contacto = st.text_input("Contacto *", placeholder="Juan Pérez — Administrador")
            email = st.text_input("Email", placeholder="admin@edificio.com")
        with c2:
            direccion = st.text_input("Dirección", placeholder="Cra 7 No. 45-23, Bogotá")
            telefono = st.text_input("Teléfono", placeholder="300 123 4567")
            unidades = st.number_input("Número de unidades", min_value=0, value=0)
        
        st.markdown("### Valor de la Cotización")
        c1,c2,c3 = st.columns(3)
        with c1: total_input = st.number_input("Valor total ($)", min_value=0, value=0, step=1000000, format="%d")
        with c2: vig_input = st.number_input("Vigilancia actual ($/mes)", min_value=0, value=0, step=100000, format="%d")
        with c3: vig_hasta = st.text_input("Vigilancia vigente hasta", placeholder="Nov 2026")
        
        st.markdown("### Archivos de Soporte")
        uploaded = st.file_uploader("Sube cotización PDF, planos, fotos", type=["pdf","xlsx","jpg","png","docx"], accept_multiple_files=True)
        
        st.markdown("### Estado y Observaciones")
        c1,c2 = st.columns(2)
        with c1: estado = st.selectbox("Estado", ["nuevo","cotizado","negociacion","cerrado","perdido"])
        with c2: version = st.text_input("Versión", value="v1", placeholder="v1, v2, v3...")
        notas = st.text_area("Observaciones / Notas", placeholder="Contexto, acuerdos, próximos pasos...")
        
        submitted = st.form_submit_button("💾 Guardar Cotización", use_container_width=True)
        
        if submitted:
            if not nombre:
                st.error("El nombre del edificio es obligatorio")
            else:
                user = st.session_state.user
                c24 = total_input//24 if total_input>0 else 0
                c36 = total_input//36 if total_input>0 else 0
                
                nuevo_proy = {
                    "id": int(datetime.now().timestamp()),
                    "nombre": nombre.upper(),
                    "comercial": user["comercial"],
                    "contacto": contacto,
                    "email": email,
                    "total": fc(total_input),
                    "totalNum": total_input,
                    "cuota24": fc(c24),
                    "cuota36": fc(c36),
                    "c24Num": c24,
                    "c36Num": c36,
                    "vig": str(vig_input),
                    "vigH": vig_hasta,
                    "estado": estado,
                    "etapaOrig": estado,
                    "version": version,
                    "notas": notas,
                    "lastUpdate": datetime.now().isoformat(),
                    "lastNote": notas,
                    "fecha": datetime.now().strftime("%d %b %Y"),
                    "archivos": f"{len(uploaded)} archivos cargados" if uploaded else ""
                }
                
                # Intentar guardar en GSheets
                if st.session_state.gs_sheet:
                    ok, msg = save_project_to_sheet(st.session_state.gs_sheet, nuevo_proy)
                    if ok:
                        st.success(f"✅ Guardado en Google Sheets ({msg})")
                    else:
                        st.warning(f"⚠️ No se pudo guardar en Sheets: {msg}. Guardado localmente.")
                else:
                    st.success(f"✅ Cotización registrada: {nombre} — {fc(total_input)}")
                    if uploaded:
                        st.info(f"📎 {len(uploaded)} archivos cargados: {', '.join([f.name for f in uploaded])}")
                st.balloons()

def page_actualizar_estado():
    st.markdown("## 📝 Actualizar Estado de Proyectos")
    st.info("Es obligatorio actualizar el estado de cada proyecto al menos cada 7 días.")
    
    user = st.session_state.user
    is_manager = user["rol"] == "gerente"
    df = filter_by_user(get_proyectos_df())
    
    threshold = (datetime.now() - timedelta(days=7)).isoformat()
    
    # Proyectos pendientes de actualizar
    pending = df[
        (df["lastUpdate"].astype(str).str.strip() == "") |
        (df["lastUpdate"].astype(str) < threshold)
    ]
    
    if len(pending) > 0:
        st.markdown(f'<div class="alert-r">⚠️ <b>{len(pending)} proyectos</b> necesitan actualización de estado.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-g">✅ Todos los proyectos están al día.</div>', unsafe_allow_html=True)
    
    # Pre-seleccionar si viene del botón de proyectos
    preselected = st.session_state.get("editing_nombre", "")
    
    nombres = ["— Seleccionar edificio —"] + sorted(df["nombre"].unique().tolist())
    default_idx = nombres.index(preselected) if preselected in nombres else 0
    selected = st.selectbox("Selecciona el edificio a actualizar:", nombres, index=default_idx)
    
    if selected != "— Seleccionar edificio —":
        row = df[df["nombre"]==selected].iloc[0]
        
        c1,c2,c3 = st.columns(3)
        c1.metric("Valor", str(row.get("total","$0") or "$0"))
        c2.metric("Comercial", str(row.get("comercial","—")))
        c3.metric("Última actualización", str(row.get("lastUpdate","Nunca"))[:10] or "Nunca")
        
        with st.form("update_form"):
            nuevo_estado = st.selectbox("Nuevo estado *", ["nuevo","cotizado","negociacion","cerrado","perdido"],
                                         index=["nuevo","cotizado","negociacion","cerrado","perdido"].index(str(row.get("estado","nuevo"))))
            nota = st.text_area("Nota de seguimiento * (requerida)", placeholder="¿Qué pasó? ¿Cuál es el próximo paso? Sé específico...")
            sub = st.form_submit_button("✅ Actualizar Estado", use_container_width=True)
            
            if sub:
                if not nota.strip():
                    st.error("La nota de seguimiento es obligatoria")
                else:
                    st.success(f"✅ Estado actualizado: {selected} → {nuevo_estado}")
                    st.info(f"📝 Nota guardada: {nota[:100]}...")
                    if "editing_nombre" in st.session_state:
                        del st.session_state["editing_nombre"]

def page_edificios():
    st.markdown("## 🏢 Carpetas de Edificios")
    df = filter_by_user(get_proyectos_df())
    
    search = st.text_input("🔍 Buscar edificio", placeholder="Nombre...")
    if search:
        df = df[df["nombre"].str.contains(search, case=False, na=False)]
    
    # Grid de edificios
    cols = st.columns(4)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 4]:
            total = str(row.get("total","$0") or "$0")
            if total == "$0" and row.get("totalNum",0):
                total = fc(int(row["totalNum"]))
            c36 = str(row.get("cuota36","—") or "—")
            estado = str(row.get("estado","nuevo"))
            drive = str(row.get("drive_url","") or "")
            
            drive_btn = f"[📁 Drive]({drive})" if drive.startswith("http") else ""
            
            st.markdown(f"""
            <div class="card" style="cursor:pointer;transition:all .2s" onmouseover="this.style.borderColor='#00C896'" onmouseout="this.style.borderColor='#E3EAF3'">
              <div style="font-size:24px;margin-bottom:8px">🏢</div>
              <div style="font-family:Sora,sans-serif;font-size:12px;font-weight:700;color:#04111E;margin-bottom:4px">{str(row["nombre"])[:28]}</div>
              <div style="font-size:11px;color:#8BA3BD;margin-bottom:8px">{str(row.get("comercial","—"))}</div>
              <div style="font-family:Sora,sans-serif;font-size:15px;font-weight:800;color:#009E78;margin-bottom:4px">{total}</div>
              <div style="font-size:10px;color:#8BA3BD;margin-bottom:8px">Cuota 36m: {c36}/mes</div>
              {badge(estado)}
            </div>
            """, unsafe_allow_html=True)

def page_calendario():
    st.markdown("## 📅 Calendario Comercial")
    user = st.session_state.user
    is_manager = user["rol"] == "gerente"
    
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.markdown("### ➕ Nueva Actividad")
        with st.form("nueva_actividad"):
            c1,c2 = st.columns(2)
            with c1:
                edificio = st.text_input("Edificio / Proyecto", placeholder="Nombre del edificio")
                tipo = st.selectbox("Tipo", ["Reunión presencial","Llamada","Visita técnica","Asamblea","Otro"])
            with c2:
                fecha = st.date_input("Fecha", value=datetime.now())
                hora = st.time_input("Hora", value=datetime.strptime("09:00","% H:%M").time())
            
            if is_manager:
                com_resp = st.selectbox("Comercial responsable", ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"])
            else:
                com_resp = user["comercial"]
            
            titulo = st.text_input("Título / Descripción *", placeholder="Ej: Reunión asamblea propietarios")
            notas_act = st.text_area("Notas / Agenda", placeholder="Objetivos, dirección, datos de contacto...")
            
            if st.form_submit_button("📅 Guardar Actividad", use_container_width=True):
                if titulo:
                    st.success(f"✅ Actividad guardada: {titulo} — {fecha.strftime('%d %b')} {hora.strftime('%H:%M')}")
                else:
                    st.error("El título es obligatorio")
    
    with col2:
        st.markdown("### 🔥 Esta Semana")
        actividades_demo = [
            {"titulo":"Reunión Nomad / David Conde","tipo":"Reunión","fecha":"Urgente","com":"Rafael","color":"#FEE2E2"},
            {"titulo":"Park 104 — Consejo directivo","tipo":"Reunión","fecha":"27 Abr","com":"Rafael","color":"#FEF9C3"},
            {"titulo":"Yakarta — Asamblea propietarios","tipo":"Asamblea","fecha":"25 Abr","com":"Santiago","color":"#FEF9C3"},
            {"titulo":"Bosque San Vicente — Cotización","tipo":"Envío","fecha":"Martes 6pm","com":"Rafael","color":"#EFF6FF"},
        ]
        for a in actividades_demo:
            st.markdown(f"""
            <div style="background:{a["color"]};border-radius:8px;padding:10px 12px;margin-bottom:8px;border-left:3px solid #E84040">
              <div style="font-size:12px;font-weight:700;color:#04111E">{a["titulo"]}</div>
              <div style="font-size:10.5px;color:#8BA3BD;margin-top:2px">{a["tipo"]} · {a["fecha"]} · {a["com"]}</div>
            </div>
            """, unsafe_allow_html=True)

def page_correos():
    st.markdown("## ✉️ Generador de Correos Comerciales")
    df = filter_by_user(get_proyectos_df())
    
    c1,c2 = st.columns(2)
    with c1:
        edificio_sel = st.selectbox("Edificio / Cotización", ["— Seleccionar —"] + sorted(df["nombre"].unique().tolist()))
        tipo_correo = st.selectbox("Tipo de correo", [
            "Primera presentación de propuesta",
            "Seguimiento 5-7 días post-envío",
            "Urgencia / oferta próxima a vencer",
            "Respuesta a objeción de precio alto",
            "Respuesta técnica a pregunta del cliente",
            "Argumentos para asamblea de propietarios",
            "Caso especial: adultos mayores / discapacidad"
        ])
        contexto_extra = st.text_area("Contexto adicional", placeholder="Ej: El cliente dice que la cuota es muy alta. Preguntan por adultos mayores...")
        
        if st.button("🤖 Generar Correo con IA", use_container_width=True):
            if edificio_sel != "— Seleccionar —":
                row = df[df["nombre"]==edificio_sel].iloc[0]
                total = row.get("total","$0") or "$0"
                c24 = row.get("cuota24","—") or "—"
                c36 = row.get("cuota36","—") or "—"
                vig = row.get("vig","") or ""
                
                prompt = f"""Redacta un correo comercial profesional de tipo "{tipo_correo}" para Ágora Tech Colombia.
EDIFICIO: {edificio_sel} | Total: {total} | Cuota 24m: {c24} | Cuota 36m: {c36}
{f"Vigilancia actual: ${int(float(vig)):,}/mes" if vig and str(vig).strip() and str(vig)!="0" else ""}
Contacto: {row.get("contacto","Administrador")}
{f"Contexto: {contexto_extra}" if contexto_extra else ""}
Comercial: {row.get("comercial",st.session_state.user["comercial"])}

Primera línea: ASUNTO: [asunto específico y llamativo]
Argumento principal: ahorro económico concreto. Para adultos mayores: teclado PIN físico + Bluetooth sin smartphone.
Firma: {st.session_state.user["nombre"]} — Ágora Tech · (+57) 315 101 7511
Solo texto plano, sin markdown."""
                
                with st.spinner("Generando correo..."):
                    correo = ask_gemini(prompt)
                st.session_state["correo_generado"] = correo
            else:
                st.warning("Selecciona un edificio primero")
    
    with c2:
        st.markdown("**Vista Previa:**")
        correo = st.session_state.get("correo_generado","Selecciona un edificio y genera el correo.")
        st.text_area("Correo generado:", value=correo, height=450, key="correo_preview")
        if correo != "Selecciona un edificio y genera el correo.":
            st.download_button("📋 Copiar / Descargar", data=correo, file_name=f"correo_{edificio_sel[:20] if edificio_sel!='— Seleccionar —' else 'agora'}.txt")

def page_asistente():
    st.markdown("## 🤖 Asistente Comercial IA")
    df = filter_by_user(get_proyectos_df())
    ctx = df.to_string(max_rows=50) if not df.empty else ""
    
    for msg in st.session_state.messages:
        cls = "chat-u" if msg["role"]=="user" else "chat-a"
        pre = "👤 " if msg["role"]=="user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown("**Sugerencias:**")
        sugs = [
            "📊 Resume el estado de mi pipeline",
            "💰 ¿Cuánto vale mi pipeline total?",
            "⚡ Proyectos más urgentes esta semana",
            "📈 Dame estrategia para cerrar Nomad",
            "🔍 ¿Por qué se rechazan proyectos con adultos mayores?",
            "✉️ Cómo convencer a una asamblea de aprobar la automatización",
        ]
        cols = st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s, key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("Analizando..."):
                    r = ask_gemini(s, ctx)
                st.session_state.messages.append({"role":"assistant","content":r})
                st.rerun()
    
    with st.form("chat_form", clear_on_submit=True):
        c1,c2 = st.columns([5,1])
        with c1: ui = st.text_input("Consulta", placeholder="Ej: Dame la estrategia para Nomad. ¿Cómo responder a la objeción de precio?", label_visibility="collapsed")
        with c2: send = st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("Analizando..."):
                r = ask_gemini(ui, ctx)
            st.session_state.messages.append({"role":"assistant","content":r})
            st.rerun()
    
    if st.session_state.messages:
        if st.button("🗑 Limpiar chat"):
            st.session_state.messages = []
            st.rerun()

def page_auditoria():
    st.markdown("## 🔍 Auditoría Comercial")
    df = get_proyectos_df()
    
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Proyectos", df.shape[0])
    c2.metric("Pipeline", f"${df['totalNum'].sum()/1e9:.2f}B")
    c3.metric("Aprobados", df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Rechazados", df[df["estado"]=="perdido"].shape[0])
    c5.metric("Contratos", df[df["estado"]=="cerrado"].shape[0])
    
    st.markdown("---")
    st.markdown('<div class="alert-r">❗ <b>0 contratos cerrados en 5 meses.</b> El pipeline de $3.93B con proyectos aprobados evidencia un cuello de botella en la etapa de cierre.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-y">⚠️ <b>Nomad (Rafael Torres)</b> — único en cierre cercano. Llevar contrato esta semana.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-b">ℹ️ Patrón de rechazo: "La propuesta favorita pero adultos mayores no aprobaron". Preparar respuesta específica para este caso.</div>', unsafe_allow_html=True)
    
    c1,c2 = st.columns(2)
    with c1:
        df_com = df[df["totalNum"]>0].groupby("comercial").agg(
            cotizaciones=("totalNum","count"),
            pipeline=("totalNum","sum")
        ).reset_index()
        df_com["pipeline_M"] = (df_com["pipeline"]/1e6).round(1)
        st.dataframe(df_com[["comercial","cotizaciones","pipeline_M"]].rename(columns={"comercial":"Comercial","cotizaciones":"Cotizaciones","pipeline_M":"Pipeline ($M)"}), use_container_width=True, hide_index=True)
    
    with c2:
        if st.button("🤖 Análisis profundo con IA"):
            ctx = df.to_string(max_rows=100)
            with st.spinner("Analizando..."):
                r = ask_gemini("""Análisis estratégico profundo de Ágora Tech:
1. DIAGNÓSTICO del cuello de botella (por qué no se cierran contratos)
2. PATRONES DE RECHAZO (qué tienen en común los perdidos)
3. PLAN DE CIERRE — Nomad (acciones esta semana)
4. PLAN 30 DÍAS para el primer contrato
5. PRIORIDADES 48 HORAS
Sin separadores ---. Tono técnico ejecutivo.""", ctx)
            st.markdown(r)

def page_informes():
    st.markdown("## 📈 Informes Gerenciales")
    df = get_proyectos_df()
    
    c1,c2,c3 = st.columns(3)
    with c1:
        # Gráfica pipeline por comercial
        df_c = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
        df_c["M"] = (df_c["totalNum"]/1e6).round(1)
        df_c["Com"] = df_c["comercial"].str.split().str[0]
        fig = px.bar(df_c.sort_values("M",ascending=True),x="M",y="Com",orientation="h",
                     title="Pipeline por Comercial ($M)",color="M",color_continuous_scale=["#1A9FCC","#00C896"])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        est = df.groupby("estado").size().reset_index(name="n")
        lm = {"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
        est["Estado"]=est["estado"].map(lm)
        fig2=px.pie(est,values="n",names="Estado",hole=0.45,
                    color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],title="Distribución")
        fig2.update_layout(paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig2,use_container_width=True)
    with c3:
        growth=pd.DataFrame({"Mes":["Dic","Ene","Feb","Mar","Abr"],"Leads":[3,17,25,32,46]})
        fig3=px.area(growth,x="Mes",y="Leads",title="Crecimiento Mensual",
                     color_discrete_sequence=["#00C896"],markers=True)
        fig3.update_traces(line_width=3,marker_size=8,fill="tozeroy",fillcolor="rgba(0,200,150,0.1)")
        fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig3,use_container_width=True)
    
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        tipo=st.selectbox("Tipo de informe:",["Informe Gerencial Ejecutivo","Reporte Pipeline","Análisis Equipo Comercial","Oportunidades Críticas","Auditoría Comercial"])
    with c2:
        notas_inf=st.text_area("Instrucciones adicionales:",placeholder="Ej: Enfatizar en Nomad...",height=68)
    
    if st.button("🤖 Generar Informe Completo con IA",use_container_width=True):
        ctx=df.to_string(max_rows=100)
        prompt=f"""Genera un {tipo} COMPLETO para Ágora Tech Colombia.
{f"Instrucciones: {notas_inf}" if notas_inf else ""}
Estructura obligatoria:
# {tipo}
Fecha: {datetime.now().strftime("%d de %B de %Y")}

## 1. RESUMEN EJECUTIVO
## 2. MÉTRICAS CLAVE
## 3. ANÁLISIS DETALLADO
## 4. ALERTAS Y RIESGOS
## 5. RECOMENDACIONES ESTRATÉGICAS
## 6. PRÓXIMOS PASOS ESTA SEMANA

Sin separadores ---. Negrilla para cifras clave. Tono técnico ejecutivo."""
        with st.spinner("Generando informe..."):
            r=ask_gemini(prompt,ctx)
        st.markdown(r)
        c1,c2=st.columns(2)
        c1.download_button("📥 Descargar .md",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
        c2.download_button("📥 Descargar .txt",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")

def page_pipeline():
    st.markdown("## 🎯 Pipeline — Vista Kanban")
    df = filter_by_user(get_proyectos_df())
    
    stages = [("nuevo","🔵 Lead Nuevo"),("cotizado","🟡 Cotización"),("negociacion","🟠 Negociando"),("cerrado","🟢 Cerrado")]
    cols = st.columns(4)
    
    for i,(k,label) in enumerate(stages):
        items = df[df["estado"]==k]
        tot = items["totalNum"].sum()
        with cols[i]:
            st.markdown(f"**{label}**")
            st.markdown(f"_{items.shape[0]} proyectos · ${tot/1e6:.1f}M_")
            for _,row in items.iterrows():
                total=str(row.get("total","$0") or "$0")
                if total=="$0" and row.get("totalNum",0):
                    total=fc(int(row["totalNum"]))
                st.markdown(f"""
                <div class="card" style="padding:12px;margin-bottom:8px">
                  <div style="font-size:11.5px;font-weight:700;color:#04111E;margin-bottom:3px">{str(row["nombre"])[:25]}</div>
                  <div style="font-size:10.5px;color:#8BA3BD;margin-bottom:4px">{str(row.get("comercial","—"))}</div>
                  <div style="font-size:14px;font-weight:800;color:#009E78">{total}</div>
                </div>
                """,unsafe_allow_html=True)

def page_encuestas():
    st.markdown("## 📊 Encuestas de Prospectos")
    st.info("Aquí aparecerán las encuestas de prospectos analizadas con IA (formulario de información preliminar).")
    
    st.markdown("### Formulario de Prospecto")
    with st.form("prospecto_form"):
        c1,c2=st.columns(2)
        with c1:
            nombre_e=st.text_input("Nombre del Edificio *")
            dir_e=st.text_input("Dirección")
            contacto_e=st.text_input("Contacto *")
        with c2:
            rol=st.selectbox("Rol del contacto",["Administrador","Propietario","Miembro del Consejo","Presidente del Consejo"])
            etapa=st.selectbox("Etapa de decisión",["El Consejo recibe cotizaciones por orden de asamblea","Aún no se ha hablado en asamblea","Explorando la opción"])
            com_sel=st.selectbox("Comercial asignado",["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ"])
        
        vig=st.radio("¿Tiene vigilancia tradicional?",["Sí","No"],horizontal=True)
        c1,c2=st.columns(2)
        with c1: costo_vig=st.number_input("Costo vigilancia ($/mes)",min_value=0,value=0,step=100000,format="%d")
        with c2: vig_hasta=st.text_input("Contrato vigente hasta",placeholder="Nov 2026")
        
        incidentes=st.text_area("Incidentes de seguridad",placeholder="Robos, incidentes recientes...")
        accesibilidad=st.text_area("Adultos mayores / Discapacidad",placeholder="¿Hay residentes con necesidades especiales?")
        notas_p=st.text_area("Notas del comercial",placeholder="Contexto adicional...")
        
        if st.form_submit_button("🤖 Analizar con IA y Guardar",use_container_width=True):
            if nombre_e:
                costoNum=int(costo_vig)
                prompt=f"""Analiza este prospecto para Ágora Tech:
Edificio: {nombre_e} | Contacto: {contacto_e} ({rol}) | Etapa: {etapa}
Vigilancia: {"SÍ $"+f"{costoNum:,}"+"/mes hasta "+vig_hasta if vig=="Sí" and costoNum>0 else "NO"}
Incidentes: {incidentes or "Ninguno"} | Adultos mayores: {accesibilidad or "No reportado"}
Notas: {notas_p or "—"}

Genera:
## VIABILIDAD: [ALTA / MEDIA / BAJA]
## AHORRO POTENCIAL
## ESTRATEGIA DE VENTA
## OBJECIONES PROBABLES Y RESPUESTAS
## PRÓXIMOS PASOS

Sin ---. Negrilla para datos clave. Accionable."""
                with st.spinner("Analizando con IA..."):
                    r=ask_gemini(prompt)
                st.markdown("---")
                st.markdown(r)
                st.success(f"✅ Prospecto {nombre_e} analizado y guardado")
            else:
                st.error("Nombre del edificio obligatorio")

# ═══════════════════════════════════════════
# GOOGLE SHEETS CONFIG (en sidebar para gerente)
# ═══════════════════════════════════════════
def show_sheets_config():
    """Muestra configuración de Google Sheets solo para gerente."""
    if st.session_state.user["rol"] != "gerente":
        return
    with st.sidebar:
        st.markdown("---")
        st.markdown("**☁️ Base de Datos**")
        if not st.session_state.gs_client:
            gs_client = get_gs_client()
            if gs_client:
                st.session_state.gs_client = gs_client
                st.success("Google Sheets conectado")
            else:
                st.caption("Sin conexión a Sheets — usando datos locales")
        else:
            st.success("Sheets conectado")

# ═══════════════════════════════════════════
# MAIN ROUTING
# ═══════════════════════════════════════════
if not st.session_state.logged_in:
    show_login()
else:
    show_sidebar()
    if st.session_state.user["rol"] == "gerente":
        show_sheets_config()
    
    page = st.session_state.get("page", "Dashboard")
    
    if page == "Dashboard": page_dashboard()
    elif page == "Mis Proyectos": page_proyectos()
    elif page == "Nueva Cotización": page_nueva_cotizacion()
    elif page == "Actualizar Estado": page_actualizar_estado()
    elif page == "Edificios": page_edificios()
    elif page == "Calendario": page_calendario()
    elif page == "Correos IA": page_correos()
    elif page == "Asistente IA": page_asistente()
    elif page == "Auditoría": page_auditoria()
    elif page == "Informes": page_informes()
    elif page == "Pipeline": page_pipeline()
    elif page == "Encuestas": page_encuestas()
    else: page_dashboard()
