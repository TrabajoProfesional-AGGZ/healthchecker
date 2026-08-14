---
layout: default
title: Justificación tecnológica
nav_order: 3
---

# 🛠️ Justificación tecnológica

En esta sección documentamos las decisiones técnicas tomadas para la construcción del healthchecker, asegurando que cada herramienta elegida aporte valor real al desarrollo y mantenimiento del producto.

## Lenguajes y Frameworks

Para este microservicio, la selección de nuestra pila tecnológica se basó en la agilidad, la escalabilidad y la facilidad de mantenimiento continuo:

* **Python:** Se eligió como lenguaje principal por su sintaxis clara, curva de aprendizaje rápida y su excelente manejo de operaciones de red. Para un servicio que actúa como monitor central y auditor de transacciones, Python nos permite realizar peticiones concurrentes y procesar respuestas con un altísimo rendimiento y pocas líneas de código.
* **FastAPI:** Seleccionado como framework web por su rendimiento de clase mundial (soporte asíncrono nativo). Su mayor ventaja para este proyecto es la validación estricta de datos y la **autogeneración de documentación interactiva (Swagger/OpenAPI)**. Esto garantiza que nuestros contratos de API estén siempre sincronizados con el código, facilitando la integración con los demás sistemas de SocioUnido.
* **Pytest:** Adoptado como nuestro framework de pruebas. Su ecosistema, simplicidad y uso de *fixtures* nos permite escribir tests escalables y legibles, asegurando que el motor de auditoría y monitoreo no tenga falsos positivos ni caídas silenciosas.
* **Docker y Docker Compose:** La contenerización es indispensable en nuestra arquitectura. Nos permite aislar el healthchecker y garantizar la paridad entre entornos (desarrollo, *staging* y producción).

## Integración y Despliegue Continuo (CI/CD)

La implementación de pipelines de CI/CD es fundamental en el healthchecker para garantizar entregas ágiles y seguras. Nos permite automatizar la ejecución de pruebas y el despliegue a los distintos entornos, reduciendo el error humano y acelerando el *time-to-market*.

## Pruebas unitarias y Code Coverage

Para asegurar la robustez y estabilidad del código, mantenemos un estándar estricto de calidad:

* Se ha implementado una gran cantidad de pruebas unitarias cubriendo los casos de uso principales y casos borde.
* Mantenemos un **estricto nivel de Code Coverage** (cobertura de código) fijado en un mínimo del **90%**, el cual es validado automáticamente en cada Pull Request mediante nuestro pipeline.

## Documentación integral

Utilizamos **JustTheDocs** para mantener esta documentación viva, versionada junto con el código y fácilmente accesible para cualquier miembro del equipo. Esto centraliza el conocimiento y reduce los cuellos de botella en la comunicación.
