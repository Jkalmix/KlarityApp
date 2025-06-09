# ====================================================================================================
# DOCUMENTACIÓN DETALLADA DE LAS FUNCIONES DE INTERACCIÓN DE USUARIO (MAIN.PY)
# ====================================================================================================
# Estas funciones son el "cerebro" detrás de los botones y acciones que el usuario realiza en la GUI.
# Se encargan de validar la entrada, comunicarse con Firebase a través de 'firebase_service.py',
# y luego actualizar la interfaz o mostrar mensajes al usuario según el resultado.
# ====================================================================================================

def intentar_login():
    """
    Propósito:
        Esta función se activa cuando el usuario hace clic en el botón "Iniciar Sesión"
        en la ventana de Login. Su objetivo es tomar el email y la contraseña ingresados,
        intentar autenticar al usuario con Firebase, y luego decidir qué hacer:
        si el login es exitoso, abre la pantalla principal; si falla, muestra un error.

    Cómo funciona paso a paso:

    1.  `global current_user`:
        * `global` es una palabra clave en Python que nos permite decirle a la función
            que vamos a usar y posiblemente cambiar una variable que está definida
            fuera de esta función (en este caso, `current_user` está definida al inicio
            de `main.py`).
        * `current_user` es una variable que guardará los datos del usuario que
            ha iniciado sesión exitosamente. Es como tener un "estado de sesión" en tu app.

    2.  `email = email_entry.get()` y `password = password_entry.get()`:
        * Aquí, recuperamos lo que el usuario ha escrito en los campos de entrada
            (los cuadros de texto) de la ventana de login.
        * `email_entry` y `password_entry` son variables que representan esos cuadros
            de texto en la GUI. `.get()` es un método de Tkinter que extrae el texto actual.

    3.  `if not email or not password:`:
        * Esta es una **validación básica**. Antes de intentar conectar con Firebase,
            verificamos si el usuario dejó alguno de los campos de email o contraseña vacíos.
        * `not email` es `True` si la cadena `email` está vacía.
        * Si algún campo está vacío, se ejecuta el siguiente bloque:
            * `messagebox.showerror(...)`: Muestra una pequeña ventana emergente
                con un mensaje de error. Es una forma amigable de avisar al usuario
                sin que la aplicación se caiga.
                * "Error de Login": Es el título de la ventana de error.
                * "Por favor, introduce tu email y contraseña.": Es el mensaje que ve el usuario.
                * `parent=login_window`: Indica que esta ventana de error debe aparecer
                    encima de la ventana de login (para que el usuario sepa de qué ventana
                    proviene el error).
            * `return`: Detiene la ejecución de la función `intentar_login()` aquí mismo.
                No se procede con el intento de conexión a Firebase.

    4.  `user, error = firebase_service.login_user(email, password)`:
        * ¡Esta es la **integración clave con Firebase**!
        * Llamamos a la función `login_user` que está definida en el archivo
            `firebase_service.py`. Esta función es la que realmente se conecta con Firebase.
        * Le pasamos el `email` y la `password` que el usuario ingresó.
        * `firebase_service.login_user()` está diseñada para devolver dos cosas:
            * `user`: Si el inicio de sesión fue exitoso, esto será un diccionario
                        con los datos del usuario logueado (como su email, su UID - ID único, etc.).
                        Si falla, será `None`.
            * `error`: Si hubo un error, esto será un mensaje de texto descriptivo
                         del problema (ej. "Contraseña incorrecta", "Usuario no encontrado").
                         Si no hubo error, será `None`.

    5.  `if user:`:
        * Aquí verificamos el resultado de la llamada a `firebase_service.login_user()`.
        * Si `user` tiene un valor (es decir, no es `None`), significa que el login fue exitoso.
            * `current_user = user`: Guardamos el diccionario `user` en nuestra
                                       variable global `current_user`. Esto es importante porque
                                       otras partes de la aplicación necesitarán saber quién
                                       está logueado (ej. para mostrar su email en el dashboard).
            * `messagebox.showinfo(...)`: Muestra una ventana de información
                indicando que el login fue exitoso, saludando al usuario por su email.
            * `login_window.destroy()`: Cierra la ventana de login, ya que el usuario
                                          ha accedido.
            * `mostrar_home()`: Llama a otra función para abrir la ventana principal
                                  (el dashboard) de la aplicación.

    6.  `else:`:
        * Si `user` es `None`, significa que el login falló.
            * `messagebox.showerror("Error de Login", error, parent=login_window)`:
                Muestra una ventana de error. El mensaje de error (`error`) proviene
                directamente de `firebase_service.login_user()`, lo que permite
                mostrar mensajes específicos de Firebase (como "Contraseña incorrecta").

    """
    global current_user

    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Error de Login", "Por favor, introduce tu email y contraseña.", parent=login_window)
        return

    # --- INTEGRACIÓN CON FIREBASE SERVICE ---
    user, error = firebase_service.login_user(email, password)

    if user:
        current_user = user
        messagebox.showinfo("Login Exitoso", f"¡Bienvenido/a a Klarity, {current_user['email']}!", parent=login_window)
        login_window.destroy()
        mostrar_home()
    else:
        messagebox.showerror("Error de Login", error, parent=login_window)


