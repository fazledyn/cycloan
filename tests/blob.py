import cx_Oracle as ora
import io


connection = ora.connect("HR", "password", "localhost/orcl", encoding="UTF-8")
cursor = connection.cursor()

sql = "SELECT * FROM HR.TEST"
filename = 'File1'
cursor.execute(sql)
result = cursor.fetchall()

print(result)

file_byte = result[0][1]
file = file_byte.read()

img_file = open('img.jpg', 'w')
img_file.write(str(file))



print(file)

connection.close()
print("Exit")


