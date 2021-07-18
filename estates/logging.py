

# Open a file with access mode 'a'
file_object = open('errors.log', 'a')

# Append 'hello' at the end of file
file_object.write('hello')
# Close the file
file_object.close()