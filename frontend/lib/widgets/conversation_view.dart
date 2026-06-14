import 'package:flutter/material.dart';
import '../models/rag_response.dart';
import 'chat_message.dart';

class ConversationView extends StatefulWidget {
  final List<Map<String, dynamic>> messages;
  final int? selectedMessageIndex;
  final Function(int index, List<Citation> citations) onMessageTap;

  const ConversationView({
    super.key,
    required this.messages,
    required this.selectedMessageIndex,
    required this.onMessageTap,
  });

  @override
  State<ConversationView> createState() => _ConversationViewState();
}

class _ConversationViewState extends State<ConversationView> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(ConversationView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.messages.length != oldWidget.messages.length) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 20),
      itemCount: widget.messages.length,
      itemBuilder: (context, index) {
        final msg = widget.messages[index];
        final List<Citation> citations = List<Citation>.from(
          msg['citations'] ?? [],
        );
        final bool isSelected = widget.selectedMessageIndex == index;

        return Center(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 800),
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: ChatMessage(
              message: msg,
              isSelected: isSelected,
              onTap: citations.isNotEmpty
                  ? () => widget.onMessageTap(index, citations)
                  : null,
            ),
          ),
        );
      },
    );
  }
}
