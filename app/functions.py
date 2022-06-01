import numpy as np
import pandas as pd

def most_frequent_num(dataset, column_number):
  '''
    Returns the list of most frequent number in perticular column number within dataset

    parameter:
      dataset => simple dataset with np.values
      column_number => In perticular dataset column number 
  '''
  freq_num = []
  for i in np.sort(np.unique(dataset[:, column_number], return_counts=True)[1])[::-1]:
    freq_num.append(np.unique(dataset[:, column_number])[np.where(np.unique(dataset[:, column_number], return_counts=True)[1] == i)[0][0]]) # for appending value in list
  return freq_num

def find_correlation(column_1, column_2):
  '''
    Returns dictionary of higher probably number with respect to all colums (in order 1, 2, ...) from actual dataset

    Parameters:
      column_1 => with respect to this we find the occurances of column_2
      column_2 => for finding occurances with respect to column_1
  '''
  zero = []
  one = []
  two = []
  three = []
  four = []
  five = []
  six = []
  seven = []
  eight = []
  nine = []
  j = 0
  for i in column_2:
    if column_1[j] == 0:
      zero.append(i)
    elif column_1[j] == 1:
      one.append(i)
    elif column_1[j] == 2:
      two.append(i)
    elif column_1[j] == 3:
      three.append(i)
    elif column_1[j] == 4:
      four.append(i)
    elif column_1[j] == 5:
      five.append(i)
    elif column_1[j] == 6:
      six.append(i)
    elif column_1[j] == 7:
      seven.append(i)
    elif column_1[j] == 8:
      eight.append(i)
    elif column_1[j] == 9:
      nine.append(i)
    j += 1

  disc = {}
  j = -1
  #print("For ", dataset.columns[1],"the most probabily value for ", dataset.columns[4]," ===> ")
  for i in zero, one, two, three, four, five, six, seven, eight, nine:
    temp = []
    prob = []
    j += 1
    if len(i) == 0:
        continue
    for k in range(0, len(np.unique(i, return_counts=True)[1])):
      individual_prob = (np.unique(i, return_counts=True)[1][k]/np.unique(i, return_counts=True)[1].sum())*100
      prob.append(individual_prob)
    # print(j, ' ==> ', np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.max(np.unique(i, return_counts=True)[1]))[0]], ' ==> Probabilty: ', np.max(prob))
    for l in np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.max(np.unique(i, return_counts=True)[1]))[0]]:
      temp.append(l)
    if len(np.unique(i)) == 1:
      disc[j] = temp
      # print('---------------------------------------------------')
      continue
    if np.max(prob) != np.sort(prob)[-2]:
        # print("       ", np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.sort(np.unique(i, return_counts=True)[1])[-2])[0]], ' ==> Probability: ', np.sort(prob)[-2])
        for l in np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.sort(np.unique(i, return_counts=True)[1])[-2])[0]]:
          temp.append(l)
    if len(np.unique(i)) == 2:
      disc[j] = temp
      # print('---------------------------------------------------')
      continue
    if np.sort(prob)[-2] == np.sort(prob)[-3]:
      disc[j] = temp
      # print('---------------------------------------------------')
      continue
    # print("       ", np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.sort(np.unique(i, return_counts=True)[1])[-3])[0]], ' ==> Probability: ', np.sort(prob)[-3])
    for l in np.unique(i)[np.where(np.unique(i, return_counts=True)[1] == np.sort(np.unique(i, return_counts=True)[1])[-3])[0]]:
      temp.append(l)
    disc[j] = temp
    # print('---------------------------------------------------')
  return disc

def prediction_set_for_column_by_weekday(start_date, end_date, number, column_num, freq_num_by_month, freq_num_by_day):
  '''
    Returns the list of numbers by probability by given number within date range for week day

    Parameter:
      start_date => starting date in string format or datetime.time format
      end_date => starting date in string format or datetime.time format
      number => It is number by which we get that probabilty number from perticular column
      column_num => it's column number in dataset
      freq_num_by_month => it's dictionary type data which has all frequent number by column wise in all months
      freq_num_by_day => it's dictionary type data which has all frequent number by column wise in all weekdays
  '''
  predictions_open_num_1_by_weekday = []
  for i in pd.date_range(start_date, end_date, freq='D').date:
    if int(i.strftime('%w')) != 0:
      if number < len(freq_num_by_month[int(i.strftime('%w'))][column_num]):
        temp = []
        temp.append(freq_num_by_day[int(i.strftime('%w'))][column_num][number])
        predictions_open_num_1_by_weekday.append(temp[0])
      else:
        return False
  return predictions_open_num_1_by_weekday

