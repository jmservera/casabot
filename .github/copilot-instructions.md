# Copilot Instructions for CasaBot

## Project Overview

CasaBot is a modern chat interface for Home Assistant built with C# and Blazor Server. It provides both text and audio interactions with Home Assistant through a clean, responsive web interface.

### Key Features
- **Text Chat**: Real-time messaging interface with Home Assistant
- **Audio Support**: Voice input and audio response capabilities
- **Home Assistant Integration**: Uses MCP (Model Context Protocol) for communication
- **Multi-Architecture Support**: Builds for amd64, aarch64, and armv7
- **Container Ready**: Designed as a Home Assistant add-on

## Architecture

This is a **Blazor Server** application with the following structure:

```
src/
├── CasaBot.csproj          # Project file with dependencies
├── Program.cs              # Application startup and DI configuration
├── Components/
│   ├── App.razor           # Root Blazor component
│   ├── Routes.razor        # Routing configuration
│   ├── Layout/             # Layout components
│   └── Pages/              # Page components (Chat.razor is main page)
├── Models/
│   └── ChatModels.cs       # Data transfer objects
├── Services/
│   ├── IChatService.cs     # Chat service interface
│   ├── ChatService.cs      # Chat implementation
│   ├── IMcpService.cs      # MCP service interface
│   └── McpService.cs       # Home Assistant MCP integration
└── wwwroot/                # Static web assets
```

### Technology Stack
- **.NET 8.0** - Target framework
- **ASP.NET Core** - Web framework
- **Blazor Server** - Interactive UI framework with SignalR
- **System.Text.Json** - JSON serialization
- **Microsoft.Extensions.Http** - HTTP client factory

## Development Setup

### Prerequisites
- .NET 8.0 SDK or later
- Home Assistant instance with MCP server configured (for full functionality)

### Local Development
```bash
# Restore dependencies
dotnet restore src/CasaBot.csproj

# Build the project
dotnet build src/CasaBot.csproj

# Run in development mode
dotnet run --project src/CasaBot.csproj

# The app will be available at http://localhost:8000
```

### Build Configuration
- **Default Port**: 8000 (configurable via `ASPNETCORE_URLS`)
- **Reverse Proxy Ready**: Configured for forwarded headers
- **Health Check**: Available at `/health` endpoint

## Coding Standards

### C# Guidelines
- **Nullable Reference Types**: Enabled project-wide
- **Implicit Usings**: Enabled for cleaner code
- **Async/Await**: Use for all I/O operations
- **Dependency Injection**: Register services in `Program.cs`
- **Interface Segregation**: Use interfaces for all services

### Blazor Patterns
- **Interactive Server**: Use `@rendermode InteractiveServer` for interactive components
- **Component Lifecycle**: Implement `IDisposable` when needed
- **State Management**: Use scoped services for component state
- **JavaScript Interop**: Use `IJSRuntime` for browser APIs

### File Organization
- **Models**: Place in `Models/` namespace, use record types for immutable data
- **Services**: Implement interface + concrete class pattern
- **Components**: Use `.razor` files in `Components/Pages/` or `Components/Layout/`
- **CSS**: Component-specific styles in `<style>` sections

## Architecture Patterns

### Service Layer
```csharp
// Service registration in Program.cs
builder.Services.AddScoped<IChatService, ChatService>();
builder.Services.AddScoped<IMcpService, McpService>();

// Interface-first design
public interface IChatService
{
    Task<ChatResponse> SendMessageAsync(string message);
    Task<ChatResponse> SendAudioAsync(string audioData);
}
```

### Model Design
- Use simple POCOs for data transfer
- Include timestamp and metadata properties
- Nullable properties for optional data

### Component Structure
- Page components use `@page` directive
- Inject services with `@inject`
- Use `@bind` for two-way data binding
- Handle async operations properly in event handlers

## Testing Guidelines

Currently, there are no automated tests in the repository. When adding tests:

### Recommended Testing Structure
```
tests/
├── CasaBot.Tests.csproj
├── Services/
│   ├── ChatServiceTests.cs
│   └── McpServiceTests.cs
└── Components/
    └── ChatComponentTests.cs
```

### Testing Frameworks
- **xUnit** - Unit testing framework
- **bUnit** - Blazor component testing
- **Moq** - Mocking framework
- **Microsoft.AspNetCore.Mvc.Testing** - Integration testing

## Deployment

### Multi-Architecture Build
The CI/CD pipeline builds for three architectures:
- **amd64** (`linux-musl-x64`)
- **aarch64** (`linux-musl-arm64`) 
- **armv7** (`linux-musl-arm`)

### Build Commands
```bash
# Production build
dotnet publish src/CasaBot.csproj \
  --configuration Release \
  --runtime linux-musl-x64 \
  --self-contained true \
  --output ./publish
```

### Container Deployment
- Designed as a Home Assistant add-on
- Add-on repository: [jmservera/addon-casabot](https://github.com/jmservera/addon-casabot)
- Listens on port 8000 by default
- Configured for reverse proxy deployment

## Home Assistant Integration

### MCP Protocol
- Uses Model Context Protocol for Home Assistant communication
- Service interface: `IMcpService`
- HTTP-based communication through `HttpClient`

### Configuration
- Connection settings via `IConfiguration`
- Logging through `ILogger<T>`
- Error handling for connection failures

## Common Development Tasks

### Adding a New Service
1. Create interface in `Services/I{ServiceName}.cs`
2. Implement in `Services/{ServiceName}.cs`
3. Register in `Program.cs`: `builder.Services.AddScoped<I{ServiceName}, {ServiceName}>()`
4. Inject where needed: `@inject I{ServiceName} ServiceName`

### Adding a New Page
1. Create `Components/Pages/{PageName}.razor`
2. Add `@page "/route"` directive
3. Use `@rendermode InteractiveServer` for interactivity
4. Add navigation link in layout if needed

### Working with Audio
- Use JavaScript interop for audio recording
- Store audio as base64 or blob URLs
- Handle browser permissions for microphone access

### Styling Components
- Use CSS isolation with `{ComponentName}.razor.css`
- Or add styles in `<style>` section within component
- Bootstrap-like utility classes are available

## Performance Considerations

- **SignalR Connection**: Blazor Server uses SignalR for real-time updates
- **Stateful Components**: Components maintain state on server
- **Network Dependency**: UI responsiveness depends on connection quality
- **Memory Management**: Dispose of resources in component lifecycle

## Security Notes

- **HTTPS**: Configured for reverse proxy scenarios
- **CORS**: Configure if needed for cross-origin requests
- **Authentication**: Currently no authentication implemented
- **Input Validation**: Validate user inputs before processing

## Troubleshooting

### Common Issues
1. **Build Warnings**: Currently one async/await warning in `Chat.razor:256`
2. **Port Conflicts**: Change `ASPNETCORE_URLS` environment variable
3. **SignalR Issues**: Check network connectivity and proxy settings
4. **MCP Connection**: Verify Home Assistant MCP server configuration

### Debugging
- Use `dotnet run` for development with hot reload
- Check browser console for JavaScript errors
- Monitor server logs for MCP communication issues
- Use Visual Studio or VS Code debugger for C# debugging