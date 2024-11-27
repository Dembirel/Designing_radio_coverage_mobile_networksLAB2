import math
import numpy as np
import matplotlib.pyplot as plt

TxPower_UE = 24  # Мощность передатчика UE в дБм
TxPower_BS = 46  # Мощность передатчика BS в дБм
FeederLoss = 2  # Потери в фидере в дБ
AntGain_BS = 21  # Коэффициент усиления антенны BS в дБи
MIMOGain = 3  # Выигрыш от MIMO в дБ
IM = 1  # Запас мощности на интерференцию в дБ
PenetrationM = 15  # Запас мощности на проникновение в дБ
BW_UL = 10e6  # Полоса частот для UL (10 МГц)
BW_DL = 20e6  # Полоса частот для DL (20 МГц)
NoiseFigure_BS = 2.4  # Коэффициент шума приемника BS в дБ
NoiseFigure_UE = 6  # Коэффициент шума приемника UE в дБ
SINR_UL = 4  # Требуемое отношение SINR для UL в дБ
SINR_DL = 2  # Требуемое отношение SINR для DL в дБ

# Функции для расчета потерь сигнала (PL) по разным моделям
def calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL):
    # Чувствительность приемника UE для DL
    ThermalNoise = -174 + 10 * math.log10(BW_DL)  # Тепловой шум в дБм
    RxSens_UE = ThermalNoise + NoiseFigure_UE + SINR_DL  # Чувствительность приемника в дБм

    # Расчет максимально допустимых потерь сигнала (MAPL_DL)
    MAPL_DL = TxPower_BS - FeederLoss + AntGain_BS + MIMOGain - RxSens_UE - IM - PenetrationM

    return MAPL_DL

def calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL):
    # Чувствительность приемника BS для UL
    ThermalNoise = -174 + 10 * math.log10(BW_UL)  # Тепловой шум в дБм
    RxSens_BS = ThermalNoise + NoiseFigure_BS + SINR_UL  # Чувствительность приемника в дБм

    # Расчет максимально допустимых потерь сигнала (MAPL_UL)
    MAPL_UL = TxPower_UE - FeederLoss + AntGain_BS + MIMOGain - RxSens_BS - IM - PenetrationM

    return MAPL_UL

def OkomuraHata(d):
    f_MHz = 1.8e9 / 1e6  # ГГц в МГц
    d_Km = d / 1e3  # Переводим из метров в километры
    A = 46.3
    B = 33.9
    hBS = 30
    hms = 1.5
    Lclutter_du = 3
    Lclutter_u = 0

    a = 3.2 * np.ceil(np.log10(11.75 * hms)) ** 2 - 4.97
    
    s = np.where(d_Km >= 1, 44.9 - 6.55 * np.log10(f_MHz), (47.88 + 13.9 * np.log10(f_MHz) - 13.9 * np.log10(hBS)) * (1 / np.log10(50)))
    
    PL_DU = A + B * np.log10(f_MHz) - 13.82 * np.log10(hBS) - a + s * np.log10(d_Km) + Lclutter_du
    PL_U = A + B * np.log10(f_MHz) - 13.82 * np.log10(hBS) - a + s * np.log10(d_Km) + Lclutter_u

    return PL_DU, PL_U

def UMiNLOS(d):
    f_GHz = 1.8
    PL = 26 * np.log10(f_GHz) + 22.7 + 36.7 * np.log10(d)
    return PL

# Функция для нахождения пересечения значений
def findIntersection(values, threshold, distances):
    idx = np.where(values <= threshold)[0][-1]
    return distances[idx], values[idx]

UL = calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL)
DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL)


print(f"Пороговое значение DownLink: {DL:.2f}")
print(f"Пороговое значение UpLink: {UL:.2f}")

MAX_LEVEL = min(DL, UL)
MAX_LEVEL_2 = max(DL, UL)

DISTANCE_KM = np.linspace(0.01, 100, 1000)  # Диапазон от 0.01 до 100 км

# Расчет потерь по моделям
PL_DU, PL_U = OkomuraHata(DISTANCE_KM * 1e3)
PL_UMLS = UMiNLOS(DISTANCE_KM * 1e3)

# Находим пересечения для различных уровней потерь
Hata_DU_1x, Hata_DU_1y = findIntersection(PL_DU, MAX_LEVEL, DISTANCE_KM)
Hata_U_1x, Hata_U_1y = findIntersection(PL_U, MAX_LEVEL, DISTANCE_KM)
PL_UMLS_1x, PL_UMLS_1y = findIntersection(PL_UMLS, MAX_LEVEL, DISTANCE_KM)

