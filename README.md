# Smart Parking Lot — Backend API

FastAPI backend for the Smart Parking Lot system (Group 7 - CMP6210).

---

## 1. Run locally (for frontend development)

Uses SQLite — no database server needed.

**Requirements:** Python 3.10+

```bash
git clone https://github.com/your-org/smart-parking-lot-backend.git
cd smart-parking-lot-backend

pip install -r requirements.txt
```

Create a `.env` file:

```
USE_SQLITE=true
SECRET_KEY=any_random_string
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API is running at `http://localhost:8000`

On first startup, tables are created automatically in a local `test.db` file.

### API docs

Open `http://localhost:8000/docs` in your browser.

To test protected endpoints:
1. Call `POST /users/register` to create an account
2. Call `POST /users/login` to get a token
3. Click **Authorize** (top right), paste the token, confirm
4. All protected routes now work in the UI

---

## 2. Deploy to EC2 + RDS

**Prerequisites:**
- EC2 instance (Amazon Linux 2 or Ubuntu)
- RDS MySQL instance with a database created (e.g. `parking_db`)
- EC2 security group: inbound port 22 (SSH) and 8000 (API)
- RDS security group: inbound port 3306 from the EC2 instance

### Connect and set up

```bash
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

sudo yum update -y
sudo yum install python3 python3-pip git -y

git clone https://github.com/your-org/smart-parking-lot-backend.git
cd smart-parking-lot-backend
pip3 install -r requirements.txt
```

### Configure environment

```bash
nano .env
```

```
DB_HOST=<RDS endpoint>
DB_PORT=3306
DB_NAME=parking_db
DB_USER=admin
DB_PASSWORD=<your password>
SECRET_KEY=<a long random string>
USE_SQLITE=false
```

### Apply schema to RDS (first deploy only)

Run from EC2 (requires `mysql` client) or from your local machine:

```bash
mysql -h <RDS endpoint> -u admin -p parking_db < schema.sql
```

### Start the API

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

API is running at `http://<EC2_PUBLIC_IP>:8000`

### Update the app

```bash
cd smart-parking-lot-backend
git pull
pkill -f uvicorn
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```
