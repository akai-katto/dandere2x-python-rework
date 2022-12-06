import dearpygui.dearpygui as dpg

dpg.create_context()

def callback_function():
    print('hi')

with dpg.window(tag="Primary Window", width=640, height=360):
    dpg.add_text("Select Input Video")
    dpg.add_button(label="input video", callback=callback_function, width=150, height = 30 )
    dpg.add_text("Select Output Video", pos=[175, 8])
    dpg.add_button(label="output video", callback=callback_function, width=150, height=30, pos = [175,31])

    dpg.add_button(label="upscale video", callback=callback_function, width=150, height=30, pos = [100,280])

with dpg.window(label="Settings", height=360, width=240, pos=[350, 0]):
    pass

dpg.create_viewport(title='Dandere2x', width=600, height=360)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()