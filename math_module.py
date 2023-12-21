import numpy as np
import scipy.stats as st


# функция для вычисления доверительного интервала с помощью критерия Стьюдента
def hamming_mera(E: list[float]) -> (float, float):
    # преобразуем список в массив numpy
    arr = np.array(E)
    # проверяем, что передан одномерный массив
    if arr.ndim != 1 or arr.shape[0] < 2:
        raise ValueError('Передан неверный массив!')
    # вычисляем размер выборки
    n = len(arr)
    # задаем уровень значимости
    alpha = 0.01
    # вычисляем стандартную ошибку среднего
    std_err = arr.std() / np.sqrt(n)
    # вычисляем критическое значение t-статистики
    t = st.t.ppf(1 - alpha / 2, n - 1)
    # вычисляем среднее значение выборки
    mean = arr.mean()
    # вычисляем доверительный интервал
    return mean - t * std_err, mean + t * std_err


# функция для вычисления среднего значения по столбцам матрицы
def averaging_value(matrix: list[list[float]]) -> list[float]:
    # преобразуем список списков в двумерный массив numpy и вычисляем среднее значение по столбцам
    return list(np.mean(np.array(matrix)[:, :], axis=0))


# функция для вычисления расстояния Хэмминга между двумя векторами
def hamming_distance(x1: list[float], x2: list[float]) -> float:
    # вычисляем L1-норму разности векторов с помощью функции np.linalg.norm
    return np.linalg.norm(np.array(x1) - np.array(x2), ord=1)
