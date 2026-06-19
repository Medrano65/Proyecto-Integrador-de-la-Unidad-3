# ==============================================================================
# PROYECTO INTEGRADOR - UNIDAD 3: MANEJO DE ESTRUCTURAS DE DATOS
# SISTEMA DE GESTIÓN DE EMERGENCIAS MÉDICAS (TRIAJE HOSPITALARIO)
# UNIVERSIDAD DE EL SALVADOR
# ==============================================================================

# 1. CLASE PACIENTE (Contiene la PILA para el historial de procedimientos)
class Paciente:
    def __init__(self, id_paciente, nombre, sintomas, nivel_triaje):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.sintomas = sintomas
        self.nivel_triaje = nivel_triaje  # Entero del 1 (Leve) al 5 (Crítico)
        self.historial_medico = []         # Pila LIFO usando una lista de Python

    def registrar_procedimiento(self, procedimiento):
        """Operación Push de la Pila (Añadir procedimiento)"""
        self.historial_medico.append(procedimiento)

    def deshacer_ultimo_procedimiento(self):
        """Operación Pop de la Pila (Remover último procedimiento por error)"""
        if self.historial_medico:
            return self.historial_medico.pop()
        return None


# 2. CLASES PARA LA COLA (Estructura Lineal FIFO por cada nivel de triaje)
class NodoCola:
    def __init__(self, paciente):
        self.paciente = paciente
        self.siguiente = None


class ColaPacientes:
    def __init__(self):
        self.frente = None
        self.final = None

    def encolar(self, paciente):
        """Operación Enqueue (Inserta al final de la fila)"""
        nuevo_nodo = NodoCola(paciente)
        if self.final is None:
            self.frente = self.final = nuevo_nodo
            return
        self.final.siguiente = nuevo_nodo
        self.final = nuevo_nodo

    def desencolar(self):
        """Operación Dequeue (Remueve y retorna al primero de la fila)"""
        if self.frente is None:
            return None
        temporal = self.frente
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        return temporal.paciente


# 3. CLASE NODO DEL ÁRBOL (Estructura No Lineal - Organiza los niveles de triaje)
class NodoArbolTriaje:
    def __init__(self, nivel_triaje):
        self.nivel_triaje = nivel_triaje        # Clave del nodo (1, 2, 3, 4 o 5)
        self.cola_pacientes = ColaPacientes()   # Cada nodo maneja su propia cola FIFO
        self.izquierdo = None                   # Subárbol izquierdo (menor prioridad)
        self.derecho = None                     # Subárbol derecho (mayor prioridad)


# 4. CLASE NODO DE LISTA ENLAZADA (Almacenamiento Dinámico para Historial de Altas)
class NodoHistorialGlobal:
    def __init__(self, paciente):
        self.paciente = paciente
        self.siguiente = None


