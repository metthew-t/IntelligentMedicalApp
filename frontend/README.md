# Intelligent Medical System - Flutter Frontend

Cross-platform Flutter application for the Intelligent Medical and Hospital Management System.

## Features

- 🏥 **Patient Management** - Complete patient records and history
- 📅 **Appointment Scheduling** - Efficient queue and appointment management
- 💊 **Prescription Management** - Digital prescriptions with safety checks
- 🧪 **Laboratory Integration** - Test orders and results
- 📊 **Clinical Decision Support** - AI-assisted diagnosis
- 🔐 **Secure Authentication** - JWT-based authentication with role-based access
- 📱 **Responsive Design** - Works on web, mobile, and tablet
- 🌍 **Multi-language Support** - English, Amharic, Afaan Oromo

## Prerequisites

- Flutter SDK 3.16 or higher
- Dart 3.2 or higher
- Android Studio / VS Code with Flutter extensions
- For iOS development: Xcode 15+
- For Android development: Android SDK 21+

## Getting Started

### 1. Install Flutter

Follow the official Flutter installation guide for your platform:
https://docs.flutter.dev/get-started/install

Verify installation:
```bash
flutter doctor
```

### 2. Clone and Setup

```bash
# Navigate to frontend directory
cd frontend

# Get dependencies
flutter pub get

# Run code generation (for freezed and json_serializable)
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. Configure API Endpoint

Create a `.env` file in the frontend directory (optional):
```env
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

Or use command line arguments:
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

### 4. Run the Application

**For Web:**
```bash
flutter run -d chrome
```

**For Android:**
```bash
flutter run -d <device-id>
```

**For iOS:**
```bash
flutter run -d <device-id>
```

**List available devices:**
```bash
flutter devices
```

## Project Structure

```
frontend/
├── lib/
│   ├── main.dart                      # Application entry point
│   ├── core/                          # Core functionality
│   │   ├── config/                    # Configuration
│   │   │   └── app_config.dart        # App configuration and constants
│   │   ├── network/                   # Network layer
│   │   │   ├── dio_client.dart        # Dio HTTP client
│   │   │   └── interceptors/          # HTTP interceptors
│   │   │       ├── auth_interceptor.dart
│   │   │       └── error_interceptor.dart
│   │   ├── router/                    # Navigation
│   │   │   └── app_router.dart        # GoRouter configuration
│   │   ├── theme/                     # Theming
│   │   │   └── app_theme.dart         # Material theme configuration
│   │   └── utils/                     # Utilities
│   │       └── logger.dart            # Logging utility
│   ├── features/                      # Feature modules
│   │   ├── auth/                      # Authentication
│   │   │   ├── data/                  # Data layer
│   │   │   ├── domain/                # Domain layer
│   │   │   └── presentation/          # Presentation layer
│   │   ├── dashboard/                 # Dashboard
│   │   ├── patients/                  # Patient management
│   │   ├── encounters/                # Clinical encounters
│   │   ├── prescriptions/             # Prescriptions
│   │   ├── laboratory/                # Laboratory
│   │   ├── pharmacy/                  # Pharmacy
│   │   └── appointments/              # Appointments
│   └── shared/                        # Shared components
│       ├── models/                    # Shared data models
│       ├── widgets/                   # Reusable widgets
│       └── providers/                 # Shared providers
├── assets/                            # Static assets
│   ├── images/                        # Images
│   ├── icons/                         # Icons
│   └── fonts/                         # Custom fonts
├── test/                              # Test files
├── pubspec.yaml                       # Dependencies
└── README.md                          # This file
```

## Architecture

This project follows **Clean Architecture** principles with **Feature-First** organization:

- **Presentation Layer**: UI components, screens, and state management (Riverpod)
- **Domain Layer**: Business logic, entities, and use cases
- **Data Layer**: API clients, repositories, and data models

### State Management

We use **Riverpod** for state management:

