from flask import Flask, render_template, url_for, request, g
import sqlite3
import os
app = Flask(__name__)

#grab the current directory for locating (or creating) the database
directory = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():

    #take array from html input form
    array = request.form['num_array']

    #find the longest range
    longest_range = find_range(array)

    #connect to the db, connect() creates it if it doesn't exist, create cursor for accessing data
    connection = sqlite3.connect(directory + "/array_history.db")
    cursor = connection.cursor()

    #create history table if it doesn't exist already
    query = "CREATE TABLE IF NOT EXISTS history (ID INTEGER NOT NULL PRIMARY KEY, input TEXT, output TEXT)"
    cursor.execute(query)

    #insert input array and range into database
    query = "INSERT INTO history VALUES(NULL, '{arr}', '{range}')".format(arr = array, range = longest_range)
    cursor.execute(query)
    connection.commit()

    #return the results page, passing the input array and range into html via Jinja template
    return render_template('result.html', num_array=array, longest_range_array=longest_range)

@app.route('/history', methods=['GET'])
def history():

    #make sure the database exists using try except
    #if it does then grab all the data from the db and pass into html
    try:
        connection = sqlite3.connect(directory + "/array_history.db")
        cursor = connection.cursor()
        query = "SELECT * FROM history"
        cursor.execute(query)
        result = cursor.fetchall()
        return render_template('history.html', result=result)

    #if it doesn't then pass nothing so the Jinja if-else in history.html falls to else 
    except:
        return render_template('history.html')
    

def find_range(num_array):

    #this function does not validate for proper input, as stated in the coding challenge specification
    #you will get an error code 500 if you input anything besides integers separated by commas (with no trailing comma)

    #if the input results in >1 ranges having the same longest length, it will return the one earliest in the sorted array
    #if you only input one number, the longest range will be the range between that number and that number

    #appropriately reformat the array so it is an array of ints and not a string
    num_array = num_array.split(',')
    num_array = [int(x) for x in num_array]

    #sort the array
    #we will simply do one pass through the array making this O(n log n) complexity because of sort
    num_array.sort()

    #define (temp) variables
    #counters for counting the current range length, as well as the highest reported range length
    counter = 0
    highest_counter = 0

    #bounds for the current range, these are indices in the sorted array
    lower = 0
    higher = 0

    #bounds for storing the indices of the longest reported range
    longest_range_lower = 0
    longest_range_higher = 0

    #start iterating through the array from index 1
    for i,num in enumerate(num_array[1:], start=1):

        #if the currently inspected number is exactly +1 more than the preceeding number in the array
        if num == num_array[i-1] + 1:

            #move the temp higher bound marker one along the array
            higher = i

            #increment the temp counter used for determining the length of the current range
            counter+=1

            #if we reach the end of the array and the current range hasn't been broken
            #and it is longer than the previous longest range
            if (i == len(num_array)-1 and counter > highest_counter):

                #set the longest range bounds appropriately
                longest_range_lower = lower
                longest_range_higher = higher

        #if the currently inspected number is not exactly +1 more than the preceeding number in the array
        else:

            #if this was the longest range then set the longest range bounds appropriately
            if counter > highest_counter:
                longest_range_lower = lower
                longest_range_higher = higher

                #set the highest counter variable to the current counter value
                #to determine the length of the new longest range
                highest_counter = counter

            #set the lower bound to the higher bound, ready to start counting again from the current position
            #reset the counter
            lower = i
            higher = i
            counter = 0

    #format the answer to a string that looks like an array with two ints in it
    answer = "[" + str(num_array[longest_range_lower]) + ", " + str(num_array[longest_range_higher]) + "]"
    return(answer)

if __name__ == "__main__":
    app.run(debug=True)