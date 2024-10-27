Farukon работает в нескольких режимах:

флаг -m --mode optimize
python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m optimize

Запускает farukon в режиме оптимизации параметров:  "strat_params":{}, "pos_sizer":{}.
Доступны 2 вида оптимизации: полный переобор всех параметров Grid_Search() и генетический алгоритм Genetic_Search().
Результаты оптимизации сохраняются в файл в директории программы в папку opt_results. 
По завершении работы генетического алгоритма выводится график обучения.

<img width="562" alt="Снимок экрана 2024-10-26 в 18 58 59" src="https://github.com/user-attachments/assets/95b62a80-93a1-4749-a564-07738e99245e">
