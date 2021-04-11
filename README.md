# wallet-service-aplazame

## Descripción

Se desea desarrollar un servicio monedero con una API Rest que permite realizar pagos
utilizando exclusivamente un token.

Se consideran distintos tipos de usuario con endpoints para realizar las siguientes operaciones:

- Cliente: debe ser capaz de realizar el registro en el servicio, crear una o varias cuentas
monedero (que se identificarán por un token único), recargar el saldo de sus cuentas, consultar
el estado de sus cuentas y listar las operaciones de sus cuentas.

- Comercio: debe ser capaz de realizar el registro en el servicio, crear una cuenta monedero,
realizar cargos en la cuenta monedero de un cliente teniendo como referencia el token de la
cuenta y listar las operaciones de su cuenta comercio.

En el histórico de operaciones se deben contemplar tanto las operaciones con éxito de recarga
y cobro, como los intentos fallidos de cobro por falta de saldo.

Los campos necesarios para el registro de clientes y comercios, así como el proceso de
generación del token asociado a cada una de las cuentas quedan a elección del candidato. No
es necesario encargarse del proceso de pago del cliente durante la operación de recarga del
saldo de sus cuentas.

## Objetivos a completar


1. Indica cómo se puede optimizar el rendimiento del servicio de listado de operaciones.

    - Respuesta: Según los requisitos de la aplicación, no especifican que pudiese haber 
      algún tipo de filtro a la hora de listar las operaciones de las cuentas, incluso entro
      en duda si para los clientes se quieren todas las operaciones de sus cuentas en una única
      consulta, en vez de por cuenta monedero (como lo he implementado yo). Pero definitivamente, 
      una de las mejores maneras de mejorar el rendimiento de esta consulta, es hacer un filtrado 
      por rango de fechas, igualmente ya le puse un índice a la columna donde se guarda la fecha de 
      cada transacción para su futuro uso. Adicionalmente, como esta tabla, a modo de histórico de operaciones, 
      se espera que su crecimiento sea muy alto, para mejorar la performance se podrían hacer 
      particiones de esta misma mediante el campo "date" (que guarda el datetime de cada operación), 
      creando por ejemplo, una partición para cada dia de operaciones. Al usar la base de datos de 
      postgresql, es muy fácil introducir una función para que te cree las particiones automáticamente.

2. ¿Qué alternativas planteas en el caso que la base de datos relacional de la aplicación se
convierta en un cuello de botella por saturación en las operaciones de lectura? ¿Y para las de
escritura?
   
    - Respuesta: Cuando el cuello de botella se genera en la parte de operaciones de lectura, debemos
      de empezar a mirar si nuestra solución pudiera ser pasar por un sistema de cacheado de datos, como
      pudiera ser Redis. Pero este sistema se necesita que los datos a consultar no cambien con 
      muy alta frecuencia, si no estaríamos mostrando información desactualizada, o incluso, replicando
      el problema con un sistema más complejo de mantener. Por otro lado también podríamos añadir
      réplicas de solo lectura a nuestra base de datos, y pasar todas las operaciones de lectura
      distribuyéndose entre las distintas réplicas.
      Para la parte del cuello de botella en las operaciones de escritura, algunas bases de datos como
      MySQL o PostgreSQL (la que hemos elegido para este proyecto!) cuentan con opciones para poder realizar
      escrituras en bloques, en vez de fila a fila, esto seria util si los comercios de nuestra aplicación
      necesitaran hacer un mismo cargo a multiples clientes (como si estuvieran cobrándose una suscripción,
      por ejemplo). Otra opción para solucionar los problemas de escritura, es hacer distintas particiones
      para la tabla de históricos (en nuestro caso la que más sobrecarga puede tener) y distribuirlas cada
      una de ellas en distintos filesystem, usando discos físicos independientes, distribuyendo asi la 
      carga de trabajo.
      Finalmente también podemos optar por alguna solución que ayude a escalar horizontalmente las bases
      de datos relacionales, en nuestro caso, usando PostgreSQL, seria Citus (www.citusdata.com/)

3. Dicen que las bases de datos relacionales no escalan bien, se me ocurre montar el proyecto
con alguna NoSQL, ¿qué me recomiendas?
   
    - Respuesta: Para las aplicaciones que manejan transacciones de dinero o información especialmente
      sensible que se necesita que sea muy consistente, siempre se busca que cumplan los estándares
      ACID (atomicity, consistency, isolation, durability) en los que las bases de datos relacionales
      son el mejor candidato. No obstante, también hay algunas bases de datos NoSQL que cumplen estos 
      estándares, como pueden ser: CouchDB o FoundationDB. Actualmente también existen muchas 
      utilidades para poder escalar bases de datos SQL como Citus, por lo que personalmente
      para esta aplicación, yo recomendaría el uso de alguna base de datos SQL.

