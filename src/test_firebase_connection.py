# src/test_firebase_connection.py

# Importación de librerías necesarias
import pyrebase  # La biblioteca principal para interactuar con Firebase
import os        # Para operaciones del sistema operativo, como verificar la existencia de archivos
import time      # Para generar timestamps únicos y pausas si fuera necesario

# Importación de la configuración de Firebase desde el archivo local firebase_config.py
# Se asume que 'firebase_config.py' está en la misma carpeta 'src'.
# FIREBASE_CONFIG contiene los detalles de tu proyecto (API Key, Project ID, etc.).
# SERVICE_ACCOUNT_KEY_PATH es la ruta al archivo JSON de las credenciales de servicio.
from config.firebase_config import FIREBASE_CONFIG, SERVICE_ACCOUNT_KEY_PATH

def run_firebase_connection_test():
    """
    Función principal que ejecuta las pruebas de conexión y operaciones CRUD
    (Crear, Leer, Actualizar, Eliminar) con Firebase Realtime Database
    y también verifica la autenticación.
    """
    print("\n--- Iniciando prueba de conexión a Firebase ---")

    try:
        # --- Verificación del archivo de clave de servicio ---
        # Es crucial que el archivo JSON de las credenciales de servicio exista y sea accesible.
        print(f"Verificando archivo de clave de servicio en: {SERVICE_ACCOUNT_KEY_PATH}")
        if os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
            print("Archivo de clave de servicio encontrado. ¡Bien!")
        else:
            # Si el archivo no se encuentra, se imprime una advertencia detallada
            # y la función termina, ya que la conexión no sería posible.
            print("¡ADVERTENCIA: Archivo de clave de servicio NO encontrado en la ruta especificada!")
            print("Por favor, revisa la ruta en src/firebase_config.py y la ubicación del archivo.")
            print(f"La ruta absoluta esperada es: {os.path.abspath(SERVICE_ACCOUNT_KEY_PATH)}")
            return # Salir de la función si el archivo no está

        # --- Inicialización de Pyrebase4 ---
        # Se inicializa la aplicación de Firebase utilizando la configuración importada.
        # Esto establece la conexión principal con tu proyecto de Firebase.
        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        print("Pyrebase4 inicializado correctamente con la configuración.")

        # --- Prueba de Autenticación (Firebase Authentication) ---
        # Esta sección verifica la capacidad de interactuar con el servicio de autenticación de Firebase.
        # Permite registrar nuevos usuarios o iniciar sesión con existentes.
        print("\n--- Probando Autenticación ---")
        auth = firebase.auth() # Obtiene el objeto de autenticación de Firebase.

        # Se genera un correo electrónico de prueba con un timestamp para asegurar unicidad
        # en caso de múltiples ejecuciones, evitando el error EMAIL_EXISTS.
        timestamp_auth = int(time.time())
        test_email = f"testuser_{timestamp_auth}@klarityfinanzas.com"
        test_password = "password123"

        try:
            # Intenta registrar un nuevo usuario con el email y contraseña generados.
            user = auth.create_user_with_email_and_password(test_email, test_password)
            print(f"Usuario registrado exitosamente: {user['email']} (UID: {user['localId']})")
        except Exception as e:
            # Manejo de errores durante el registro.
            if "EMAIL_EXISTS" in str(e):
                # Si el usuario ya existe (lo cual es poco probable con el timestamp, pero posible
                # si se ejecuta muy rápido o se usa un email fijo), se intenta iniciar sesión.
                print(f"El usuario con email generado ({test_email}) ya existía o hubo un conflicto.")
                print("Intentando iniciar sesión con un usuario preexistente (puedes cambiarlo).")
                try:
                    # Aquí se puede cambiar a un correo y contraseña de un usuario conocido si se desea
                    # probar específicamente el inicio de sesión de un usuario existente.
                    existing_email = "known_test@klarityfinanzas.com" # CAMBIA ESTO A UN EMAIL REAL SI LO NECESITAS
                    existing_password = "password123" # Y SU CONTRASEÑA
                    user = auth.sign_in_with_email_and_password(existing_email, existing_password)
                    print(f"Inicio de sesión exitoso para usuario existente: {user['email']}")
                except Exception as login_e:
                    print(f"Error al iniciar sesión con usuario existente: {login_e}")
            else:
                # Otros errores inesperados durante la autenticación.
                print(f"Error inesperado al registrar/iniciar sesión: {e}")
                print("Asegúrate de que el método de inicio de sesión 'Email/contraseña' esté habilitado en Firebase Authentication.")


        # --- Probando Operaciones CRUD en Realtime Database ---
        # Esta es la sección principal para probar la interacción con la base de datos en tiempo real.
        print("\n--- Probando Operaciones CRUD en Realtime Database ---")
        db = firebase.database() # Obtiene el objeto de la base de datos de Firebase.

        # 1. Crear Datos (Create) - Usando `set()` con una clave personalizada
        # `set()` sobrescribe los datos en la ruta especificada. Es útil para nodos
        # con IDs conocidos o para establecer un nodo completo.
        print("\n--- Creando un nuevo usuario con ID personalizado (set()) ---")
        custom_user_id = "usuario_test_001" # ID de usuario que definimos
        user_data = {
            "name": "Pedro Prueba",
            "email": "pedro.prueba@example.com",
            "saldo": 1500.75,
            "activo": True
        }
        try:
            # Se navega al nodo "usuarios" y luego al hijo con el ID personalizado,
            # y se establecen los datos definidos en `user_data`.
            db.child("usuarios").child(custom_user_id).set(user_data)
            print(f"Usuario '{custom_user_id}' creado/actualizado exitosamente en la base de datos.")
        except Exception as e:
            print(f"Error al crear usuario con set(): {e}")

        # 2. Crear Datos (Create) - Usando `push()` para un nodo auto-generado
        # `push()` crea un nuevo nodo hijo con una clave única generada por Firebase
        # (basada en timestamp, garantizando unicidad y orden cronológico).
        print("\n--- Agregando una transacción con clave auto-generada (push()) ---")
        transaction_data = {
            "descripcion": "Compra de víveres",
            "monto": -50.25,
            "fecha": int(time.time()), # Timestamp actual para la fecha
            "categoria": "alimentos",
            "usuario_id": custom_user_id
        }
        try:
            # Se navega al nodo "transacciones" y se añade la `transaction_data`.
            # `push()` devuelve una referencia al nuevo nodo, y `['name']` contiene la clave generada.
            new_transaction_ref = db.child("transacciones").push(transaction_data)
            new_key = new_transaction_ref['name']
            print(f"Transacción agregada exitosamente con clave: {new_key}")
            # Se guarda la clave globalmente para poder eliminar esta transacción específica más tarde.
            global_transaction_key = new_key
        except Exception as e:
            print(f"Error al agregar transacción con push(): {e}")


        # 3. Leer Datos (Read) - Leer el usuario creado con ID personalizado
        # `get()` recupera los datos de la ubicación especificada. `.val()` obtiene el valor
        # real del snapshot de datos como un diccionario/lista de Python.
        print(f"\n--- Leyendo datos del usuario '{custom_user_id}' ---")
        try:
            # Se obtiene el snapshot del usuario con el ID personalizado.
            user_snapshot = db.child("usuarios").child(custom_user_id).get()
            user_data_read = user_snapshot.val()
            if user_data_read:
                print(f"Datos del usuario '{custom_user_id}':")
                # Se itera sobre los ítems del diccionario para una impresión formateada.
                for key, value in user_data_read.items():
                    print(f"    {key}: {value}")
            else:
                print(f"No se encontraron datos para el usuario '{custom_user_id}'.")
        except Exception as e:
            print(f"Error al leer datos del usuario: {e}")

        # 4. Leer Datos (Read) - Leer todas las transacciones (iterar sobre claves push)
        # Cuando los datos son auto-generados por `push()`, se recupera el nodo padre
        # y se itera sobre sus hijos usando `.each()`.
        print("\n--- Leyendo todas las transacciones ---")
        try:
            transactions_snapshot = db.child("transacciones").get()
            if transactions_snapshot.val(): # Verifica si hay datos en el snapshot
                print("Transacciones encontradas:")
                # `.each()` itera sobre los hijos directos, proporcionando objetos snapshot
                # que tienen métodos `.key()` (la clave generada) y `.val()` (los datos).
                for transaction_item in transactions_snapshot.each():
                    print(f"    Clave: {transaction_item.key()} | Datos: {transaction_item.val()}")
            else:
                print("No se encontraron transacciones.")
        except Exception as e:
            print(f"Error al leer todas las transacciones: {e}")


        # 5. Actualizar Datos (Update) - Actualizar el saldo del usuario
        # `update()` fusiona los datos proporcionados con los datos existentes en la ubicación.
        # No sobrescribe el nodo completo, solo los campos especificados.
        print(f"\n--- Actualizando saldo del usuario '{custom_user_id}' ---")
        updates = {
            "saldo": 1450.50,         # Nuevo valor para el campo 'saldo'
            "ultima_actualizacion": int(time.time()) # Se añade un nuevo campo
        }
        try:
            # Se actualizan los datos del usuario con el ID personalizado.
            db.child("usuarios").child(custom_user_id).update(updates)
            print(f"Saldo del usuario '{custom_user_id}' actualizado.")
            # Se lee el usuario de nuevo para confirmar la actualización.
            updated_user = db.child("usuarios").child(custom_user_id).get().val()
            print(f"Datos del usuario '{custom_user_id}' después de la actualización: {updated_user}")
        except Exception as e:
            print(f"Error al actualizar el saldo del usuario: {e}")

        # 6. Eliminar Datos (Delete) - Eliminar un campo específico (ej. "activo")
        # `remove()` elimina el nodo en la ruta especificada.
        print(f"\n--- Eliminando el campo 'activo' del usuario '{custom_user_id}' ---")
        try:
            # Se navega hasta el campo 'activo' dentro del usuario y se elimina.
            db.child("usuarios").child(custom_user_id).child("activo").remove()
            print(f"Campo 'activo' eliminado para el usuario '{custom_user_id}'.")
            # Se lee el usuario de nuevo para confirmar la eliminación del campo.
            user_after_delete_field = db.child("usuarios").child(custom_user_id).get().val()
            print(f"Usuario '{custom_user_id}' después de eliminar campo 'activo': {user_after_delete_field}")
        except Exception as e:
            print(f"Error al eliminar campo 'activo': {e}")


        # 7. Eliminar Datos (Delete) - Eliminar un nodo completo (opcional, cuidado al ejecutar)
        # Esta operación eliminará el usuario de prueba completo que creamos.
        # Es muy importante tener precaución con `remove()` ya que elimina todo en la ruta.
        # Se comenta por defecto para evitar borrados accidentales de datos de prueba.
        print(f"\n--- Eliminando al usuario '{custom_user_id}' (opcional, descomentar si deseas borrar) ---")
        try:
            # Descomenta la siguiente línea para eliminar el usuario completamente:
            # db.child("usuarios").child(custom_user_id).remove()
            # print(f"Usuario '{custom_user_id}' eliminado completamente.")
            pass # No hace nada si la línea de arriba está comentada
        except Exception as e:
            print(f"Error al eliminar el usuario completo: {e}")

        # 8. Eliminar Datos (Delete) - Eliminar una transacción específica por su clave auto-generada
        # Para eliminar un nodo creado con `push()`, necesitas su clave única.
        print(f"\n--- Eliminando la transacción creada con clave auto-generada (si existe) ---")
        # Se verifica si la clave de la transacción fue guardada durante la creación.
        if 'global_transaction_key' in locals() and global_transaction_key:
            try:
                # Se navega directamente a la transacción usando la clave guardada y se elimina.
                db.child("transacciones").child(global_transaction_key).remove()
                print(f"Transacción con clave '{global_transaction_key}' eliminada.")
            except Exception as e:
                print(f"Error al eliminar la transacción: {e}")
        else:
            print("No se generó una clave de transacción para eliminar en esta ejecución.")


    except Exception as e:
        # Bloque de manejo de errores general para capturar cualquier problema
        # que impida la inicialización de Pyrebase4 o cause un error crítico.
        print(f"\n--- ¡ERROR CRÍTICO EN LA CONFIGURACIÓN DE FIREBASE! ---")
        print(f"No se pudo inicializar Pyrebase4 o ocurrió un error general: {e}")
        print("Revisa los mensajes de error detallados arriba y tu configuración.")
        print("Posibles causas:")
        print("1. Los valores en FIREBASE_CONFIG en firebase_config.py son incorrectos o incompletos.")
        print("2. La ruta a SERVICE_ACCOUNT_KEY_PATH es incorrecta o el archivo JSON no existe.")
        print("3. No tienes conexión a Internet.")
        print("4. Alguna dependencia de Pyrebase4 no está instalada correctamente.")

    print("\n--- Fin de la prueba de conexión y CRUD de Firebase ---")

# Este bloque asegura que la función `run_firebase_connection_test()` se ejecute
# solo cuando el script es el programa principal y no cuando es importado como un módulo.
if __name__ == "__main__":
    run_firebase_connection_test()