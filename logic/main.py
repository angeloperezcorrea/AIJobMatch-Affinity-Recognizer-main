import os
from time import sleep
from threading import Thread
from vtt import video_to_text
from emotions_afinity import analize_emotions, progress_queue
from speech_processing import analize_speech
from TypeWriterEffectControl import TypeWriterControl

import flet as ft

VERSION = "1.0.0"

deterministic_progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor=ft.colors.BLUE, opacity=0, value=0)
deterministic_progress_bar_percentage = ft.Text("", text_align=ft.TextAlign.CENTER, selectable=True)

def update_progress():
    while True:
        progress = progress_queue.get()
        deterministic_progress_bar.value = progress
        deterministic_progress_bar_percentage.value = f"{progress * 100:.2f}%"
        deterministic_progress_bar_percentage.update()
        deterministic_progress_bar.update()

def gui(page: ft.Page):
    page.title = f"Affinity Recognizer v{VERSION}"
    page.scroll = ft.ScrollMode.ALWAYS
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_height = 650
    page.window_width = 580
    
    def pick_video(e: ft.FilePickerResultEvent):
        selected_video.value = (
            ", ".join(map(lambda f: f.path, e.files)
                      ) if e.files else "Cancelled!"
        )
        selected_video.update()
    
    pick_video_dialog = ft.FilePicker(on_result=pick_video)
    selected_video = ft.Text(text_align=ft.TextAlign.CENTER, selectable=True)
    
    def close_dialog(e):
        success_dialog.open = False
        page.update()
    
    success_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Éxito!"),
        content=ft.Text("Vídeo analizado correctamente!"),
        actions=[
            ft.TextButton("OK", on_click=close_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: close_dialog(e),
    )
    
    video_label_checkbox = ft.Checkbox(
        label="Mostrar ventana emergente con el vídeo mientras se procesa",
        value=False,
    )
    
    select_video_btn = ft.ElevatedButton(
                                "Seleccionar video",
                                icon=ft.icons.VIDEO_FILE,
                                on_click=lambda _: pick_video_dialog.pick_files(
                                    allowed_extensions=["mp4", "avi", "mov"]
                                ),
                                disabled=page.web
                            )
    
    
        
    video_to_text_msg = TypeWriterControl(value="", transparency=False, color=ft.colors.BLUE)
    video_to_text_progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor=ft.colors.BLUE, opacity=0)
    
    video_emotions_msg = TypeWriterControl(value="", transparency=False, color=ft.colors.BLUE)
    video_emotions_progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor=ft.colors.BLUE, opacity=0)
    
    speech_emotions_msg = TypeWriterControl(value="", transparency=False, color=ft.colors.BLUE)
    speech_emotions_progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor=ft.colors.BLUE, opacity=0)
    
    update_progress_thread = Thread(target=update_progress)
    update_progress_thread.start()
    
    def on_analyze_button_click(e):
        # Disable buttons
        select_video_btn.disabled = True
        analize_video_btn.disabled = True
        video_label_checkbox.disabled = True
        select_video_btn.update()
        analize_video_btn.update()
        video_label_checkbox.update()
                
        # Reset values
        video_to_text_progress_bar.opacity = 0
        video_to_text_progress_bar.value = None
        video_to_text_progress_bar.update()
        video_emotions_progress_bar.opacity = 0
        video_emotions_progress_bar.value = None
        video_emotions_progress_bar.update()
        speech_emotions_progress_bar.opacity = 0
        speech_emotions_progress_bar.value = None
        speech_emotions_progress_bar.update()
        deterministic_progress_bar.opacity = 0
        deterministic_progress_bar.value = 0
        deterministic_progress_bar.update()
        
        # Reset messages
        video_to_text_msg.text_to_print = ""
        video_to_text_msg.text_color = ft.colors.BLUE
        video_to_text_msg.update()
        video_emotions_msg.text_to_print = ""
        video_emotions_msg.text_color = ft.colors.BLUE
        video_emotions_msg.update()
        speech_emotions_msg.text_to_print = ""
        speech_emotions_msg.text_color = ft.colors.BLUE
        speech_emotions_msg.update()
        deterministic_progress_bar_percentage.value = ""
        deterministic_progress_bar_percentage.update()
        
        video_to_text_progress_bar.opacity = 1
        video_to_text_progress_bar.update()
        video_to_text_msg.transparency = True
        video_to_text_msg.text_to_print = "> Convirtiendo video a texto... [⏳]"
        video_to_text_msg.update()
        try:
            text = video_to_text(selected_video.value)
        except Exception as e:
            video_to_text_msg.text_to_print = f"> Error al convertir video a texto: {e} [❌]"
            video_to_text_msg.text_color = ft.colors.RED
            video_to_text_msg.update()
            video_to_text_progress_bar.value = 1
            video_to_text_progress_bar.update()
            return
        video_to_text_msg.text_to_print = "> Vídeo convertido a texto satisfactoriamente... [✅]"
        video_to_text_msg.text_color = ft.colors.GREEN
        video_to_text_progress_bar.value = 1
        video_to_text_msg.update()
        video_to_text_progress_bar.update()
        
        if video_label_checkbox.value == True: # Activate indeterministic progress bar
            video_emotions_progress_bar.opacity = 1
            video_emotions_progress_bar.update()
            deterministic_progress_bar_percentage.opacity = 0
            deterministic_progress_bar_percentage.update()
        else: # Activate deterministic progress bar
            deterministic_progress_bar.opacity = 1
            deterministic_progress_bar.update()
            deterministic_progress_bar_percentage.opacity = 1
            deterministic_progress_bar_percentage.update()
        
        video_emotions_msg.update()
        video_emotions_msg.transparency = True
        video_emotions_msg.text_to_print = "> Analizando emociones del vídeo... [⏳]"
        video_emotions_msg.update()
        try:
            total_emotions, \
            positive_emotions_count, \
            negative_emotions_count, \
            emotions_confidence = analize_emotions(selected_video.value, video_label_checkbox.value)
        except Exception as e:
            video_emotions_msg.text_to_print = f"> Error al analizar emociones del video: {e} [❌]"
            video_emotions_msg.text_color = ft.colors.RED
            video_emotions_msg.update()
            video_emotions_progress_bar.value = 1
            video_emotions_progress_bar.update()
            return
        video_emotions_msg.text_to_print = "> Emociones del vídeo analizadas satisfactoriamente... [✅]"
        video_emotions_msg.text_color = ft.colors.GREEN
        video_emotions_progress_bar.value = 1
        video_emotions_msg.update()
        video_emotions_progress_bar.update()
        
        
        speech_emotions_progress_bar.opacity = 1
        speech_emotions_progress_bar.update()
        speech_emotions_msg.transparency = True
        
        speech_emotions_msg.text_to_print = "> Analizando emociones del discurso... [⏳]"
        speech_emotions_msg.update()
        sleep(1)
        try:
            speech_confidence = analize_speech(text)
        except Exception as e:
            speech_emotions_msg.text_to_print = f"> Error al analizar emociones del discurso: {e} [❌]"
            speech_emotions_msg.text_color = ft.colors.RED
            speech_emotions_msg.update()
            speech_emotions_progress_bar.value = 1
            speech_emotions_progress_bar.update()
            return
        speech_emotions_msg.text_to_print = "> Emociones del discurso analizadas satisfactoriamente... [✅]"
        speech_emotions_msg.text_color = ft.colors.GREEN
        speech_emotions_progress_bar.value = 1
        speech_emotions_msg.update()
        speech_emotions_progress_bar.update()
        
        success_dialog.content = ft.Text(
            f"RESULTADOS DE ANALISIS DE EMOCIONES\n"
            f"Total de emociones positivas: {positive_emotions_count:.2f}\n"
            f"Total de emociones negativas: {negative_emotions_count:.2f}\n"
            f"Total de emociones: {total_emotions:.2f}\n"
            f"Porcentaje de confianza para contratar según sus emociones: {emotions_confidence:.2f}%\n"
            f"RESULTADOS DE ANALISIS DE DISCURSO\n"
            f"Confiablidad para contratar según su discurso: {speech_confidence.capitalize()}",
            selectable=True
        )
        
        # Enable buttons
        select_video_btn.disabled = False
        analize_video_btn.disabled = False
        video_label_checkbox.disabled = False
        select_video_btn.update()
        analize_video_btn.update()
        video_label_checkbox.update()
        
        # print("*** RESULTADOS DE ANALISIS DE EMOCIONES ***")
        # print(f"Total de emociones positivas: {positive_emotions_count}")
        # print(f"Total de emociones negativas: {negative_emotions_count}")
        # print(f"Total de emociones: {total_emotions}")
        # print(f"Porcentaje de confianza para contratar según sus emociones: {emotions_confidence:.2f}%")
        # print("*** RESULTADOS DE ANALISIS DE DISCURSO ***")
        # print(f"Confiablidad para contratar según su discurso: {speech_confidence}")
        page.dialog = success_dialog
        success_dialog.open = True
        page.update()
        
    analize_video_btn = ft.ElevatedButton(
                                "Analizar",
                                icon=ft.icons.PLAY_ARROW,
                                on_click=on_analyze_button_click,
                                disabled=page.web
                            )
    
    page.overlay.extend([pick_video_dialog])
    
    page.add(
        ft.Row(
            [
                ft.Container(
                    content=ft.Text("Affinity Recognizer", size=30),
                    alignment=ft.alignment.top_center,
                    margin=ft.margin.only(top=30),
                ),
                ft.Container(
                    content=ft.Image(src=".\logo.png", width=80, height=80),
                    alignment=ft.alignment.top_center,
                    margin=ft.margin.only(top=30),                    
                    
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Seleccione el video a analizar:", text_align=ft.TextAlign.CENTER),
                            select_video_btn,
                            selected_video,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [   
                            video_label_checkbox,
                            analize_video_btn,
                            video_to_text_msg,
                            video_to_text_progress_bar,
                            video_emotions_msg,
                            video_emotions_progress_bar,
                            deterministic_progress_bar,
                            deterministic_progress_bar_percentage,
                            speech_emotions_msg,
                            speech_emotions_progress_bar,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=10)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

ft.app(target=gui, assets_dir="assets")
# video_path = os.path.join("data/videos/Graciela.mp4")
# text = video_to_text(video_path)
# total_emotions, \
# positive_emotions_count, \
# negative_emotions_count, \
# emotions_confidence = analize_emotions(video_path)
# print("*** RESULTADOS DE ANALISIS DE EMOCIONES ***")
# print(f"Total de emociones positivas: {positive_emotions_count}")
# print(f"Total de emociones negativas: {negative_emotions_count}")
# print(f"Total de emociones: {total_emotions}")
# print(f"Porcentaje de confianza para contratar según sus emociones: {emotions_confidence:.2f}%")

# speech_confidence = analize_speech(text)
# print("*** RESULTADOS DE ANALISIS DE DISCURSO ***")
# print(f"Confiablidad para contratar según su discurso: {speech_confidence}")