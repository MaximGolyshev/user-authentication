import time
import keyboard

# задаем множество игнорируемых клавиш
ignored_for_input: set = {'enter', 'backspace', 'caps lock', 'tab',
                          'shift', 'ctr', 'lalt', 'ralt', 'left',
                          'up', 'down', 'right', 'space'}


# функция для сбора данных ввода с клавиатуры
def collect_data_for_input() -> (str, list[float], list[float]):
    # создаем пустой список для символов ввода, интервалов между нажатиями клавиш и времени удерживания клавиш
    chars = []
    intervals = []
    holdings_time = []
    # создаем словарь для хранения времени последнего нажатия каждой клавиши
    key_timer = dict()

    # функция-обработчик событий клавиатуры
    def pressed_keys(e):
        if e.event_type == 'down':
            # если была нажата клавиша Backspace, удаляем последний символ и соответствующие интервалы и времена удерживания
            if e.name == 'backspace':
                if chars:
                    chars.pop()
                if intervals:
                    intervals.pop()
                if holdings_time:
                    holdings_time.pop()
            # если нажата не игнорируемая клавиша, добавляем ее в список символов ввода и вычисляем интервал между нажатиями
            if e.name not in ignored_for_input:
                if chars and key_timer.get(chars[-1], None) is not None:
                    intervals.append(time.time() - key_timer[chars[-1]])
                key_timer.update({e.name: time.time()})
                chars.append(e.name)
        # если клавиша отпущена и это не игнорируемая клавиша, вычисляем время удерживания
        elif e.event_type == 'up':
            if e.name not in ignored_for_input:
                holdings_time.append(time.time() - key_timer[e.name])

    # подключаем функцию-обработчик к событиям клавиатуры
    keyboard.hook(pressed_keys)
    # ждем, пока будет нажата клавиша Enter
    keyboard.wait('Enter')
    # отключаем функцию-обработчик от событий клавиатуры
    keyboard.unhook(pressed_keys)

    return ''.join(chars), intervals, holdings_time
