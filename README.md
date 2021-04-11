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

## Documentación API

Nuestra aplicación trae embebida su propia documentación de los endpoints API, simplemente hay que
dirigirse a la url '/documentation/', y allí encontraremos la documentación para todos nuestros
endpoints. Esta documentación es automática, y se refresca en cada cambio que se realiza en el código.

Por defecto, solo tendrás visibilidad a los endpoints abiertos (login y signup), para obtener el acceso
al resto de endpoints necesitarás presionar en el botón "Authenticate" e introducir tu token de 
autenticación (previamente has tenido que crearte tu usuario, client o company), con la siguiente estructura:

`Token asef786se6af97se8sa5e8f6se`