def intentar_registro():
    """
    Propósito:
        Esta función se activa cuando el usuario hace clic en el botón "Registrar Cuenta"
        en la ventana de Registro. Su objetivo es crear un nuevo usuario en Firebase
        Authentication y, si es exitoso, también guardar un perfil inicial para ese
        usuario en la Realtime Database.

    Cómo funciona paso a paso:

    1.  `global current_user`:
        * Al igual que en `intentar_login`, indicamos que usaremos la variable global
            `current_user` para guardar el usuario recién registrado.

    2.  `nombre = nombre_entry.get()` ... `confirm_password = confirm_password_entry.get()`:
        * Obtenemos todos los datos que el usuario ingresó en los campos de la ventana de registro.

    3.  `if not nombre or not email or ...`:
        * **Primera validación de entrada:** Verifica que *ninguno* de los campos esté vacío.
        * Si alguno está vacío, muestra un error y detiene la función (`return`).

    4.  `if password != confirm_password:`:
        * **Segunda validación:** Compara si la contraseña ingresada coincide con la confirmación.
        * Si no coinciden, muestra un error específico y detiene la función.

    5.  `if len(password) < 6:`:
        * **Tercera validación:** Verifica la longitud mínima de la contraseña. Firebase Authentication
            requiere un mínimo de 6 caracteres. Es buena práctica validarlo en la GUI también.
        * Si es muy corta, muestra un error y detiene la función.

    6.  `user, error = firebase_service.register_user(email, password)`:
        * **Integración con Firebase Authentication:** Llama a la función `register_user`
            de `firebase_service.py`. Esta función intenta crear la cuenta de usuario
            en Firebase.
        * Devuelve `user` (el objeto de usuario si es exitoso, `None` si falla) y `error` (un mensaje).

    7.  `if user:`:
        * Si `user` tiene un valor (registro exitoso en Firebase Authentication):
            * `current_user = user`: El usuario recién registrado se convierte en el `current_user`.
            * `messagebox.showinfo(...)`: Confirma al usuario que su cuenta ha sido creada y que ha iniciado sesión.
            * **Preparación del perfil inicial (`profile_data`):**
                * Creamos un diccionario llamado `profile_data` con información básica del usuario.
                * `"email": user['email']`: Guardamos su correo electrónico.
                * `"nombre": nombre`: Usamos el nombre que el usuario proporcionó.
                * `"saldo_inicial": 0.0`: Un valor predeterminado para su saldo.
                * `"fecha_registro": time.time()`: Registramos la fecha y hora exactas del registro
                    usando un "timestamp" (número de segundos desde una fecha específica, útil para ordenar).

            * `profile_success, profile_msg = firebase_service.create_user_profile(user['localId'], profile_data)`:
                * **Integración con Firebase Realtime Database:** Una vez que el usuario está
                    registrado en la autenticación, creamos su perfil en la base de datos.
                * `user['localId']` es el **UID** (User ID) único que Firebase asigna a cada usuario.
                    Es la clave principal para almacenar sus datos en la base de datos.
                * Le pasamos el `UID` y los `profile_data` a `create_user_profile`.
                * Esta función devuelve `profile_success` (True/False) y `profile_msg`.

            * `if profile_success:` y `else:` para el perfil:
                * Verificamos si la creación del perfil en la base de datos fue exitosa.
                * `print(...)`: Imprimimos mensajes en la consola para nuestra propia depuración
                    (no los ve el usuario).
                * `messagebox.showwarning(...)`: Si hubo un problema al guardar el perfil
                    (por ejemplo, un problema de reglas en la base de datos), advertimos al usuario
                    pero le informamos que su cuenta *sí* fue creada.

            * `registro_window.destroy()`: Cierra la ventana de registro.
            * `mostrar_home()`: Abre la ventana principal (dashboard) de la aplicación.

    8.  `else:`:
        * Si el registro en Firebase Authentication falló (el `user` es `None`):
            * `messagebox.showerror("Error de Registro", error, parent=registro_window)`:
                Muestra el mensaje de error específico que vino de Firebase (ej. "Este correo ya está registrado").

    """
    global current_user

    nombre = nombre_entry.get()
    email = email_registro_entry.get()
    password = password_registro_entry.get()
    confirm_password = confirm_password_entry.get()

    if not nombre or not email or not password or not confirm_password:
        messagebox.showerror("Error de Registro", "Todos los campos son obligatorios.", parent=registro_window)
        return

    if password != confirm_password:
        messagebox.showerror("Error de Registro", "Las contraseñas no coinciden.", parent=registro_window)
        return

    if len(password) < 6:
        messagebox.showerror("Error de Registro", "La contraseña debe tener al menos 6 caracteres.", parent=registro_window)
        return

    # --- INTEGRACIÓN CON FIREBASE SERVICE ---
    user, error = firebase_service.register_user(email, password)

    if user:
        current_user = user
        messagebox.showinfo("Registro Exitoso", "¡Tu cuenta ha sido creada y has iniciado sesión!", parent=registro_window)

        profile_data = {
            "email": user['email'],
            "nombre": nombre,
            "saldo_inicial": 0.0,
            "fecha_registro": time.time()
        }
        profile_success, profile_msg = firebase_service.create_user_profile(user['localId'], profile_data)
        if profile_success:
            print(f"Perfil de usuario creado en DB: {profile_msg}")
        else:
            print(f"Error al crear perfil en DB: {profile_msg}")
            messagebox.showwarning("Advertencia", "Tu cuenta fue creada, pero hubo un problema al guardar tu perfil inicial. Podrás editarlo más tarde.", parent=registro_window)

        registro_window.destroy()
        mostrar_home()
    else:
        messagebox.showerror("Error de Registro", error, parent=registro_window)


