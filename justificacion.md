---
layout: default
title: Justificación tecnológica
nav_order: 3
---

# 🛠️ Justificación tecnológica

En esta sección documentamos las decisiones técnicas tomadas para la construcción del healthchecker, asegurando que cada herramienta elegida aporte valor real al desarrollo y mantenimiento del producto.

## Lenguajes y Frameworks

X.

## Integración y Despliegue Continuo (CI/CD)

La implementación de pipelines de CI/CD es fundamental en el healthchecker para garantizar entregas ágiles y seguras. Nos permite automatizar la ejecución de pruebas y el despliegue a los distintos entornos, reduciendo el error humano y acelerando el *time-to-market*.

## Pruebas unitarias y Code Coverage

Para asegurar la robustez y estabilidad del código, mantenemos un estándar estricto de calidad:

* Se ha implementado una gran cantidad de pruebas unitarias cubriendo los casos de uso principales y casos borde.
* Mantenemos un **estricto nivel de Code Coverage** (cobertura de código) fijado en un mínimo del **[90]%**, el cual es validado automáticamente en cada Pull Request mediante nuestro pipeline.

## Documentación integral

Utilizamos **JustTheDocs** para mantener esta documentación viva, versionada junto con el código y fácilmente accesible para cualquier miembro del equipo. Esto centraliza el conocimiento y reduce los cuellos de botella en la comunicación.