def prediction_set_for_column_by_month(start_date, end_date, number, column_num, freq_num_by_month):
  '''
    Returns the list of numbers by probability by given number within date range for month

    Parameter:
      start_date => starting date in string format or datetime.time format
      end_date => starting date in string format or datetime.time format
      number => It is number by which we get that probabilty number from perticular column
      column_num => it's column number in dataset
      freq_num_by_month => it's dictionary type data which has all frequent number by column wise in all months
      freq_num_by_day => it's dictionary type data which has all frequent number by column wise in all weekdays
  '''
  predictions_open_num_1_by_month = []
  for i in pd.date_range(start_date, end_date, freq='D').date:
    if int(i.strftime('%w')) != 0:
      if number < len(freq_num_by_month[int(i.strftime('%m'))][column_num]):
        temp = []
        temp.append(freq_num_by_month[int(i.strftime('%m'))][column_num][number])
        predictions_open_num_1_by_month.append(temp[0])
      else:
        return False
  return predictions_open_num_1_by_month

def open_close_number_finder(list, all_prob):
  '''
    Returns open and close numbers with respect to open num 1 column's number

    Perameters:
      list => represent the open_num_1 column numbers
      all_prob => it's list of dictionaries type which has all highest probably values of all numbers with all columns    
  '''
  if list != 0:
    n = 0
    magic_number_parts = []
    for i in list:
      magic_number_parts.append(i)
      for j in range(0, 5):
        magic_number_parts.append(all_prob[j][i][0])
      n += 1
    return magic_number_parts
  return False

def dataframe_converter_weekday(week_start, week_end, n, all_prob, freq_num_by_month, freq_num_by_day):
  '''
    Returns the dataframe with number selected by user for weekdays

    Perameters:
      week_start => starting date has type datetime.date or string inn format(YYYY-MM-DD)
      end_start => ending date has type datetime.date or string inn format(YYYY-MM-DD)
      number => will be selected by user and based on that dataframe will prepare
      all_prob => it's list of dictionaries type which has all highest probably values of all numbers with all columns
      freq_num_by_month => it's dictionary type data which has all frequent number by column wise in all months
      freq_num_by_day => it's dictionary type data which has all frequent number by column wise in all weekdays
  '''
  x = open_close_number_finder(prediction_set_for_column_by_weekday(week_start, week_end, n, 0, freq_num_by_month, freq_num_by_day), all_prob)
  temp_weekday = pd.DataFrame(np.reshape(x, (int(len(x)/6), 6)), columns=['open_num_1', 'open_num_2', 'open_num_3', 'close_num_1', 'close_num_2', 'close_num_3'])
  temp_weekday['magic_number'] = (magic_number_finder(x))
  temp = []
  for i in pd.date_range(week_start, week_end, freq='d').date:
    if int(i.strftime('%w')) != 0:
      temp.append(i)
  temp_weekday.index = temp
  return temp_weekday

def dataframe_converter_month(week_start, week_end, n, all_prob, freq_num_by_month):
  '''
    Returns the dataframe with number selected by user for months

    Perameters:
      week_start => starting date has type datetime.date or string inn format(YYYY-MM-DD)
      end_start => ending date has type datetime.date or string inn format(YYYY-MM-DD)
      number => will be selected by user and based on that dataframe will prepare
      all_prob => it's list of dictionaries type which has all highest probably values of all numbers with all columns
      freq_num_by_month => it's dictionary type data which has all frequent number by column wise in all months
      freq_num_by_day => it's dictionary type data which has all frequent number by column wise in all weekdays
  '''
  # st.write("By", n+1, "most frequent number ==>")
  x = open_close_number_finder(prediction_set_for_column_by_month(week_start, week_end, n, 0, freq_num_by_month), all_prob)
  temp_month = pd.DataFrame(np.reshape(x, (int(len(x)/6), 6)), columns=['open_num_1', 'open_num_2', 'open_num_3', 'close_num_1', 'close_num_2', 'close_num_3'])
  temp_month['magic_number'] = magic_number_finder(open_close_number_finder(prediction_set_for_column_by_month(week_start, week_end, n, 0, freq_num_by_month), all_prob))
  temp = []
  for i in pd.date_range(week_start, week_end, freq='d').date:
    if int(i.strftime('%w')) != 0:
      temp.append(i)
  temp_month.index = temp
  return temp_month

def magic_number_finder(list):
  '''
    Returns the list of magic numbers calculated by equation

    Parameter:
      list = list having open and close number of columns
  '''
  if len(list) != 0:
    j = 1
    magic_number = []
    magic_number_part_1 = 0
    magic_number_part_2 = 0
    for i in list:
      if j <= 3:
        magic_number_part_1 += i
      else:
        magic_number_part_2 += i
      if j == 6:
        magic_number.append(int(str(magic_number_part_1 % 10) + str(magic_number_part_2 % 10)))
        magic_number_part_1 = 0
        magic_number_part_2 = 0
        j = 0 
      j += 1
    return magic_number
  return False

