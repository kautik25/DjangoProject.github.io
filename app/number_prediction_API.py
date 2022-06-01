import numpy as np
import pandas as pd
from . import functions as fs
from django.conf import settings
import os

def number_prediction(start_date, end_date, num):
    result = {}
    #start_date = request.form.get('start_date')
    #end_date = request.form.get('end_date')
    #num = request.form.get('num')
    predicted_open_close_numbers, predicted_magic_number, accuracy = api_program(start_date, end_date, num)
    predicted_open_close_numbers = np.reshape(predicted_open_close_numbers, (len(predicted_open_close_numbers)//6, 6))
    result = {'Predicted-Open-Close-Numbers': predicted_open_close_numbers.tolist(), 'Predicted-Magic Numbers':predicted_magic_number, 'Accuracy':'{:.2%}'.format(accuracy)}
    #return jsonify(result)
    return result

def api_program(week_start, week_end, num):
    dataset = pd.read_excel((os.path.join(settings.STATIC_ROOT, 'dataset', 'Compelete Statistics for Magic Number Prediction_gdrive.xlsx')), sheet_name='Preprocess Dataset On Excel', engine='openpyxl')
    #dataset = pd.read_excel('/mnt/d/Jeny/Paybills/magic_number_prediction_env/src/magic-number-prediction/Compelete Statistics for Magic Number Prediction_gdrive.xlsx', sheet_name='Preprocess Dataset On Excel', engine='openpyxl')
    dataset.drop(columns= ['Unnamed: 12', 'Calculated Magic Number'], inplace=True)
    dataset.drop(columns= ['Unnamed: 14'], inplace=True)
    dataset.rename(columns={"Unnamed: 11": "Weekday"}, inplace=True)

    jan = dataset[dataset.month == 1].values[:, [1,2,3,4,5,6]]
    fab = dataset[dataset.month == 2].values[:, [1,2,3,4,5,6]]
    mar = dataset[dataset.month == 3].values[:, [1,2,3,4,5,6]]
    apr = dataset[dataset.month == 4].values[:, [1,2,3,4,5,6]]
    may = dataset[dataset.month == 5].values[:, [1,2,3,4,5,6]]
    jun = dataset[dataset.month == 6].values[:, [1,2,3,4,5,6]]
    july = dataset[dataset.month == 7].values[:, [1,2,3,4,5,6]]
    aug = dataset[dataset.month == 8].values[:, [1,2,3,4,5,6]]
    sept = dataset[dataset.month == 9].values[:, [1,2,3,4,5,6]]
    oct = dataset[dataset.month == 10].values[:, [1,2,3,4,5,6]]
    nov = dataset[dataset.month == 11].values[:, [1,2,3,4,5,6]]
    dec = dataset[dataset.month == 12].values[:, [1,2,3,4,5,6]]

    mon = dataset[dataset.weekday == 1].values[:, [1,2,3,4,5,6]]
    tue = dataset[dataset.weekday == 2].values[:, [1,2,3,4,5,6]]
    wed = dataset[dataset.weekday == 3].values[:, [1,2,3,4,5,6]]
    thu = dataset[dataset.weekday == 4].values[:, [1,2,3,4,5,6]]
    fri = dataset[dataset.weekday == 5].values[:, [1,2,3,4,5,6]]
    sat = dataset[dataset.weekday == 6].values[:, [1,2,3,4,5,6]]

    df = dataset.iloc[:,[1,2,3,4,5,6,8,9,10]].values

    all_prob = []
    for i in range(0, 5):
        for j in range(i+1,6):
            all_prob.append(fs.find_correlation(df[:, i], df[:, j]))

    j = 0
    freq_num_by_month = {}
    for i in jan, fab, mar, apr, may, jun, july, aug, sept, oct, nov, dec:
        temp = []
        for k in range(6):
            temp.append(fs.most_frequent_num(i, k))
        j += 1
        freq_num_by_month[j] = temp

    j = 0
    freq_num_by_day = {}
    for i in mon, tue, wed, thu, fri, sat:
        temp = []
        for k in range(6):
            temp.append(fs.most_frequent_num(i, k))
        j += 1
        freq_num_by_day[j] = temp

    actual_numbers = (dataset.iloc[:, [1,2,3,4,5,6]].values).ravel()
    actual_magic_number = (dataset.iloc[:, [7]].values).ravel()

    predicted_num_by_weekday = []
    #all predicted Number by weekday
    for j in range(10):
        try:
            i = 0
            temp = []
            while i <= 2304:
                temp.append(fs.dataframe_converter_weekday(dataset.iloc[i, :][0].date().strftime('%Y-%m-%d'), dataset.iloc[i+5, :][0].date().strftime('%Y-%m-%d'), j, all_prob, freq_num_by_month, freq_num_by_day).iloc[:, [0,1,2,3,4,5]].values.ravel())
                i += 6
            predicted_num_by_weekday.append(np.array(temp))
        except Exception as e:
            pass

    predicted_num_by_month = []
    #all predicted Number by month
    for j in range(10):
        try:
            i = 0
            temp = []
            while i <= 2304:
                temp.append(fs.dataframe_converter_month(dataset.iloc[i, :][0].date().strftime('%Y-%m-%d'), dataset.iloc[i+5, :][0].date().strftime('%Y-%m-%d'), j, all_prob, freq_num_by_month).iloc[:, [0,1,2,3,4,5]].values.ravel())
                i += 6
            predicted_num_by_month.append(np.array(temp))
        except Exception as e:
            pass

    maximum_prob_by_weekday = []

    # num = int(input("Enter Number for predication(high 1 -> low -> 8): "))
    # week_start = input("Enter Week Start Date: ")
    # week_end = input("Enter Week End Date: ")
    maximum_prob_by_weekday = fs.highest_number_probability(num, maximum_prob_by_weekday, predicted_num_by_weekday, dataset)
    predicted_numbers, predicted_magic_number = fs.final_table_data(week_start, week_end, freq_num_by_month, freq_num_by_day, all_prob, maximum_prob_by_weekday, num)
    predicted_numbers = np.reshape(predicted_numbers, len(predicted_numbers)*6)
    print("predicted_numbers.tolist()", predicted_numbers.tolist())
    print("predicted_magic_number", predicted_magic_number)
    print("fs.accuracy(week_start, week_end, dataset, predicted_numbers)", fs.accuracy(week_start, week_end, dataset, predicted_numbers))
    return predicted_numbers.tolist(), predicted_magic_number, fs.accuracy(week_start, week_end, dataset, predicted_numbers)

    