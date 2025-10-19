# fastapi-secrets-backend

## Prerequisites
- In order to test the tokens, an enviroment variables file (.env) must be created in the root of this backend repo
- In env should contain a line with a SHARED_KEY. An example is: SHARED_KEY=ASDF12345QWERTY1234
- Alternatively in Mac or linux if you are in this folder you can write into the .env from the command line using echo "SECRET_KEY=ADSDFQWERTY123456" > .env

## Running instructions
- Run:
    - docker compose up --build
- The backend will then be active on port 8000



