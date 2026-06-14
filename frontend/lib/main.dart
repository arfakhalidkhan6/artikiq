import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: 'https://udpasevphntlzxunqthu.supabase.co',
    anonKey:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkcGFzZXZwaG50bHp4dW5xdGh1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyOTM2OTgsImV4cCI6MjA5Mzg2OTY5OH0.1lMeR2QDdf_gk-UYmgUJz4ZEgU_rs_C9bXtyQRb8CcA',
  );
  runApp(const ArtikIQApp());
}