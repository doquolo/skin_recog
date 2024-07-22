import PySimpleGUI as sg
sg.theme("SystemDefaultForReal")

import socket

import sys
import os
import home
import handbook
import map
import history
import threading
import logging
import time

class MultilineHandler(logging.Handler):
    def __init__(self, multiline):
        super().__init__()
        self.multiline = multiline

    def emit(self, record):
        msg = self.format(record)
        self.multiline.print(msg)

def startServer():
    # Define the layout of your window
    layout = [
        [sg.Button('Chạy máy chủ', key="-run-"), sg.Button('Thoát', key="-exit-")],
        [sg.Text("Nhật kí máy chủ:")],
        [sg.Multiline(size=(120, 20), key="-output-", background_color="#fff", text_color="#000",
                      reroute_stdout=True, reroute_stderr=True, reroute_cprint=True, auto_size_text=True, autoscroll=True)],
        [sg.Text("", visible=False, key="-iptext-")],
        [sg.StatusBar(text="Trạng thái máy chủ: Ngoại tuyến", key="-status-", relief=sg.RELIEF_FLAT)]           
    ]

    # Create the window
    window = sg.Window('Nhận diện da - Nhật ký máy chủ', layout, finalize=True,
                       enable_close_attempted_event=True)

    # Get the multiline element to add the handler
    multiline = window['-output-']
    handler = MultilineHandler(multiline)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # Event loop to process events and display output
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '-exit-'):
            window.close()
            os._exit(1)
        elif event == '-run-':
            # Start server
            def runApp1():
                logging.info("Starting home app on port 5000")
                home.app.run("0.0.0.0", debug=False, port=5000)

            def runApp2():
                time.sleep(2)  # Add delay to avoid conflict
                logging.info("Starting handbook app on port 80")
                handbook.app.run("0.0.0.0", debug=False, port=80)
                
            def runApp3():
                time.sleep(2)  # Add delay to avoid conflict
                logging.info("Starting map app on port 8080")
                map.app.run("0.0.0.0", debug=False, port=8080)
                
            def runApp4():
                time.sleep(2)  # Add delay to avoid conflict
                logging.info("Starting map app on port 8000")
                history.app.run("0.0.0.0", debug=False, port=8000)

            server1 = threading.Thread(target=runApp1)
            server1.start()
            server2 = threading.Thread(target=runApp2)
            server2.start()
            server3 = threading.Thread(target=runApp3)
            server3.start()
            server4 = threading.Thread(target=runApp4)
            server4.start()

            # Gray out the run button
            window["-run-"].update(disabled=True)
            # get local ip
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            window["-iptext-"].update(visible=True)
            window["-iptext-"].update(f"Máy chủ trực tuyến tại: http://{s.getsockname()[0]}:5000")
            # update status
            window["-status-"].update("Trạng thái máy chủ: Trực tuyến")

if __name__ == "__main__":
    startServer()
