from xml.dom.minidom import parse
import base64
from M2Crypto import RSA
from lxml import etree as ET
import hashlib
import subprocess
from datetime import datetime

print("""
---------------------------------------------------------------------
| AL HACER USO DE ESTE SCRIPT DEBE TOMAR EN CUENTA QUE LAS RUTAS DE |
|  LOS ARCHIVOS NO DEBE IR ENTRE COMILLAS Y QUE EL XML DEL CUAL SE  |
| QUIERE EXTRAER LOS COMPLEMENTOS DEBE ESTAR PREVIAMENTE MODIFICADO |
|         ASI COMO TAMBIEN DEBE DEJAR EN BLANCO LOS CAMPOS:         |
|            NoCertificado, Certificado, Serial y fecha             |
--------------------------------------------------------------------\n""")

get_serial = ""
get_certificado = ""
get_sello = ""

fecha = datetime.now().strftime("%Y-%m-%d")+"T"+datetime.now().strftime("%H:%M:%S")

ruta_cadena = raw_input("Archivo Cadena Original: ")
ruta_cer = raw_input("Archivo CER: ")
ruta_xml = raw_input("Archivo XML: ")
ruta_pem = raw_input("Archivo KEY.PEM: ")

certificado = subprocess.check_output('openssl x509 -inform DER -in ' + str(ruta_cer), shell=True).replace("\n", "")
serial = subprocess.check_output('openssl x509 -inform DER -in ' + str(ruta_cer) + ' -noout -serial', shell=True)

indice = 7
while indice < len(serial):
	if indice % 2 == 0:
		get_serial += serial[indice]
	indice += 1

indice = 27
while indice < len(certificado) - 25:
	get_certificado += certificado[indice]
	indice += 1

def generar_sello( nombre_archivo, llave_pem ):
	f1 = open(nombre_archivo, "r")
	f2 = open("cfdi_modificado.xml", "w")
	for line in f1:
		f2.write(line.replace('NumCert=""', 'NumCert="' + str(get_serial) + '"').replace('Cert=""', 'Cert="' + str(get_certificado) + '"').replace('FechaExp=""', 'FechaExp="' + str(fecha) + '-05:00"'))
		#f2.write(line.replace('Serial=""', 'NoCertificado="' + str(get_serial) + '"'))
		#f2.write(line.replace('Fecha=""', 'Fecha"' + str(fecha) + "'"))
	f1.close()
	f2.close()

	file = open("cfdi_modificado.xml", 'r')
	comprobante = file.read()
	file.close()
	keys = RSA.load_key(llave_pem)
	xdoc = ET.fromstring(comprobante)

	xsl_root = ET.parse(ruta_cadena)
	xsl = ET.XSLT(xsl_root)
	cadena_original = xsl(xdoc)
	digest = hashlib.new("sha1", str(cadena_original)).digest()
	get_sello = base64.b64encode(keys.sign(digest, "sha1"))

	f1 = open("cfdi_modificado.xml", "r")
	f2 = open(nombre_archivo, "w")
	for line in f1:
		f2.write(line.replace('Sello=""', 'Sello="' + str(get_sello) + '"'))
	f1.close()
	f2.close()

generar_sello( ruta_xml, ruta_pem )