Hata_DU_2x, Hata_DU_2y = findIntersection(PL_DU, MAX_LEVEL_2, DISTANCE_KM)
Hata_U_2x, Hata_U_2y = findIntersection(PL_U, MAX_LEVEL_2, DISTANCE_KM)
PL_UMLS_2x, PL_UMLS_2y = findIntersection(PL_UMLS, MAX_LEVEL_2, DISTANCE_KM)

# График для Hata и UMiNLOS
plt.figure()
plt.plot(DISTANCE_KM, DL * np.ones_like(DISTANCE_KM), 'y--', linewidth=1)  # линия для DL
plt.plot(DISTANCE_KM, UL * np.ones_like(DISTANCE_KM), 'g--', linewidth=1)  # линия для UL
plt.plot(DISTANCE_KM, PL_U, 'g-', linewidth=1.5)

# Вертикальные линии для пересечений
plt.axvline(Hata_U_1x, color='k', linestyle=':', linewidth=1.5)  # вертикальная линия для PL_U
plt.axvline(Hata_U_2x, color='k', linestyle=':', linewidth=1.5)  # вертикальная линия для PL_U

# Подписываем значения на вертикальных линиях
plt.text(Hata_U_1x, Hata_U_1y, f'{Hata_U_1x:.2f} km', verticalalignment='bottom', horizontalalignment='right', color='black', fontsize=10)
plt.text(Hata_U_2x, Hata_U_2y, f'{Hata_U_2x:.2f} km', verticalalignment='bottom', horizontalalignment='right', color='black', fontsize=10)

plt.xlabel('Расстояние, км L_{clutter} = 0')
plt.ylabel('Потеря сигнала, dB')
plt.title('Зависимость потерь радиосигнала от расстояния (Hata, UMiNLOS)')
plt.grid(True)
plt.legend(['DL', 'UL', 'Hata (Macrocells)'])
plt.show()

# Вычисление радиуса и количества базовых станций для покрытия
area = 100  # площадь в кв.км
rBS_1 = min(Hata_U_1x, Hata_U_2x)
print(f"Радиус базовой станции для 100 кв.км: {rBS_1:.2f} км")
sBS_1 = 1.95 * (rBS_1 ** 2)
print(f"Площадь базовой станции кв.км: {sBS_1:.2f}")
print(f"Требуемое количество для покрытия: {np.ceil(area / sBS_1).astype(int)}")

# График для UMiNLOS
plt.figure()
plt.plot(DISTANCE_KM, DL * np.ones_like(DISTANCE_KM), 'y--', linewidth=1)  # линия для DL
plt.plot(DISTANCE_KM, UL * np.ones_like(DISTANCE_KM), 'g--', linewidth=1)  # линия для UL
plt.plot(DISTANCE_KM, PL_UMLS, 'm-', linewidth=1.5)

# Вертикальные линии для пересечений
plt.axvline(PL_UMLS_1x, color='k', linestyle=':', linewidth=1.5)  # вертикальная линия для PL_U
plt.axvline(PL_UMLS_2x, color='k', linestyle=':', linewidth=1.5)  # вертикальная линия для PL_U

# Подписываем значения на вертикальных линиях
plt.text(PL_UMLS_1x, PL_UMLS_1y, f'{PL_UMLS_1x:.2f} km', verticalalignment='bottom', horizontalalignment='right', color='black', fontsize=10)
plt.text(PL_UMLS_2x, PL_UMLS_2y, f'{PL_UMLS_2x:.2f} km', verticalalignment='bottom', horizontalalignment='right', color='black', fontsize=10)

plt.xlabel('Расстояние, км')
plt.ylabel('Потеря сигнала, dB')
plt.title('Зависимость потерь радиосигнала от расстояния (UMiNLOS)')
plt.grid(True)
plt.legend(['DL', 'UL', 'UMiNLOS (Femto- Micro- Cells)'])
plt.show()

# Вычисление радиуса и количества базовых станций для покрытия
area = 4  # площадь в кв.км
rBS_2 = min(PL_UMLS_1x, PL_UMLS_2x)
print(f"Радиус базовой станции для 4 кв.км: {rBS_2:.2f} км")
sBS_2 = 1.95 * (rBS_2 ** 2)
print(f"Площадь базовой станции кв.км: {sBS_2:.2f}")
print(f"Требуемое количество для покрытия: {np.ceil(area / sBS_2).astype(int)}")