# 5. CLASE PRINCIPAL DEL SISTEMA (Controla la lógica del hospital y recursividad)
class SistemaEmergencias:
    def __init__(self):
        self.raiz_triaje = None         # Raíz del Árbol Binario de Búsqueda
        self.historial_altas = None     # Cabeza de la Lista Enlazada Simple

    # --- RECURSIVIDAD: Inserción en el Árbol Binario de Búsqueda ---
    def _insertar_en_arbol(self, raiz, nivel_triaje, paciente):
        if raiz is None:
            nuevo_nodo = NodoArbolTriaje(nivel_triaje)
            nuevo_nodo.cola_pacientes.encolar(paciente)
            return nuevo_nodo
        
        if nivel_triaje == raiz.nivel_triaje:
            raiz.cola_pacientes.encolar(paciente)
        elif nivel_triaje < raiz.nivel_triaje:
            raiz.izquierdo = self._insertar_en_arbol(raiz.izquierdo, nivel_triaje, paciente)
        else:
            raiz.derecho = self._insertar_en_arbol(raiz.derecho, nivel_triaje, paciente)
        return raiz

    def registrar_paciente(self, paciente):
        """Interfaz pública para registrar un paciente en el ABB"""
        self.raiz_triaje = self._insertar_en_arbol(self.raiz_triaje, paciente.nivel_triaje, paciente)

    # --- RECURSIVIDAD: Búsqueda del paciente más crítico activo ---
    def _obtener_nodo_maximo_con_espera(self, raiz):
        if raiz is None:
            return None
        
        # Intentamos buscar en el subárbol derecho primero (valores de triaje más altos)
        nodo_derecho = self._obtener_nodo_maximo_con_espera(raiz.derecho)
        if nodo_derecho is not None:
            return nodo_derecho
            
        # Si a la derecha no hay nadie con fila activa, evaluamos el nodo actual
        if raiz.cola_pacientes.frente is not None:
            return raiz
            
        # Si el actual está vacío de pacientes, buscamos por el subárbol izquierdo
        return self._obtener_nodo_maximo_con_espera(raiz.izquierdo)

    # --- MÉTODO: Atender Siguiente Paciente ---
    def atender_paciente(self):
        nodo_critico = self._obtener_nodo_maximo_con_espera(self.raiz_triaje)
        
        if nodo_critico is None:
            print("\n[INFO]: No hay pacientes en la sala de espera actualmente.")
            return None
            
        # Desencolamos de la estructura lineal interna del nodo
        paciente_atendido = nodo_critico.cola_pacientes.desencolar()
        
        print(f"\n[ATENCIÓN]: Llamando a {paciente_atendido.nombre} (Gravedad: {paciente_atendido.nivel_triaje})")
        print(f" -> Diagnóstico/Síntomas: {paciente_atendido.sintomas}")
        
        # Uso automático de la Pila para registrar la atención
        paciente_atendido.registrar_procedimiento("Control de Signos Vitales")
        paciente_atendido.registrar_procedimiento("Suministro de medicamento de primera respuesta")
        print(f" -> Procedimientos en Pila LIFO: {paciente_atendido.historial_medico}")
        
        # Insertar dinámicamente en la Lista Enlazada de Altas (O(1) al inicio)
        nuevo_nodo_alta = NodoHistorialGlobal(paciente_atendido)
        if self.historial_altas is None:
            self.historial_altas = nuevo_nodo_alta
        else:
            nuevo_nodo_alta.siguiente = self.historial_altas
            self.historial_altas = nuevo_nodo_alta
            
        print(f"[ÉXITO]: {paciente_atendido.nombre} trasladado a la Lista de Altas Médicas.")
        return paciente_atendido

    # --- RECURSIVIDAD: Mostrar Reporte In-Order Invertido (Mayor a Menor Gravedad) ---
    def mostrar_reporte_recursivo(self, raiz):
        if raiz is not None:
            self.mostrar_reporte_recursivo(raiz.derecho)
            
            print(f"\n--- [Nivel de Triaje: {raiz.nivel_triaje}] ---")
            actual = raiz.cola_pacientes.frente
            if actual is None:
                print("    (No hay pacientes esperando en este nivel)")
            else:
                posicion = 1
                while actual is not None:
                    p = actual.paciente
                    print(f"    {posicion}. ID: {p.id_paciente} | {p.nombre} | Síntomas: {p.sintomas}")
                    actual = actual.siguiente
                    posicion += 1
                
            self.mostrar_reporte_recursivo(raiz.izquierdo)

    # --- MÉTODO: Recorrer de forma lineal la Lista Enlazada de Altas ---
    def mostrar_historial_altas(self):
        print("\n" + "="*45)
        print("   HISTORIAL GLOBAL DE ALTAS MÉDICAS")
        print("="*45)
        actual = self.historial_altas
        if actual is None:
            print("No se han registrado altas médicas en el sistema todavía.")
            return
            
        while actual is not None:
            p = actual.paciente
            ultimo_proc = p.historial_medico[-1] if p.historial_medico else "Ninguno"
            print(f" * [ID: {p.id_paciente}] - {p.nombre}")
            print(f"   Triaje: {p.nivel_triaje} | Última acción registrada: {ultimo_proc}")
            print("-" * 45)
            actual = actual.siguiente


