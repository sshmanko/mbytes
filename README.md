This is a demo app for COVID-19 cases statistics per country.

It uses 2 free APIs:
https://ipwhois.io/ - For country autodetection by IP address
https://covid19api.com/ - For data per country statistics

# Installation

1. Clone the repo:

    ```git clone https://github.com/sshmanko/mbytes; cd mbytes```

2. Build application docker image:

    ```docker build --tag mbytes/app:latest .```

3. Run the  container:

    ```docker run -p 5000:5000 mbytes/app```

4. Application should be available at http://localhost:5000/


Live demo of the app: http://covid.pingtool.org

o7
