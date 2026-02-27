FROM python:3.10-slim

# 1. Sistem Bağımlılıkları (Java Spark için zorunludur)
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    procps \
    curl \
    && apt-get clean

WORKDIR /app

# 2. Spark JAR Bağımlılıkları (Postgres + S3/MinIO Support)
# PostgreSQL JDBC Driver
ADD https://jdbc.postgresql.org/download/postgresql-42.7.2.jar /opt/spark/jars/postgresql.jar

# Hadoop AWS Connector (S3 protokolü için)
RUN curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    mv hadoop-aws-3.3.4.jar /opt/spark/jars/hadoop-aws.jar

# AWS Java SDK Bundle (Hadoop AWS için gerekli bağımlılık)
RUN curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    mv aws-java-sdk-bundle-1.12.262.jar /opt/spark/jars/aws-sdk.jar

# 3. Python Bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Uygulama Kodları
COPY . .

# Log dosyaları için yetkilendirme (İsteğe bağlı)
RUN touch info.log error.log && chmod 666 info.log error.log

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]