import math

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

def calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL):
    # Чувствительность приемника BS для UL
    ThermalNoise = -174 + 10 * math.log10(BW_UL)  # Тепловой шум в дБм
    RxSens_BS = ThermalNoise + NoiseFigure_BS + SINR_UL  # Чувствительность приемника в дБм

    # Расчет максимально допустимых потерь сигнала (MAPL_UL)
    MAPL_UL = TxPower_UE - FeederLoss + AntGain_BS + MIMOGain - RxSens_BS - IM - PenetrationM

    return MAPL_UL

def calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL):
    # Чувствительность приемника UE для DL
    ThermalNoise = -174 + 10 * math.log10(BW_DL)  # Тепловой шум в дБм
    RxSens_UE = ThermalNoise + NoiseFigure_UE + SINR_DL  # Чувствительность приемника в дБм

    # Расчет максимально допустимых потерь сигнала (MAPL_DL)
    MAPL_DL = TxPower_BS - FeederLoss + AntGain_BS + MIMOGain - RxSens_UE - IM - PenetrationM

    return MAPL_DL

# Вызов функций для вычисления MAPL_UL и MAPL_DL
MAPL_UL = calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL)
MAPL_DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL)

# Вывод результатов
print(f"Максимально допустимые потери сигнала (MAPL_UL): {MAPL_UL:.2f} дБ")
print(f"Максимально допустимые потери сигнала (MAPL_DL): {MAPL_DL:.2f} дБ")