# MarketPlace UC6 app

Contact: [Yoav Nahshon](mailto:yoav.nahshon@iwm.fraunhofer.de), [Pablo de Andres](mailto:pablo.de.andres@iwm.fraunhofer.de)

## Overview

The MatCalc App demonstrates the seamless integration of the MarketPlace project with the [MatCalc](https://www.matcalc.at/) software. Developed with the primary intent to reduce the experimental effort in the development of customized steel powder, this app offers thermodynamic calculations that provide insight into the material forms produced by laser cladding and laser metal deposition techniques. Users can use the MatCalc App for evaluating thermodynamic equilibriums and the dynamics during solidification, all without needing deep knowledge of thermodynamic calculations and MatCalc.

App is developed using [FastAPI](https://fastapi.tiangolo.com/) and [pydantic](https://pydantic-docs.helpmanual.io) for data validation. Refer to MarketPlace [standar-app-api](https://github.com/materials-marketplace/standard-app-api) for more details. 

---
To start the server:

```sh
docker compose up --build
```

## Features

1. Element Selection: Users can choose from alloying elements such as Cr, Mn, Mo, Ni, and Si.

2. Thermodynamic Calculations: After the user defines the weight percentages of C and the chosen alloying element (with Fe as the balance), the app presents the phase fractions of stable phases in equilibrium and their composition based on temperature variations.

3. Result Interpretation: Post solidification, the app presents the resultant phase fractions and phase compositions, vital for understanding microstructure evolution during further cooling.

## Endpoints:

### Health Check:
```http
GET /health: Check the application status.
```
### Transformations:
```http
POST /transformations

GET /transformations/{transformation_id}

PATCH /transformations/{transformation_id}

GET /transformations/{transformation_id}/state

GET /transformations

DELETE /transformations/{transformation_id}
```
### Results:
```http
GET /results
```

An equivalent [OpenAPI](https://www.openapis.org/) representation in the [openapi.yml](https://github.com/materials-marketplace/uc6-app/blob/main/openapi.yml) file. 

