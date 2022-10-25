# ¿Cómo utilizar este proyecto?

Se debe tener Docker instalado en la máquina donde se vaya a ejecutar

## ¿Cómo ejecutarlo?

Crear la red para que los contenedores de Redis y del proyecto puedan comunicarse:
```
sudo docker network create proyecto-network
```

Crear un contenedor de Redis:
```
sudo docker run -d --name=redis-container redis
```

Crear un Contenedor del proyecto:
```
sudo docker run -p 5000:5000 -d --name=proyecto-container alvarodpm/proyecto_nube:latest
```

Conectar ambos contenedores a la red:
```
sudo docker network connect proyecto-network proyecto-container
sudo docker network connect proyecto-network redis-container
```

En este punto ya se pueden hacer llamados al API del proyecto en localhost:5000

## ¿Cómo crear la imagen de Docker?
```
sudo docker image build -t proyecto_nube .
sudo docker tag proyecto_nube alvarodpm/proyecto_nube:latest
sudo docker push alvarodpm/proyecto_nube
```
