import flet as ft


def main(page: ft.Page):
    page.title = "Una pregunta"
    page.bgcolor = "#F5F5F5"
    page.padding = 20
    page.spacing = 0

    cantidad_no = 0

    texto = ft.Text(
        "¿Eres un Pendejo?",
        size=30,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
        color="#222222",
    )

    def mostrar_final(e):
        page.controls.clear()
        page.padding = 0
        page.spacing = 0
        page.bgcolor = "#171717"

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    "JAJA, pendejo",
                    size=42,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        )
        page.update()

    boton_si = ft.Button(
        content="Sí",
        width=120,
        height=55,
        on_click=mostrar_final,
        style=ft.ButtonStyle(
            bgcolor="#4CAF50",
            color="#FFFFFF",
        ),
    )

    boton_no = ft.Button(
        content="No",
        width=120,
        height=55,
        style=ft.ButtonStyle(
            bgcolor="#F44336",
            color="#FFFFFF",
        ),
    )

    def presionar_no(e):
        nonlocal cantidad_no

        cantidad_no += 1
        texto.value = "Te lo pregunto de nuevo, ¿Eres un Pendejo?"

        if cantidad_no >= 6:
            page.controls.clear()
            page.padding = 0
            page.spacing = 0
            page.bgcolor = "#4CAF50"

            boton_final = ft.Button(
                content=ft.Text(
                    "SÍ",
                    size=60,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
                expand=True,
                style=ft.ButtonStyle(
                    bgcolor="#4CAF50",
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=0),
                ),
                on_click=mostrar_final,
            )

            page.add(
                ft.Container(
                    content=ft.Row(
                        controls=[boton_final],
                        expand=True,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    ),
                    expand=True,
                    width=float("inf"),
                    height=float("inf"),
                    padding=0,
                    margin=0,
                )
            )

            page.update()
            return

        # El botón SÍ crece progresivamente.
        boton_si.width = 120 + cantidad_no * 70
        boton_si.height = 55 + cantidad_no * 15

        # El botón NO se hace cada vez más pequeño.
        boton_no.width = max(120 - cantidad_no * 20, 10)
        boton_no.height = max(55 - cantidad_no * 8, 10)

        page.update()

    boton_no.on_click = presionar_no

    contenedor_botones = ft.Row(
        controls=[boton_si, boton_no],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    contenido = ft.Column(
        controls=[
            texto,
            contenedor_botones,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=35,
    )

    page.add(
        ft.Container(
            padding=ft.Padding(
                top=35,
                left=10,
                right=10,
                bottom=10,
            ),
            content=contenido,
            alignment=ft.Alignment.TOP_CENTER,
        )
    )


ft.run(main)