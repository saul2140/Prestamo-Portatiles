# Usa una imagen base oficial de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias desde requirements.txt si existe
RUN pip install --no-cache-dir -r requirements.txt

# Define variables de entorno para la conexión a la base de datos
ENV MYSQL_HOST=10.3.29.20
ENV MYSQL_PORT=33060
ENV MYSQL_USER=user_gr2
ENV MYSQL_PASSWORD=portatil123
ENV MYSQL_DB=gr2_db
ENV FLASK_APP=app.py

# Expone el puerto 5000 para la aplicación Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]
