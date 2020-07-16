FROM python:3.8.2-buster

ENV FLASK_ENV development
ENV FLASK_DEBUG 1
ENV FLASK_APP aergia.py

EXPOSE 5000

WORKDIR /app
RUN pip install pipenv

# Install runtime and development dependencies
COPY Pipfile* ./
RUN pipenv install

# Copy the project files
COPY . .

CMD ["pipenv", "run", "flask", "run", "--host", "0.0.0.0"]


