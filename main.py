import flet as ft
import json
import math
import re
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

ARCHIVO_HISTORIAL = "historial_gastos.json"

CATEGORIAS = [
    "Vivienda",
    "Alimentación",
    "Transporte",
    "Servicios",
    "Educación",
    "Salud",
    "Entretenimiento",
    "Compras",
    "Suscripciones",
    "Otros"
]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# Un color y un ícono por categoría (se usan en campos y gráficos)
COLORES_CATEGORIAS = {
    "Vivienda": ft.Colors.INDIGO_500,
    "Alimentación": ft.Colors.ORANGE_500,
    "Transporte": ft.Colors.BLUE_500,
    "Servicios": ft.Colors.AMBER_600,
    "Educación": ft.Colors.PURPLE_500,
    "Salud": ft.Colors.RED_500,
    "Entretenimiento": ft.Colors.PINK_400,
    "Compras": ft.Colors.TEAL_500,
    "Suscripciones": ft.Colors.CYAN_600,
    "Otros": ft.Colors.BLUE_GREY_500
}

ICONOS_CATEGORIAS = {
    "Vivienda": ft.Icons.HOME,
    "Alimentación": ft.Icons.RESTAURANT,
    "Transporte": ft.Icons.DIRECTIONS_CAR,
    "Servicios": ft.Icons.BOLT,
    "Educación": ft.Icons.SCHOOL,
    "Salud": ft.Icons.FAVORITE,
    "Entretenimiento": ft.Icons.MOVIE,
    "Compras": ft.Icons.SHOPPING_BAG,
    "Suscripciones": ft.Icons.SUBSCRIPTIONS,
    "Otros": ft.Icons.MORE_HORIZ
}

COLOR_POSITIVO = ft.Colors.GREEN_600
COLOR_NEGATIVO = ft.Colors.RED_500
COLOR_AVISO = ft.Colors.AMBER_700
COLOR_INFO = ft.Colors.BLUE_500

MENSAJE_ERROR_NUMERO = "Solo introduzca números"


# ============================================================
# HISTORIAL
# ============================================================

def cargar_historial():
    try:
        with open(
            ARCHIVO_HISTORIAL,
            "r",
            encoding="utf-8"
        ) as archivo:
            return json.load(archivo)

    except FileNotFoundError:
        return {}

    except Exception:
        return {}


def guardar_historial(historial):
    with open(
        ARCHIVO_HISTORIAL,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            historial,
            archivo,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# COMPONENTES VISUALES REUTILIZABLES
# (usan colores del tema, así se adaptan solos a claro/oscuro)
# ============================================================

def borde(color=None, ancho=1):

    color = color or ft.Colors.OUTLINE_VARIANT

    return ft.Border(
        top=ft.BorderSide(ancho, color),
        right=ft.BorderSide(ancho, color),
        bottom=ft.BorderSide(ancho, color),
        left=ft.BorderSide(ancho, color)
    )


def tarjeta(contenido, padding=20):

    return ft.Container(
        content=contenido,
        padding=padding,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        border=borde(),
        shadow=[
            ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.with_opacity(
                    0.08,
                    ft.Colors.BLACK
                ),
                offset=ft.Offset(0, 4)
            )
        ]
    )


def titulo_seccion(texto, icono):

    return ft.Row(
        [
            ft.Icon(icono, color=ft.Colors.PRIMARY),
            ft.Text(
                texto,
                size=18,
                weight=ft.FontWeight.BOLD
            )
        ],
        spacing=8
    )


def subtitulo(texto):

    return ft.Text(
        texto,
        size=15,
        weight=ft.FontWeight.W_600,
        color=ft.Colors.ON_SURFACE_VARIANT
    )


def fila_texto(texto, icono, color):

    return ft.Row(
        [
            ft.Icon(icono, color=color, size=20),
            ft.Text(texto, expand=True)
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=10
    )


def tarjeta_kpi(titulo, valor, icono, color):

    return ft.Container(
        width=230,
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.12, color),
        content=ft.Row(
            [
                ft.Container(
                    width=44,
                    height=44,
                    border_radius=22,
                    bgcolor=color,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        icono,
                        color=ft.Colors.WHITE
                    )
                ),
                ft.Column(
                    [
                        ft.Text(
                            titulo,
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            valor,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=color
                        )
                    ],
                    spacing=2,
                    expand=True
                )
            ],
            spacing=12
        )
    )


