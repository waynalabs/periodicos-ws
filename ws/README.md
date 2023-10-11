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

## Documentación OPEN API

[openapi.yaml](openapi.yaml)

Para ver cómo usar el servicio.

