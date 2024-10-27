Farukon работает в нескольких режимах:

флаг -m --mode optimize

Пример:
python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m optimize

Запускает farukon в режиме оптимизации параметров:  "strat_params":{}, "pos_sizer":{}.
Доступны 2 вида оптимизации: полный переобор всех параметров Grid_Search() и генетический алгоритм Genetic_Search(). Через параметр "workers= " передается количество ядер процессора для выполнения оптимизации.
Результаты оптимизации сохраняются в файл .csv в корневой директории программы в папку opt_results. 
По завершении работы генетического алгоритма выводится график обучения.

<img width="562" alt="Снимок экрана 2024-10-26 в 18 58 59" src="https://github.com/user-attachments/assets/95b62a80-93a1-4749-a564-07738e99245e">


флаг -m --mode visual

Пример:
python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m visual
Статистические результаты выполнения сохраняются в файл visual.csv в корневой директории программы. 
Статистика сохраняется в разрезе тестируемых финансовых инструментов + общая аггрегированная статистика. И имеют вид:

<img width="617" alt="Снимок экрана 2024-10-27 в 20 22 19" src="https://github.com/user-attachments/assets/2beea490-b45e-41ee-a50c-de43bab4921f">

Набор показателей, включенных в статистику стратегии реализован в фале performance.py. TODO: добаавить справку по статистическим показателям.

По завершении работы программы выводится шрафик доходности и просадки.

<img width="1220" alt="Снимок экрана 2024-10-27 в 20 37 31" src="https://github.com/user-attachments/assets/347947b4-680d-46ec-9e56-50b0a951b82c">


Флаг -f --folder

Указывается путь к папке с историческими данными по тестируемым инструментам. Для csv файлов необходимо указать формат полей файла:

data_parser_params = {

        "separator": ',',               # Разделитель рядов данных
        "dtformat": "%Y%m%d",           # Формат даты
        "tmformat": "%H%M%S",           # Формат времени
        "headers": 0,                   # Содержат ли наши данные заголовок
        "date": 0,                      # Первый столбец данных = Date
        "time": 1,                      # Второй столбец данных = Time
        "open": 2,                      # Третий столбец данных = Open
        "high": 3,                      # Четветрый столбец данных = High
        "low": 4,                       # Пятый столбец данных = Low
        "close": 5,                     # Шестой столбец данных = Close
        "vol": 6,                       # Седьмой столбец данных
        "oi": -1,                       # Данных по открытому интересу нет в файле
        "timeframe": "min",             # timframe of input data
        "timeframebars": 1
    }


Флаги -t --timeframe и -c --compression

Сжимают свечи в файлах с историческими данными до указанного значения compression + timeframe.

Пример: python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m optimize

сожмут 1 минутные исходные данные (см. data_parser_params выше) до 4х минутного таймфрейма.

Флаг -sm --stats_mode 

Принимаемые значения min и full. Отображение статистических результатов: минимальный или полный наборы.



По завершению работы основного оптимизатора можно запустить вспомогательный скрипт обработки полученных результатов opresults_handler.py:

Пример:
python.exe .\optresults_handler.py -f .\opt_results\SYMI_Ch_SMA_up_5min.csv -d 2D -y set -x mpr -m visual

Флаг -f --file путь к файлу с обрабатываемыми результатами оптимизации

Флаг -m --mode режим visual или select

Режим visual работает одновременно с флагами: 

-d --dimension принимаемыен значения "2D" или "3D"

-x --xaxis значения по оси х

-y --yaxis значение по оси y

Пример: python .\optresults_handler.py -f .\opt_results\Price_Channel_5min.csv -d 2D -y recovery_factor -x mpr -m visual

<img width="555" alt="Снимок экрана 2024-10-27 в 21 08 59" src="https://github.com/user-attachments/assets/1170a61e-3e09-4ff4-9943-212673b2f27b">


Если в качестве значения флага -y --yaxis передать значение "set", то выведется набор показателей, перечисленных в параметре

results_scope = {

    "APR/DD_factor": {"value": 4, "optim": "max"},
    "DD_pcr": {"value": 0.25, "optim": "min"},
    "recovery_factor":  {"value": 5, "optim": "max"},
    "profit_factor": {"value": 2, "optim": "max"},
    "expected_payoff_probability": {"value": 0, "optim": "max"},
    "breakeven_tradeoff": {"value": 0, "optim": "max"},
    "sharp_ratio": {"value": 0.1, "optim": "max"},
    "APR": {"value": 0, "optim": "max"},
    "deals_count": {"value": 12, "optim": "max"},
}


<img width="1218" alt="Снимок экрана 2024-10-27 в 21 14 24" src="https://github.com/user-attachments/assets/e072509b-db73-4a8f-8013-b3b98b96c1cd">


Режим select выбирает такие результаты оптимизации, которые соответсвуют значениям параметра "results_scope" (см. выше). Где параметр "optim" отвечает за направление оптимизации, а параметр "value" за пороговое значение.








