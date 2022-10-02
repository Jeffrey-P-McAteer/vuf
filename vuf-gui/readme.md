# Setup steps

 - Have `dotnet` tools installed
 - `dotnet new --install Avalonia.Templates`
 - `sudo dotnet workload install wasm-tools` (required by Avalonia apparently)
 - `dotnet new avalonia.app` (dumps a crap-ton of config files all over the CWD)


# Running

 - `dotnet run --configuration Release --runtime win-x64`
 - `dotnet run --configuration Release --runtime linux-x64`
 - `dotnet run --configuration Release --runtime osx-x64`

# Cross-compiling

See https://learn.microsoft.com/en-us/dotnet/core/rid-catalog

 - `dotnet build --self-contained --configuration Release --runtime win-x64`
 - `dotnet build --self-contained --configuration Release --runtime linux-x64`
 - `dotnet build --self-contained --configuration Release --runtime linux-musl-x64`
 - `dotnet build --self-contained --configuration Release --runtime osx-x64`


 - `dotnet publish --self-contained --configuration Release --runtime win-x64`
 - `dotnet publish --self-contained --configuration Release --runtime linux-x64`
 - `dotnet publish --self-contained --configuration Release --runtime linux-musl-x64`
 - `dotnet publish --self-contained --configuration Release --runtime osx-x64`

