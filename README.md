# CodingChallengeAPI

### Clone repository

First at all, we need to clone the repository with the following code:
```
git clone https://github.com/pgarciap/CodingChallengeAPI.git
```
### Docker-compose
#### Prerequisites
You need to have Docker Engine and Docker Compose on your machine. You can either:
  - Install Docker Engine and Docker Compose as standalone binaries
  - Install Docker Desktop which includes both Docker Engine and Docker Compose
    
From Coding challenge API project directory, start up your application by running:
```
docker-compose build
```
and then
```
docker-compose up
```

### Test

Open pgAdmin
```
http://localhost/
```
select register -> server, in the cconnection tab you have to write the information that appear in database.env

create the following tables:
```
CREATE TABLE IF NOT EXISTS departments(
	id int PRIMARY KEY NOT NULL,
	department text NOT NULL,
	last_update timestamp
);
```
```
CREATE TABLE IF NOT EXISTS jobs(
	id int PRIMARY KEY NOT NULL,
	job text NOT NULL,
	last_update timestamp
);
```

```
CREATE TABLE IF NOT EXISTS hired_employees(
	id int PRIMARY KEY NOT NULL,
	name text,
	datetime text,
	department_id int references departments,
	job_id int references jobs,
	last_update timestamp
);
```

# Receive historical data from CSV files and Upload these files to the new DB, and upload the file in S3
```
POST: http://127.0.0.1:80/files
```
Body: Json

Test for departments
```
{
        "file":"\departments.csv"
}
```

Test for jobs
```
{
        "file":"\jobs.csv"
}
```

Test for hired_employees
```
{
        "file":"\hired_employees.csv"
}
```

#### Receives a batch of transactions and inserts them into the database.
```
POST: http://127.0.0.1:80/transactions/batch?tablename=jobs
```
Body: Json

Test for jobs
```
{
        "transactions": [
            {
                "id": 1,
                "job": Marketing Assistant
            },
            {
                "id": 2,
                "job": VP Sales
            }
        ]
}
```

Test for departments
```
POST: http://127.0.0.1:80/transactions/batch?tablename=departments
```
Body: Json

```
{
        "transactions": [
            {
                "id": 1,
                "department": Product Management
            },
            {
                "id": 2,
                "department": Sales
            }
        ]
}
```

Test for hired_employees
```
POST: http://127.0.0.1:80/transactions/batch?tablename=hired_employees
```
Body: Json

```
{
        "transactions": [
            {
                "id": 1,
                "name": "Harold",
                "datetime": "2021-11-07T02:48:42Z",
                "department_id": 1,
                "job_id": 2
            },
            {
                "id": 2,
                "name": "Ty Hofer",
                "datetime": "2021-05-30T05:43:46Z",
                "department_id": 2,
		        "job_id": 2
            }
        ]
}

```

#### get employees hired by job and department
```
GET: http://172.21.0.3:80/employees_hired/by-job-and-department?year=2021
```

### get employees hired by department
```
GET: http://127.0.0.1:80/employees_hired/by-department?year=2021
```

