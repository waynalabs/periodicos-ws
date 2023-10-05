# Servicio web noticias periódicos



## Instalación
```
cd ws/
sudo apt install python3-dev libpq-dev

# crear entorno virtual
python3 -m venv venv
# activar
source venv/bin/activate

# instalar requerimientos
pip install -r requirements.txt

# ajustar valores de base de datos en ws/settings.py DATABASES

# ejecutar en modo desarrollo
python manage.py runserver
```

## Actualización de la documentación OPEN API

```
# Una vez activado el entorno virtual
cd ws/
python manage.py generateschema

```

## Revisar los endpoints

Desde el navegador `/schema` muestra la especificación de los endpoints.
