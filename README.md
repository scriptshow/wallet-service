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

2. ¿Qué alternativas planteas en el caso que la base de datos relacional de la aplicación se
convierta en un cuello de botella por saturación en las operaciones de lectura? ¿Y para las de
escritura?

3. Dicen que las bases de datos relacionales no escalan bien, se me ocurre montar el proyecto
con alguna NoSQL, ¿qué me recomiendas?

4. ¿Qué tipo de métricas y servicios nos pueden ayudar a comprobar que la API y el servidor
funcionan correctamente?

## Bonus

1. Nos gustaría contemplar que las operaciones de recarga y cobro sean en todo momento
atómicas, es decir, si se intenta cobrar dos operaciones al mismo tiempo sólo deben ser
aceptadas si existe dinero suficiente en la cuenta para completar ambas.

Debe evitarse que por algún error en la integración del comercio se repitan operaciones de
cobro.

2. Desplegar el proyecto en la instancia proporcionada. Idealmente con Docker, puedes incluirlo
todo en el único repositorio. Puedes elegir entre hacer un despliegue manual o automatizado.
En el segundo caso, también te pedimos que nos puedas proporcionar el código que hayas
empleado.
