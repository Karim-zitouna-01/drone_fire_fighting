# services/data_interpreter.py

class DataInterpreter:
    """
    Process raw sensor data + context to estimate real environmental danger.
    """

    @staticmethod
    def estimate_temperature(temp_sensor: float, distance_fire_m: float) -> float:
        """
        Estimate real temperature based on sensor + proximity to fire.
        """
        if distance_fire_m <= 0:
            distance_fire_m = 0.1

        # Example formula — adjustable later
        fire_factor = 50 / distance_fire_m  
        return temp_sensor + fire_factor

    @staticmethod
    def estimate_co2(co2_sensor: float, distance_fire_m: float) -> float:
        """
        Estimate real CO2 concentration using sensor + distance from fire.
        """
        if distance_fire_m <= 0:
            distance_fire_m = 0.1

        fire_factor = 100 / distance_fire_m
        return co2_sensor + fire_factor

    @staticmethod
    def interpret_data(temp_sensor: float, co2_sensor: float, distance_fire_m: float) -> dict:
        """
        Combine temperature + CO2 interpretation in one result.
        """
        # real_temp = DataInterpreter.estimate_temperature(temp_sensor, distance_fire_m)
        # real_co2 = DataInterpreter.estimate_co2(co2_sensor, distance_fire_m)
        real_temp = temp_sensor
        real_co2 = co2_sensor
        return {
            "real_temp": real_temp,
            "real_co2": real_co2
        }