def barra(porcentaje, color, alto=10):

    # Barra de progreso hecha con contenedores proporcionales
    porcentaje = max(0, min(100, porcentaje))

    parte_llena = int(round(porcentaje * 10))
    parte_vacia = 1000 - parte_llena

    partes = []

    if parte_llena > 0:
        partes.append(
            ft.Container(
                expand=parte_llena,
                height=alto,
                bgcolor=color,
                border_radius=alto / 2
            )
        )

    if parte_vacia > 0:
        partes.append(
            ft.Container(
                expand=parte_vacia,
                height=alto
            )
        )

    return ft.Container(
        height=alto,
        border_radius=alto / 2,
        bgcolor=ft.Colors.with_opacity(
            0.15,
            ft.Colors.ON_SURFACE
        ),
        content=ft.Row(partes, spacing=0)
    )


def color_por_nivel(porcentaje):

    if porcentaje >= 80:
        return COLOR_NEGATIVO

    if porcentaje >= 60:
        return COLOR_AVISO

    return COLOR_POSITIVO


def valor_a_texto(valor):

    # Convierte un número guardado al formato que entiende
    # el campo (punto = miles, coma = decimales)
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return ""

    if valor == int(valor):
        return str(int(valor))

    return f"{valor:.2f}".replace(".", ",")


# ============================================================
# APLICACIÓN
# ============================================================

