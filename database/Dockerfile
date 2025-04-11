FROM postgres:13
ENV POSTGRES_DB=ferme
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=secret
COPY init.sql /docker-entrypoint-initdb.d/