def cerrar_sesion():
    """
    Propósito:
        Esta función se ejecuta cuando el usuario hace clic en el botón "Cerrar Sesión"
        desde la ventana principal (Dashboard). Su objetivo es "desloguear" al usuario
        y llevarlo de vuelta a la pantalla de inicio de sesión.

    Cómo funciona paso a paso:

    1.  `global current_user`:
        * Necesitamos acceder a la variable global `current_user` para poder modificarla.

    2.  `current_user = None`:
        * ¡Esta es la acción clave! Al establecer `current_user` a `None`, estamos
            indicando que no hay ningún usuario actualmente logueado en la aplicación.
            Esto es como "borrar" la información de la sesión actual.

    3.  `home_window.destroy()`:
        * Cierra la ventana actual del Dashboard (`home_window`).

    4.  `mostrar_login_window()`:
        * Llama a la función que se encarga de mostrar la ventana de inicio de sesión,
            permitiendo que otro usuario (o el mismo) pueda loguearse de nuevo.

    5.  `messagebox.showinfo("Sesión Cerrada", "Has cerrado sesión correctamente.")`:
        * Muestra un pequeño mensaje informativo al usuario confirmando que la sesión
            ha sido cerrada con éxito.

    """
    global current_user
    current_user = None
    home_window.destroy()
    mostrar_login_window()
    messagebox.showinfo("Sesión Cerrada", "Has cerrado sesión correctamente.")


def toggle_password_visibility(password_entry_widget, check_button_var):
    """
    Propósito:
        Esta función es un "utilitario" que permite al usuario alternar entre
        mostrar y ocultar la contraseña en los campos de entrada. Se conecta
        directamente a los "Checkbuttons" (las casillas de verificación de
        "Mostrar Contraseña").

    Argumentos (lo que la función necesita para trabajar):

    * `password_entry_widget`: Es el "Entry widget" (el cuadro de texto)
                                donde se escribe la contraseña. Por ejemplo,
                                podría ser `password_entry` o `password_registro_entry`.
                                La función necesita saber qué campo de contraseña
                                debe afectar.
    * `check_button_var`: Es la variable de control de Tkinter (un `tk.BooleanVar()`)
                            que está conectada al Checkbutton. Esta variable almacena
                            si el Checkbutton está marcado (`True`) o desmarcado (`False`).

    Cómo funciona paso a paso:

    1.  `if check_button_var.get():`:
        * Pregunta: "¿Está el Checkbutton marcado (`True`)?"
        * `check_button_var.get()`: Obtiene el valor actual de la variable del Checkbutton.

    2.  `password_entry_widget.config(show="")`:
        * Si el Checkbutton *está* marcado (`True`):
            * `password_entry_widget.config(show="")`: Cambia la configuración del
                cuadro de texto de la contraseña. El atributo `show=""` significa
                "no ocultar nada, mostrar el texto tal cual".

    3.  `else:`:
        * Si el Checkbutton *no está* marcado (`False`):
            * `password_entry_widget.config(show="*")`: Cambia la configuración
                del cuadro de texto de la contraseña a `show="*"`. Esto le dice
                a Tkinter que reemplace cada carácter escrito con un asterisco (`*`),
                ocultando la contraseña.

    """
    if check_button_var.get():
        password_entry_widget.config(show="")
    else:
        password_entry_widget.config(show="*")



# ====================================================================================================
# DOCUMENTACIÓN DETALLADA DE LAS FUNCIONES DE CREACIÓN DE VENTANAS (MAIN.PY)
# ====================================================================================================
# Estas funciones son las encargadas de construir las diferentes pantallas de la interfaz
# gráfica de tu aplicación utilizando Tkinter. Cada una crea una ventana nueva (Toplevel)
# y organiza los "widgets" (botones, campos de texto, etiquetas) dentro de ella.
# ====================================================================================================

