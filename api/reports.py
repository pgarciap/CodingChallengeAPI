import json
import psycopg2

# create a connection in posgrest by psycopg2
def connectionPsycopg2():
     try:
        conn = psycopg2.connect(database="company_pg", user="postgres_user_pg", password="postgres_pwd_pg", host="localhost", port=5432)
     except Exception as error:
         return "Something went wrong when creating the Psycopg2 connection. "+"An exception occurred:" + type(error).__name__

# get report employees hired by Job and Department
def getReportEmployeesHiredByJobAndDepartment(conn, strYear):
    try:
        query = """
            with hired_emp as(
            select department_id,
                job_id,
                DATE(datetime) as date_he
                from hired_employees_test
            ),groupByDepAndJob as(
                select he.department_id,
                he.job_id,
                d.department as department,
                j.job as job
                from hired_employees_test as he
                left join departments as d on d.id = he.department_id
                left join jobs as j on j.id = he.job_id
                where department_id is not null and job_id is not null
                group by 1,2,3,4
                order by department asc,job asc
            ),filterQ1 as (
                select department_id,job_id,count(*) as Q1
                        from hired_emp
                        where date_he between '%s-01-01' and '%s-03-31'
                        group by 1,2
            ),filterQ2 as (
                    select department_id,job_id,count(*) as Q2
                        from hired_emp
                        where date_he between '%s-04-01' and '%s-06-30'
                        group by 1,2
            ),filterQ3 as (
                    select department_id,job_id,count(*) as Q3
                        from hired_emp
                        where date_he between '%s-07-01' and '%s-09-30'
                        group by 1,2
            ),filterQ4 as (
                    select department_id,job_id,count(*) as Q4
                        from hired_emp
                        where date_he between '%s-10-01' and '%s-12-31'
                        group by 1,2
            )
            select 
                gdj.department,
                gdj.job,
                filterQ1.Q1,
                filterQ2.Q2,
                filterQ3.Q3,
                filterQ4.Q4
                from groupByDepAndJob as gdj
                left join filterQ1 on filterQ1.department_id = gdj.department_id and filterQ1.job_id = gdj.job_id
                left join filterQ2 on filterQ2.department_id = gdj.department_id and filterQ2.job_id = gdj.job_id
                left join filterQ3 on filterQ3.department_id = gdj.department_id and filterQ3.job_id = gdj.job_id
                left join filterQ4 on filterQ4.department_id = gdj.department_id and filterQ4.job_id = gdj.job_id
                where  not(filterQ1.Q1 is null and filterQ2.Q2 is null and filterQ3.Q3 is null and filterQ4.Q4 is null)
            """

        if strYear is not None:
            params = (strYear,strYear,strYear,strYear,strYear,strYear,strYear,strYear,)
        else:
            params = ()

        cur = conn.cursor()
        cur.execute(query, params)

        metrics = []
        for row in cur:
            metrics.append({
            "department": row[0],
            "job": row[1],
            "q1": row[2],
            "q2": row[3],
            "q3": row[4],
            "q4": row[5]
            })
        return metrics
    except Exception as error:
         return "Something went wrong when creating the Psycopg2 connection. "+"An exception occurred:" + type(error).__name__
    


