% Параметры
TxPower_UE = 24;  % Мощность передатчика UE в дБм
TxPower_BS = 46;  % Мощность передатчика BS в дБм
FeederLoss = 2;   % Потери в фидере в дБ
MIMOGain = 3;     % Выигрыш от MIMO в дБ
IM = 1;           % Запас мощности на интерференцию в дБ
PenetrationM = 15; % Запас мощности на проникновение в дБ
BW_UL = 10e6;     % Полоса частот для UL (10 МГц)
BW_DL = 20e6;     % Полоса частот для DL (20 МГц)
NoiseFigure_BS = 2.4;  % Коэффициент шума приемника BS в дБ
NoiseFigure_UE = 6;    % Коэффициент шума приемника UE в дБ
SINR_UL = 4;          % Требуемое отношение SINR для UL в дБ
SINR_DL = 2;          % Требуемое отношение SINR для DL в дБ

% Диапазон значений AntGain_BS
AntGain_BS_values = 5:4:24;

% Массив для хранения радиусов
rBS_values = zeros(size(AntGain_BS_values));

% Расчет радиусов покрытия для каждого значения AntGain_BS
for i = 1:length(AntGain_BS_values)
    AntGain_BS = AntGain_BS_values(i);
    
    % Вычисляем MAPL для DL и UL
    UL = calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL);
    DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL);
    
    % Вычисляем максимальный уровень
    MAX_LEVEL = min(DL, UL);
    MAX_LEVEL_2 = max(DL, UL);
    DISTANCE_KM = linspace(0.01, 100, 1000);  % Диапазон от 0.01 до 100 км
    
    % Расчет потерь по модели Okomura-Hata (только DU)
    PL_DU = OkomuraHata(DISTANCE_KM * 1e3);  % Мы оставляем только PL_DU
    
    % Находим пересечение
    [Hata_DU_x, ~] = findIntersection(PL_DU, MAX_LEVEL, DISTANCE_KM);
    [Hata_DU_1x, ~] = findIntersection(PL_DU, MAX_LEVEL_2, DISTANCE_KM);
    % Радиус покрытия
    rBS_values(i) = round(min(Hata_DU_x, Hata_DU_1x), 3);
end

% Интерполяция для сглаживания графика (если нужно)
AntGain_BS_interp = linspace(min(AntGain_BS_values), max(AntGain_BS_values), 30);  % Интерполяция для более плавной кривой
rBS_values_interp = interp1(AntGain_BS_values, rBS_values, AntGain_BS_interp, 'makima');  % Интерполяция с использованием сплайнов

% Построение графика зависимости радиуса покрытия от AntGain_BS
figure;
plot(AntGain_BS_interp, rBS_values_interp, 'b-', 'LineWidth', 2);  % Плавная кривая
xlabel('Коэффициент усиления антенны BS (dBi)');
ylabel('Радиус покрытия (км)');
title('Зависимость радиуса покрытия от коэффициента усиления антенны BS');
grid on;

% Функция для вычисления MAPL_DL
function MAPL_DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL)
    ThermalNoise = -174 + 10 * log10(BW_DL);  % Тепловой шум в дБм
    RxSens_UE = ThermalNoise + NoiseFigure_UE + SINR_DL;  % Чувствительность приемника в дБм
    MAPL_DL = TxPower_BS - FeederLoss + AntGain_BS + MIMOGain - RxSens_UE - IM - PenetrationM;
end

% Функция для вычисления MAPL_UL
function MAPL_UL = calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL)
    ThermalNoise = -174 + 10 * log10(BW_UL);  % Тепловой шум в дБм
    RxSens_BS = ThermalNoise + NoiseFigure_BS + SINR_UL;  % Чувствительность приемника в дБм
    MAPL_UL = TxPower_UE - FeederLoss + AntGain_BS + MIMOGain - RxSens_BS - IM - PenetrationM;
end

% Модель Okomura-Hata (только DU)
function PL_DU = OkomuraHata(d)
    f_MHz = 1.8e9 / 1e6;  % ГГц в МГц
    d_Km = d / 1e3;  % Переводим из метров в километры
    A = 46.3;
    B = 33.9;
    hBS = 30;
    hms = 1.5;
    Lclutter_du = 3;
    a = 3.2 * ceil(log10(11.75 * hms))^2 - 4.97;
    s = zeros(size(d_Km));
    for i = 1:length(d_Km)
        if d_Km(i) >= 1
            s(i) = 44.9 - 6.55 * log10(f_MHz);
        else
            s(i) = (47.88 + 13.9 * log10(f_MHz) - 13.9 * log10(hBS)) * (1 / log10(50));
        end
    end
    PL_DU = A + B * log10(f_MHz) - 13.82 * log10(hBS) - a + s .* log10(d_Km) + Lclutter_du;
end

% Функция для нахождения пересечения значений
function [distance, value] = findIntersection(values, threshold, distances)
    idx = find(values <= threshold, 1, 'last');
    distance = distances(idx);
    value = values(idx);
end