# 6. INTERFAZ DE USUARIO POR CONSOLA (Menú Principal con try-except)
def mostrar_menu():
    print("\n" + "="*50)
    print("   SISTEMA DE GESTIÓN DE EMERGENCIAS MÉDICAS - UES")
    print("="*50)
    print("1. Registrar ingreso de nuevo paciente")
    print("2. Atender al paciente de mayor gravedad activo")
    print("3. Visualizar sala de espera (Reporte Recursivo)")
    print("4. Mostrar historial global de altas (Lista Enlazada)")
    print("5. Corregir/Deshacer último procedimiento (Uso de Pila)")
    print("6. Salir de la aplicación")
    print("="*50)


def ejecutar_sistema():
    sistema = SistemaEmergencias()
    
    # Carga de datos iniciales para pruebas rápidas
    print("\n[SISTEMA]: Cargando entradas de prueba obligatorias...")
    sistema.registrar_paciente(Paciente(101, "Carlos Ramos", "Sospecha de infarto", 5))
    sistema.registrar_paciente(Paciente(102, "María Mendoza", "Fractura expuesta", 4))
    sistema.registrar_paciente(Paciente(103, "Juan Pérez", "Fiebre persistente", 2))
    sistema.registrar_paciente(Paciente(104, "Ana Gómez", "Crisis respiratoria severa", 5))
    print("[SISTEMA]: Datos listos para verificación.")
    
    while True:
        mostrar_menu()
        try:
            opcion = int(input("Ingrese su opción (1-6): "))
            
            if opcion == 1:
                print("\n>>> REGISTRO DE TRIAJE <<<")
                id_p = int(input("Número de expediente único (ID): "))
                nombre = input("Nombre completo del paciente: ")
                sintomas = input("Descripción de síntomas: ")
                
                while True:
                    nivel = int(input("Clasificación de triaje (1: Leve, 5: Crítico): "))
                    if 1 <= nivel <= 5:
                        break
                    print("[AVISO]: Por norma médica el triaje debe estar en el rango de 1 a 5.")
                
                paciente = Paciente(id_p, nombre, sintomas, nivel)
                sistema.registrar_paciente(paciente)
                print(f"\n[ÉXITO]: {nombre} ordenado en el nivel de espera {nivel}.")

            elif opcion == 2:
                sistema.atender_paciente()

            elif opcion == 3:
                print("\n=== REPORTE GENERADO RECURSIVAMENTE DESDE EL ABB ===")
                sistema.mostrar_reporte_recursivo(sistema.raiz_triaje)

            elif opcion == 4:
                sistema.mostrar_historial_altas()

            elif opcion == 5:
                print("\n>>> MENÚ DE CORRECCIÓN DE EXPEDIENTE (PILA LIFO) <<<")
                nodo_critico = sistema._obtener_nodo_maximo_con_espera(sistema.raiz_triaje)
                if nodo_critico and nodo_critico.cola_pacientes.frente:
                    paciente_en_espera = nodo_critico.cola_pacientes.frente.paciente
                    
                    # Registramos un procedimiento de simulación erróneo para probar
                    paciente_en_espera.registrar_procedimiento("Inyección errónea de analgésico")
                    print(f"Historial actual de {paciente_en_espera.nombre}: {paciente_en_espera.historial_medico}")
                    
                    # Se remueve mediante POP
                    removido = paciente_en_espera.deshacer_ultimo_procedimiento()
                    print(f"\n[CORRECCIÓN AUTOMÁTICA]: Se ejecutó POP. Removido: '{removido}'")
                    print(f"Historial corregido de forma segura: {paciente_en_espera.historial_medico}")
                else:
                    print("[INFO]: No hay pacientes en atención activa para alterar su pila.")

            elif opcion == 6:
                print("\n[SISTEMA]: Finalizando simulación. Código libre de errores ejecutado.")
                break
            else:
                print("[ERROR]: Por favor inserte un número válido dentro de las opciones (1-6).")
                
        except ValueError:
            print("\n[ERROR DE ENTRADA]: Se esperaba un número entero. Evite letras y caracteres especiales.")


# Punto de arranque del script de Python
if __name__ == "__main__":
    ejecutar_sistema()