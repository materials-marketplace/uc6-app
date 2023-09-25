FROM matcalctuw/matcalc:6.04

RUN apt update \
    && apt install -y --no-install-recommends \
    python3 python3-pip xz-utils

WORKDIR /root/app
RUN mkdir simulation_files
ADD models ./models
ADD simulation_controller ./simulation_controller
ADD app.py .
ADD setup.cfg .
ADD setup.py .
RUN python3 -m pip install .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