4. ¿Qué tipo de métricas y servicios nos pueden ayudar a comprobar que la API y el servidor
funcionan correctamente?
   
    - Respuesta: Como parte de la monitorización, ya que nuestra aplicación esta basada en dockers,
      el primer servicio a monitorizar sería el servicio de docker, seguido de las instancias de docker
      creadas para esta aplicación (la imagen de la web, y la imagen de la base de datos), que estén 
      arriba y sin reiniciarse infinitamente.
      Adicionalmente se le puede añadir un extra de monitorización a algunos endpoints de la API Rest,
      incluso se podría crear un único endpoint de '/status', que únicamente devolviera el código 200, 
      significando asi el correcto funcionamiento del servicio REST. Otro chequeo extra que se puede
      añadir, es el de hacer log in con una cuenta de usuario para este tipo de automatización. En la
      parte del servidor, se le puede añadir métricas para ver el consumo de memoria, cpu y I/O de
      los filesystem, asi como el espacio libre en disco.

## Bonus

1. Nos gustaría contemplar que las operaciones de recarga y cobro sean en todo momento
atómicas, es decir, si se intenta cobrar dos operaciones al mismo tiempo solo deben ser
aceptadas si existe dinero suficiente en la cuenta para completar ambas.

Debe evitarse que por algún error en la integración del comercio se repitan operaciones de
cobro.

2. Desplegar el proyecto en la instancia proporcionada. Idealmente con Docker, puedes incluirlo
todo en el único repositorio. Puedes elegir entre hacer un despliegue manual o automatizado.
En el segundo caso, también te pedimos que nos puedas proporcionar el código que hayas
empleado.

# Documentación

Aquí comienza la documentación de la aplicación finalizada, hay que tener en consideración las siguientes
decisiones que se han tomado en el proyecto:
- Tanto clientes como comercios usaran el mismo endpoint "/wallet" cuando interactúan con sus carteras,
ya que las carteras son objetos idénticos para ambos.
- Los comercios solamente podrán crearse una cartera, mientras que los clientes tienen el límite de carteras
configurado en una variable, que por defecto son ilimitadas.
- Tanto clientes como comercios pueden hacer depósitos en sus carteras.
- Ya que los comercios también pueden hacer depósitos a sus propias carteras, se contempla de que un comercio
pueda realizarle cargos a la cartera de otro comercio, ya que pueden interactuar entre ellos.
- Solo los comercios podrán realizar cargos a otras carteras.

## Instalación

La aplicación está basada en docker-compose, la cual trae embebida la aplicación y la base de datos a usar,
por lo que lo único necesario, es tener instalado docker y docker-compose.

## Configuración
Dentro de docker-compose.yml encontrarás los siguientes parámetros, los cuales puedes modificar:

WALLET_SERVICE_LOG_LEVEL -> Values allowed: ['debug', 'info', 'warning', 'error', 'critical']

WALLET_SERVICE_SECRET_KEY -> Secret key used by Django project

WALLET_SERVICE_DEBUG_MODE -> Values allowed: ['True', 'False']

WALLET_SERVICE_ALLOWED_HOSTS -> Por defecto: "localhost 127.0.0.1"

WALLET_SERVICE_ALLOWED_ORIGINS -> Por defecto: "http://localhost:8000 http://127.0.0.1:8000"

WALLET_SERVICE_AUTH_TOKEN_EXPIRATION -> Tiempo de expiración para nuestro token de autenticación (en horas)

WALLET_SERVICE_MAX_WALLETS_BY_CLIENT -> Limite de carteras creadas por cada cliente, 0 para ilimitadas

## Ejecutando la aplicación

Dirigirse donde se encuentra nuestro docker-compose.yml dentro del proyecto.

Ejecutar el siguiente comando para construir nuestro docker-compose:

`docker-compose build`

Ejecutar el siguiente comando para lanzar nuestro docker-compose:

`docker-compose up`

## Despliegue automático

Para desplegar automáticamente nuestra aplicación con los valores por defecto, vamos a usar ansible,
por lo que lo único que vamos a necesitar es una máquina con ansible instalado, llevarnos nuestro fichero
'ansible_deployment.yml' y ejecutar el siguiente comando:

