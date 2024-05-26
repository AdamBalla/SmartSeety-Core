import asyncio
import tkinter as tk

from screens.splash_screen import SplashScreen
from config import RESOLUTION, BACKGROUND_COLOR, ENABLE_FULL_SCREEN_MODE


class App(tk.Tk):

    def __init__(self, loop, interval=1/120):
        super().__init__()
        self.loop = loop
        self.tasks = []
        self.tasks.append(loop.create_task(self.updater(interval)))
        self.geometry(RESOLUTION)

        if ENABLE_FULL_SCREEN_MODE:
            self.attributes("-fullscreen", True)
        self.configure(background=BACKGROUND_COLOR)
        self.title("Smart SeeTy Emulator")
        splash = SplashScreen(self)

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = App(loop)
    loop.run_forever()
    loop.close()
    print('App exited gracefully')
