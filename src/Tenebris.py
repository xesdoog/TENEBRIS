from Misc import utils
from pathlib import Path
from win32gui import FindWindow, SetForegroundWindow
import os
import sys

PARENT_PATH = Path(__file__).parent
ASSETS_PATH = PARENT_PATH / Path(r"assets")
LOG         = utils.LOGGER()
config_file = PARENT_PATH / Path('tenebris.json')
this_window = FindWindow(None, 'TENEBRIS')

if this_window != 0:
    LOG.warning("\nTENEBRIS is aleady running! Only one instance can be launched at once.\n")
    SetForegroundWindow(this_window)
    sys.exit(0)
LOG.OnStart(PARENT_PATH)

import atexit
import imgui
import os
from GUI import gui
from imgui.integrations.glfw import GlfwRenderer
from webbrowser import open_new_tab

file_items = utils.read_cfg(config_file)
file_names = []
Icons      = gui.Icons

def res_path(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def append_file_names():
    if len(file_items) > 0:
        for file in file_items:
            file_names.append(file["name"])

def OnDraw():
    imgui.create_context()
    window = gui.impl_glfw_init("TENEBRIS", 300, 480)
    impl = GlfwRenderer(window)
    font_scaling_factor = gui.fb_to_window_factor(window)
    io = imgui.get_io()
    io.fonts.clear()
    io.font_global_scale = 1.0 / font_scaling_factor
    font_config = imgui.core.FontConfig(merge_mode=True)
    icons_range = imgui.core.GlyphRanges([0xF013, 0xF0D0, 0])
    main_font = io.fonts.add_font_from_file_ttf(
        str(res_path("fonts/Rokkitt-Regular.ttf")), 18 * font_scaling_factor,
    )

    io.fonts.add_font_from_file_ttf(
        str(res_path("fonts/fontawesome-webfont.ttf")), 15 * font_scaling_factor,
        font_config, icons_range
    )

    impl.refresh_font_texture()
    append_file_names()
    DLL_list_index  = 0
    proc_list_index = 0
    selected_proc   = None
    selected_DLL    = None
    process_list, proc_names = utils.update_process_list()

    while not gui.glfw.window_should_close(window):
        gui.glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        win_w, win_h = gui.glfw.get_window_size(window)
        texture, t_width, t_height = gui.gl_draw_image(res_path('img/launchpad-logo.png'))
        imgui.set_next_window_size(win_w, win_h)
        imgui.set_next_window_position(0, 0)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.08, 0.08, 0.08)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_ACTIVE, 0.2, 0.2, 0.2)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_HOVERED, 0.3, 0.3, 0.3)
        imgui.push_style_color(imgui.COLOR_HEADER, 0.1, 0.1, 0.1)
        imgui.push_style_color(imgui.COLOR_HEADER_ACTIVE, 0.2, 0.2, 0.2)
        imgui.push_style_color(imgui.COLOR_HEADER_HOVERED, 0.3, 0.3, 0.3)
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.08, 0.08, 0.08)
        imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.2, 0.2, 0.2)
        imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.3, 0.3, 0.3)
        imgui.push_style_var(imgui.STYLE_CHILD_ROUNDING, 10)
        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 10)
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (10, 10))
        imgui.push_style_var(imgui.STYLE_ITEM_INNER_SPACING, (10, 10))
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (10, 10))
        imgui.begin("Main Window", flags =
                    imgui.WINDOW_NO_TITLE_BAR |
                    imgui.WINDOW_NO_RESIZE |
                    imgui.WINDOW_NO_MOVE
                    )
        imgui.same_line(spacing = (win_w / 2) - (t_width / 13))
        imgui.image(texture, t_width / 7, t_height / 7)
        if imgui.is_item_hovered():
            imgui.set_tooltip(f"Click to open GitHub  {Icons.GitHub}")
        if imgui.is_item_clicked(0):
            open_new_tab('https://github.com/xesdoog/TENEBRIS')

        imgui.push_font(main_font)
        imgui.push_text_wrap_pos(win_w - 5)
        imgui.text(f"{Icons.List}  Process List:")
        imgui.push_item_width(240)
        pl_clicked, proc_list_index = imgui.combo("##proclist", proc_list_index, proc_names)
        if pl_clicked:
            selected_proc = process_list[proc_list_index]["pid"]

        imgui.same_line(spacing=10)
        if imgui.button(Icons.Repeat):
            process_list, proc_names = utils.update_process_list()
            proc_list_index = 0
            selected_proc = None
        if imgui.is_item_hovered():
            imgui.set_tooltip("Refresh the process list.")

        if imgui.begin_child("##dlllist", win_w - 17, win_h / 2.5, True):
            imgui.text(f"{Icons.Save}  Saved DLLs:"); imgui.separator()
            imgui.push_item_width(win_w - 35)
            imgui.set_next_window_bg_alpha(0.0)
            clicked, DLL_list_index = imgui.listbox("##List", DLL_list_index, file_names, len(file_items))
            imgui.pop_item_width()
            if clicked:
                selected_DLL = file_items[DLL_list_index]["path"]

        imgui.end_child()

        if imgui.button(f"{Icons.Plus} Add DLL", 120, 35):
            dll_file = gui.start_file_dialog(extension="DLL\0*.dll\0All Files\0*.*\0", multiselect=False)
            if dll_file is not None:
                file_name = utils.get_file_name(dll_file)
                if not utils.is_file_saved(file_name, file_items):
                    file_items.append({"name": file_name, "path": dll_file})
                    file_names.append(file_name)
                    utils.save_cfg(config_file, file_items)

        if len(file_items) > 0:
            imgui.same_line(spacing=30)
            if imgui.button(f"{Icons.Minus} Remove DLL", 120, 35):
                file_items.remove(file_items[DLL_list_index])
                file_names.remove(file_names[DLL_list_index])
                utils.save_cfg(config_file, file_items)
        
        if selected_DLL is not None and os.path.isfile(selected_DLL) and selected_proc is not None and selected_proc != 0:
            if imgui.button(f"{Icons.Magic}    Inject", 120, 35):
                img_handle = utils.inject_dll(selected_proc, selected_DLL, logger=LOG)
                LOG.debug(f"Injected {selected_DLL} into {process_list[proc_list_index]}. Image Handle: {img_handle}")
        
        else:
            imgui.dummy(1, 5); imgui.text_disabled(f"    {Icons.Magic}    Inject") # there is no binding for ImGui::BeginDisabled() so this will do.
        

        imgui.pop_font()
        imgui.pop_text_wrap_pos()
        imgui.pop_style_color(9)
        imgui.pop_style_var(5)
        imgui.end()

        gui.gl.glClearColor(1.0, 1.0, 1.0, 1)
        gui.gl.glClear(gui.gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        gui.glfw.swap_buffers(window)
        gui.gl.glDeleteTextures([texture])

    impl.shutdown()
    gui.glfw.terminate()

@atexit.register
def OnExit():
    LOG.info("Closing application...\n\nFarewell!")

if __name__ == "__main__":
    # freeze_support()
    OnDraw()
