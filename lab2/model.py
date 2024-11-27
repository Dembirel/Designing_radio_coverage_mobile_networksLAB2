import math
import matplotlib.pyplot as plt
import numpy as np

# Исходные данные для расчета
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

def FSPM(d):
    f_Hz = 1.8e9  # Частота в Гц
    PL = 20 * math.log10(4 * math.pi * d * f_Hz / 3e8)
    return PL

def OkomuraHata(d):
    f_MHz = 1.8e9 / 1e6  # Частота в МГц
    d_Km = d / 1e3  # Расстояние в км
    A = 46.3
    B = 33.9
    hBS = 30  # Высота антенны BS в м
    hms = 1.5  # Высота мобильного устройства в м
    Lclutter_du = 3  # Плотная застройка для DU
    Lclutter_u = 0  # Плотная застройка для U

    a = 3.2 * math.ceil(math.log10(11.75 * hms)) ** 2 - 4.97
    if d_Km >= 1:
        s = 44.9 - 6.55 * math.log10(f_MHz)
    else:
        s = (47.88 + 13.9 * math.log10(f_MHz) - 13.9 * math.log10(hBS)) * (1 / math.log10(50))

    PL_DU = A + B * math.log10(f_MHz) - 13.82 * math.log10(hBS) - a + s * math.log10(d_Km) + Lclutter_du
    PL_U = A + B * math.log10(f_MHz) - 13.82 * math.log10(hBS) - a + s * math.log10(d_Km) + Lclutter_u

    return PL_DU, PL_U

def UMiNLOS(d):
    f_GHz = 1.8  # Частота в ГГц
    PL = 26 * math.log10(f_GHz) + 22.7 + 36.7 * math.log10(d)
    return PL

def WalfishIkegamiLOS(d):
    d = d / 1e3  # Переводим расстояние в км
    f = 1.8 * 1e3  # Частота в Гц
    PL = 42.6 + 20 * math.log10(f) + 26 * math.log10(d)
    return PL

def WalfishIkegamiNLOS(d):
    d = d / 1e3  # Переводим расстояние в км
    f = 1.8 * 1e3  # Частота в Гц
    fi = 28  # Угол в градусах
    w = 10  # Размер улицы
    b = 50  # Ширина улицы
    hBS = 30  # Высота антенны BS
    hms = 1.5  # Высота мобильного устройства
    dh = hBS - hms  # Разница в высоте

    L0 = 32.44 + 20 * math.log10(f) + 20 * math.log10(d)
    if hBS > dh:
        L11 = -18 * math.log10(1 + hBS - dh)
    else:
        L11 = 0

    if hBS > dh:
        ka = 54
    elif hBS <= dh:
        if d > 0.5:
            ka = 54 - 0.8 * (hBS - dh)
        else:
            ka = 54 - 0.8 * (hBS - dh) * (d / 0.5)

    if hBS > dh:
        kd = 18
    else:
        kd = 18 - 15 * (hBS - dh) / dh

    kf = -4 + 0.7 * (f / 925 - 1)
    L1 = L11 + ka + kd * math.log10(d) + kf * math.log10(f) - 9 * math.log10(b)

    L2 = -16.9 - 10 * math.log10(w) + 10 * math.log10(f) + 20 * math.log10(dh - hms) - 10 + 0.354 * fi
    if L1 + L2 > 0:
        Lnlos = L0 + L1 + L2
    else:
        Lnlos = L0

    return Lnlos

# Создаем массив расстояний от 1 до 5000 метров
distances = np.linspace(1, 5000, 500)

# Рассчитываем потери для каждой модели
pl_fspm = [FSPM(d) for d in distances]
pl_okomura_du, pl_okomura_u = zip(*[OkomuraHata(d) for d in distances])
pl_uminlos = [UMiNLOS(d) for d in distances]
pl_walfi_ikegami_los = [WalfishIkegamiLOS(d) for d in distances]
pl_walfi_ikegami_nlos = [WalfishIkegamiNLOS(d) for d in distances]

# Строим графики
plt.figure(figsize=(10, 6))

# Графики для каждой модели
plt.plot(distances, pl_fspm, label="FSPM", linestyle='-', color='blue')
plt.plot(distances, pl_okomura_du, label="Okomura-Hata DU", linestyle='-', color='red')
plt.plot(distances, pl_okomura_u, label="Okomura-Hata U", linestyle='-', color='green')
plt.plot(distances, pl_uminlos, label="UMiNLOS", linestyle='-', color='purple')
plt.plot(distances, pl_walfi_ikegami_los, label="Walfish-Ikegami LOS", linestyle='-', color='orange')
plt.plot(distances, pl_walfi_ikegami_nlos, label="Walfish-Ikegami NLOS", linestyle='-', color='brown')

# Настройка графика
plt.title("Сравнение потерь сигнала (PL) для различных моделей")
plt.xlabel("Расстояние (м)")
plt.ylabel("Потери сигнала (дБ)")
plt.legend()
plt.grid(True)
plt.xscale('linear')  # Логарифмическая шкала по оси X (расстояние)
plt.yscale('linear')  # Логарифмическая шкала по оси Y (потери)

# Показываем график
plt.tight_layout()
plt.show()