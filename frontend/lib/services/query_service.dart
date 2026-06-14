import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/rag_response.dart';

class QueryService {
  // Change this to your Railway URL after deployment
  final String baseUrl = 'http://127.0.0.1:8000';

  Future<RagResponse> ask(String question) async {
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/api/query'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'query': question}),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        return RagResponse.fromJson(jsonDecode(response.body));
      }

      // Backend responded but with an error status
      return RagResponse(
        answer: "Backend error. Status: ${response.statusCode}",
        citations: [],
      );
    } catch (e) {
      // Network failed or timeout
      return RagResponse(
        answer: "Could not connect to ArtikIQ backend.",
        citations: [],
      );
    }
  }
}