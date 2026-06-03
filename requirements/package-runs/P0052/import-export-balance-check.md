# P0052 import/export balance check

Balance residual fields are stored as `production + import - consumption - export` where P0051 physical rows join. Residuals are diagnostic only because SvK/Statnett flow/import-export concepts may not close exactly against eSett production/consumption definitions.
