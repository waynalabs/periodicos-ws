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

Para ver cómo usar el servicio.

- [https://api.periodicos.rmgss.net/schema](https://api.periodicos.rmgss.net/schema)
- [openapi.yaml](openapi.yaml)

### Levantar openapi con swagger-ui

En el directorio raíz de este proyecto.

```
docker run --rm -p 8080:8080 -e 80 -e SWAGGER_JSON=/temp/openapi.json -v $(pwd):/temp swaggerapi/swagger-ui
```

## Notas deploy

### postgres y debian

Para postgres 15 se pudo conectar a postgres modificando el password a algo mas seguro. Quizá por políticas de seguridad nuevas.

```
ALTER USER postgres WITH ENCRYPTED PASSWORD 'U1nP4as5-W@$ord';
```
