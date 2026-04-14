"""
THRIVE - Evaluación para Encargados de Tienda
Flask backend with SQLite for storing quiz results
"""
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "resultados.db")

# ── Quiz Data ──────────────────────────────────────────────────────────────────
QUIZ = {
    "title": "Evaluación para Encargados de Tienda",
    "time_limit_minutes": 15,
    "passing_score": 70,
    "questions": [
        {
            "id": 1,
            "category": "Cambios y Devoluciones",
            "text": "Sobre el proceso de cambio o devolución, ¿cuál de las siguientes afirmaciones es CORRECTA?",
            "options": [
                "El cliente tiene hasta 30 días para solicitar un cambio o devolución.",
                "El producto puede estar abierto si no ha sido usado completamente.",
                "Si el producto nuevo es de mayor valor al cambiado, el cliente paga la diferencia y la factura se emite solo por esa diferencia.",
                "El crédito del producto cambiado puede guardarse para compras futuras."
            ],
            "correct": 2,
            "explanation": "El valor del producto cambiado es un crédito que debe usarse al 100% en la misma compra. Si el nuevo producto es mayor, el cliente paga la diferencia y la factura se emite solo por ese monto."
        },
        {
            "id": 2,
            "category": "Cierre de Caja",
            "text": "Al procesar un cierre de caja, el total de ventas de sistema es MAYOR al total de facturas registradas. ¿Qué debe hacer?",
            "options": [
                "Reportar inmediatamente al supervisor sin investigar la causa.",
                "Verificar si hubo errores de POS durante el día, comparar montos, facturar si coinciden; si no, reportar la diferencia para recibir reporte detallado.",
                "Cubrir la diferencia con efectivo propio para cuadrar el cierre.",
                "Ignorar la diferencia si es menor a Q10.00."
            ],
            "correct": 1,
            "explanation": "Primero se verifica si hubo errores de POS. Si el monto coincide con la diferencia, se factura. Si no coincide, se reporta para recibir el reporte detallado de facturación."
        },
        {
            "id": 3,
            "category": "Cierre de Caja",
            "text": "En el cierre de caja encuentra una discrepancia de Q3.00 por facturar entre lo facturado y ventas. ¿Qué procede?",
            "options": [
                "Si no se cuenta con una venta precisa por ese monto, reportar en correo de cierre para recibir reporte de facturación y determinar qué factura se emitió por un monto menor.",
                "Colocar la diferencia en efectivo con una boleta adicional en la bolsa de valores de Forza.",
                "Registrar una factura por ese monto con NIT CF para que cuadre el cierre.",
                "Registrar en otro importe y registrar la venta en sistema."
            ],
            "correct": 0,
            "explanation": "Se debe reportar en el correo de cierre para recibir el reporte de facturación y así determinar cuál factura se emitió por un monto menor al correcto."
        },
        {
            "id": 4,
            "category": "Recepción de Producto",
            "text": "¿Cuál es el ÚLTIMO paso en el proceso estándar de recepción de producto?",
            "options": [
                "Firmar las hojas de entrega del piloto.",
                "Tomar fotos de las hojas como respaldo de los ingresos.",
                "Guardar y ajustar cantidades en el sistema de inventario.",
                "Ingresar a la orden de compra y marcarla como \"MARK COMPLETE\" para evitar que se ingresen más productos."
            ],
            "correct": 3,
            "explanation": "Después de guardar y ajustar cantidades, se debe volver a la orden de compra (que cambió a parcialmente recibida) y marcarla como MARK COMPLETE."
        },
        {
            "id": 5,
            "category": "Recepción de Producto",
            "text": "Durante la recepción de producto, ¿qué se debe verificar ANTES de firmar las hojas de entrega?",
            "options": [
                "Únicamente la cantidad de cajas recibidas.",
                "El estado físico de los productos, cantidad, códigos y que las etiquetas de SAP estén correctamente asignadas.",
                "Solo que los códigos de barras sean legibles.",
                "Que el piloto tenga identificación vigente."
            ],
            "correct": 1,
            "explanation": "Se debe verificar el estado físico, cantidad, códigos que coincidan con las hojas, y que las etiquetas de códigos de barras de SAP vengan correctamente asignadas."
        },
        {
            "id": 6,
            "category": "Reportes",
            "text": "¿Cuándo se envía el reporte semanal de fechas de vencimiento?",
            "options": [
                "Los lunes al inicio del turno.",
                "Los viernes al cierre de operaciones.",
                "Los domingos antes de finalizar turno.",
                "Cuando se encuentran productos próximos a vencer."
            ],
            "correct": 2,
            "explanation": "El reporte se envía los domingos antes de finalizar turno, con cada integrante del equipo pasando sus datos, ordenados de fechas más cercanas a más lejanas."
        },
        {
            "id": 7,
            "category": "Reportes",
            "text": "¿A quiénes se envía el reporte semanal de fechas de vencimiento?",
            "options": [
                "Pedro, Marlene, Angélica, con copia a Nicolás y Laura.",
                "Nicolás y Laura únicamente.",
                "Todo el equipo de la tienda por grupo de WhatsApp.",
                "Pedro y Ventura con copia a Marlene."
            ],
            "correct": 0,
            "explanation": "Se envía por correo electrónico a Pedro, Marlene, Angélica, con copia (CC) a Nicolás y Laura."
        },
        {
            "id": 8,
            "category": "Reportes",
            "text": "¿Qué información indispensable debe tener un reporte de cambio o devolución de productos?",
            "options": [
                "Solo el código y descripción del producto.",
                "Código, descripción, cantidad, tipo (cambio/devolución), fecha de vencimiento, lote y motivo breve del cambio o devolución.",
                "Solo el nombre del cliente, fecha y monto.",
                "El número de factura original y el nuevo producto adquirido."
            ],
            "correct": 1,
            "explanation": "Debe incluir: código, descripción, cantidad, si es cambio o devolución, fecha de vencimiento, lote del producto y explicación breve y concisa del motivo."
        },
        {
            "id": 9,
            "category": "Preparación de Alimentos",
            "text": "¿Cuál es la temperatura y tiempo correctos para preparar un goaffle?",
            "options": [
                "180° por 4 minutos.",
                "200° por 3.5 minutos.",
                "220° por 3 minutos.",
                "200° por 5 minutos."
            ],
            "correct": 1,
            "explanation": "La temperatura correcta es 200° y el tiempo es 3.5 minutos."
        },
        {
            "id": 10,
            "category": "Preparación de Alimentos",
            "text": "¿Cuál es el tiempo de cocción correcto para baos y dumplings?",
            "options": [
                "7-8 minutos baos, 11-12 minutos dumplings.",
                "11-12 minutos baos, 7-8 minutos dumplings.",
                "10 minutos para ambos.",
                "15 minutos baos, 5 minutos dumplings."
            ],
            "correct": 1,
            "explanation": "Los baos requieren 11-12 minutos y los dumplings 7-8 minutos de cocción."
        },
        {
            "id": 11,
            "category": "Equipos",
            "text": "¿Cuál es la presión máxima ideal en el generador de vapor?",
            "options": [
                "0.1 PSI",
                "0.2 PSI",
                "0.4 PSI",
                "0.6 PSI"
            ],
            "correct": 1,
            "explanation": "La presión máxima ideal es 0.2 PSI. El sensor del generador va de 0.0 a 0.6 PSI."
        },
        {
            "id": 12,
            "category": "Equipos",
            "text": "¿Por qué es importante que el generador de vapor NO exceda el límite de presión?",
            "options": [
                "Para evitar el consumo excesivo de electricidad.",
                "Para evitar daños en las tuberías y que el generador active su mecanismo de seguridad que libera toda la presión.",
                "Para mantener la temperatura correcta de los alimentos servidos.",
                "Para evitar ruidos molestos en el establecimiento."
            ],
            "correct": 1,
            "explanation": "Se debe evitar daños en las tuberías de presión y evitar que el generador active su mecanismo de seguridad, el cual libera toda la presión por una válvula específica."
        },
        {
            "id": 13,
            "category": "Equipos",
            "text": "¿Qué hacer ante un equipo de congelación que no funciona apropiadamente?",
            "options": [
                "Intentar reparar el equipo internamente antes de reportar a alguien.",
                "Reportar a Pedro, desocupar el equipo, no dejar producto sensible dentro, y desconectar según sus indicaciones.",
                "Desconectar inmediatamente sin consultar y reportar al día siguiente.",
                "Mantener el producto dentro con monitoreo constante hasta que llegue un técnico."
            ],
            "correct": 1,
            "explanation": "Se reporta a Pedro, se desocupa el equipo (especialmente en horarios sin personal de monitoreo) y se desconecta según indicaciones de Pedro."
        },
        {
            "id": 14,
            "category": "Contactos y Soporte",
            "text": "¿A quién se debe acudir si el internet en tienda se ha cortado?",
            "options": [
                "Pedro",
                "Marlene",
                "Ventura",
                "Nicolás"
            ],
            "correct": 2,
            "explanation": "En caso de corte de internet, se debe acudir a Ventura."
        },
        {
            "id": 15,
            "category": "Contactos y Soporte",
            "text": "¿A quién se debe acudir si la sesión del programa de cobro se cerró?",
            "options": [
                "Pedro",
                "Angélica",
                "Laura",
                "Ventura"
            ],
            "correct": 3,
            "explanation": "Si la sesión del programa de cobro se cierra, se debe acudir a Ventura."
        },
        {
            "id": 16,
            "category": "Promociones",
            "text": "Cuando nos notifican promociones, ¿cuál de los siguientes aspectos NO es indispensable?",
            "options": [
                "Periodo de vigencia de la promoción.",
                "Lote que aplica la promoción.",
                "El nombre del proveedor que otorga la promoción.",
                "En dónde aplicará la promoción (sucursales, página web, PedidosYa)."
            ],
            "correct": 2,
            "explanation": "Los aspectos indispensables son: periodo de vigencia, lote, precio, descripción y dónde aplicará. El nombre del proveedor no es un parámetro indispensable."
        },
        {
            "id": 17,
            "category": "Operaciones",
            "text": "¿Qué se debe hacer antes de un asueto donde no habrá operaciones, para evitar pedidos de delivery no aceptados?",
            "options": [
                "Solo enviar correo al equipo interno informando del cierre.",
                "Actualizar horarios en PedidosYa/Uber Eats marcando como cerrado, y enviar correo a Ventura para actualizar página web.",
                "Desconectar la tablet de PedidosYa y Uber Eats.",
                "Publicar en redes sociales que la tienda estará cerrada."
            ],
            "correct": 1,
            "explanation": "Se deben actualizar los horarios en PedidosYa y Uber Eats marcando como cerrados, y enviar correo a Ventura para actualizar los métodos de envío en la página web."
        },
        {
            "id": 18,
            "category": "Servicio al Cliente",
            "text": "¿Qué hacer ante un cliente molesto que desea anotar su queja en el libro de DIACO?",
            "options": [
                "Negarle el libro de quejas y pedirle que se comunique por correo.",
                "Darle el libro inmediatamente sin intentar resolver la situación.",
                "Agotar todas las vías posibles de solución antes; y si aún lo solicita, nunca negar el libro de quejas.",
                "Llamar al supervisor para que él atienda al cliente."
            ],
            "correct": 2,
            "explanation": "Se debe intentar solucionar el reclamo por todas las vías posibles. Nunca se niega el libro de quejas, pero idealmente se agotan todas las instancias de solución."
        },
        {
            "id": 19,
            "category": "Servicio al Cliente",
            "text": "¿Cuál de los siguientes reclamos NO procede en el libro de quejas de DIACO?",
            "options": [
                "Precios equivocados en estanterías o góndolas.",
                "Productos con fecha de vencimiento expirada en tienda.",
                "Queja sobre el tipo de música del establecimiento.",
                "Mala calidad o estado caducado de los alimentos servidos."
            ],
            "correct": 2,
            "explanation": "Reclamos que NO proceden incluyen: tipo de música, iluminación, ambiente o factores externos, y negarse a vender alcohol a menores o personas en estado etílico."
        },
        {
            "id": 20,
            "category": "Atención al Cliente",
            "text": "Un cliente ingresa a la tienda. ¿Cuál es la forma correcta de atenderlo?",
            "options": [
                "Quedarse en caja y esperar a que el cliente se acerque con una consulta.",
                "Salir del mostrador, saludar al cliente con contacto visual y una sonrisa, darle la bienvenida y preguntar si necesita ayuda.",
                "Gritar desde la caja '¡Bienvenido!' y seguir con lo que estaba haciendo.",
                "Seguir al cliente por toda la tienda para asegurarse de que no robe nada."
            ],
            "correct": 1,
            "explanation": "Lo correcto es salir del mostrador, hacer contacto visual, saludar con una sonrisa, dar la bienvenida y ofrecer ayuda. El cliente debe sentirse atendido desde que entra."
        },
        {
            "id": 21,
            "category": "Atención al Cliente",
            "text": "Estás atendiendo a un cliente en caja y entra otro cliente a la tienda. ¿Qué debes hacer?",
            "options": [
                "Ignorar al nuevo cliente hasta terminar con el que estás atendiendo.",
                "Dejar al cliente actual para ir a atender al nuevo.",
                "Hacer contacto visual con el nuevo cliente, saludarlo y decirle que en un momento lo atiendes, mientras terminas con el cliente actual.",
                "Pedirle al nuevo cliente que espere afuera hasta que termines."
            ],
            "correct": 2,
            "explanation": "Nunca se ignora a un cliente. Se hace contacto visual, se saluda y se le indica que en un momento será atendido. El cliente actual mantiene la prioridad pero el nuevo debe sentirse reconocido."
        },
        {
            "id": 22,
            "category": "Atención al Cliente",
            "text": "Un cliente está recorriendo la tienda sin pedir ayuda. ¿Cuál es la actitud correcta?",
            "options": [
                "Dejarlo completamente solo para que no se sienta presionado.",
                "Mantener una actitud atenta y disponible, y si pasa un tiempo prudente, acercarse amablemente a preguntar si necesita ayuda o busca algo en particular.",
                "Acercarse cada 30 segundos para preguntarle si ya encontró lo que busca.",
                "Avisarle que si no va a comprar nada, otros clientes están esperando."
            ],
            "correct": 1,
            "explanation": "El equilibrio es clave: estar disponible sin ser invasivo. Después de un tiempo prudente, acercarse de forma amable a ofrecer ayuda demuestra interés genuino en el cliente."
        },
        {
            "id": 23,
            "category": "Atención al Cliente",
            "text": "Un cliente te hace una pregunta sobre un producto que no conoces o no sabes la respuesta. ¿Qué debes hacer?",
            "options": [
                "Inventar una respuesta para no quedar mal.",
                "Decirle que no sabes y que busque la información en internet.",
                "Ser honesto, decirle que vas a verificar la información y consultar con un compañero o buscar la respuesta correcta para darle una respuesta precisa.",
                "Decirle que ese producto no se vende aquí para evitar la pregunta."
            ],
            "correct": 2,
            "explanation": "Nunca se inventa información. La honestidad genera confianza. Se debe consultar con un compañero o verificar la información para dar una respuesta correcta al cliente."
        },
        {
            "id": 24,
            "category": "Atención al Cliente",
            "text": "Un cliente pide un producto que está agotado. ¿Cuál es la respuesta correcta?",
            "options": [
                "Decirle 'no hay' y seguir con otra cosa.",
                "Informarle que está agotado, ofrecerle una alternativa similar si existe, y si es posible indicarle cuándo podría estar disponible nuevamente.",
                "Decirle que venga mañana porque tal vez llega.",
                "Culpar a logística o bodega frente al cliente por no haber enviado el producto."
            ],
            "correct": 1,
            "explanation": "Se informa con amabilidad, se ofrece una alternativa y si es posible se da un estimado de reabastecimiento. Nunca se culpa a otros departamentos frente al cliente."
        },
        {
            "id": 25,
            "category": "Atención al Cliente",
            "text": "Al despedir a un cliente después de su compra, ¿cuál es la forma correcta?",
            "options": [
                "No es necesario despedirlo, con cobrarle es suficiente.",
                "Agradecerle su compra, entregarle su bolsa y despedirlo con amabilidad invitándolo a regresar.",
                "Decirle 'siguiente' para atender al próximo cliente rápidamente.",
                "Despedirlo solo si compró mucho, si compró poco no es necesario."
            ],
            "correct": 1,
            "explanation": "Todo cliente merece una despedida amable sin importar el monto de su compra. Agradecer, entregar su bolsa y despedirlo con cortesía genera una buena experiencia y fidelización."
        },
        {
            "id": 26,
            "category": "Higiene y Presentación",
            "text": "¿Cuál es la presentación personal correcta que debe tener un colaborador durante su turno?",
            "options": [
                "Usar la ropa que quiera siempre que esté limpia.",
                "Uniforme completo y limpio, cabello recogido o presentable, uñas cortas y limpias, sin accesorios excesivos, y uso de redecilla o gorra en área de alimentos.",
                "Solo es necesario usar el uniforme, lo demás no importa.",
                "Uniforme limpio y cualquier tipo de calzado es aceptable."
            ],
            "correct": 1,
            "explanation": "La presentación incluye: uniforme completo y limpio, cabello recogido, uñas cortas y limpias, sin accesorios excesivos, y redecilla o gorra en áreas de preparación de alimentos."
        },
        {
            "id": 27,
            "category": "Higiene y Presentación",
            "text": "¿Cuándo es obligatorio lavarse las manos durante el turno?",
            "options": [
                "Solo al inicio del turno.",
                "Antes y después de manipular alimentos, después de ir al baño, después de tocar basura o superficies sucias, después de toser o estornudar, y al cambiar de actividad.",
                "Solo cuando se manipulan alimentos crudos.",
                "Una vez cada hora es suficiente."
            ],
            "correct": 1,
            "explanation": "El lavado de manos es obligatorio: antes y después de manipular alimentos, después del baño, después de tocar basura o superficies contaminadas, después de toser/estornudar, y al cambiar de actividad."
        },
        {
            "id": 28,
            "category": "Higiene y Presentación",
            "text": "¿Cuál es la forma correcta de mantener el área de mostrador y exhibición durante el turno?",
            "options": [
                "Limpiar solo al final del día cuando se hace el cierre.",
                "Limpiar solo cuando el encargado lo indique.",
                "Mantener limpio y ordenado en todo momento: limpiar derrames de inmediato, organizar productos, y asegurarse de que las vitrinas y superficies estén libres de polvo y residuos.",
                "Limpiar únicamente si un cliente hace un comentario sobre la limpieza."
            ],
            "correct": 2,
            "explanation": "Las áreas de exhibición y mostrador deben mantenerse limpias y ordenadas TODO el turno, no solo al cierre. Los derrames se limpian de inmediato y las superficies deben estar libres de polvo y residuos."
        },
        {
            "id": 29,
            "category": "Higiene y Presentación",
            "text": "¿Está permitido comer o beber en el área de atención al cliente o zona de preparación de alimentos?",
            "options": [
                "Sí, siempre que sea rápido y no haya clientes.",
                "Sí, solo si es agua.",
                "No. Comer y beber está permitido únicamente en el área designada para descanso, nunca en zonas de atención al cliente o preparación de alimentos.",
                "Sí, si se tiene un recipiente con tapa."
            ],
            "correct": 2,
            "explanation": "Comer y beber solo se permite en el área designada para descanso. En zonas de atención al cliente y preparación de alimentos está prohibido por normas de higiene y por imagen profesional."
        },
        {
            "id": 30,
            "category": "Higiene y Presentación",
            "text": "¿Con qué frecuencia se debe limpiar y desinfectar el equipo de preparación de alimentos (vaporeras, wafleras, utensilios)?",
            "options": [
                "Solo al final del día.",
                "Una vez por semana a fondo es suficiente.",
                "Después de cada uso y una limpieza profunda al cierre del día. Los utensilios deben estar siempre limpios y listos para el siguiente servicio.",
                "Solo cuando se note suciedad visible."
            ],
            "correct": 2,
            "explanation": "Los equipos se limpian después de cada uso para evitar contaminación cruzada, y se realiza una limpieza profunda al cierre. Los utensilios deben estar siempre listos y en condiciones higiénicas."
        },
        {
            "id": 31,
            "category": "Higiene y Presentación",
            "text": "Un cliente nota que la tienda está desordenada o sucia. ¿Qué imagen proyecta esto?",
            "options": [
                "No tiene mayor importancia mientras los productos estén bien.",
                "Proyecta desorganización, falta de profesionalismo y genera desconfianza sobre la calidad e higiene de los productos, especialmente los alimentos.",
                "Solo importa si es la primera vez que el cliente visita la tienda.",
                "Solo afecta si el área de alimentos está sucia, las demás áreas no importan."
            ],
            "correct": 1,
            "explanation": "La limpieza y orden de TODA la tienda refleja profesionalismo y genera confianza. Un establecimiento desordenado o sucio genera desconfianza sobre la calidad de los productos y alimentos."
        },
        {
            "id": 32,
            "category": "Higiene y Presentación",
            "text": "¿Qué elementos de protección son obligatorios al preparar alimentos para los clientes?",
            "options": [
                "Solo guantes.",
                "Guantes desechables, redecilla o gorra para el cabello, y uniforme limpio. En caso de heridas en las manos, cubrir con vendaje y guante adicional.",
                "No se necesita protección si uno se lavó las manos antes.",
                "Solo redecilla, los guantes son opcionales."
            ],
            "correct": 1,
            "explanation": "Para manipular alimentos se requieren guantes desechables, redecilla o gorra, uniforme limpio, y en caso de heridas cubrir con vendaje y guante adicional para evitar contaminación."
        },
        {
            "id": 33,
            "category": "Apertura de Tienda",
            "text": "¿Cuál es la PRIMERA acción al llegar a la tienda antes de la apertura?",
            "options": [
                "Encender las luces y abrir la puerta al público.",
                "Revisar que todo esté en orden: verificar que no haya indicios de ingreso no autorizado, revisar equipos de refrigeración y congelación, encender luces y sistemas.",
                "Ir directo a caja a contar el fondo.",
                "Poner música y preparar café."
            ],
            "correct": 1,
            "explanation": "Lo primero es verificar la seguridad del establecimiento, revisar que equipos de refrigeración y congelación estén funcionando correctamente, y luego encender luces y sistemas."
        },
        {
            "id": 34,
            "category": "Apertura de Tienda",
            "text": "¿Qué se debe hacer con los equipos de preparación de alimentos (vaporera, waflera) antes de abrir?",
            "options": [
                "Encenderlos cuando llegue el primer cliente que pida algo.",
                "Encenderlos con anticipación para que estén a temperatura correcta al momento de la apertura, verificar que estén limpios y en buen estado.",
                "Solo encender la waflera, la vaporera no es necesaria temprano.",
                "No encenderlos hasta después de las 10am."
            ],
            "correct": 1,
            "explanation": "Los equipos se encienden con anticipación para que alcancen la temperatura adecuada al abrir. Se verifica que estén limpios del cierre anterior y funcionando correctamente."
        },
        {
            "id": 35,
            "category": "Apertura de Tienda",
            "text": "¿Qué tareas de limpieza se deben realizar ANTES de abrir la tienda al público?",
            "options": [
                "Solo barrer la entrada.",
                "Barrer y trapear pisos, limpiar vitrinas y mostradores, limpiar vidrios de la entrada, verificar que los baños estén limpios y con insumos, y asegurarse de que el área de alimentos esté desinfectada.",
                "Limpiar solo si se ve sucio, si se ve bien no es necesario.",
                "La limpieza se hace al cierre, no a la apertura."
            ],
            "correct": 1,
            "explanation": "Antes de abrir se debe: barrer y trapear pisos, limpiar vitrinas y mostradores, limpiar vidrios, verificar baños con insumos, y desinfectar el área de alimentos. La tienda debe estar impecable al abrir."
        },
        {
            "id": 36,
            "category": "Apertura de Tienda",
            "text": "¿Qué se debe verificar en las góndolas y estanterías antes de la apertura?",
            "options": [
                "No es necesario revisarlas, se llenan cuando se acaban los productos.",
                "Verificar que estén surtidas, con productos al frente (FIFO), etiquetas de precios visibles y correctas, y que no haya productos vencidos en exhibición.",
                "Solo verificar que las etiquetas de precios estén puestas.",
                "Revisarlas solo los lunes cuando llega producto nuevo."
            ],
            "correct": 1,
            "explanation": "Antes de abrir se verifica: góndolas surtidas, productos al frente rotados (FIFO - primero en entrar, primero en salir), etiquetas de precio visibles y correctas, y sin productos vencidos en exhibición."
        },
        {
            "id": 37,
            "category": "Apertura de Tienda",
            "text": "¿Qué significa la rotación FIFO y por qué es importante aplicarla al surtir góndolas?",
            "options": [
                "FIFO significa 'First In, First Out': el producto que entró primero a inventario se coloca al frente para que se venda primero, evitando vencimientos.",
                "FIFO significa colocar los productos más bonitos al frente.",
                "FIFO es un sistema de conteo de inventario que se usa al cierre.",
                "FIFO significa que el producto más caro va al frente."
            ],
            "correct": 0,
            "explanation": "FIFO (First In, First Out / Primero en Entrar, Primero en Salir) asegura que los productos con fecha de vencimiento más cercana estén al frente y se vendan primero, reduciendo merma por vencimiento."
        },
        {
            "id": 38,
            "category": "Cierre de Tienda",
            "text": "¿Cuáles son las tareas de limpieza obligatorias al cierre de la tienda?",
            "options": [
                "Solo barrer y apagar luces.",
                "Limpiar y desinfectar área de preparación de alimentos y equipos, barrer y trapear pisos, limpiar mostradores y vitrinas, vaciar basureros, y dejar baños limpios.",
                "Solo limpiar si fue un día con mucho movimiento.",
                "Barrer y dejar la limpieza profunda para el turno de la mañana."
            ],
            "correct": 1,
            "explanation": "Al cierre se debe: limpiar y desinfectar área de alimentos y equipos, barrer y trapear, limpiar mostradores y vitrinas, vaciar basureros, y dejar baños limpios. La tienda debe quedar lista para la apertura del siguiente día."
        },
        {
            "id": 39,
            "category": "Cierre de Tienda",
            "text": "¿Qué se debe hacer con los equipos de preparación de alimentos al cierre?",
            "options": [
                "Solo apagarlos.",
                "Apagarlos, limpiarlos a fondo, desinfectar superficies, vaciar residuos de agua del generador de vapor si aplica, y dejarlos listos para el siguiente día.",
                "Dejarlos encendidos toda la noche para que estén listos en la mañana.",
                "Limpiarlos solo por fuera y apagarlos."
            ],
            "correct": 1,
            "explanation": "Al cierre los equipos se apagan, se limpian a fondo por dentro y fuera, se desinfectan superficies, se vacían residuos, y se dejan listos para el uso del siguiente día."
        },
        {
            "id": 40,
            "category": "Cierre de Tienda",
            "text": "¿Qué verificaciones de seguridad se deben realizar antes de cerrar la tienda?",
            "options": [
                "Solo cerrar la puerta con llave.",
                "Verificar que todos los equipos estén apagados (excepto refrigeración y congelación), cerrar llaves de gas si aplica, asegurar puertas y accesos, activar alarma si existe, y confirmar que no quede nadie dentro.",
                "Solo verificar que la caja esté cerrada.",
                "Apagar las luces y cerrar la puerta principal."
            ],
            "correct": 1,
            "explanation": "Al cierre se verifica: equipos apagados (excepto refrigeración/congelación que deben quedar encendidos), llaves de gas cerradas, puertas aseguradas, alarma activada, y confirmación de que no quede nadie dentro."
        },
        {
            "id": 41,
            "category": "Cierre de Tienda",
            "text": "¿Qué se debe hacer con los productos perecederos y alimentos preparados que quedaron al cierre?",
            "options": [
                "Dejarlos en el mostrador para venderlos al día siguiente.",
                "Almacenar correctamente en refrigeración los que aún estén en buen estado y dentro de su vida útil, desechar los que ya no cumplan con los estándares de calidad, y registrar la merma.",
                "Regalar todo lo que sobró a los empleados.",
                "Guardarlos en cualquier lugar fresco."
            ],
            "correct": 1,
            "explanation": "Los perecederos en buen estado se almacenan correctamente en refrigeración. Los que no cumplan estándares se desechan y se registra la merma. Nunca se dejan fuera de refrigeración."
        }
    ]
}

