import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/estacion.dart';

void main() => runApp(const SmatApp());

class SmatApp extends StatelessWidget {
  const SmatApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SMAT - Live Update',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.blue),
      home: const EstacionesPage(),
    );
  }
}

class EstacionesPage extends StatefulWidget {
  const EstacionesPage({super.key});

  @override
  State<EstacionesPage> createState() => _EstacionesPageState();
}

class _EstacionesPageState extends State<EstacionesPage> {
  // 2. Lógica de Refresco: Definimos el Future como una variable de estado
  late Future<List<Estacion>> futureEstaciones;

  @override
  void initState() {
    super.initState();
    // Carga inicial de datos
    futureEstaciones = ApiService().fetchEstaciones();
  }

  // Esta función es el corazón del reto: vuelve a llamar a la API y actualiza la UI
  void _refreshData() {
    setState(() {
      futureEstaciones = ApiService().fetchEstaciones();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SMAT - Monitoreo Real Time'),
        centerTitle: true,
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No hay datos.'));
          }

          return ListView.builder(
            itemCount: snapshot.data!.length,
            itemBuilder: (context, index) {
              final estacion = snapshot.data![index];
              return ListTile(
                leading: const Icon(Icons.satellite_alt, color: Colors.blue),
                title: Text(estacion.nombre),
                subtitle: Text(estacion.ubicacion),
              );
            },
          );
        },
      ),
      // 1. Añadir un FloatingActionButton: El botón con icono de refrescar
      floatingActionButton: FloatingActionButton(
        onPressed: _refreshData, // Ejecuta la lógica de refresco
        tooltip: 'Refrescar Estaciones',
        child: const Icon(Icons.refresh),
      ),
    );
  }
}