def mostrar_home():
    """
    Propósito:
        Crea y muestra la ventana principal de la aplicación, conocida como el Dashboard.
        Esta ventana se muestra después de que el usuario inicia sesión o se registra exitosamente.
        Contiene elementos de bienvenida y botones para navegar a otras secciones
        funcionales de la aplicación (como registrar transacciones, ver perfil, etc.).

    Cómo funciona paso a paso:

    1.  `global home_window`:
        * Declara que `home_window` es una variable global. Esto significa que
            cualquier otra parte de tu código que necesite referirse a esta ventana
            (por ejemplo, para cerrarla) puede hacerlo a través de esta variable.

    2.  `home_window = tk.Toplevel(root)`:
        * Crea una nueva ventana Tkinter.
        * `tk.Toplevel`: Es el tipo de ventana que se usa para crear ventanas secundarias
            o emergentes. Se comporta como una ventana independiente pero pertenece
            a la aplicación principal (`root`).
        * `root`: Es la ventana principal "invisible" de Tkinter que se inicializa al inicio
            de `main.py` y que gestiona toda la aplicación.

    3.  `home_window.title("Klarity - Dashboard")`:
        * Establece el texto que aparecerá en la barra de título de la ventana.

    4.  `home_window.geometry("800x600")`:
        * Define el tamaño inicial de la ventana en píxeles (ancho x alto).

    5.  `home_window.configure(bg=COLOR_FONDO_GRIS)`:
        * Establece el color de fondo de la ventana usando una constante de color
            definida previamente.

    6.  `home_window.resizable(False, False)`:
        * `(False, False)` significa que el usuario no podrá redimensionar la ventana
            ni en ancho ni en alto. La ventana tendrá un tamaño fijo.

    7.  `user_email = current_user['email'] if current_user else "Usuario"`:
        * Esta es una línea de código elegante (un "operador ternario") para obtener
            el email del usuario.
        * `current_user`: Es la variable global que guarda la información del usuario
            que ha iniciado sesión (establecida en `intentar_login` o `intentar_registro`).
        * Si `current_user` existe (es decir, el usuario está logueado), se usa su email.
        * Si `current_user` es `None` (por alguna razón no hay usuario logueado),
            se usa la palabra "Usuario" como valor predeterminado para evitar errores.

    8.  `tk.Label(...)`:
        * Crea una etiqueta (texto) en la ventana.
        * `home_window`: Indica que esta etiqueta pertenece a la ventana `home_window`.
        * `text=f"¡Bienvenido/a a tu Dashboard, {user_email}!"`: El texto a mostrar,
            usando un "f-string" para insertar el `user_email` dinámicamente.
        * `font=FONT_TITLE`, `bg=COLOR_FONDO_GRIS`, `fg=COLOR_PRINCIPAL_AZUL`:
            Establecen la fuente, el color de fondo y el color del texto de la etiqueta,
            usando constantes de estilo.
        * `.pack(pady=20)`: Organiza la etiqueta dentro de la ventana. `pack()` es un
            gestor de geometría simple que apila los widgets. `pady=20` añade un
            espacio de 20 píxeles por encima y por debajo de la etiqueta.

    9.  `button_frame = tk.Frame(home_window, bg=COLOR_FONDO_GRIS)`:
        * Crea un `Frame` (un contenedor rectangular) dentro de la ventana `home_window`.
        * Esto es útil para agrupar y organizar varios widgets juntos, permitiendo un
            control más preciso sobre su disposición que si se usara `pack()` directamente
            en todos ellos.

    10. `tk.Button(...)`:
        * Crea botones interactivos.
        * `button_frame`: Indica que estos botones se colocarán dentro del `button_frame`.
        * `text="Registrar Transacción"`: Texto que se muestra en el botón.
        * `font=FONT_NORMAL`, `bg=COLOR_VERDE_CRECIMIENTO`, `fg=COLOR_BLANCO`:
            Estilos del botón.
        * `command=lambda: messagebox.showinfo(...)`: Define qué función se ejecutará
            cuando se haga clic en el botón.
            * `lambda`: Se usa aquí para crear una pequeña función anónima que permite
                ejecutar un comando más complejo (en este caso, un `messagebox.showinfo`)
                y pasarle argumentos. Sin `lambda`, `command` solo puede aceptar
                funciones sin argumentos directamente.
            * `messagebox.showinfo(...)`: Muestra un mensaje informativo temporal.
            * "Funcionalidad aún no implementada.": Mensaje que indica al usuario
                que esta parte de la aplicación está en desarrollo.
        * `relief="flat"`: Quita el efecto de relieve 3D del botón, dándole un aspecto plano.
        * `padx=15, pady=8`: Añade espacio de relleno horizontal y vertical dentro del botón.
        * `.grid(row=0, column=0, padx=10, pady=10)`:
            * `grid()` es otro gestor de geometría de Tkinter, más potente que `pack()`.
                Organiza los widgets en filas y columnas, como una cuadrícula.
            * `row=0, column=0`: Coloca el botón en la primera fila, primera columna.
            * `padx=10, pady=10`: Añade un espacio de relleno alrededor del botón en la cuadrícula.
        * (Los otros botones de navegación son similares, solo cambian texto, color y posición en la cuadrícula).

    11. `tk.Button(home_window, text="Cerrar Sesión", ..., command=cerrar_sesion).pack(pady=50)`:
        * Crea el botón de "Cerrar Sesión".
        * `command=cerrar_sesion`: Cuando se haga clic, se llamará directamente a la función `cerrar_sesion`.

    12. `home_window.protocol("WM_DELETE_WINDOW", root.destroy)`:
        * Esta línea es muy importante para el comportamiento de tu aplicación.
        * `WM_DELETE_WINDOW`: Es un "evento" de Tkinter que se dispara cuando el usuario
            hace clic en el botón "X" de cerrar la ventana.
        * `root.destroy`: Le dice a Tkinter que, cuando se cierre la `home_window` (la ventana principal
            de la aplicación, una vez logueado el usuario), se debe terminar también
            la ventana raíz (`root`), lo que efectivamente **cierra toda la aplicación de Python**.
            Esto evita que la aplicación siga ejecutándose en segundo plano después de cerrar la ventana GUI.

    """
    global home_window
    home_window = tk.Toplevel(root)
    home_window.title("Klarity - Dashboard")
    home_window.geometry("800x600")
    home_window.configure(bg=COLOR_FONDO_GRIS)
    home_window.resizable(False, False)

    user_email = current_user['email'] if current_user else "Usuario"
    tk.Label(home_window, text=f"¡Bienvenido/a a tu Dashboard, {user_email}!", font=FONT_TITLE, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(pady=20)
    tk.Label(home_window, text="Aquí verás tus gráficos y resúmenes de finanzas.", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=10)

    button_frame = tk.Frame(home_window, bg=COLOR_FONDO_GRIS)
    button_frame.pack(pady=30)

    tk.Button(button_frame, text="Registrar Transacción", font=FONT_NORMAL, bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO, command=lambda: messagebox.showinfo("Info", "Funcionalidad de transacción aún no implementada.", parent=home_window), relief="flat", padx=15, pady=8).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(button_frame, text="Ver Transacciones", font=FONT_NORMAL, bg=COLOR_PRINCIPAL_AZUL, fg=COLOR_BLANCO, command=lambda: messagebox.showinfo("Info", "Funcionalidad de ver transacciones aún no implementada.", parent=home_window), relief="flat", padx=15, pady=8).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(button_frame, text="Ver/Editar Perfil", font=FONT_NORMAL, bg=COLOR_PRINCIPAL_AZUL, fg=COLOR_BLANCO, command=lambda: messagebox.showinfo("Info", "Funcionalidad de perfil aún no implementada.", parent=home_window), relief="flat", padx=15, pady=8).grid(row=1, column=0, padx=10, pady=10)

    tk.Button(home_window, text="Cerrar Sesión", font=FONT_NORMAL, bg=COLOR_ROJO_GASTO, fg=COLOR_BLANCO, command=cerrar_sesion, relief="flat", padx=10, pady=5).pack(pady=50)

    home_window.protocol("WM_DELETE_WINDOW", root.destroy)


def mostrar_registro_window():
    """
    Propósito:
        Crea y muestra la ventana donde los nuevos usuarios pueden registrar una cuenta
        en la aplicación. Incluye campos para nombre, email, contraseña y confirmación
        de contraseña, además de opciones para mostrar/ocultar contraseñas.

    Cómo funciona paso a paso:

    1.  `global registro_window, nombre_entry, ...`:
        * Declara todas las variables de la ventana (`registro_window`) y de los
            campos de entrada (`nombre_entry`, `email_registro_entry`, etc.)
            como globales. Esto permite que otras funciones (como `intentar_registro`)
            puedan acceder a los datos que el usuario ingresa en estos campos.

    2.  `registro_window = tk.Toplevel(root)`:
        * Crea la nueva ventana de registro como una ventana secundaria.

    3.  `registro_window.title("Klarity - Crear Cuenta")`, `geometry`, `configure`, `resizable`:
        * Configuran las propiedades básicas de la ventana, como el título, tamaño,
            color de fondo y si es redimensionable (en este caso, no).

    4.  `tk.Label(registro_window, text="Crear Nueva Cuenta", ...).pack(...)`:
        * Crea el título principal de la ventana de registro.

    5.  `tk.Label(registro_window, text="Nombre Completo:", ...).pack(...)`:
        * Crea una etiqueta para indicar al usuario qué debe ingresar en el siguiente campo.

    6.  `nombre_entry = tk.Entry(registro_window, width=35, ...)`, y otros `tk.Entry`:
        * Crea un campo de texto donde el usuario puede escribir.
        * `width=35`: Establece el ancho del campo en caracteres.
        * `relief="flat"`: Remueve el borde predeterminado para un aspecto más moderno.
        * `highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1`: Añade un
            borde delgado y de un color específico cuando el campo no está enfocado.
        * `show="*"` (para `password_registro_entry` y `confirm_password_entry`):
            Hace que el texto escrito se oculte y se muestre como asteriscos.

    7.  `show_password_registro_var = tk.BooleanVar()`:
        * Crea una "variable de control" especial de Tkinter. Este tipo de variable
            es fundamental para los `Checkbutton`s (casillas de verificación), ya que
            almacena su estado (`True` si está marcada, `False` si no lo está).

    8.  `check_show_password_registro = tk.Checkbutton(...)`:
        * Crea la casilla de verificación "Mostrar Contraseña".
        * `variable=show_password_registro_var`: Conecta esta casilla de verificación
            a la variable de control que creamos en el paso anterior.
        * `command=lambda: toggle_password_visibility(...)`: Cuando se hace clic en la
            casilla, se llama a la función `toggle_password_visibility`. La `lambda`
            se usa aquí para pasarle dos argumentos: el campo de contraseña que debe afectar
            (`password_registro_entry`) y su variable de control (`show_password_registro_var`).
        * `anchor="w", padx=25`: Posiciona la casilla a la izquierda ("w" de "west") con un
            relleno horizontal.
        * `selectcolor=COLOR_FONDO_GRIS`: Configura el color del "cuadrado" de la casilla
            cuando está marcada para que coincida con el fondo.

    9.  `tk.Button(registro_window, text="Registrar Cuenta", ..., command=intentar_registro).pack(...)`:
        * Crea el botón de registro. Cuando se hace clic, llama a la función `intentar_registro`.

    10. `frame_login = tk.Frame(...)`:
        * Crea un `Frame` para agrupar los elementos del enlace "Inicia Sesión",
            permitiendo que se coloquen uno al lado del otro (`side="left"`).

    11. `link_login = tk.Label(..., text="Inicia Sesión", ..., cursor="hand2")`:
        * Crea una etiqueta de texto que actúa como un enlace.
        * `fg=COLOR_LINK_AZUL`: Le da el color de enlace.
        * `cursor="hand2"`: Cambia el puntero del ratón a una mano cuando se pasa
            sobre el texto, sugiriendo que es un elemento clickable.

    12. `link_login.bind("<Button-1>", lambda e: [registro_window.destroy(), mostrar_login_window()])`:
        * `bind("<Button-1>", ...)`: Asocia la acción de hacer clic izquierdo del ratón (`<Button-1>`)
            con la función lambda proporcionada.
        * `lambda e: [registro_window.destroy(), mostrar_login_window()]`: Cierra la ventana
            actual de registro y abre la ventana de login. `e` es un objeto de evento que Tkinter
            pasa a la función, aunque no lo usemos explícitamente aquí.

    13. `registro_window.protocol("WM_DELETE_WINDOW", root.destroy)`:
        * Configura el comportamiento de cierre de la ventana de registro para que,
            si el usuario hace clic en la "X", la aplicación completa se cierre.

    """
    global registro_window, nombre_entry, email_registro_entry, password_registro_entry, confirm_password_entry, show_password_registro_var, show_confirm_password_registro_var
    registro_window = tk.Toplevel(root)
    registro_window.title("Klarity - Crear Cuenta")
    registro_window.geometry("400x550")
    registro_window.configure(bg=COLOR_FONDO_GRIS)
    registro_window.resizable(False, False)

    tk.Label(registro_window, text="Crear Nueva Cuenta", font=FONT_BOLD, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))

    tk.Label(registro_window, text="Nombre Completo:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    nombre_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    nombre_entry.pack()

    tk.Label(registro_window, text="Email:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    email_registro_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    email_registro_entry.pack()

    tk.Label(registro_window, text="Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    password_registro_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    password_registro_entry.pack()

    show_password_registro_var = tk.BooleanVar()
    check_show_password_registro = tk.Checkbutton(registro_window, text="Mostrar Contraseña",
                                                    variable=show_password_registro_var,
                                                    command=lambda: toggle_password_visibility(password_registro_entry, show_password_registro_var),
                                                    bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                    selectcolor=COLOR_FONDO_GRIS)
    check_show_password_registro.pack(anchor="w", padx=25)

    tk.Label(registro_window, text="Confirmar Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    confirm_password_entry = tk.Entry(registro_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    confirm_password_entry.pack()

    show_confirm_password_registro_var = tk.BooleanVar()
    check_show_confirm_password_registro = tk.Checkbutton(registro_window, text="Mostrar Contraseña",
                                                    variable=show_confirm_password_registro_var,
                                                    command=lambda: toggle_password_visibility(confirm_password_entry, show_confirm_password_registro_var),
                                                    bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                    selectcolor=COLOR_FONDO_GRIS)
    check_show_confirm_password_registro.pack(anchor="w", padx=25)

    tk.Button(registro_window, text="Registrar Cuenta", font=FONT_NORMAL, bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO, command=intentar_registro, relief="flat", padx=20, pady=5).pack(pady=20)

    frame_login = tk.Frame(registro_window, bg=COLOR_FONDO_GRIS)
    frame_login.pack(pady=10)
    tk.Label(frame_login, text="¿Ya tienes una cuenta?", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(side="left")
    link_login = tk.Label(frame_login, text="Inicia Sesión", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_LINK_AZUL, cursor="hand2")
    link_login.pack(side="left", padx=5)
    link_login.bind("<Button-1>", lambda e: [registro_window.destroy(), mostrar_login_window()])

    registro_window.protocol("WM_DELETE_WINDOW", root.destroy)


def mostrar_login_window():
    """
    Propósito:
        Crea y muestra la ventana de inicio de sesión de la aplicación.
        Esta es la ventana que generalmente se ve primero si no hay una sesión activa.
        Permite al usuario ingresar su email y contraseña para acceder.

    Cómo funciona paso a paso:

    1.  `global login_window, email_entry, ...`:
        * Declara las variables de la ventana y de los campos de entrada (`email_entry`,
            `password_entry`) como globales, para que puedan ser accedidas por
            otras funciones (como `intentar_login`).

    2.  `login_window = tk.Toplevel(root)`:
        * Crea la nueva ventana de login como una ventana secundaria.

    3.  `login_window.title("Klarity - Iniciar Sesión")`, `geometry`, `configure`, `resizable`:
        * Configuran las propiedades básicas de la ventana, igual que en `mostrar_registro_window`.

    4.  `tk.Label(login_window, text="Iniciar Sesión", ...).pack(...)`:
        * Crea el título principal de la ventana de inicio de sesión.

    5.  `tk.Label(login_window, text="Email:", ...).pack(...)` y `email_entry = tk.Entry(...)`:
        * Crean la etiqueta y el campo de texto para el email.

    6.  `tk.Label(login_window, text="Contraseña:", ...).pack(...)` y `password_entry = tk.Entry(..., show="*")`:
        * Crean la etiqueta y el campo de texto para la contraseña.
        * `show="*"`: Es crucial aquí, ya que oculta los caracteres de la contraseña
            con asteriscos por defecto.

    7.  `show_password_login_var = tk.BooleanVar()` y `check_show_password_login = tk.Checkbutton(...)`:
        * Crean el `Checkbutton` "Mostrar Contraseña" y lo conectan a su variable
            de control (`show_password_login_var`).
        * `command=lambda: toggle_password_visibility(password_entry, show_password_login_var)`:
            Cuando se hace clic en la casilla, llama a `toggle_password_visibility`
            para mostrar u ocultar la contraseña en el campo `password_entry`.

    8.  `tk.Button(login_window, text="Ingresar", ..., command=intentar_login).pack(...)`:
        * Crea el botón de "Ingresar". Cuando se hace clic, llama a la función `intentar_login`.

    9.  `frame_registro = tk.Frame(...)`:
        * Crea un `Frame` para agrupar los elementos del enlace "Regístrate aquí".

    10. `link_registro = tk.Label(..., text="Regístrate aquí", ..., cursor="hand2")`:
        * Crea la etiqueta que actúa como enlace para ir a la ventana de registro.
        * `cursor="hand2"`: Cambia el puntero del ratón a una mano.

    11. `link_registro.bind("<Button-1>", lambda e: [login_window.destroy(), mostrar_registro_window()])`:
        * Asocia el clic izquierdo del ratón en el enlace con la acción de cerrar la ventana
            de login y abrir la ventana de registro.

    12. `login_window.protocol("WM_DELETE_WINDOW", root.destroy)`:
        * Configura el comportamiento de cierre de la ventana de login para que,
            si el usuario hace clic en la "X", la aplicación completa se cierre.

    """
    global login_window, email_entry, password_entry, show_password_login_var
    login_window = tk.Toplevel(root)
    login_window.title("Klarity - Iniciar Sesión")
    login_window.geometry("400x380")
    login_window.configure(bg=COLOR_FONDO_GRIS)
    login_window.resizable(False, False)

    tk.Label(login_window, text="Iniciar Sesión", font=FONT_BOLD, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(pady=(20, 10))
    tk.Label(login_window, text="Email:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    email_entry = tk.Entry(login_window, width=35, font=FONT_NORMAL, relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    email_entry.pack()

    tk.Label(login_window, text="Contraseña:", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(pady=(10, 5))
    password_entry = tk.Entry(login_window, width=35, font=FONT_NORMAL, show="*", relief="flat", highlightbackground=COLOR_TEXTO_GRIS, highlightthickness=1)
    password_entry.pack()

    show_password_login_var = tk.BooleanVar()
    check_show_password_login = tk.Checkbutton(login_window, text="Mostrar Contraseña",
                                                    variable=show_password_login_var,
                                                    command=lambda: toggle_password_visibility(password_entry, show_password_login_var),
                                                    bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS, font=FONT_NORMAL,
                                                    selectcolor=COLOR_FONDO_GRIS)
    check_show_password_login.pack(anchor="w", padx=25)

    tk.Button(login_window, text="Ingresar", font=FONT_NORMAL, bg=COLOR_VERDE_CRECIMIENTO, fg=COLOR_BLANCO, command=intentar_login, relief="flat", padx=20, pady=5).pack(pady=20)

    frame_registro = tk.Frame(login_window, bg=COLOR_FONDO_GRIS)
    frame_registro.pack(pady=10)
    tk.Label(frame_registro, text="¿No tienes una cuenta?", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_TEXTO_GRIS).pack(side="left")
    link_registro = tk.Label(frame_registro, text="Regístrate aquí", font=FONT_NORMAL, bg=COLOR_FONDO_GRIS, fg=COLOR_LINK_AZUL, cursor="hand2")
    link_registro.pack(side="left", padx=5)
    link_registro.bind("<Button-1>", lambda e: [login_window.destroy(), mostrar_registro_window()])

    login_window.protocol("WM_DELETE_WINDOW", root.destroy)


def mostrar_slogan_window():
    """
    Propósito:
        Muestra una ventana temporal con el eslogan de la aplicación.
        Esta ventana aparece después de la pantalla de bienvenida (splash screen)
        y antes de la ventana de login. Su objetivo es dar una pequeña "pausa"
        y mostrar el mensaje clave de la marca.

    Cómo funciona paso a paso:

    1.  `slogan_window = tk.Toplevel(root)`:
        * Crea una nueva ventana secundaria para el eslogan.

    2.  `slogan_window.overrideredirect(True)`:
        * ¡Importante para las ventanas tipo splash/slogan! Esta línea elimina
            completamente los bordes, la barra de título, y los botones de cerrar/minimizar/maximizar.
            La ventana se convierte en un simple "cuadro flotante" sin decoración del sistema.

    3.  `slogan_window.geometry("500x150+400+300")`:
        * Establece el tamaño de la ventana (`500x150` píxeles) y su posición
            en la pantalla.
        * `+400+300`: Significa que la esquina superior izquierda de la ventana
            se colocará a 400 píxeles del borde izquierdo de la pantalla
            y a 300 píxeles del borde superior.

    4.  `slogan_window.configure(bg=COLOR_FONDO_GRIS)`:
        * Establece el color de fondo de la ventana.

    5.  `tk.Label(slogan_window, text=SLOGAN_APP, ...).pack(expand=True)`:
        * Crea una etiqueta para mostrar el texto del eslogan (`SLOGAN_APP` es una constante).
        * `expand=True`: Hace que la etiqueta se expanda para ocupar todo el espacio
            disponible dentro de su contenedor, lo que ayuda a centrar el texto
            tanto horizontal como verticalmente.

    6.  `slogan_window.after(2500, lambda: [slogan_window.destroy(), mostrar_login_window()])`:
        * `after(milisegundos, función)`: Este método programa la ejecución de una
            función después de un cierto retraso.
        * `2500`: Significa 2500 milisegundos, es decir, 2.5 segundos.
        * `lambda: [slogan_window.destroy(), mostrar_login_window()]`: Después de 2.5 segundos,
            se ejecuta esta función anónima, que primero cierra la ventana del eslogan
            (`slogan_window.destroy()`) y luego llama a `mostrar_login_window()`
            para abrir la pantalla de inicio de sesión.

    """
    slogan_window = tk.Toplevel(root)
    slogan_window.overrideredirect(True)
    slogan_window.geometry("500x150+400+300")
    slogan_window.configure(bg=COLOR_FONDO_GRIS)
    tk.Label(slogan_window, text=SLOGAN_APP, font=FONT_SLOGAN, bg=COLOR_FONDO_GRIS, fg=COLOR_PRINCIPAL_AZUL).pack(expand=True)
    slogan_window.after(2500, lambda: [slogan_window.destroy(), mostrar_login_window()])


def iniciar_splash_screen():
    """
    Propósito:
        Crea y gestiona la pantalla de carga inicial (Splash Screen) de la aplicación.
        Esta es la primera ventana que aparece cuando la aplicación se inicia.
        Generalmente muestra el logo, un mensaje de carga y una barra de progreso.

    Cómo funciona paso a paso:

    1.  `splash_window = tk.Toplevel(root)`:
        * Crea la ventana del splash screen.

    2.  `splash_window.overrideredirect(True)`:
        * Al igual que la ventana del eslogan, elimina los bordes y la barra de título
            para que parezca una pantalla de carga real.

    3.  `splash_window.geometry("400x400+450+150")`:
        * Define el tamaño y la posición inicial de la ventana del splash.

    4.  `splash_window.configure(bg=COLOR_PRINCIPAL_AZUL)`:
        * Establece el color de fondo del splash.

    5.  `frame = tk.Frame(splash_window, bg=COLOR_PRINCIPAL_AZUL)`:
        * Crea un `Frame` interno para contener y centrar los elementos del splash
            (logo, texto, barra de progreso).

    6.  **Carga del Logo (`try-except`):**
        * `try:`: Intenta cargar el archivo de imagen `assets/klarity_logo.png`.
            * `Image.open(...)`: Abre la imagen usando la librería Pillow.
            * `.resize((150, 150), Image.Resampling.LANCZOS)`: Redimensiona la imagen
                a 150x150 píxeles. `Image.Resampling.LANCZOS` es un algoritmo de
                redimensionamiento de alta calidad.
            * `ImageTk.PhotoImage(logo_image)`: Convierte la imagen de Pillow a un
                formato que Tkinter pueda mostrar.
            * `label_logo = tk.Label(frame, image=logo_photo, ...).pack(...)`:
                Crea una etiqueta para mostrar el logo.
            * `label_logo.image = logo_photo`: **Muy importante:** Esta línea evita que
                la imagen sea "recogida por el recolector de basura" de Python y desaparezca.
                Mantener una referencia a la `PhotoImage` en el propio widget `Label`
                asegura que la imagen se mantenga en memoria.
        * `except FileNotFoundError:`: Si el archivo del logo no se encuentra,
            este bloque se ejecuta.
            * `tk.Label(frame, text="K", ...).pack(...)`: En lugar del logo, muestra
                una gran letra "K" como alternativa visual, avisando al usuario de un posible
                problema con el archivo del logo.
        * `except Exception as e:`: Captura cualquier otro tipo de error al cargar el logo.

    7.  `tk.Label(frame, text="Klarity", ...).pack()` y `tk.Label(frame, text="Cargando...", ...).pack()`:
        * Crean las etiquetas de texto para el nombre de la aplicación y el mensaje de "Cargando...".

    8.  **Barra de Progreso (`ttk.Progressbar`):**
        * `style = ttk.Style()`: Crea un objeto `Style` para personalizar la apariencia
            de los widgets `ttk` (los widgets "temáticos" de Tkinter que se ven más modernos).
        * `style.theme_use('clam')`: Establece el tema visual que se usará. 'clam' es un tema
            moderno y plano.
        * `style.configure("green.Horizontal.TProgressbar", ...)`: Define un nuevo estilo
            llamado "green.Horizontal.TProgressbar". Configura el color de la barra (`background`)
            y el color del "riel" donde se mueve la barra (`troughcolor`).
        * `progress_bar = ttk.Progressbar(...)`: Crea la barra de progreso.
            * `style="green.Horizontal.TProgressbar"`: Aplica el estilo personalizado.
            * `orient="horizontal"`: La barra se moverá de izquierda a derecha.
            * `length=300`: El ancho de la barra en píxeles.
            * `mode='determinate'`: Indica que el progreso es conocido y se mostrará
                como un porcentaje o un valor fijo (en este caso, 0 a 100).

    9.  `def actualizar_progreso(step=0):`:
        * Define una función interna (dentro de `iniciar_splash_screen`) para animar
            la barra de progreso.
        * `step=0`: `step` es el valor actual del progreso, inicializado en 0.

    10. `if step <= 100:`:
        * Mientras el progreso no haya alcanzado el 100%.
        * `progress_bar['value'] = step`: Actualiza el valor de la barra de progreso.
        * `splash_window.after(30, lambda: actualizar_progreso(step + 2))`:
            * Programa la próxima llamada a `actualizar_progreso`.
            * `30`: El retraso es de 30 milisegundos (la barra se actualizará cada 30 ms).
            * `lambda: actualizar_progreso(step + 2)`: Llama a `actualizar_progreso`
                de nuevo, incrementando el `step` en 2. Esto crea el efecto de animación.

    11. `else:` (cuando `step` es mayor que 100):
        * Cuando la barra de progreso ha terminado su animación.
        * `splash_window.destroy()`: Cierra la ventana del splash screen.
        * `mostrar_slogan_window()`: Llama a la función para mostrar la ventana del eslogan,
            iniciando la siguiente fase de la aplicación.

    12. `actualizar_progreso()`:
        * Llama a la función `actualizar_progreso` por primera vez para iniciar
            la animación del splash screen.

    """
    splash_window = tk.Toplevel(root)
    splash_window.overrideredirect(True)
    splash_window.geometry("400x400+450+150")
    splash_window.configure(bg=COLOR_PRINCIPAL_AZUL)

    frame = tk.Frame(splash_window, bg=COLOR_PRINCIPAL_AZUL)
    frame.pack(expand=True)

    try:
        logo_image = Image.open("assets/klarity_logo.png").resize((150, 150), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)
        label_logo = tk.Label(frame, image=logo_photo, bg=COLOR_PRINCIPAL_AZUL)
        label_logo.pack(pady=10)
        label_logo.image = logo_photo
    except FileNotFoundError:
        tk.Label(frame, text="K", font=("Lato", 80, "bold"), fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack(pady=10)
    except Exception as e:
        print(f"Error al cargar el logo para el splash screen: {e}")
        tk.Label(frame, text="K", font=("Lato", 80, "bold"), fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack(pady=10)

    tk.Label(frame, text="Klarity", font=FONT_TITLE, fg=COLOR_BLANCO, bg=COLOR_PRINCIPAL_AZUL).pack()
    tk.Label(frame, text="Cargando...", font=FONT_NORMAL, fg=COLOR_FONDO_GRIS, bg=COLOR_PRINCIPAL_AZUL).pack(pady=10)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("green.Horizontal.TProgressbar", foreground=COLOR_VERDE_CRECIMIENTO, background=COLOR_VERDE_CRECIMIENTO, troughcolor=COLOR_TEXTO_GRIS)

    progress_bar = ttk.Progressbar(frame, style="green.Horizontal.TProgressbar", orient="horizontal", length=300, mode='determinate')
    progress_bar.pack(pady=20)

    def actualizar_progreso(step=0):
        if step <= 100:
            progress_bar['value'] = step
            splash_window.after(30, lambda: actualizar_progreso(step + 2))
        else:
            splash_window.destroy()
            mostrar_slogan_window()

    actualizar_progreso()

    