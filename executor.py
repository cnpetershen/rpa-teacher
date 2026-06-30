import pyautogui
import time
import pygetwindow as gw

class Executor:

    def _activate_window(self, title):
        try:
            wins = gw.getWindowsWithTitle(title)
            if wins:
                win = wins[0]
                win.activate()
                time.sleep(0.3)
                return win
        except Exception:
            pass
        return None

    def run(self, skill):

        print("[Hermes] Executing skill...")

        for step in skill["steps"]:

            try:
                if step["action"] == "click":
                    win = self._activate_window(step.get("window", ""))
                    if win and "rel_x" in step and "rel_y" in step:
                        x = win.left + step["rel_x"]
                        y = win.top + step["rel_y"]
                    else:
                        x = step["x"]
                        y = step["y"]
                    pyautogui.click(x, y)

                elif step["action"] == "type":
                    pyautogui.typewrite(step["value"])

            except Exception as e:
                print(f"[Hermes] Step failed: {e}")

            time.sleep(0.2)

        print("[Hermes] Execution finished")
