import 'dart:convert';
import 'dart:async';
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

  // Streaming version — yields chunks as they arrive from the backend
  Stream<Map<String, dynamic>> askStream(String question) async* {
    final request = http.Request('POST', Uri.parse('$baseUrl/api/query/stream'));
    request.headers['Content-Type'] = 'application/json';
    request.body = jsonEncode({'query': question});

    final client = http.Client();
    final streamedResponse = await client.send(request);

    String buffer = '';

    await for (final chunk in streamedResponse.stream.transform(utf8.decoder)) {
      buffer += chunk;

      while (buffer.contains('\n\n')) {
        final index = buffer.indexOf('\n\n');
        final rawEvent = buffer.substring(0, index);
        buffer = buffer.substring(index + 2);

        if (rawEvent.startsWith('data: ')) {
          final jsonStr = rawEvent.substring(6);
          try {
            final data = jsonDecode(jsonStr);
            yield data;
          } catch (e) {
            // skip malformed chunk
          }
        }
      }
    }

    client.close();
  }
}