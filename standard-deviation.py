# Import statistics Library
import statistics 

# Get a list of numbers from the user
i = 0
nums = []
print("Enter the numbers that you want to calculate ")

while i != "x":
    i = input()
    if i != "x":
        i = int(i)
        nums.append(i)
    
# print(nums)



# Calculate the standard deviation of the data, from library
print(statistics.stdev(nums))
