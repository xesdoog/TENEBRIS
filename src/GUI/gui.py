from cv2 import cvtColor, imread, COLOR_BGR2RGBA, IMREAD_UNCHANGED
from pywintypes import error as pywinErr
from types import SimpleNamespace
from win32gui import GetOpenFileNameW
import glfw
import OpenGL.GL as gl
import os
import win32con

Icons = SimpleNamespace(
    Gear   = "\uf013",
    Down   = "\uf01a",
    Up     = "\uf01b",
    Repeat = "\uf01e",
    List   = "\uf03a",
    Plus   = "\uf055",
    Minus  = "\uf056",
    Close  = "\uf05c",
    GitHub = "\uf09b",
    Save   = "\uf0c7",
    Magic  = "\uf0d0",
)

def start_file_dialog(extension: str, multiselect: bool) -> list | str:
    try:
        fnames = []
        customfilter = "All Files\0*.*\0"
        fname, customfilter, _ = GetOpenFileNameW(
            InitialDir   = os.getcwd(),
            Flags        = multiselect and
                            win32con.OFN_EXPLORER | win32con.OFN_ALLOWMULTISELECT or
                            win32con.OFN_EXPLORER,
            DefExt       = None,
            Title        = "Select DLL",
            File         = "",
            MaxFile      = 65535,
            Filter       = extension,
            CustomFilter = customfilter,
            FilterIndex  = 0,
        )

        if str(fname).find('\x00'):
            split_n = str(fname).split('\x00')
            fnames.append(split_n)
        
        if len(fnames[0]) > 1:
            filePath_lst = []
            parent_path = fnames[0][0]
            for i in range(1, len(fnames[0])):
                filePaths = os.path.join(parent_path, fnames[0][i])
                filePath_lst.append(filePaths)

            final_list = filePath_lst

        else:
            final_list = fnames[0][0]

        return final_list

    except pywinErr:
        return None

def gl_draw_image(path):
    img = imread(path, IMREAD_UNCHANGED)

    # swap CV2's BGR to RGBA
    img = cvtColor(img, COLOR_BGR2RGBA)
    h, w = img.shape[:2]
    texture = gl.glGenTextures(1)

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH,0)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img)
    
    return texture, w, h


def fb_to_window_factor(window):
    """
    Frame buffer to window factor.
    """
    win_w, win_h = glfw.get_window_size(window)
    fb_w, fb_h = glfw.get_framebuffer_size(window)

    return max(float(fb_w) / win_w, float(fb_h) / win_h)

def impl_glfw_init(window_title: str, width: int, height: int) -> object:

    if not glfw.init():
        raise Exception("Failed to initialize OpenGL context!")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.RESIZABLE, gl.GL_FALSE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_title, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        raise Exception("Failed to initialize Window!")

    return window
