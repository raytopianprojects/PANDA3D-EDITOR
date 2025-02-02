from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.directbase import DirectStart
from panda3d.core import SamplerState, load_prc_file_data

load_prc_file_data("", """
textures-power-2 none
""")

base.setBackgroundColor(0, 0, 0, 1)

frame_tex = loader.loadTexture('frame.png')
frame_tex.wrap_u = SamplerState.WM_clamp
frame_tex.wrap_v = SamplerState.WM_clamp
frame_tex.wrap_w = SamplerState.WM_clamp

button_textures = []
for state in 'normal', 'active', 'hover', 'disabled':
    tex = loader.loadTexture(f'button-{state}.png')
    tex.wrap_u = SamplerState.WM_clamp
    tex.wrap_v = SamplerState.WM_clamp
    tex.wrap_w = SamplerState.WM_clamp
    button_textures.append(tex)

frame = DirectFrame(pos=(0, 0, 0), frameSize=(-0.8, 0.8, -0.65, 0.25), relief=DGG.TEXTUREBORDER, borderUvWidth=(0.1, 0.1), frameTexture=frame_tex, frameColor=(1, 1, 1, 1))
frame.setTransparency(1)

btn1 = DirectButton(parent=frame, pos=(-0.5, 0, -0.5), text="OK", text_scale=0.06, text_fg=(1, 1, 1, 0.8), relief=DGG.TEXTUREBORDER, borderWidth=(0.12, 0.04), borderUvWidth=(0.35, 0.35), frameTexture=button_textures, frameColor=(1, 1, 1, 1))
btn1.setTransparency(1)

btn2 = DirectButton(parent=frame, pos=(0.2, 0, -0.5), text="Cancel cancel cancel cancel", text_scale=0.06, text_fg=(1, 1, 1, 0.8), relief=DGG.TEXTUREBORDER, borderWidth=(0.12, 0.04), borderUvWidth=(0.35, 0.35), frameTexture=button_textures, frameColor=(1, 1, 1, 1))
btn2.setTransparency(1)

base.run()