def final_table_data(week_start, week_end, freq_num_by_month, freq_num_by_day, all_prob, maximum_prob_by_weekday, num):  
  '''
    Returns the list of open_close numbers and magic numbers in given date range

    Parameters:
      start_date => starting date in string format or datetime.time format
      end_date => starting date in string format or datetime.time format
      freq_num_by_month => it's dictionary type data which has all frequent number by column wise in all months
      freq_num_by_day => it's dictionary type data which has all frequent number by column wise in all weekdays
      all_prob => it's list of dictionaries type which has all highest probably values of all numbers with all columns
      maximum_prob_by_weekday => list of higher probably numbers in ascending order
  '''
  j = 0
  temp_list_predicated_num_weekday = []
  temp_list_predicated_magic_num_weekday = []
  for i in pd.date_range(week_start, week_end).date:
    if i.weekday() == 6 or j == 6:
      j = 0
    else:
      open_num_1_by_weekday = prediction_set_for_column_by_weekday(i, i, maximum_prob_by_weekday[j], 0, freq_num_by_month, freq_num_by_day)
      magic_number_parts_by_weekday = open_close_number_finder(open_num_1_by_weekday, all_prob)
      temp_list_predicated_num_weekday.append(magic_number_parts_by_weekday)
      magic_numbers = magic_number_finder(magic_number_parts_by_weekday)
      temp_list_predicated_magic_num_weekday.append(magic_numbers)
      j+=1
  return temp_list_predicated_num_weekday, temp_list_predicated_magic_num_weekday

def accuracy_by_weekday(predicted_num, weekday_number, dataset):
  '''
    Returns list having accuracy by given number for predicated_num by weekday

    Parameters:
      predicted_num => 2d list having predicated numbers by weekday
      weekday_number => week day numebr
      dataset => actual dataset
  '''
  temp = []
  for n1 in range(len(predicted_num)):
    actual_weekday_num = dataset[dataset.weekday == weekday_number].iloc[:, [1,2,3,4,5,6]].values.ravel()
    predicted_weekday_num = by_weekday_record(weekday_number, predicted_num[n1], len(dataset)).reshape(actual_weekday_num.shape)
    temp.append(accuracy_magic_number(actual_weekday_num, predicted_weekday_num))
  return temp

def by_weekday_record(starting_index, num_list, len_dataset):
  '''
    Return np array(list) of given starting_index(weekday number)

    Parameters:
      starting_index => weekday number (mon = 0, tue = 1, etc.)
      num_list => list of numbers
      len_dataset => length of dataset
  '''
  x = num_list.reshape(len_dataset, 6)
  y = []
  starting_index = starting_index - 1
  while starting_index < len(x):
    y.append(x[starting_index])
    starting_index += 6
  return np.array(y)

def accuracy_magic_number(actual_magic_number, predicted_magic_number):
  '''
    Returns the accuracy of predicted and actual magic number for both open-close-numbers and magic number 

    Perameters:
      actual_magic_number => list that has actual numbers
      predicted_magic_number => list that has predicted numbers
  '''
  if len(predicted_magic_number) != 0:
    if len(actual_magic_number) != 0:
      count = 0
      j = 0
      for i in actual_magic_number:
        if i == predicted_magic_number[j]:
          count += 1
        j += 1
      return (count / len(predicted_magic_number))
  return False

def accuracy(week_start, week_end, dataset, predicted_magic_number):
  '''
    Returns the accuracy of predicted and actual open clsoe numbers by given date range

    Perameters:
      week_start => starting date has type datetime.date or string inn format(YYYY-MM-DD)
      end_start => ending date has type datetime.date or string inn format(YYYY-MM-DD)
      dataset => actual dataset from where it finds the actual magic numbers for calculate accuracy
      predicted_magic_number => list that has predicted numbers
  '''
  if len(predicted_magic_number) != 0:
    actual_magic_number = dataset[(dataset.Date >= str(week_start)) & (dataset.Date <= str(week_end))].iloc[:, [1,2,3,4,5,6]].values.ravel()
    if len(actual_magic_number) != 0:
      count = 0
      j = 0
      for i in actual_magic_number:
        if i == predicted_magic_number[j]:
          count += 1
        j += 1
      return (count / len(predicted_magic_number))
  return False

#maximum accuracy number in overall accuracy by weekdays
def highest_number_probability(num, maximum_prob_by_weekday, predicted_num_by_weekday, dataset):
    '''
    Will appends the number of num's of every week day 

    Parameters: 
        num => number that user wants to predict
        maximum_prob_by_weekday =>
        predicted_num_by_weekday =>
        dataset => actual database object
    '''
    for i in range(1, 7):  
        temp = accuracy_by_weekday(predicted_num_by_weekday, i, dataset)
        # for maximum probabilty number
        try:
            maximum_prob_by_weekday.append(int(np.where(temp == np.sort(temp)[-int(num)])[0][0])) # here we have to select number for highest probably
        except:
            print('Number Not Exist')
    return maximum_prob_by_weekday