def main(page: ft.Page):

    page.title = "Asesor de Gastos Personales"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Tema claro / oscuro
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    historial = cargar_historial()

    fecha_actual = datetime.now()

    mes_actual = MESES[fecha_actual.month - 1]
    anio_actual = str(fecha_actual.year)

    # ========================================================
    # CAMPOS
    # ========================================================

    def crear_campo(label, hint, icono):

        # Mensaje que aparece debajo del campo cuando hay letras
        aviso = ft.Row(
            [
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    size=14,
                    color=ft.Colors.RED
                ),
                ft.Text(
                    MENSAJE_ERROR_NUMERO,
                    size=12,
                    color=ft.Colors.RED
                )
            ],
            spacing=4,
            visible=False
        )

        campo = ft.TextField(
            label=label,
            hint_text=hint,
            prefix_icon=icono,
            width=300,
            border_radius=12,
            filled=True
        )

        # Guardamos el aviso dentro del campo para encontrarlo
        # fácilmente desde el evento on_change
        campo.data = aviso

        return campo

    def con_aviso(campo):

        return ft.Column(
            [campo, campo.data],
            spacing=2,
            width=300
        )

    ingreso = crear_campo(
        "Ingreso mensual",
        "Ejemplo: 500000",
        ft.Icons.PAYMENTS
    )

    campos_gastos = {}

    for categoria in CATEGORIAS:
        campos_gastos[categoria] = crear_campo(
            categoria,
            "0",
            ICONOS_CATEGORIAS[categoria]
        )

    selector_mes = ft.Dropdown(
        label="Mes",
        width=200,
        value=mes_actual,
        border_radius=12,
        filled=True
    )

    selector_mes.options = [
        ft.DropdownOption(
            key=mes,
            text=mes
        )
        for mes in MESES
    ]

    selector_anio = ft.Dropdown(
        label="Año",
        width=150,
        value=anio_actual,
        border_radius=12,
        filled=True
    )

    selector_anio.options = [
        ft.DropdownOption(
            key=str(anio),
            text=str(anio)
        )
        for anio in range(2020, 2031)
    ]

    contenido = ft.Column(
        spacing=16
    )

    resultado = ft.Column(
        spacing=16
    )

    mensaje = ft.Text("", weight=ft.FontWeight.W_600)


    def mostrar_mensaje(texto, tipo="info"):

        mensaje.value = texto

        if tipo == "ok":
            mensaje.color = COLOR_POSITIVO
        elif tipo == "error":
            mensaje.color = COLOR_NEGATIVO
        else:
            mensaje.color = None


    # ========================================================
    # CONVERTIR NÚMEROS
    # ========================================================

    def convertir_numero(campo):

        try:

            valor = campo.value

            if valor is None:
                return 0

            valor = valor.strip()

            if valor == "":
                return 0

            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

            return float(valor)

        except Exception:

            return 0


    # ========================================================
    # VALIDAR CAMPOS (rojo + mensaje mientras se escribe)
    # ========================================================

    def es_numero_valido(texto):

        # Vacío se considera válido (se interpreta como 0)
        if texto is None or texto.strip() == "":
            return True

        valor = texto.strip()

        # Solo se aceptan dígitos, puntos y comas
        # (esto bloquea letras, símbolos, "e", "nan", "inf", etc.)
        if not re.fullmatch(r"[0-9.,]+", valor):
            return False

        try:

            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

            numero = float(valor)

            return math.isfinite(numero)

        except ValueError:

            return False


    def aplicar_estado(campo, valido):

        if valido:
            campo.border_color = None
            campo.focused_border_color = None
            campo.color = None
        else:
            campo.border_color = ft.Colors.RED
            campo.focused_border_color = ft.Colors.RED
            campo.color = ft.Colors.RED

        campo.data.visible = not valido


    def validar_campo(e):

        # Se ejecuta en cada tecla, no al final
        campo = e.control

        aplicar_estado(
            campo,
            es_numero_valido(campo.value)
        )

        page.update()


    def validar_todos():

        # Necesario cuando el valor se cambia por código
        # (cargar período, limpiar), porque ahí no se dispara on_change
        campos = [ingreso] + list(campos_gastos.values())

        hay_errores = False

        for campo in campos:

            valido = es_numero_valido(campo.value)

            aplicar_estado(campo, valido)

            if not valido:
                hay_errores = True

        return hay_errores


    ingreso.on_change = validar_campo

    for campo in campos_gastos.values():
        campo.on_change = validar_campo


    # ========================================================
    # OBTENER DATOS
    # ========================================================

    def obtener_datos():

        ingreso_total = convertir_numero(ingreso)

        gastos = {}

        for categoria in CATEGORIAS:

            gastos[categoria] = convertir_numero(
                campos_gastos[categoria]
            )

        total_gastos = sum(gastos.values())

        balance = ingreso_total - total_gastos

        if ingreso_total > 0:
            porcentaje_utilizado = (
                total_gastos / ingreso_total
            ) * 100
        else:
            porcentaje_utilizado = 0

        return (
            ingreso_total,
            gastos,
            total_gastos,
            balance,
            porcentaje_utilizado
        )


    # ========================================================
    # GRÁFICOS
    # ========================================================

    def construir_graficos(gastos, total_gastos):

        datos = sorted(
            [
                (categoria, monto)
                for categoria, monto in gastos.items()
                if monto > 0
            ],
            key=lambda par: par[1],
            reverse=True
        )

        # ---------- Gráfico de anillo ----------

        secciones = []

        for categoria, monto in datos:

            porcentaje = monto / total_gastos * 100

            secciones.append(
                ft.PieChartSection(
                    value=monto,
                    title=(
                        f"{porcentaje:.0f}%"
                        if porcentaje >= 6
                        else ""
                    ),
                    color=COLORES_CATEGORIAS[categoria],
                    radius=50,
                    title_style=ft.TextStyle(
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                )
            )

        anillo = ft.Container(
            width=240,
            height=240,
            content=ft.Stack(
                [
                    ft.PieChart(
                        sections=secciones,
                        sections_space=2,
                        center_space_radius=70,
                        width=240,
                        height=240
                    ),
                    ft.Container(
                        width=240,
                        height=240,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Total gastos",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                                ft.Text(
                                    f"${total_gastos:,.0f}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                )
                            ],
                            spacing=0,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=(
                                ft.CrossAxisAlignment.CENTER
                            )
                        )
                    )
                ],
                width=240,
                height=240
            )
        )

        # ---------- Leyenda ----------

        leyenda = ft.Column(spacing=8)

        for categoria, monto in datos:

            porcentaje = monto / total_gastos * 100

            leyenda.controls.append(
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    width=12,
                                    height=12,
                                    border_radius=6,
                                    bgcolor=COLORES_CATEGORIAS[categoria]
                                ),
                                ft.Text(categoria)
                            ],
                            spacing=8
                        ),
                        ft.Text(
                            f"{porcentaje:.1f}%",
                            weight=ft.FontWeight.BOLD
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=240
                )
            )

        # ---------- Barras por categoría ----------

        barras = ft.Column(spacing=12)

        monto_maximo = datos[0][1]

        for categoria, monto in datos:

            porcentaje = monto / total_gastos * 100

            barras.controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ICONOS_CATEGORIAS[categoria],
                                            size=18,
                                            color=COLORES_CATEGORIAS[
                                                categoria
                                            ]
                                        ),
                                        ft.Text(categoria)
                                    ],
                                    spacing=8
                                ),
                                ft.Text(
                                    f"${monto:,.2f}  ·  "
                                    f"{porcentaje:.1f}%",
                                    size=13,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            wrap=True
                        ),
                        barra(
                            monto / monto_maximo * 100,
                            COLORES_CATEGORIAS[categoria]
                        )
                    ],
                    spacing=4
                )
            )

        return tarjeta(
            ft.Column(
                [
                    titulo_seccion(
                        "Gráficos de gastos",
                        ft.Icons.PIE_CHART
                    ),
                    subtitulo("Distribución del total de gastos"),
                    ft.Row(
                        [anillo, leyenda],
                        wrap=True,
                        spacing=30,
                        run_spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(height=20),
                    subtitulo("Comparación entre categorías"),
                    barras
                ],
                spacing=12
            )
        )


    # ========================================================
    # ANÁLISIS COMPLETO
    # ========================================================

    def analizar(e=None):

        if validar_todos():

            mostrar_mensaje(
                "⚠ Hay campos en rojo: ingresá solo números.",
                "error"
            )

            page.update()
            return

        mostrar_mensaje("")

        (
            ingreso_total,
            gastos,
            total_gastos,
            balance,
            porcentaje_utilizado
        ) = obtener_datos()

        resultado.controls.clear()

        resultado.controls.append(
            ft.Text(
                "Resultado del análisis",
                size=24,
                weight=ft.FontWeight.BOLD
            )
        )


        # ====================================================
        # RESUMEN (tarjetas)
        # ====================================================

        color_balance = (
            COLOR_POSITIVO if balance >= 0 else COLOR_NEGATIVO
        )

        resultado.controls.append(
            ft.Row(
                [
                    tarjeta_kpi(
                        "Ingresos mensuales",
                        f"${ingreso_total:,.2f}",
                        ft.Icons.ARROW_CIRCLE_UP,
                        COLOR_POSITIVO
                    ),
                    tarjeta_kpi(
                        "Total de gastos",
                        f"${total_gastos:,.2f}",
                        ft.Icons.ARROW_CIRCLE_DOWN,
                        COLOR_NEGATIVO
                    ),
                    tarjeta_kpi(
                        "Balance / diferencia",
                        f"${balance:,.2f}",
                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                        color_balance
                    )
                ],
                wrap=True,
                spacing=12,
                run_spacing=12
            )
        )

        color_porcentaje = color_por_nivel(porcentaje_utilizado)

        resultado.controls.append(
            tarjeta(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    "Porcentaje utilizado",
                                    weight=ft.FontWeight.W_600
                                ),
                                ft.Text(
                                    f"{porcentaje_utilizado:.2f}%",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=color_porcentaje
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        barra(
                            porcentaje_utilizado,
                            color_porcentaje,
                            alto=12
                        )
                    ],
                    spacing=8
                ),
                padding=16
            )
        )


        # ====================================================
        # GRÁFICOS
        # ====================================================

        if total_gastos > 0:

            resultado.controls.append(
                construir_graficos(gastos, total_gastos)
            )

        else:

            resultado.controls.append(
                tarjeta(
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PIE_CHART_OUTLINE,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            ft.Text(
                                "Cargá al menos un gasto para "
                                "ver los gráficos.",
                                expand=True
                            )
                        ],
                        spacing=10
                    ),
                    padding=16
                )
            )


        # ====================================================
        # CONCLUSIONES
        # ====================================================

        conclusiones = ft.Column(
            [
                titulo_seccion(
                    "Conclusiones",
                    ft.Icons.INSIGHTS
                )
            ],
            spacing=10
        )

        if ingreso_total <= 0:

            conclusiones.controls.append(
                fila_texto(
                    "No se puede realizar un análisis "
                    "completo porque no se ingresó un ingreso mensual.",
                    ft.Icons.INFO_OUTLINE,
                    COLOR_INFO
                )
            )

        else:

            if balance < 0:

                conclusiones.controls.append(
                    fila_texto(
                        f"Existe un déficit mensual de "
                        f"${abs(balance):,.2f}.",
                        ft.Icons.TRENDING_DOWN,
                        COLOR_NEGATIVO
                    )
                )

            elif balance == 0:

                conclusiones.controls.append(
                    fila_texto(
                        "Tus ingresos y gastos son iguales. "
                        "No queda dinero disponible al finalizar el mes.",
                        ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        COLOR_AVISO
                    )
                )

            else:

                conclusiones.controls.append(
                    fila_texto(
                        f"Existe un saldo disponible de "
                        f"${balance:,.2f} después de cubrir los gastos.",
                        ft.Icons.TRENDING_UP,
                        COLOR_POSITIVO
                    )
                )


            if porcentaje_utilizado > 100:

                conclusiones.controls.append(
                    fila_texto(
                        "Los gastos superan el 100% de los ingresos.",
                        ft.Icons.INFO_OUTLINE,
                        COLOR_NEGATIVO
                    )
                )

            elif porcentaje_utilizado >= 80:

                conclusiones.controls.append(
                    fila_texto(
                        "Se utiliza una parte muy elevada "
                        "de los ingresos para cubrir los gastos.",
                        ft.Icons.INFO_OUTLINE,
                        COLOR_NEGATIVO
                    )
                )

            elif porcentaje_utilizado >= 60:

                conclusiones.controls.append(
                    fila_texto(
                        "Una parte importante de los ingresos "
                        "está destinada a los gastos.",
                        ft.Icons.INFO_OUTLINE,
                        COLOR_AVISO
                    )
                )

            elif porcentaje_utilizado >= 40:

                conclusiones.controls.append(
                    fila_texto(
                        "El nivel general de gastos es moderado.",
                        ft.Icons.INFO_OUTLINE,
                        COLOR_INFO
                    )
                )

            else:

                conclusiones.controls.append(
                    fila_texto(
                        "El porcentaje de ingresos utilizado "
                        "es relativamente bajo.",
                        ft.Icons.INFO_OUTLINE,
                        COLOR_POSITIVO
                    )
                )


            categorias_con_gasto = []

            for categoria in CATEGORIAS:

                monto = gastos[categoria]

                if monto > 0:

                    porcentaje_categoria = (
                        monto / ingreso_total
                    ) * 100

                    categorias_con_gasto.append(
                        (
                            categoria,
                            monto,
                            porcentaje_categoria
                        )
                    )

            if categorias_con_gasto:

                conclusiones.controls.append(
                    ft.Divider(height=20)
                )

                conclusiones.controls.append(
                    subtitulo("Análisis por categoría")
                )

                for (
                    categoria,
                    monto,
                    porcentaje_categoria
                ) in categorias_con_gasto:

                    if porcentaje_categoria >= 40:

                        conclusiones.controls.append(
                            fila_texto(
                                f"{categoria}: gasto elevado "
                                f"de {porcentaje_categoria:.2f}% "
                                f"de los ingresos.",
                                ICONOS_CATEGORIAS[categoria],
                                COLOR_NEGATIVO
                            )
                        )

                    elif porcentaje_categoria >= 10:

                        conclusiones.controls.append(
                            fila_texto(
                                f"{categoria}: representa "
                                f"{porcentaje_categoria:.2f}% "
                                f"de los ingresos.",
                                ICONOS_CATEGORIAS[categoria],
                                COLORES_CATEGORIAS[categoria]
                            )
                        )


            if total_gastos > 0:

                categoria_mayor = max(
                    gastos,
                    key=gastos.get
                )

                monto_mayor = gastos[categoria_mayor]

                porcentaje_mayor = (
                    monto_mayor / ingreso_total
                ) * 100

                conclusiones.controls.append(
                    ft.Divider(height=20)
                )

                conclusiones.controls.append(
                    subtitulo("Mayor gasto")
                )

                conclusiones.controls.append(
                    fila_texto(
                        f"{categoria_mayor}: "
                        f"${monto_mayor:,.2f}",
                        ICONOS_CATEGORIAS[categoria_mayor],
                        COLORES_CATEGORIAS[categoria_mayor]
                    )
                )

                conclusiones.controls.append(
                    fila_texto(
                        f"Representa el "
                        f"{porcentaje_mayor:.2f}% "
                        f"de tus ingresos.",
                        ft.Icons.DONUT_SMALL,
                        COLORES_CATEGORIAS[categoria_mayor]
                    )
                )

        resultado.controls.append(tarjeta(conclusiones))


        # ====================================================
        # ALERTAS
        # ====================================================

        alertas = ft.Column(
            [
                titulo_seccion(
                    "Alertas",
                    ft.Icons.NOTIFICATIONS_ACTIVE
                )
            ],
            spacing=10
        )

        hay_alertas = False

        if ingreso_total <= 0:

            alertas.controls.append(
                fila_texto(
                    "No se puede analizar la situación "
                    "sin ingresar un ingreso mensual.",
                    ft.Icons.WARNING_AMBER_ROUNDED,
                    COLOR_AVISO
                )
            )

            hay_alertas = True

        else:

            if total_gastos > ingreso_total:

                alertas.controls.append(
                    fila_texto(
                        "Los gastos superan los ingresos.",
                        ft.Icons.WARNING_AMBER_ROUNDED,
                        COLOR_NEGATIVO
                    )
                )

                hay_alertas = True

            if porcentaje_utilizado >= 80:

                alertas.controls.append(
                    fila_texto(
                        "El porcentaje de ingresos utilizado "
                        "es elevado.",
                        ft.Icons.WARNING_AMBER_ROUNDED,
                        COLOR_AVISO
                    )
                )

                hay_alertas = True

            for categoria in CATEGORIAS:

                monto = gastos[categoria]

                if monto <= 0:
                    continue

                porcentaje_categoria = (
                    monto / ingreso_total
                ) * 100

                if porcentaje_categoria >= 40:

                    alertas.controls.append(
                        fila_texto(
                            f"El gasto en {categoria} "
                            f"es elevado: "
                            f"{porcentaje_categoria:.2f}% "
                            f"de los ingresos.",
                            ft.Icons.WARNING_AMBER_ROUNDED,
                            COLOR_NEGATIVO
                        )
                    )

                    hay_alertas = True


        if not hay_alertas:

            alertas.controls.append(
                fila_texto(
                    "No se detectaron alertas importantes "
                    "en tus gastos.",
                    ft.Icons.CHECK_CIRCLE_OUTLINE,
                    COLOR_POSITIVO
                )
            )

        resultado.controls.append(tarjeta(alertas))


        # ====================================================
        # RECOMENDACIONES
        # ====================================================

        recomendaciones = []

        if ingreso_total <= 0:

            recomendaciones.append(
                "Ingresá un ingreso mensual para obtener "
                "recomendaciones personalizadas."
            )

        else:

            if total_gastos > ingreso_total:

                recomendaciones.append(
                    "Reducir los gastos para evitar un déficit mensual."
                )

            if porcentaje_utilizado >= 80:

                recomendaciones.append(
                    "Revisar especialmente los gastos que "
                    "puedan reducirse o eliminarse."
                )

            if porcentaje_utilizado < 50:

                recomendaciones.append(
                    "Podés aprovechar parte del saldo disponible "
                    "para ahorro o para objetivos futuros."
                )

            for categoria in CATEGORIAS:

                monto = gastos[categoria]

                if monto <= 0:
                    continue

                porcentaje_categoria = (
                    monto / ingreso_total
                ) * 100

                if porcentaje_categoria >= 40:

                    recomendaciones.append(
                        f"Revisar el gasto de {categoria}, "
                        f"ya que representa "
                        f"{porcentaje_categoria:.2f}% "
                        f"de tus ingresos."
                    )

                elif (
                    categoria in [
                        "Entretenimiento",
                        "Compras",
                        "Suscripciones"
                    ]
                    and porcentaje_categoria >= 15
                ):

                    recomendaciones.append(
                        f"Considerar reducir algunos gastos "
                        f"de {categoria}."
                    )


        if not recomendaciones:

            recomendaciones.append(
                "Mantener el control mensual de los gastos "
                "y continuar registrando cada categoría."
            )


        columna_recomendaciones = ft.Column(
            [
                titulo_seccion(
                    "Recomendaciones",
                    ft.Icons.LIGHTBULB_OUTLINE
                )
            ],
            spacing=10
        )

        for recomendacion in recomendaciones:

            columna_recomendaciones.controls.append(
                fila_texto(
                    recomendacion,
                    ft.Icons.LIGHTBULB_OUTLINE,
                    COLOR_AVISO
                )
            )

        resultado.controls.append(
            tarjeta(columna_recomendaciones)
        )


        page.update()


    # ========================================================
    # GUARDAR PERÍODO
    # ========================================================

    def guardar_periodo(e=None):

        mes = selector_mes.value
        anio = selector_anio.value

        if not mes or not anio:

            mostrar_mensaje(
                "Seleccioná un mes y un año.",
                "error"
            )

            page.update()
            return


        if validar_todos():

            mostrar_mensaje(
                "⚠ No se guardó: hay campos en rojo, "
                "ingresá solo números.",
                "error"
            )

            page.update()
            return


        (
            ingreso_total,
            gastos,
            total_gastos,
            balance,
            porcentaje_utilizado
        ) = obtener_datos()


        if anio not in historial:

            historial[anio] = {}


        historial[anio][mes] = {

            "ingreso": ingreso_total,

            "gastos": gastos,

            "total_gastos": total_gastos,

            "balance": balance,

            "saldo": balance,

            "porcentaje_utilizado":
                porcentaje_utilizado,

            "fecha_guardado":
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
        }


        guardar_historial(historial)


        mostrar_mensaje(
            f"✓ Período guardado: "
            f"{mes} de {anio}",
            "ok"
        )

        page.update()


    # ========================================================
    # LIMPIAR
    # ========================================================

    def limpiar(e=None):

        ingreso.value = ""

        for categoria in CATEGORIAS:

            campos_gastos[categoria].value = ""


        validar_todos()

        resultado.controls.clear()

        mostrar_mensaje("")

        page.update()


    # ========================================================
    # CARGAR UN PERÍODO DEL HISTORIAL
    # ========================================================

    def cargar_periodo(anio, mes):

        datos = historial[anio][mes]

        selector_anio.value = anio
        selector_mes.value = mes

        ingreso.value = valor_a_texto(
            datos.get("ingreso", 0)
        )

        gastos_guardados = datos.get(
            "gastos",
            {}
        )


        for categoria in CATEGORIAS:

            campos_gastos[categoria].value = valor_a_texto(
                gastos_guardados.get(
                    categoria,
                    0
                )
            )


        mostrar_asesor()

        analizar()

        mostrar_mensaje(
            f"✓ Cargado: {mes} de {anio}",
            "ok"
        )

        page.update()


    # ========================================================
    # PANTALLA DEL ASESOR
    # ========================================================

    def mostrar_asesor(e=None):

        actualizar_nav("asesor")

        contenido.controls.clear()

        contenido.controls.extend([

            ft.Text(
                "Ingresá tus datos mensuales "
                "para analizar tus gastos.",
                size=16,
                color=ft.Colors.ON_SURFACE_VARIANT
            ),

            tarjeta(
                ft.Column(
                    [
                        titulo_seccion(
                            "Período",
                            ft.Icons.CALENDAR_MONTH
                        ),
                        ft.Row(
                            [
                                selector_mes,
                                selector_anio
                            ],
                            wrap=True
                        )
                    ],
                    spacing=12
                )
            ),

            tarjeta(
                ft.Column(
                    [
                        titulo_seccion(
                            "Ingreso mensual",
                            ft.Icons.PAYMENTS
                        ),
                        con_aviso(ingreso)
                    ],
                    spacing=12
                )
            ),

            tarjeta(
                ft.Column(
                    [
                        titulo_seccion(
                            "Gastos por categoría",
                            ft.Icons.CATEGORY
                        ),
                        ft.Row(
                            [
                                con_aviso(campos_gastos[categoria])
                                for categoria in CATEGORIAS
                            ],
                            wrap=True,
                            spacing=16,
                            run_spacing=12
                        )
                    ],
                    spacing=12
                )
            ),

            ft.Row(
                [
                    ft.Button(
                        content="Analizar",
                        icon=ft.Icons.INSIGHTS,
                        height=46,
                        on_click=analizar,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY,
                            shape=ft.RoundedRectangleBorder(
                                radius=12
                            )
                        )
                    ),

                    ft.OutlinedButton(
                        content="Guardar período",
                        icon=ft.Icons.SAVE,
                        height=46,
                        on_click=guardar_periodo,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(
                                radius=12
                            )
                        )
                    ),

                    ft.OutlinedButton(
                        content="Limpiar",
                        icon=ft.Icons.CLEAR_ALL,
                        height=46,
                        on_click=limpiar,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(
                                radius=12
                            )
                        )
                    )
                ],
                wrap=True,
                spacing=12,
                run_spacing=12
            ),

            mensaje,

            resultado
        ])


        page.update()


    # ========================================================
    # PANTALLA HISTORIAL
    # ========================================================

    def mostrar_historial(e=None):

        actualizar_nav("historial")

        contenido.controls.clear()

        contenido.controls.append(
            ft.Text(
                "Acá podés consultar todos los "
                "meses que hayas guardado.",
                size=16,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        )


        if not historial:

            contenido.controls.append(
                tarjeta(
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.HISTORY,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            ft.Text(
                                "Todavía no hay períodos guardados.",
                                expand=True
                            )
                        ],
                        spacing=10
                    )
                )
            )

        else:

            for anio in sorted(
                historial.keys(),
                reverse=True
            ):

                contenido.controls.append(
                    titulo_seccion(
                        f"Año {anio}",
                        ft.Icons.EVENT
                    )
                )


                for mes in MESES:

                    if mes not in historial[anio]:
                        continue


                    datos = historial[anio][mes]

                    ingreso_guardado = datos.get(
                        "ingreso",
                        0
                    )

                    gastos_guardados = datos.get(
                        "total_gastos",
                        0
                    )

                    balance_guardado = datos.get(
                        "balance",
                        datos.get("saldo", 0)
                    )

                    fecha_guardado = datos.get(
                        "fecha_guardado",
                        ""
                    )


                    def cargar(
                        e,
                        anio=anio,
                        mes=mes
                    ):

                        cargar_periodo(
                            anio,
                            mes
                        )


                    def dato(titulo, valor, color=None):

                        return ft.Column(
                            [
                                ft.Text(
                                    titulo,
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                                ft.Text(
                                    valor,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=color
                                )
                            ],
                            spacing=2
                        )


                    color_balance_guardado = (
                        COLOR_POSITIVO
                        if balance_guardado >= 0
                        else COLOR_NEGATIVO
                    )


                    contenido.controls.append(

                        tarjeta(
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                f"{mes} {anio}",
                                                size=18,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            ft.Text(
                                                fecha_guardado,
                                                size=12,
                                                color=(
                                                    ft.Colors
                                                    .ON_SURFACE_VARIANT
                                                )
                                            )
                                        ],
                                        alignment=(
                                            ft.MainAxisAlignment
                                            .SPACE_BETWEEN
                                        ),
                                        wrap=True
                                    ),

                                    ft.Row(
                                        [
                                            dato(
                                                "Ingresos",
                                                f"${ingreso_guardado:,.2f}",
                                                COLOR_POSITIVO
                                            ),
                                            dato(
                                                "Gastos",
                                                f"${gastos_guardados:,.2f}",
                                                COLOR_NEGATIVO
                                            ),
                                            dato(
                                                "Balance",
                                                f"${balance_guardado:,.2f}",
                                                color_balance_guardado
                                            )
                                        ],
                                        wrap=True,
                                        spacing=30,
                                        run_spacing=10
                                    ),

                                    ft.Row(
                                        [
                                            ft.Button(
                                                content="Cargar período",
                                                icon=ft.Icons.UPLOAD_FILE,
                                                on_click=cargar,
                                                style=ft.ButtonStyle(
                                                    shape=(
                                                        ft.RoundedRectangleBorder(
                                                            radius=12
                                                        )
                                                    )
                                                )
                                            )
                                        ]
                                    )
                                ],
                                spacing=12
                            )
                        )
                    )


        page.update()


    # ========================================================
    # TEMA CLARO / OSCURO
    # ========================================================

    def cambiar_tema(e=None):

        if page.theme_mode == ft.ThemeMode.DARK:

            page.theme_mode = ft.ThemeMode.LIGHT
            boton_tema.icon = ft.Icons.DARK_MODE
            boton_tema.tooltip = "Cambiar a tema oscuro"

        else:

            page.theme_mode = ft.ThemeMode.DARK
            boton_tema.icon = ft.Icons.LIGHT_MODE
            boton_tema.tooltip = "Cambiar a tema claro"

        page.update()


    # ========================================================
    # NAVEGACIÓN Y ENCABEZADO
    # ========================================================

    def estilo_nav(activo):

        return ft.ButtonStyle(
            bgcolor=(
                ft.Colors.WHITE
                if activo
                else ft.Colors.with_opacity(0.18, ft.Colors.WHITE)
            ),
            color=(
                ft.Colors.INDIGO_700
                if activo
                else ft.Colors.WHITE
            ),
            shape=ft.RoundedRectangleBorder(radius=12)
        )


    def actualizar_nav(pantalla):

        boton_asesor.style = estilo_nav(pantalla == "asesor")
        boton_historial.style = estilo_nav(pantalla == "historial")


    boton_asesor = ft.Button(
        content="Asesor",
        icon=ft.Icons.CALCULATE,
        on_click=mostrar_asesor,
        style=estilo_nav(True)
    )

    boton_historial = ft.Button(
        content="Historial",
        icon=ft.Icons.HISTORY,
        on_click=mostrar_historial,
        style=estilo_nav(False)
    )

    boton_tema = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        icon_color=ft.Colors.WHITE,
        tooltip="Cambiar a tema oscuro",
        on_click=cambiar_tema
    )


    encabezado = ft.Container(
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[
                ft.Colors.INDIGO_600,
                ft.Colors.PURPLE_500
            ]
        ),
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=48,
                            height=48,
                            border_radius=24,
                            bgcolor=ft.Colors.with_opacity(
                                0.2,
                                ft.Colors.WHITE
                            ),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Asesor de Gastos Personales",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    "Controlá tus finanzas mes a mes",
                                    size=12,
                                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)
                                )
                            ],
                            spacing=0
                        )
                    ],
                    spacing=12
                ),

                ft.Row(
                    [
                        boton_asesor,
                        boton_historial,
                        boton_tema
                    ],
                    spacing=8,
                    wrap=True
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True,
            run_spacing=12
        )
    )


    page.add(
        encabezado,
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=contenido,
                    padding=20,
                    col={
                        "xs": 12,
                        "md": 11,
                        "lg": 10,
                        "xl": 8
                    }
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )


    mostrar_asesor()


# ============================================================
# INICIO
# ============================================================

if __name__ == "__main__":
    ft.run(main)
