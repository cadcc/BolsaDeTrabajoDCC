#!/usr/bin/env bash
python manage.py loaddata region
python manage.py loaddata comuna
python manage.py loaddata jornada
python manage.py loaddata rol
python manage.py loaddata tipoetiqueta
python manage.py loaddata etiqueta
printf 'Ejecutado todo correctamente\n'