# ── Database ───────────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            sucursal TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER NOT NULL,
            time_taken_seconds INTEGER,
            submitted_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            category TEXT NOT NULL,
            selected_option INTEGER,
            correct_option INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
    """)
    db.commit()
    db.close()

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def quiz_page():
    return render_template("quiz.html", quiz=QUIZ)

@app.route("/resultados")
def results_page():
    db = get_db()
    submissions = db.execute(
        "SELECT * FROM submissions ORDER BY submitted_at DESC"
    ).fetchall()

    # Per-question stats
    question_stats = []
    for q in QUIZ["questions"]:
        row = db.execute(
            "SELECT COUNT(*) as total, SUM(is_correct) as correct FROM answers WHERE question_id = ?",
            (q["id"],)
        ).fetchone()
        total = row["total"] or 0
        correct = row["correct"] or 0
        question_stats.append({
            "id": q["id"],
            "text": q["text"],
            "category": q["category"],
            "total": total,
            "correct": correct,
            "pct": round(correct / total * 100) if total > 0 else 0
        })

    # Overall stats
    total_submissions = len(submissions)
    avg_score = 0
    pass_rate = 0
    if total_submissions > 0:
        avg_score = round(sum(s["percentage"] for s in submissions) / total_submissions, 1)
        pass_rate = round(sum(1 for s in submissions if s["passed"]) / total_submissions * 100)

    return render_template("resultados.html",
        submissions=submissions,
        question_stats=question_stats,
        total_submissions=total_submissions,
        avg_score=avg_score,
        pass_rate=pass_rate,
        quiz=QUIZ
    )

@app.route("/resultados/<int:submission_id>")
def submission_detail(submission_id):
    db = get_db()
    submission = db.execute(
        "SELECT * FROM submissions WHERE id = ?", (submission_id,)
    ).fetchone()
    if not submission:
        return "No encontrado", 404
    answers = db.execute(
        "SELECT * FROM answers WHERE submission_id = ? ORDER BY question_id",
        (submission_id,)
    ).fetchall()
    return render_template("detalle.html",
        submission=submission,
        answers=answers,
        quiz=QUIZ
    )

@app.route("/api/submit", methods=["POST"])
def submit_quiz():
    data = request.get_json()
    nombre = data.get("nombre", "").strip()
    sucursal = data.get("sucursal", "").strip()
    respuestas = data.get("respuestas", {})
    time_taken = data.get("time_taken_seconds", None)

    if not nombre or not sucursal:
        return jsonify({"error": "Nombre y sucursal son requeridos"}), 400

    score = 0
    total = len(QUIZ["questions"])
    answer_records = []

    for q in QUIZ["questions"]:
        qid = str(q["id"])
        selected = respuestas.get(qid)
        is_correct = selected == q["correct"] if selected is not None else False
        if is_correct:
            score += 1
        answer_records.append({
            "question_id": q["id"],
            "question_text": q["text"],
            "category": q["category"],
            "selected_option": selected,
            "correct_option": q["correct"],
            "is_correct": 1 if is_correct else 0
        })

    percentage = round(score / total * 100, 1)
    passed = 1 if percentage >= QUIZ["passing_score"] else 0
    submitted_at = datetime.now().isoformat()

    db = get_db()
    cursor = db.execute(
        """INSERT INTO submissions (nombre, sucursal, score, total, percentage, passed, time_taken_seconds, submitted_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (nombre, sucursal, score, total, percentage, passed, time_taken, submitted_at)
    )
    submission_id = cursor.lastrowid

    for a in answer_records:
        db.execute(
            """INSERT INTO answers (submission_id, question_id, question_text, category, selected_option, correct_option, is_correct)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (submission_id, a["question_id"], a["question_text"], a["category"],
             a["selected_option"], a["correct_option"], a["is_correct"])
        )
    db.commit()

    # Build result details for the candidate
    results_detail = []
    for q in QUIZ["questions"]:
        qid = str(q["id"])
        selected = respuestas.get(qid)
        results_detail.append({
            "id": q["id"],
            "text": q["text"],
            "category": q["category"],
            "options": q["options"],
            "selected": selected,
            "correct": q["correct"],
            "is_correct": selected == q["correct"] if selected is not None else False,
            "explanation": q["explanation"]
        })

    return jsonify({
        "score": score,
        "total": total,
        "percentage": percentage,
        "passed": passed,
        "time_taken_seconds": time_taken,
        "results": results_detail
    })

@app.route("/api/quiz-data")
def quiz_data():
    """Return quiz metadata (no answers) for the frontend."""
    safe_questions = []
    for q in QUIZ["questions"]:
        safe_questions.append({
            "id": q["id"],
            "category": q["category"],
            "text": q["text"],
            "options": q["options"]
        })
    return jsonify({
        "title": QUIZ["title"],
        "time_limit_minutes": QUIZ["time_limit_minutes"],
        "total_questions": len(QUIZ["questions"]),
        "questions": safe_questions
    })

# Initialize DB on import (for gunicorn)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055, debug=True)
