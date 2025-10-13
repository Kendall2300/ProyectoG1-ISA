# Manual de Usuario — Simulador de CPU secureRISC

## 1. Introducción

En este documento explica cómo instalar, ejecutar y usar el simulador de CPU **secureRISC**. El simulador permite escribir, compilar y ejecutar programas en ensamblador secureRISC mediante una interfaz gráfica e incluye funciones para firmar y autenticar documentos digitalmente.

---

## 2. Requisitos del sistema

* Python 3.8 o superior
* pip
* git

Compatible con Windows, Linux y macOS.

---

## 3. Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Kendall2300/ProyectoG1-ISA
cd SimuladorCPU/src
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
```

### 3. Activar entorno virtual

**En Linux/Mac:**

```bash
source venv/bin/activate
```

**En Windows:**

```bash
venv\Scripts\activate
```

### 4. Verificar instalación

```bash
python3 main.py --version
```

---

## 4. Ejecución del simulador

1. Ejecutar el programa:

   ```bash
   python3 main.py
   ```

   Se abrirá la interfaz gráfica principal.

2. Cargar o escribir código:

   * Escribir código directamente usando la gramática **secureRISC**.
   * O cargar un archivo `.asm` o `.s` desde el explorador de archivos de la interfaz.

3. Compilar:

   * Presionar el botón **Compile**.
   * Si hay errores de sintaxis la interfaz mostrará información para corregirlos.

4. Ejecutar:

   * Tras compilar sin errores, presionar **Run** para ejecutar la simulación.

---

## 5. Visualización de memoria y registros

* Presionar **Memory View** en la interfaz.
* Se abrirá una ventana que muestra los valores actuales de los registros y la memoria.
* Los valores se actualizan durante la ejecución del programa.

---

## 6. Firma digital de documentos

El simulador permite agregar, firmar y autenticar documentos:

* **Agregar documento:** seleccionar un archivo desde el diálogo.
* **Firmar documento:** generar y adjuntar una firma digital al documento.
* **Autenticar firma:** verificar la integridad y autoría de un documento firmado.
  Las opciones de firma están disponibles en el menú principal de la interfaz.

---

## 7. Solución de problemas

| Problema                             | Causa probable                                | Solución                                                        |
| ------------------------------------ | --------------------------------------------- | --------------------------------------------------------------- |
| El simulador no inicia               | Python no instalado o versión < 3.8           | Instalar Python 3.8+ y repetir la instalación                   |
| `python3 main.py --version` falla    | Entorno virtual no activado o ruta incorrecta | Activar `venv` y ejecutar desde `SimuladorCPU/src`              |
| Error al compilar código             | Sintaxis inválida según gramática secureRISC  | Revisar y corregir el código fuente                             |
| La vista de memoria no muestra datos | Programa no compilado o no ejecutado          | Compilar y ejecutar; luego abrir **Memory View**                |
| Operación de firma falla             | Archivo no válido o error de configuración    | Verificar el archivo y revisar mensajes de error en la interfaz |


## 8. Créditos

Proyecto para el curso **Arquitectura de Computadores** — **Ingeniería en Computadores**.
Autores: Equipo G1.
Repositorio: `https://github.com/Kendall2300/ProyectoG1-ISA`.
