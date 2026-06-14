import 'package:flutter/material.dart';
import '../app.dart';
import '../models/rag_response.dart';
import '../services/query_service.dart';
import '../widgets/header.dart';
import '../widgets/empty_state.dart';
import '../widgets/conversation_view.dart';
import '../widgets/source_panel.dart';
import '../widgets/query_input_bar.dart';
import '../widgets/session_drawer.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final QueryService _queryService = QueryService();
  final TextEditingController _inputController = TextEditingController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  bool _isLoading = false;
  String? _currentThreadId;
  List<Map<String, dynamic>> _messages = [];
  List<Citation> _currentCitations = [];
  List<Map<String, dynamic>> _sessionThreads = [];
  int? _selectedMessageIndex;

  @override
  void initState() {
    super.initState();
    _loadSessionThreads();
  }

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  // ── Supabase: load all chat sessions for sidebar ──────────────────────────

  Future<void> _loadSessionThreads() async {
    try {
      final userId = supabase.auth.currentUser?.id;
      if (userId == null) return;
      final List<dynamic> data = await supabase
          .from('chat_threads')
          .select()
          .eq('user_id', userId)
          .order('created_at', ascending: false);
      setState(() => _sessionThreads = List<Map<String, dynamic>>.from(data));
    } catch (e) {}
  }

  Future<void> _deleteSession(String threadId, int index) async {
    try {
      await supabase.from('chat_threads').delete().eq('id', threadId);
      setState(() {
        _sessionThreads.removeAt(index);
        if (_currentThreadId == threadId) _resetChat();
      });
    } catch (e) {}
  }

  Future<void> _openSession(String threadId) async {
    setState(() {
      _isLoading = true;
      _currentThreadId = threadId;
      _messages = [];
      _currentCitations = [];
      _selectedMessageIndex = null;
    });
    try {
      final List<dynamic> data = await supabase
          .from('chat_messages')
          .select()
          .eq('thread_id', threadId)
          .order('created_at', ascending: true);

      setState(() {
        _messages = data.map((m) {
          List<Citation> citations = [];
          if (m['citations'] != null) {
            citations = (m['citations'] as List)
                .map((c) => Citation.fromJson(Map<String, dynamic>.from(c)))
                .toList();
          }
          return {
            'sender': m['sender'],
            'text': m['message_text'],
            'citations': citations,
          };
        }).toList();

        // Show citations from the last bot message that has them
        for (int i = _messages.length - 1; i >= 0; i--) {
          final List<Citation> cits = List<Citation>.from(
            _messages[i]['citations'] ?? [],
          );
          if (cits.isNotEmpty) {
            _currentCitations = cits;
            _selectedMessageIndex = i;
            break;
          }
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
    _scaffoldKey.currentState?.closeDrawer();
  }

  // ── Send question to backend ───────────────────────────────────────────────

  Future<void> _sendQuestion(String question) async {
    if (question.trim().isEmpty) return;

    final int userMsgIndex = _messages.length;
    setState(() {
      _messages.add({
        'sender': 'user',
        'text': question,
        'citations': <Citation>[],
      });
      _isLoading = true;
    });

    try {
      _currentThreadId ??= await _createThread(question);

      await supabase.from('chat_messages').insert({
        'thread_id': _currentThreadId,
        'sender': 'user',
        'message_text': question,
        'citations': [],
      });

      final response = await _queryService.ask(question);

      await supabase.from('chat_messages').insert({
        'thread_id': _currentThreadId,
        'sender': 'bot',
        'message_text': response.answer,
        'citations': response.citations.map((c) => c.toJson()).toList(),
      });

      final int botMsgIndex = _messages.length;
      final bool hasCitations = response.citations.isNotEmpty;

      setState(() {
        _messages.add({
          'sender': 'bot',
          'text': response.answer,
          'citations': response.citations,
        });

        if (hasCitations) {
          _messages[userMsgIndex]['citations'] = response.citations;
          _currentCitations = response.citations;
          _selectedMessageIndex = botMsgIndex;
        } else {
          _currentCitations = [];
          _selectedMessageIndex = null;
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add({
          'sender': 'bot',
          'text': 'Could not reach ArtikIQ backend.',
          'citations': <Citation>[],
        });
        _isLoading = false;
        _currentCitations = [];
      });
    }
  }

  Future<String> _createThread(String firstQuestion) async {
    final userId = supabase.auth.currentUser?.id;
    final String title = firstQuestion.length > 26
        ? '${firstQuestion.substring(0, 26)}...'
        : firstQuestion;
    final response = await supabase
        .from('chat_threads')
        .insert({'user_id': userId, 'title': title})
        .select()
        .single();
    _loadSessionThreads();
    return response['id'].toString();
  }

  void _resetChat() {
    setState(() {
      _currentThreadId = null;
      _messages = [];
      _currentCitations = [];
      _selectedMessageIndex = null;
    });
  }

  // ── UI ─────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: const Color(0xFFF8FAFB),
      drawer: SessionDrawer(
        threads: _sessionThreads,
        currentThreadId: _currentThreadId,
        onDeleteSession: _deleteSession,
        onOpenSession: _openSession,
        onNewChat: () {
          _resetChat();
          _scaffoldKey.currentState?.closeDrawer();
        },
      ),
      body: Row(
        children: [
          // Left: main chat area
          Expanded(
            flex: 8,
            child: Column(
              children: [
                Header(
                  onMenuTap: () => _scaffoldKey.currentState?.openDrawer(),
                  onLogoutTap: () => supabase.auth.signOut(),
                ),
                Expanded(
                  child: _messages.isEmpty
                      ? const EmptyState()
                      : ConversationView(
                          messages: _messages,
                          selectedMessageIndex: _selectedMessageIndex,
                          onMessageTap: (index, citations) {
                            setState(() {
                              _currentCitations = citations;
                              _selectedMessageIndex = index;
                            });
                          },
                        ),
                ),
                if (_isLoading)
                  const LinearProgressIndicator(color: Color(0xFF2A9D8F)),
                QueryInputBar(
                  controller: _inputController,
                  onSubmit: (question) {
                    _sendQuestion(question);
                    _inputController.clear();
                  },
                ),
              ],
            ),
          ),
          // Right: citation panel — only shows when citations exist
          if (_currentCitations.isNotEmpty)
            Expanded(flex: 2, child: SourcePanel(citations: _currentCitations)),
        ],
      ),
    );
  }
}
