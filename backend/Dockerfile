FROM python:3.8-buster

EXPOSE 8000

WORKDIR /etikedi
RUN pip install pipenv
COPY Pipfile* ./

# Install runtime and development dependencies
RUN pipenv install --system

# Copy the project files
COPY . ./backend/

CMD ["python", "-u", "-m", "backend"]