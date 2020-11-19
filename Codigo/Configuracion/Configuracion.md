# Procedimientos para la instalación de la aplicación en el servidor Ubuntu

**Instalación de python**

```
$ sudo apt install python3
```

**Instalación de git**

[Instalación de git](https://openwebinars.net/blog/como-instalar-git-en-ubuntu/)

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install git
$ git --version

$ git config --global user.name "Nombre Apellido"
$ git config --global user.email email@domain.com
$ git config --list
```

**Clonación del proyecto**

[Clonación del proyecto](https://git-scm.com/book/es/v2/Fundamentos-de-Git-Obteniendo-un-repositorio-Git)

```
$ git clone https://github.com/waltercueva/m1-20192-g3.git
```


**Instalación de MySQL Server**

[Instalación de MySQL Server](https://platzi.com/tutoriales/1631-java-basico/226-instalar-mysql-y-workbench-en-linux-ubuntu-1404/)

```
$ sudo apt-get install mysql-server mysql-client
$ mysql --version

$ sudo mysql_secure_installation
$ sudo apt-get install mysql-workbench

$ sudo systemctl start mysql
```

**Creación de base de datos** 

Luego de instalar MySQL Workbench, ejecutar el script SQL ubicado en *Codigo/Database Backups/metropolitano.sql* 

**Configuración de los parámetros de base de datos en el proyecto**

En la ruta del proyecto *Codigo/Configuracion/* configurar el archivo *cofig.ini* con los parametros establecidos

```
[mysql]
host = localhost
database = metropolitano
user = root
password = mysql
```

**Instalacion de dependencias del proyecto**

[Instalación de dependencias](https://medium.com/@boscacci/why-and-how-to-make-a-requirements-txt-f329c685181e)

En la ruta *Codigo/Scripts/* se encuentra el archivo *requirements.txt* en donde se listan todas las dependencias del proyecta y que necesitan ser instaladas

```
$ pip install -r requirements.txt
```

**Ejecución de la aplicación**

Al ejecutar el siguiente comando, el servicio se iniciará en [localhost:8050](http://localhost:8050/)

```
python -m Codigo.Scripts.app
```