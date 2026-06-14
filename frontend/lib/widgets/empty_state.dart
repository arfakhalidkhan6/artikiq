import 'package:flutter/material.dart';

class EmptyState extends StatelessWidget {
  const EmptyState({super.key});

  // Prompt suggestions shown as clickable chips
  // These are common SLP research questions
  static const List<String> _suggestions = [
    "What is apraxia of speech?",
    "Explain phonological disorders in children",
    "What are AAC devices used for?",
    "Describe stuttering intervention techniques",
  ];

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Logo area
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: const Color(0xFF2A9D8F).withOpacity(0.08),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.spatial_audio_off_rounded,
              size: 36,
              color: Color(0xFF2A9D8F),
            ),
          ),

          const SizedBox(height: 24),

          // Title
          const Text(
            "ArtikIQ Research Engine",
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: Color(0xFF2D3748),
            ),
          ),

          const SizedBox(height: 8),

          // Subtitle
          const Text(
            "Ask anything from the SLP clinical knowledge base",
            style: TextStyle(
              fontSize: 14,
              color: Color(0xFF64748B),
              height: 1.5,
            ),
          ),

          const SizedBox(height: 40),

          // Suggestion chips
          Wrap(
            spacing: 12,
            runSpacing: 12,
            alignment: WrapAlignment.center,
            children: _suggestions.map((suggestion) {
              return _SuggestionChip(label: suggestion);
            }).toList(),
          ),
        ],
      ),
    );
  }
}

// Small private widget — only used inside this file
// Shows one clickable prompt suggestion
class _SuggestionChip extends StatelessWidget {
  final String label;

  const _SuggestionChip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 13,
          color: Color(0xFF2D3748),
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
