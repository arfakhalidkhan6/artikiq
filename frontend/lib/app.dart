import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/auth_gate.dart';

// Global supabase client — accessible anywhere in the app
final supabase = Supabase.instance.client;

class ArtikIQApp extends StatelessWidget {
  const ArtikIQApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ArtikIQ Research Engine',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.light().copyWith(
        // Background: off-white, easy on eyes
        scaffoldBackgroundColor: const Color(0xFFF8FAFB),
        primaryColor: const Color(0xFF2A9D8F),
        textTheme: const TextTheme(
          // Body text: soft dark grey, never pure black
          bodyMedium: TextStyle(
            color: Color(0xFF2D3748),
            fontSize: 14.5,
            height: 1.6,
          ),
        ),
      ),
      home: const AuthGate(),
    );
  }
}