```dart
// Define a provider
final patientListProvider = FutureProvider<List<Patient>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  return await apiClient.getPatients();
});

// Use in widget
class PatientListScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patientsAsync = ref.watch(patientListProvider);
    
    return patientsAsync.when(
      data: (patients) => ListView.builder(...),
      loading: () => CircularProgressIndicator(),
      error: (error, stack) => ErrorWidget(error),
    );
  }
}
```

## Key Dependencies

| Package | Purpose |
|---------|---------|
| flutter_riverpod | State management |
| go_router | Navigation and routing |
| dio | HTTP client |
| flutter_secure_storage | Secure token storage |
| flutter_form_builder | Form handling |
| freezed | Immutable models |
| json_serializable | JSON serialization |
| fl_chart | Charts and graphs |
| cached_network_image | Image caching |

## Code Generation

This project uses code generation for models and API clients:

```bash
# Run code generation
flutter pub run build_runner build

# Watch for changes and regenerate
flutter pub run build_runner watch

# Delete conflicting outputs
flutter pub run build_runner build --delete-conflicting-outputs
```

## Testing

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# View coverage report (requires lcov)
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

## Building for Production

### Android APK
```bash
flutter build apk --release
```

### Android App Bundle
```bash
flutter build appbundle --release
```

### iOS
```bash
flutter build ios --release
```

### Web
```bash
flutter build web --release
```

Output locations:
- Android: `build/app/outputs/`
- iOS: `build/ios/`
- Web: `build/web/`

## Configuration

### API Endpoints

Configure in `lib/core/config/app_config.dart`:

```dart
static const String baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);
```

### Environment Variables

Pass via command line:
```bash
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

Or create different run configurations in your IDE.

## Common Tasks

### Add a New Screen

1. Create screen file in appropriate feature folder
2. Add route in `lib/core/router/app_router.dart`
3. Update drawer/navigation if needed

### Add a New API Endpoint

1. Create data model in `features/<feature>/data/models/`
2. Create API service method
3. Create provider in presentation layer
4. Use provider in UI

### Add Shared Widget

1. Create widget in `lib/shared/widgets/`
2. Export from index file
3. Import and use in screens

## Troubleshooting

### Build Runner Issues

```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Dio/Network Issues

- Check `AppConfig.baseUrl` is correct
- Verify backend is running
- Check network permissions in AndroidManifest.xml / Info.plist

### State Not Updating

- Ensure using `ConsumerWidget` or `Consumer`
- Check provider is properly defined
- Verify provider dependencies

### Platform-Specific Issues

**Android:**
- Check `android/app/build.gradle` minSdkVersion (21+)
- Verify internet permission in AndroidManifest.xml

**iOS:**
- Check Info.plist for required permissions
- Run `pod install` in ios/ directory if needed

**Web:**
- CORS issues: Backend must allow frontend origin
- Check browser console for errors

## Performance Optimization

1. **Images**: Use `cached_network_image` for network images
2. **Lists**: Use `ListView.builder` for large lists
3. **State**: Keep provider scope minimal
4. **Build**: Profile with `flutter run --profile`

## Debugging

```bash
# Run in debug mode
flutter run

# Run in profile mode (performance)
flutter run --profile

# Run in release mode
flutter run --release

# DevTools
flutter pub global activate devtools
flutter pub global run devtools
```

## Code Style

We follow Flutter's official style guide:
https://dart.dev/guides/language/effective-dart

```bash
# Format code
flutter format .

# Analyze code
flutter analyze

# Run linter
flutter pub run flutter_lints
```

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Format and analyze code
5. Submit pull request

## Security

- Never commit `.env` files
- Keep API keys secure
- Use `flutter_secure_storage` for sensitive data
- Always validate user input
- Implement proper error handling

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Riverpod Documentation](https://riverpod.dev/)
- [Go Router Documentation](https://pub.dev/packages/go_router)
- [Dio Documentation](https://pub.dev/packages/dio)

## Support

For issues and questions:
- Check documentation
- Review API documentation at backend `/api/docs/`
- Contact development team

---

**Last Updated**: 2026-10-19  
**Version**: 1.0.0
