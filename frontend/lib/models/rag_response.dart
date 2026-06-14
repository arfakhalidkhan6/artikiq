class Citation {
  final String book;
  final int page;
  final String doi;

  Citation({required this.book, required this.page, required this.doi});

  // Converts raw JSON from backend into a Citation object
  factory Citation.fromJson(Map<String, dynamic> json) {
    return Citation(
      book: json['book']?.toString() ?? 'Unknown Text',
      page: json['page'] is int
          ? json['page']
          : int.tryParse(json['page']?.toString() ?? '0') ?? 0,
      doi: json['doi']?.toString() ?? '',
    );
  }

  // Converts Citation object back to JSON (for saving to Supabase)
  Map<String, dynamic> toJson() => {'book': book, 'page': page, 'doi': doi};
}

class RagResponse {
  final String answer;
  final List<Citation> citations;

  RagResponse({required this.answer, required this.citations});

  // Converts raw JSON from backend into a RagResponse object
  factory RagResponse.fromJson(Map<String, dynamic> json) {
    final list = json['citations'] as List? ?? [];
    return RagResponse(
      answer: json['answer']?.toString() ?? '',
      citations: list
          .map((i) => Citation.fromJson(Map<String, dynamic>.from(i)))
          .toList(),
    );
  }
}