`ansible-playbook ansible_deployment.yml -i HOSTNAME, -e "githubuser=GITHUB_USER" -e "githubpassword=GITHUB_PASS" --private-key "PRIVATE_KEY_PATH" -u USERNAME`

- HOSTNAME: Debe ser reemplazado por la IP del servidor donde instalar nuestra aplicación
- USERNAME: Debe ser reemplazado por el usuario del servidor donde nuestra aplicación va a ser desplegada
- PRIVATE_KEY_PATH: Debe ser reemplazado por el path donde se encuentra la private_key para autenticarnos
- GITHUB_USER: Debe ser reemplazado por el usuario de GitHub con permisos en el repositorio
- GITHUB_PASS: Debe ser reemplazado por la contraseña de GitHub con premisos en el repositorio

## Documentación API

### Endpoints para clientes

***Registro - Sign up***

Method: POST

URL: _/client/signup_

Body: `{
    "email": "string",
    "password": "string",
    "client": {
        "first_name": "string",
        "last_name": "string",
        "phone_number": "+34666666666"
    }
}`

Response: `{"token": "auth_token"}`


***Autenticación - Log in***

Method: POST

URL: _/client/login_

Body: `{
    "email": "string",
    "password": "string"
}`

Response: `{"token": "auth_token"}`


***Cerrar sesión - Log out***

Method: POST

URL: _/client/logout_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: ``


### Endpoints para comercios

***Registro - Sign up***

Method: POST

URL: _/company/signup_

Body: `{
    "email": "string",
    "password": "string",
    "company": {
        "name": "string",
        "url": "string",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "+34666666666"
    }
}`

Response: `{"token": "auth_token"}`


***Autenticación - Log in***

Method: POST

URL: _/company/login_

Body: `{
    "email": "string",
    "password": "string"
}`

Response: `{"token": "auth_token"}`


***Cerrar sesión - Log out***

Method: POST

URL: _/company/logout_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: ``


### Endpoints para el uso de carteras


***Crear nuevas carteras***

Method: POST

URL: _/wallet/create_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{}`

Response: 
`{
    "success": "True",
    "message": "Wallet has been created successfully",
    "wallet": "your_wallet_token",
    "status_code": 201
}`


***Hacer un depósito en una de tus carteras***

Method: POST

URL: _/wallet/deposit_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{
    "wallet": "your_wallet_token",
    "amount": "amount_to_deposit"
}`

Response: 
`{
    "success": "True",
    "message": "Deposit has been done",
    "wallet": {
        "wallet": "your_wallet_token",
        "balance": total_balance_after_deposit
    },
    "status_code": 200
}`


***Obtener la información y estado de una de tus carteras***

Method: GET

URL: _/wallet/info/< your_wallet_token >_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`{
    "success": "True",
    "message": "Wallet has been found",
    "wallet": {
        "wallet": "your_wallet_token",
        "balance": current_balance
    },
    "status_code": 200
}`


***Obtener la información y estado de todas tus carteras***

Method: GET

URL: _/wallet/list_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`{
    "success": "True",
    "message": "Wallets have been found",
    "wallets": [{
        "wallet": "your_wallet_token",
        "balance": current_balance
    }, ...
    ],
    "status_code": 200
}`


***Hacer un cargo a una cartera cliente (solo disponible para comercios)***

Method: POST

URL: _/wallet/charge_

Headers: `{
    "Authorization": "Token auth_token"
}`

Body: `{
    "wallet": "wallet_to_make_a_charge",
    "amount": amount_to_be_charged,
    "summary": "short description about the charge"
}`

Response: 
`{
   "success": "True",
   "message": "Charge has been done",
   "wallet": {
        "wallet": "your_wallet_token",
        "balance": current_balance_after_receive_the_charge
    },
    "status_code": 200
}`


***Obtener el histórico de operaciones de una de tus carteras***

Method: GET

URL: _/wallet/history/< your_wallet_token >_

Headers: `{
    "Authorization": "Token auth_token"
}`

Response: 
`{
    "success": "True",
    "message": "History has been found",
    "histories": [
        {
            "summary": "short description about the operation",
            "source": "wallet_from_money_was_charged" or empty if its a deposit,
            "target": "your_wallet_where_the_money_was_deposit",
            "amount": the_amount_transfered_or_deposit,
            "success": true,
            "date": "2021-04-11T11:05:13.591091Z"
        }, ...
    ],
    "status_code": 200
}`
