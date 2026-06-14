import 'package:flutter/material.dart';
import '../app.dart';
import 'sign_in_screen.dart';
import 'sign_up_screen.dart';
import 'chat_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();

  bool _isSignUpMode = false;
  bool _isLoading = false;
  String? _selectedGender;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _clearFields() {
    _emailController.clear();
    _passwordController.clear();
    _nameController.clear();
  }

  Future<void> _handleSignIn() async {
    setState(() => _isLoading = true);
    try {
      await supabase.auth.signInWithPassword(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
    } catch (e) {}
    setState(() => _isLoading = false);
  }

  Future<void> _handleSignUp() async {
    setState(() => _isLoading = true);
    try {
      final res = await supabase.auth.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      if (res.user?.id != null) {
        await supabase.from('profiles').insert({
          'id': res.user!.id,
          'full_name': _nameController.text.trim(),
          'gender': _selectedGender,
          'updated_at': DateTime.now().toIso8601String(),
        });
        _clearFields();
        setState(() => _isSignUpMode = false);
      }
    } catch (e) {}
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    // StreamBuilder listens to Supabase auth state in real time
    // If session exists → go to ChatScreen
    // If no session → show login/signup
    return StreamBuilder(
      stream: supabase.auth.onAuthStateChange,
      builder: (context, snapshot) {
        final session = snapshot.data?.session;

        if (session != null) {
          return const ChatScreen();
        }

        return Scaffold(
          backgroundColor: const Color(0xFFF8FAFB),
          body: Center(
            child: SingleChildScrollView(
              child: _isSignUpMode
                  ? SignUpScreen(
                      key: UniqueKey(),
                      nameController: _nameController,
                      emailController: _emailController,
                      passwordController: _passwordController,
                      selectedGender: _selectedGender,
                      isLoading: _isLoading,
                      onGenderChanged: (val) =>
                          setState(() => _selectedGender = val),
                      onSignUpPressed: _handleSignUp,
                      onToggleMode: () {
                        _clearFields();
                        setState(() => _isSignUpMode = false);
                      },
                    )
                  : SignInScreen(
                      key: UniqueKey(),
                      emailController: _emailController,
                      passwordController: _passwordController,
                      isLoading: _isLoading,
                      onSignInPressed: _handleSignIn,
                      onToggleMode: () {
                        _clearFields();
                        setState(() => _isSignUpMode = true);
                      },
                    ),
            ),
          ),
        );
      },
    );
  }
}
