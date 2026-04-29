import 'dart:convert';
import 'package:flutter_application_1/models/estacion.dart';
import 'package:http/http.dart' as http;

class ApiService {
  // CAMBIO CLAVE: Para Chrome usamos localhost, no 10.0.2.2
  final String baseUrl = "http://localhost:8000/estaciones/";

  Future<List<Estacion>> fetchEstaciones() async {
    try {
      final response = await http.get(Uri.parse(baseUrl));

      if (response.statusCode == 200) {
        List jsonResponse = json.decode(response.body);
        return jsonResponse.map((data) => Estacion.fromJson(data)).toList();
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      // Esto te ayudará a ver errores de red en la consola de Flutter
      throw Exception('Fallo de conexión: $e');
    }
  }
}