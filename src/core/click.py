import pyautogui


def click(point, ctrl=False, right=False):
    pyautogui.moveTo(point)
    if ctrl:
        pyautogui.keyDown("ctrl")
    pyautogui.click(button="right" if right else "left")
    if ctrl:
        pyautogui.keyUp("ctrl")
