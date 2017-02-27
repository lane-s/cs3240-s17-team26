import csv
import psycopg2

PG_USER = "lspangler"
PG_USER_PASS = ""
PG_HOST_INFO = ""
#It's a comment


def load_course_database(db_name, csv_filename):
    conn = psycopg2.connect("dbname=" + db_name + " user=" + PG_USER + " password=" + PG_USER_PASS + PG_HOST_INFO)

    cur = conn.cursor()


    with open(csv_filename, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            cur.execute("INSERT INTO coursedata (deptid,coursenum,semester,meetingtype,seatstaken,seatsoffered,instructor) VALUES (%s,%s,%s,%s,%s,%s,%s)", (row[0],row[1],row[2],row[3],row[4],row[5],row[6],))

    conn.commit()
    cur.close()
    conn.close()


load_course_database("course1","seas-courses-5years.csv")




