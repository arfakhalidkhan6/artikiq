import 'package:flutter/material.dart';

class SourceBadgeText extends StatelessWidget {
  final String text;
  final Color baseColor;

  const SourceBadgeText({
    super.key,
    required this.text,
    required this.baseColor,
  });

  @override
  Widget build(BuildContext context) {
    final RegExp sourceRegex = RegExp(r'\[Source\s+(\d+)\]');
    final List<InlineSpan> spans = [];

    int start = 0;
    for (final match in sourceRegex.allMatches(text)) {
      // Text before the badge
      if (match.start > start) {
        spans.add(
          TextSpan(
            text: text.substring(start, match.start),
            style: TextStyle(color: baseColor, fontSize: 14.5, height: 1.6),
          ),
        );
      }

      // The badge itself
      spans.add(
        WidgetSpan(
          alignment: PlaceholderAlignment.middle,
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 3),
            padding: const EdgeInsets.all(6),
            decoration: const BoxDecoration(
              color: Color(0xFF2A9D8F),
              shape: BoxShape.circle,
            ),
            child: Text(
              match.group(1) ?? '',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      );
      start = match.end;
    }

    // Remaining text after last badge
    if (start < text.length) {
      spans.add(
        TextSpan(
          text: text.substring(start),
          style: TextStyle(color: baseColor, fontSize: 14.5, height: 1.6),
        ),
      );
    }

    return RichText(text: TextSpan(children: spans));
  }
}
