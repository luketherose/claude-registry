# C# project layout and build settings

> Reference doc for `developer-csharp`. Read at runtime when scaffolding a new
> project or adding a project to an existing solution. The coding standards that
> apply to every file (nullability, async, DI, logging, error handling, Web API,
> EF Core, testing) stay in the agent body. The solution skeleton and the
> `.csproj` property set live here.

## Project structure

For an ASP.NET Core Web API:

```
.
├── Acme.Orders.sln
├── src/
│   ├── Acme.Orders.Api/                ─ controllers / minimal APIs, DTOs
│   ├── Acme.Orders.Application/        ─ business logic (commands, queries, MediatR if used)
│   ├── Acme.Orders.Domain/             ─ entities, value objects, domain events
│   └── Acme.Orders.Infrastructure/     ─ EF Core, external clients, persistence
├── tests/
│   ├── Acme.Orders.UnitTests/
│   ├── Acme.Orders.IntegrationTests/
│   └── Acme.Orders.ArchitectureTests/  ─ NetArchTest assertions
└── .editorconfig
```

For smaller services collapse Application + Domain into a single project.

## Compiler and analyzer settings

In every `.csproj`:

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>
```

Pin Roslyn analyzers in `Directory.Packages.props` and use central package
management (`<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`).
