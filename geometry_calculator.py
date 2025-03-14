import math

class GeometryCalculator:
    @staticmethod
    def format_value(value):
        if value == int(value):
            return str(int(value))
        formatted = f"{value:.4f}"
        formatted = formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
        return formatted

    @staticmethod
    def calculate_parallelepiped_properties(params):
        width = params["width"]
        height = params["height"]
        depth = params["depth"]
        volume = width * height * depth
        front_back_area = width * height
        top_bottom_area = width * depth
        left_right_area = height * depth
        total_area = 2 * (front_back_area + top_bottom_area + left_right_area)
        face_areas = {
            "Frente": front_back_area,
            "Trás": front_back_area,
            "Topo": top_bottom_area,
            "Base": top_bottom_area,
            "Esquerda": left_right_area,
            "Direita": left_right_area
        }
        faces = {
            "Frente/Trás": front_back_area,
            "Topo/Base": top_bottom_area,
            "Esquerda/Direita": left_right_area
        }
        return {
            "volume": volume,
            "faces": faces,
            "face_areas": face_areas,
            "total_area": total_area
        }

    @staticmethod
    def calculate_pyramid_properties(params):
        width = params["width"]
        height = params["height"]
        depth = params["depth"]
        base_area = width * depth
        volume = (1/3) * base_area * height
        base_face_area = base_area
        half_width = width / 2
        half_depth = depth / 2
        # Calcula as geratrizes para os lados diferentes:
        generatriz_front_back = math.sqrt(height**2 + half_depth**2)
        generatriz_left_right = math.sqrt(height**2 + half_width**2)
        front_back_face_area = (width * generatriz_front_back) / 2
        left_right_face_area = (depth * generatriz_left_right) / 2
        total_area = base_face_area + 2 * front_back_face_area + 2 * left_right_face_area
        face_areas = {
            "Base": base_face_area,
            "Frente": front_back_face_area,
            "Trás": front_back_face_area,
            "Esquerda": left_right_face_area,
            "Direita": left_right_face_area
        }
        faces = {
            "Base": base_face_area,
            "Frente/Trás": front_back_face_area,
            "Esquerda/Direita": left_right_face_area
        }
        return {
            "volume": volume,
            "faces": faces,
            "face_areas": face_areas,
            "total_area": total_area,
            "height": height,
            "geratriz_front_back": generatriz_front_back,
            "geratriz_left_right": generatriz_left_right
        }