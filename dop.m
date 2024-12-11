% Параметры
TxPower_UE = 24;  % Мощность передатчика UE в дБм
TxPower_BS = 46;  % Мощность передатчика BS в дБм
FeederLoss = 2;   % Потери в фидере в дБ
AntGain_BS = 21;  % Коэффициент усиления антенны BS в дБи
MIMOGain = 3;     % Выигрыш от MIMO в дБ
IM = 1;           % Запас мощности на интерференцию в дБ
PenetrationM = 15; % Запас мощности на проникновение в дБ
BW_UL = 10e6;     % Полоса частот для UL (10 МГц)
BW_DL = 20e6;     % Полоса частот для DL (20 МГц)
NoiseFigure_BS = 2.4;  % Коэффициент шума приемника BS в дБ
NoiseFigure_UE = 9;    % Коэффициент шума приемника UE в дБ
SINR_UL = 4;          % Требуемое отношение SINR для UL в дБ
SINR_DL = 2;          % Требуемое отношение SINR для DL в дБ

% Вычисляем MAPL для DL и UL
UL = calculate_MAPL_UL(TxPower_UE, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_UL, NoiseFigure_BS, SINR_UL);
DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL);

fprintf('Пороговое значение DownLink: %.2f\n', DL);
fprintf('Пороговое значение UpLink: %.2f\n', UL);

MAX_LEVEL = min(DL, UL);
MAX_LEVEL_2 = max(DL, UL);

DISTANCE_KM = linspace(0.01, 100, 1000);  % Диапазон от 0.01 до 100 км

% Расчет потерь по модели Okomura-Hata (только DU)
PL_DU = OkomuraHata(DISTANCE_KM * 1e3);  % Мы оставляем только PL_DU

% Находим пересечения для различных уровней потерь
[Hata_DU_1x, Hata_DU_1y] = findIntersection(PL_DU, MAX_LEVEL, DISTANCE_KM);
[Hata_DU_2x, Hata_DU_2y] = findIntersection(PL_DU, MAX_LEVEL_2, DISTANCE_KM);

% График для Hata (только DU)
figure;
plot(DISTANCE_KM, DL * ones(size(DISTANCE_KM)), 'y--', 'LineWidth', 1); % линия для DL
hold on;
plot(DISTANCE_KM, UL * ones(size(DISTANCE_KM)), 'g--', 'LineWidth', 1); % линия для UL
plot(DISTANCE_KM, PL_DU, 'b-', 'LineWidth', 1.5);

% Вертикальные линии для пересечений
line([Hata_DU_1x Hata_DU_1x], ylim, 'Color', 'k', 'LineStyle', ':', 'LineWidth', 1.5); % вертикальная линия для PL_DU
line([Hata_DU_2x Hata_DU_2x], ylim, 'Color', 'k', 'LineStyle', ':', 'LineWidth', 1.5); % вертикальная линия для PL_DU

% Подписываем значения на вертикальных линиях
text(Hata_DU_1x, Hata_DU_1y, sprintf('%.2f km', Hata_DU_1x), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'black', 'FontSize', 10);
text(Hata_DU_2x, Hata_DU_2y, sprintf('%.2f km', Hata_DU_2x), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'black', 'FontSize', 10);

xlabel('Расстояние, км');
ylabel('Потеря сигнала, dB');
title('Зависимость потерь радиосигнала от расстояния (Hata, DU)');
grid on;
legend({'DL', 'UL', 'Hata (Macrocells)'}); % Убираем ссылку на PL_U в легенде

% Вычисление радиуса и количества базовых станций для покрытия
area = 100;  % площадь в кв.км
rBS_1 = min(Hata_DU_1x, Hata_DU_2x);
fprintf('Радиус базовой станции для 100 кв.км: %.2f км\n', rBS_1);
sBS_1 = 1.95 * (rBS_1 ^ 2);
fprintf('Площадь базовой станции кв.км: %.2f\n', sBS_1);
fprintf('Требуемое количество для покрытия: %d\n', ceil(area / sBS_1));

% Функции

% Функция для расчета MAPL_DL
function MAPL_DL = calculate_MAPL_DL(TxPower_BS, FeederLoss, AntGain_BS, MIMOGain, IM, PenetrationM, BW_DL, NoiseFigure_UE, SINR_DL)
    ThermalNoise = -174 + 10 * log10(BW_DL);  % Тепловой шум в дБм
    RxSens_UE = ThermalNoise + NoiseFigure_UE + SINR_DL;  % Чувствительность приемника в дБм
    MAPL_DL = TxPower_BS - FeederLoss + AntGain_BS + MIMOGain - RxSens_UE - IM - PenetrationM;
end

% Функция для расчета MAPL_UL
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
